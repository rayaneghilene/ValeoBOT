from langchain_community.document_loaders import PyPDFLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_community.vectorstores import FAISS

import json
from datetime import datetime
import streamlit as st
import ollama
from typing import Dict, Generator
from glob import glob
from mistralai import Mistral
from getpass import getpass
from langchain_community.graphs import Neo4jGraph

if "api_key" not in st.session_state:
    st.session_state.api_key = None

if "page" not in st.session_state:
    st.session_state.page = "landing"  # Start with the landing page

# File to save conversations
CONVERSATIONS_FILE = "conversations.json"
Data_folder_path = 'Data'

##### UI Elements: 
# 1/ Landing Page
def landing_page():
    st.sidebar.image('Images/Valeo_logo.png',  use_container_width='50%')
    st.title("Welcome to the ValeoBOT!")
    st.subheader("Please enter your Mistral AI API Key to proceed.")
    st.subheader("you can get your API Key from [Mistral AI](https://mistral.ai/)")
    api_key = st.text_input("Enter your Key here:", type="password")


    # Submit button
    if st.button("Submit"):
        try:
            # Attempt to validate the API key by calling the LLM
            llm = ChatMistralAI(mistral_api_key=api_key)
            llm.invoke("Hello")  # Test the key with a simple query
            
            # If successful, store the key and navigate to the chat page
            st.session_state.api_key = api_key
            st.session_state.page = "chat"
            st.success("API Key validated! Redirecting to the chat page...")
            return api_key
        except Exception as e:
            # Handle validation failure
            st.warning(f"Invalid API Key: {e}")

def chat_page(api_key):
    ### Load Data
    ## Generate embeddings and create a Vector data
    @st.cache_resource
    def load_pdf():
        pdf_files = glob(f"{Data_folder_path}/*.pdf")
        loaders = [PyPDFLoader(file_path) for file_path in pdf_files]
        # Initialize embedding model
        embeddings = HuggingFaceEmbeddings(model_name='all-MiniLM-L12-V2')
        # Load documents and split into chunks
        docs = []
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=0)
        for loader in loaders:
            docs.extend(text_splitter.split_documents(loader.load()))
        # Create FAISS vector store
        vector_store = FAISS.from_documents(documents=docs, embedding=embeddings)
        return vector_store
    index = load_pdf()


    ### Chain
    chain= RetrievalQA.from_chain_type(
        llm = ChatMistralAI(mistral_api_key=api_key),
        # llm= ChatOllama(model="llava:7b"),
        chain_type ='stuff',
        # retriever= index.vectorstore.as_retriever(),
        retriever= index.as_retriever(),
        input_key='question'
    )
    ### INTERFACE
    st.title('ValeoBOT')

    # Initialize conversation storage
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
        try:
            with open(CONVERSATIONS_FILE, "r") as file:
                st.session_state.conversation_history = json.load(file)
        except FileNotFoundError:
            pass

    # Save conversation to file
    def save_conversation(conversation):
        st.session_state.conversation_history.append(conversation)
        with open(CONVERSATIONS_FILE, "w") as file:
            json.dump(st.session_state.conversation_history, file)

    # Display conversations in sidebar
    st.sidebar.image('Images/Valeo_logo.png',  use_container_width='auto')
    st.sidebar.title("Conversations")
    saved_conversations = {f"Conversation {i+1} ({c['timestamp']})": i for i, c in enumerate(st.session_state.conversation_history)}
    selected_conversation = st.sidebar.selectbox("Select a conversation", list(saved_conversations.keys()))

    # Display selected conversation
    if selected_conversation:
        conversation_index = saved_conversations[selected_conversation]
        st.sidebar.write("Selected Conversation:")
        st.sidebar.write(st.session_state.conversation_history[conversation_index]["messages"])

    if "current_conversation" not in st.session_state:
        st.session_state.current_conversation = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "messages": []}

    for message in st.session_state.current_conversation["messages"]:
        st.chat_message(message['role']).markdown(message['content'])

    # Save button
    if st.button("Save Conversation"):
        save_conversation(st.session_state.current_conversation)
        st.success("Conversation saved!")
        st.session_state.current_conversation = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "messages": []}

    # Input and display chat
    prompt = st.chat_input('How can I help you?')
    if prompt:
        st.session_state.current_conversation["messages"].append({"role": "user", "content": prompt})
        st.chat_message('user').markdown(prompt)
        st.spinner(text='In progress')
        response = chain.run(prompt)
        st.session_state.current_conversation["messages"].append({"role": "assistant", "content": response})
        st.chat_message("assistant").markdown(response)


# Render the appropriate page
if st.session_state.page == "landing":
    st.session_state.api_key = landing_page()
elif st.session_state.page == "chat":
    chat_page(st.session_state.api_key)