import chromadb
from chromadb.config import Settings
from typing import List, Optional
from zettel_memory.core.models import Note
from zettel_memory.storage.interface import StorageInterface
import json
from datetime import datetime

class ChromaStorage(StorageInterface):
    def __init__(self, persist_path: str = "./brain_data"):
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(name="zettel_memory")

    def add(self, note: Note) -> None:
        if not note.embedding:
            raise ValueError("Note must have an embedding to be stored in ChromaDB")
        
        # ChromaDB requires metadata to be flat primitives usually, strict handling needed
        # Serialize complex metadata if needed, but for now we trust it's simple or handled
        # We ensure created_at is isoformat string for metadata
        metadata = note.metadata.copy()
        metadata["created_at"] = note.created_at.isoformat()
        metadata["tags"] = ",".join(note.tags) # Store tags as comma separated string
        
        # Cortex fields persistence
        metadata["importance"] = note.importance
        metadata["last_accessed"] = note.last_accessed.isoformat()
        metadata["access_count"] = note.access_count

        self.collection.upsert(
            documents=[note.content],
            embeddings=[note.embedding],
            metadatas=[metadata],
            ids=[note.id]
        )

    def get(self, note_id: str) -> Optional[Note]:
        result = self.collection.get(ids=[note_id], include=["metadatas", "documents", "embeddings"])
        if not result["ids"]:
            return None
        
        data = result["metadatas"][0]
        content = result["documents"][0]
        embedding = result["embeddings"][0] if result["embeddings"] is not None and len(result["embeddings"]) > 0 else None
        
        # Reconstruct Note
        tags = data.get("tags", "").split(",") if data.get("tags") else []
        created_at = datetime.fromisoformat(data.get("created_at"))
        
        # Cortex fields retrieval
        importance = data.get("importance", 1.0)
        last_accessed = datetime.fromisoformat(data.get("last_accessed")) if data.get("last_accessed") else datetime.now()
        access_count = data.get("access_count", 0)
        
        # Clean up metadata to not include fields we pulled out
        exclude_keys = ["created_at", "tags", "importance", "last_accessed", "access_count"]
        clean_metadata = {k: v for k, v in data.items() if k not in exclude_keys}
        
        return Note(
            id=note_id,
            content=content,
            tags=tags,
            created_at=created_at,
            embedding=embedding,
            metadata=clean_metadata,
            importance=importance,
            last_accessed=last_accessed,
            access_count=access_count
        )

    def query(self, query_embedding: List[float], top_k: int = 5) -> List[Note]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["metadatas", "documents", "embeddings", "distances"]
        )
        
        notes = []
        if not results["ids"]:
            return notes
            
        # Iterate through the first result set (since we only queried one embedding)
        num_results = len(results["ids"][0])
        for i in range(num_results):
            note_id = results["ids"][0][i]
            data = results["metadatas"][0][i]
            content = results["documents"][0][i]
            # embedding might be None if not requested or not returned, but we requested it
            # results["embeddings"] shape is (n_queries, n_results, dim)
            embedding = results["embeddings"][0][i] if results.get("embeddings") else None
            
            tags = data.get("tags", "").split(",") if data.get("tags") else []
            created_at = datetime.fromisoformat(data.get("created_at")) if data.get("created_at") else datetime.now()
            
            # Cortex fields retrieval
            importance = data.get("importance", 1.0)
            last_accessed = datetime.fromisoformat(data.get("last_accessed")) if data.get("last_accessed") else datetime.now()
            access_count = data.get("access_count", 0)

            clean_metadata = {k: v for k, v in data.items() if k not in ["created_at", "tags", "importance", "last_accessed", "access_count"]}
            
            notes.append(Note(
                id=note_id,
                content=content,
                tags=tags,
                created_at=created_at,
                embedding=embedding,
                metadata=clean_metadata,
                importance=importance,
                last_accessed=last_accessed,
                access_count=access_count
            ))
            
        return notes

    def delete(self, note_id: str) -> None:
        self.collection.delete(ids=[note_id])
        
    def clear(self) -> None:
        self.client.delete_collection("zettel_memory")
        self.collection = self.client.get_or_create_collection(name="zettel_memory")
