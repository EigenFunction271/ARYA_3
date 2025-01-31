from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
import pinecone
import os

# Initialize Pinecone
pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENVIRONMENT"))

def process_uploaded_file(file: UploadFile):
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
    embeddings = OpenAIEmbeddings()
    pinecone_index = Pinecone.from_documents(texts, embeddings, index_name="your-index-name")
    
    return {"message": "File uploaded and processed successfully"}

def query_chatbot(query: str):
    if pinecone_index is None:
        raise HTTPException(status_code=400, detail="No documents uploaded yet")
    
    # Create the QA chain
    qa = RetrievalQA.from_chain_type(
        llm=OpenAI(),
        chain_type="stuff",
        retriever=pinecone_index.as_retriever()
    )
    
    # Get the response
    response = qa.run(query)
    
    return {"response": response}