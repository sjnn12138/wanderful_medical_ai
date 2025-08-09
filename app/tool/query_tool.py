from typing import Optional

import chromadb
from chromadb.utils import embedding_functions
from .base import BaseTool, ToolResult

PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "documents"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DEFAULT_RESULTS = 5


class QueryTool(BaseTool):
    name: str = "query"
    description: str = "Query the vector database to find relevant document chunks based on a natural language query."
    parameters: Optional[dict] = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The natural language query to search for"
            },
            "num_results": {
                "type": "integer",
                "description": "Number of results to return",
                "default": DEFAULT_RESULTS
            }
        },
        "required": ["query"]
    }

    async def execute(self, **kwargs) -> ToolResult:
        query = kwargs['query']
        num_results = kwargs.get('num_results', DEFAULT_RESULTS)
        
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
            return ToolResult(error=f"Error accessing collection: {e}\nHave you run the ingest tool first?")
        
        # Query ChromaDB
        try:
            results = collection.query(
                query_texts=[query],
                n_results=num_results
            )
            
            # Format results
            output = f"\nTop {num_results} results for query: '{query}'\n"
            output += "=" * 80 + "\n"
            
            for i, (doc, doc_id) in enumerate(zip(results['documents'][0], results['ids'][0]), 1):
                output += f"Result {i} (ID: {doc_id}):\n"
                output += doc + "\n"
                output += "-" * 80 + "\n"
            
            output += "=" * 80
            return ToolResult(output=output)
        
        except Exception as e:
            return ToolResult(error=f"Error querying database: {e}")