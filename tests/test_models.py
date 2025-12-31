from zettel_memory.core.models import Note
from datetime import datetime

def test_note_creation():
    note = Note(content="Test content", tags=["tag1"])
    assert note.id is not None
    assert note.content == "Test content"
    assert "tag1" in note.tags
    assert isinstance(note.created_at, datetime)
    assert note.importance == 1.0
    assert note.access_count == 0

def test_note_defaults():
    note = Note(content="Simple note")
    assert note.tags == []
    assert note.metadata == {}
    assert note.embedding is None
