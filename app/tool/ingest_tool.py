import os
import json
import time
from typing import Optional

import chromadb
from chromadb.utils import embedding_functions
from .base import BaseTool, ToolResult

CHUNK_SIZE = 200
PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "documents"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
SUMMARY_FILE = os.path.join(PERSIST_DIR, "knowledge_base_summary.json")  # Knowledge base summary file


def chunk_text(text, chunk_size):
    """Split text into chunks of specified size"""
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]


class IngestTool(BaseTool):
    name: str = "ingest"
    description: str = "Ingest a document into the vector database by splitting it into chunks and storing them."
    parameters: Optional[dict] = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The path to the file to ingest"
            }
        },
        "required": ["file_path"]
    }

    async def execute(self, **kwargs) -> ToolResult:
        file_path = kwargs['file_path']
        
        if not os.path.exists(file_path):
            return ToolResult(error=f"File not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return ToolResult(error=f"Error reading file: {e}")
        
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
            
            # Create or update knowledge base summary
            summary = {}
            if os.path.exists(SUMMARY_FILE):
                try:
                    with open(SUMMARY_FILE, 'r', encoding='utf-8') as f:
                        summary = json.load(f)
                except:
                    pass
            
            # Add/update document entry in summary
            summary[os.path.basename(file_path)] = {
                "file_path": file_path,
                "chunk_count": len(chunks),
                "first_chunk": chunks[0] if chunks else "",
                "last_updated": time.time(),
                "size_bytes": os.path.getsize(file_path)
            }
            
            # Save updated summary
            with open(SUMMARY_FILE, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
                
            return ToolResult(output=f"Successfully ingested {len(chunks)} chunks from {file_path} and updated knowledge base summary")
        except Exception as e:
            return ToolResult(error=f"Error ingesting documents: {e}")