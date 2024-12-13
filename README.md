# ValeoBOT

ValeoBOT is a Streamlit-based chatbot application designed to interact with users and provide intelligent responses using language models. The application supports Retrieval augmented generation and Q&A functionality powered by LangChain, FAISS, and HuggingFace embeddings.

Available preview at: [https://valeobot.streamlit.app](https://valeobot.streamlit.app)
## RAG Pipeline
![Images/RAG_Pipeline.png](Images/RAG_Pipeline.png)

The pdf files in `\Data` are embedded using the `all-MiniLM-L12-V2`model from HuggingFace, the embeddings are then stored in the [FAISS](https://github.com/facebookresearch/faiss) Vectorstore. 

Once the user submits a query, the most relevant chunks of text are selected using similarity search and used as context for llm response. 


## Features

- **Landing Page:** Secure API key entry to authenticate users.
- **Chat Interface:** Interactive chat with conversation history management.
- **Document Retrieval:** Automatically loads and indexes PDF files for question-answering capabilities.
- **Conversation Management:** Save and view previous conversations.



## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/rayaneghilene/ValeoBOT.git
    cd ValeoBOT
    ```

2. Build the project:
    ```ruby
    docker build -t valeobot .
    ```

3. Run the container:
    ```ruby
    docker run -p 8501:8501 valeobot
    ```


if not automatically lanuched, open your web browser and navigate to the URL provided by Streamlit 
[http://localhost:8501](http://localhost:8501).

## Usage guide

1. **Landing Page:**

- Enter your Mistral AI API key and click "Submit" to proceed.


![Images/Prerview.png](Images/Landing_Page.png)

    - Note: If not redirected instantly to the chat interface, press again on the submit button.



2. **Chat Page:**
   - Interact with the chatbot by entering your queries in the chat input.
   - Save conversations for future reference using the "Save Conversation" button.


![Images/Prerview.png](Images/Prerview.png)


3. **Document Retrieval:**
   - The chatbot can answer questions based on the content of the PDF files in the `Data/` folder.

## File Structure

```
.
├── Data/                  # Directory for storing PDF files
├── Images/                # Directory for storing images
├── conversations.json     # File for saving conversation history
├── app.py                 # Main application script
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
└── README_French.md       # French Project documentation
```

## Technologies Used

- **Streamlit:** Interactive UI for the chatbot.
- **LangChain:** Document loading, text splitting, and retrieval QA.
- **FAISS:** Vector store for efficient similarity search.
- **HuggingFace:** Embedding model for document indexing.
- **MistralAI/Ollama:** Language models for generating responses.

## Notes
- The application is designed to handle large PDF datasets; however, performance depends on system resources.


##  Support

Pleas reach out to rayane.ghilene@ensea.fr for any questions, issues, or feedback :)