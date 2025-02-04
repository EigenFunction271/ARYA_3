import os
import pinecone
from dotenv import load_dotenv

load_dotenv()

# Initialize with host
pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment=os.getenv("PINECONE_ENVIRONMENT"),
    host=os.getenv("PINECONE_HOST")
)

# Check connection
print("Available indexes:", pinecone.list_indexes())

# Get index details
index = pinecone.Index("arya-embeddings")
print("\nIndex description:", index.describe_index_stats())

# Print environment details
print("\nEnvironment Details:")
print(f"Environment: {os.getenv('PINECONE_ENVIRONMENT')}")
print(f"Host: {os.getenv('PINECONE_HOST')}") 