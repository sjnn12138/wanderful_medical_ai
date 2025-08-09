import sys
import chromadb
from chromadb.utils import embedding_functions

PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "documents"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DEFAULT_RESULTS = 5

def main():
    if len(sys.argv) < 2:
        print("Usage: python query_tool.py <query> [num_results]")
        print(f"Example: python query_tool.py \"What is the document about?\" {DEFAULT_RESULTS}")
        sys.exit(1)
    
    query = sys.argv[1]
    num_results = DEFAULT_RESULTS
    
    if len(sys.argv) > 2:
        try:
            num_results = int(sys.argv[2])
        except ValueError:
            print(f"Invalid number of results: {sys.argv[2]}. Using default: {DEFAULT_RESULTS}")
    
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path=PERSIST_DIR)
    
    # Get collection with embedding function
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )
    
    try:
        collection = client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=sentence_transformer_ef
        )
    except Exception as e:
        print(f"Error accessing collection: {e}")
        print("Have you run the ingest tool first?")
        sys.exit(1)
    
    # Query ChromaDB
    try:
        results = collection.query(
            query_texts=[query],
            n_results=num_results
        )
        
        print(f"\nTop {num_results} results for query: '{query}'\n")
        print("=" * 80)
        
        for i, (doc, doc_id) in enumerate(zip(results['documents'][0], results['ids'][0]), 1):
            print(f"Result {i} (ID: {doc_id}):")
            print(doc)
            print("-" * 80)
        
        print("=" * 80)
    
    except Exception as e:
        print(f"Error querying database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()