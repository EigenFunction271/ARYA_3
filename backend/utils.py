from fastapi import HTTPException, UploadFile
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Pinecone
from langchain.chains import RetrievalQA
import pinecone
import os
from llm_config import get_llm, get_embeddings, LLMProvider

# Initialize Pinecone with host
pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"), 
    environment=os.getenv("PINECONE_ENVIRONMENT"),
    host=os.getenv("PINECONE_HOST")
)

# Get current LLM provider from environment
llm_provider_value = os.getenv("LLM_PROVIDER", "mistral").split('#')[0].strip()
current_provider = LLMProvider(llm_provider_value)

# Global variable for Pinecone index
pinecone_index = None

def process_uploaded_file(file: UploadFile):
    global pinecone_index
    if file.content_type != "text/plain":
        raise HTTPException(status_code=400, detail="File must be a text file")
    
    # Save the uploaded file
    file_path = f"uploads/{file.filename}"
    os.makedirs("uploads", exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    
    # Load and split the document
    loader = TextLoader(file_path)
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    
    # Create embeddings and store in Pinecone
    embeddings = get_embeddings(current_provider)
    pinecone_index = Pinecone.from_documents(
        texts, 
        embeddings, 
        index_name=os.getenv("PINECONE_INDEX_NAME", "arya-embeddings")
    )
    
    return {"message": "File uploaded and processed successfully"}

def query_chatbot(query: str):
    global pinecone_index
    if pinecone_index is None:
        raise HTTPException(status_code=400, detail="No documents uploaded yet")
    
    # Create the QA chain with the selected LLM
    qa = RetrievalQA.from_chain_type(
        llm=get_llm(current_provider),
        chain_type="stuff",
        retriever=pinecone_index.as_retriever()
    )
    
    # Get the response
    response = qa.run(query)
    
    return {"response": response}