import pinecone
from langchain.vectorstores import Pinecone

# Initialize Pinecone
pinecone.init(api_key="YOUR_PINECONE_API_KEY", environment="YOUR_PINECONE_ENVIRONMENT")

# Global variable to store the Pinecone index
pinecone_index = None

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    global pinecone_index
    
    if file.content_type != "text/plain":
        raise HTTPException(status_code=400, detail="File must be a text file")
    
    # Save the uploaded file
    file_path = f"uploads/{file.filename}"
    os.makedirs("uploads", exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # Load and split the document
    loader = TextLoader(file_path)
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    
    # Create embeddings and store in Pinecone
    embeddings = OpenAIEmbeddings()
    pinecone_index = Pinecone.from_documents(texts, embeddings, index_name="your-index-name")
    
    return {"message": "File uploaded and processed successfully"}

@app.post("/chat/")
async def chat(query: str):
    global pinecone_index
    
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