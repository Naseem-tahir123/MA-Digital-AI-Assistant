 
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils import load_env

load_env()


embedding_model = OpenAIEmbeddings()

def create_vector_store(data):
    documents = []
    for item in data:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", "!", "?", " ", ""]
        )
        chunks = text_splitter.create_documents([item["content"]])
        for chunk in chunks:
            chunk.metadata = {"url": item["url"]}
            documents.append(chunk)

    vectorstore = FAISS.from_documents(documents, embedding_model)
    vectorstore.save_local("backend/data/faiss_index")
    return vectorstore

def load_vector_store():
    return FAISS.load_local("backend/data/faiss_index", embedding_model, allow_dangerous_deserialization=True)
