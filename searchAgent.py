import streamlit as st
from lyzr import ChatBot
import os
import tempfile
from openai import OpenAI
from utils import save_uploaded_file, remove_existing_files
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

data = "data"
os.makedirs(data, exist_ok=True)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chatbot" not in st.session_state:
    st.session_state.chatbot = None

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

if "file_upload_key" not in st.session_state:
    st.session_state.file_upload_key = 0

if "chat" not in st.session_state:
    st.session_state.chat = []

vector_store_params = {
    "vector_store_type": "WeaviateVectorStore",
    "index_name": "RonitPatil"  # first letter should be capital
}

def file_checker():
    file = []
    for filename in os.listdir(data):
        file_path = os.path.join(data, filename)
        file.append(file_path)
    return file

def reset_file_uploader():
    st.session_state.file_upload_key += 1
    st.session_state.uploaded_files = []


@st.cache_resource
def rag_implementation(files):
    with st.spinner("Generating Embeddings...."):
        response = ChatBot.pdf_chat(
            input_files=files,
            vector_store_params=vector_store_params,
        )
    return response
    

# File upload section
with st.sidebar:
    with st.container():
        st.markdown("### Upload Files before asking a question")
        uploaded_files = st.file_uploader("Upload a file",
                                          accept_multiple_files=True,
                                          type=['pdf'],
                                          key=f"file_uploader_{st.session_state.file_upload_key}",
                                          label_visibility='hidden')
        if uploaded_files:
            # for uploaded_file in uploaded_files:
            save_uploaded_file(uploaded_files)
            for uploaded_file in uploaded_files:
                st.session_state.uploaded_files.append(os.path.join(data, uploaded_file.name))
        # Update chatbot with new file(s)
            st.session_state["chatbot"] = rag_implementation(st.session_state.uploaded_files)
            st.success(f"Processed file. You may ask me questions about the file now.")
            st.session_state.uploaded_files = []



def handle_user_input(user_input):
    st.chat_message("user").markdown(user_input)
    response = st.session_state["chatbot"].chat(user_input)
    st.chat_message("assistant").markdown(response)

    st.session_state.chat.append({"role": "user", "content": user_input})
    st.session_state.chat.append({"role": "assistant", "content": response})

# Display chat history
for message in st.session_state.chat:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if uploaded_files:
    if user_input := st.chat_input("Ask me anything"):
        # st.session_state.uploaded_files = []
        handle_user_input(user_input)
