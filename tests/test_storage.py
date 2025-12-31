import pytest
from zettel_memory.core.models import Note
from zettel_memory.storage.chroma_storage import ChromaStorage
from zettel_memory.storage.graph_storage import NetworkXStorage
import os

def test_chroma_storage_add_get(temp_brain_dir):
    storage = ChromaStorage(persist_path=temp_brain_dir)
    note = Note(content="Test", embedding=[0.1]*768, tags=["test"])
    
    storage.add(note)
    
    retrieved = storage.get(note.id)
    assert retrieved is not None
    assert retrieved.content == "Test"
    assert retrieved.tags == ["test"]
    assert retrieved.embedding is not None

def test_chroma_storage_upsert(temp_brain_dir):
    storage = ChromaStorage(persist_path=temp_brain_dir)
    note = Note(content="Original", embedding=[0.1]*768)
    storage.add(note)
    
    note.content = "Updated"
    note.importance = 0.5
    storage.add(note) # Should upsert
    
    retrieved = storage.get(note.id)
    assert retrieved.content == "Updated"
    assert retrieved.importance == 0.5

def test_chroma_storage_delete(temp_brain_dir):
    storage = ChromaStorage(persist_path=temp_brain_dir)
    note = Note(content="To Delete", embedding=[0.1]*768)
    storage.add(note)
    
    storage.delete(note.id)
    assert storage.get(note.id) is None

def test_graph_storage(temp_brain_dir):
    graph_path = os.path.join(temp_brain_dir, "graph.gml")
    storage = NetworkXStorage(persist_path=graph_path)
    
    storage.add_node("n1", type="note")
    storage.add_node("n2", type="note")
    storage.add_edge("n1", "n2", weight=0.5)
    
    assert "n2" in storage.get_neighbors("n1")
    
    # Test Persistence
    storage2 = NetworkXStorage(persist_path=graph_path)
    assert "n2" in storage2.get_neighbors("n1")
