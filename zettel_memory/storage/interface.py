from abc import ABC, abstractmethod
from typing import List, Optional
from zettel_memory.core.models import Note

class StorageInterface(ABC):
    @abstractmethod
    def add(self, note: Note) -> None:
        """Add a note to storage."""
        pass

    @abstractmethod
    def get(self, note_id: str) -> Optional[Note]:
        """Get a note by ID."""
        pass

    @abstractmethod
    def query(self, query_embedding: List[float], top_k: int = 5) -> List[Note]:
        """Query notes by embedding similarity."""
        pass

    @abstractmethod
    def delete(self, note_id: str) -> None:
        """Delete a note by ID."""
        pass
