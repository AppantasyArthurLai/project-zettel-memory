import pytest
import asyncio
from unittest.mock import MagicMock, call, AsyncMock
import json

@pytest.mark.asyncio
async def test_brain_add_memory_atomicity(brain, mock_genai):
    # Mock Atomization response
    # We need to distinguish calls. 
    # First call is Atomization, Second is Auto-linking (per sub-note)
    
    # Configure mock to return different things based on input prompt or just valid JSON
    # Simpler: Return a standard JSON that fits both schemas (notes list, links list)
    # Or use side_effect
    
    async def side_effect(*args, **kwargs):
        result = MagicMock()
        text_prompt = str(kwargs.get('contents', ''))
        if "split" in text_prompt or "atomic" in text_prompt.lower():
            result.text = '{"notes": ["Atomic 1", "Atomic 2"]}'
        elif "link" in text_prompt.lower():
            result.text = '{"links": []}'
        elif "insight" in text_prompt.lower():
            result.text = '{"summary": "Insight"}'
        return result
    
    mock_genai.generate_content.side_effect = side_effect

    ids = await brain.add_memory("Complex content")
    
    assert len(ids) == 2
    # Verify storage has them
    assert brain.storage.get(ids[0]).content == "Atomic 1"
    assert brain.storage.get(ids[1]).content == "Atomic 2"

@pytest.mark.asyncio
async def test_brain_auto_linking(brain, mock_genai):
    # Mock auto-linking to return a link
    async def side_effect(*args, **kwargs):
        result = MagicMock()
        text_prompt = str(kwargs.get('contents', ''))
        if "split" in text_prompt or "atomic" in text_prompt.lower():
            result.text = '{"notes": ["Note A"]}'
        elif "link" in text_prompt.lower():
            # Assume we have a candidate in prompt context (mocked by storage query)
            result.text = '{"links": [{"target_id": "existing_id", "reason": "related"}]}'
        return result
    
    mock_genai.generate_content.side_effect = side_effect
    
    # Pre-populate graph explicitly or mock add_edge
    brain.graph.add_node("existing_id")
    
    # Mock storage query to return a candidate
    mock_candidate = MagicMock()
    mock_candidate.id = "existing_id"
    mock_candidate.content = "Existing"
    brain.storage.query = MagicMock(return_value=[mock_candidate])
    
    ids = await brain.add_memory("New Note")
    
    # Verify edge added
    neighbors = brain.graph.get_neighbors(ids[0])
    assert "existing_id" in neighbors

@pytest.mark.asyncio
async def test_brain_retrieve_hybrid(brain):
    # Setup: Note A (Vector Match), Note B (Neighbor of A)
    brain.storage.add_node = MagicMock() # Chroma mock
    
    # We need to verify logic flow: 1. Vector Search, 2. Graph Expand
    # Creating a real brain with real storage fixtures is easier than full mocking logic
    
    # Add real notes
    # Note: we need to bypass add_memory atomicity to control IDs easily or just capture them
    # But add_memory is complex now. Let's use storage directly + manual graph edge
    
    from zettel_memory.core.models import Note
    n1 = Note(content="Vector Match", embedding=[0.1]*768)
    n2 = Note(content="Graph Neighbor", embedding=[0.9]*768) # Far embedding
    
    brain.storage.add(n1)
    brain.storage.add(n2)
    brain.graph.add_node(n1.id)
    brain.graph.add_node(n2.id)
    brain.graph.add_edge(n1.id, n2.id)
    
    # Mock vector search to return n1
    brain.storage.query = MagicMock(return_value=[n1])
    brain.storage.get = MagicMock(side_effect=lambda nid: n1 if nid == n1.id else n2)
    
    # Retrieve
    # mock get_query_embedding
    brain._get_query_embedding = AsyncMock(return_value=[0.1]*768)
    
    results = await brain.retrieve("query")
    
    assert "Vector Match" in results
    assert "Graph Neighbor" in results # retrieved via graph expansion

@pytest.mark.asyncio
async def test_brain_retrieve_flags(brain):
    from zettel_memory.core.models import Note
    n1 = Note(content="Test Note", embedding=[0.1]*768)
    brain.storage.add(n1)
    brain.graph.add_node(n1.id)
    
    brain.storage.query = MagicMock(return_value=[n1])
    brain._get_query_embedding = AsyncMock(return_value=[0.1]*768)
    
    # 1. Test return_objects=True
    results_obj = await brain.retrieve("q", return_objects=True)
    assert len(results_obj) == 1
    assert isinstance(results_obj[0], Note)
    assert results_obj[0].content == "Test Note"
    
    # 2. Test update_stats=False
    # Capture time before
    old_access = n1.last_accessed
    
    await brain.retrieve("q", return_objects=True, update_stats=False)
    
    # Should maintain old access time (approx equality since no update)
    # n1 is the same object in memory if storage.query returned it directly above (mock return)
    assert n1.last_accessed == old_access
    
    # 3. Test update_stats=True
    await brain.retrieve("q", return_objects=True, update_stats=True)
    assert n1.last_accessed > old_access # Updated to now
