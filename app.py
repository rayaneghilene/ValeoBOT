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

# api_key= getpass("Type your API Key")
# client = Mistral(api_key=api_key)

# File to save conversations
CONVERSATIONS_FILE = "conversations.json"

## create Vector data
folder_path = 'Data'
@st.cache_resource
def load_pdf():
    pdf_files = glob(f"{folder_path}/*.pdf")
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
    # llm = ChatMistralAI(mistral_api_key=api_key),
    llm= ChatOllama(model="llava:7b"),
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
