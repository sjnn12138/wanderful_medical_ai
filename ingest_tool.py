import os
import sys
import chromadb
from chromadb.utils import embedding_functions

CHUNK_SIZE = 200
PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "documents"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

def chunk_text(text, chunk_size):
    """Split text into chunks of specified size"""
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def main():
    if len(sys.argv) != 2:
        print("Usage: python ingest_tool.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    # Create document chunks
    chunks = chunk_text(content, CHUNK_SIZE)
    ids = [f"{os.path.basename(file_path)}_{i}" for i in range(len(chunks))]
    
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path=PERSIST_DIR)
    
    # Create or get collection with embedding function
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )
    
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=sentence_transformer_ef
    )
    
    # Add documents to ChromaDB
    try:
        collection.upsert(
            ids=ids,
            documents=chunks
        )
        print(f"Successfully ingested {len(chunks)} chunks from {file_path}")
    except Exception as e:
        print(f"Error ingesting documents: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()