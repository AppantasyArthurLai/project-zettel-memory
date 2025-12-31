import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from zettel_memory.core.cortex import Dreamer, MemoryDecayer
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_dreamer_compaction(brain, mock_genai):
    dreamer = Dreamer(brain)
    
    # Mock LLM to return summary setup
    async def side_effect(prompt):
        res = MagicMock()
        res.text = '{"summary": "Compacted Insight"}'
        return res
    mock_genai.generate_content.side_effect = side_effect
    
    # Add some dummy notes to storage so dreamer can fetch them
    from zettel_memory.core.models import Note
    n1 = Note(content="Part 1", embedding=[0.1]*768)
    n2 = Note(content="Part 2", embedding=[0.1]*768)
    brain.storage.add(n1)
    brain.storage.add(n2)
    brain.graph.add_node(n1.id)
    brain.graph.add_node(n2.id)
    
    await dreamer.compact([n1.id, n2.id])
    
    # Check if Insight created
    # Dreamer calls add_memory for insight. 
    # Since we mocked LLM for add_memory in previous test file but here this is a fresh test/fixture instantiation.
    # However, add_memory also calls atomization prompt. 
    # If we don't mock add_memory specifically, it will call generation_model.
    # Our side_effect returns "Compacted Insight" JSON for everything... 
    # add_memory expects {"notes": ...} for atomization.
    # We need a smarter side_effect for this test.
    
    async def smarter_side_effect(*args, **kwargs): # generate_content might have arguments
        res = MagicMock()
        text_prompt = str(kwargs.get('contents', '')) # Get prompt from kwargs
        if "analyze" in text_prompt.lower() or "summary" in text_prompt.lower(): # Dream Prompt
            res.text = '{"summary": "Compacted Insight"}'
        elif "atomic" in text_prompt.lower(): # Atomization Prompt
             res.text = '{"notes": ["Compacted Insight"]}' # The summary is atomic
        elif "link" in text_prompt.lower():
             res.text = '{"links": []}'
        return res
    mock_genai.generate_content.side_effect = smarter_side_effect

    await dreamer.compact([n1.id, n2.id])
    
    # Since add_memory is called, we can check if graph has edge from n1 to new insight
    # We don't know insight ID easily unless we mock add_memory return.
    # But we can check if graph edge count increased.
    # n1 -> Insight, n2 -> Insight. (2 edges) + (maybe others)
    # Actually checking edges on n1 is good enough.
    
    neighbors = brain.graph.get_neighbors(n1.id)
    assert len(neighbors) > 0 # connected to insight

@pytest.mark.asyncio
async def test_decayer_forgetting(brain):
    decayer = MemoryDecayer(brain)
    
    # Note to forget
    from zettel_memory.core.models import Note
    n1 = Note(content="To Forget", embedding=[0.1]*768)
    n1.importance = 0.1
    n1.last_accessed = datetime.now() - timedelta(days=40)
    
    brain.storage.add(n1)
    brain.graph.add_node(n1.id)
    
    # Note to keep
    n2 = Note(content="To Keep", embedding=[0.1]*768)
    n2.importance = 0.9
    brain.storage.add(n2)
    brain.graph.add_node(n2.id)
    
    await decayer.forget(threshold_days=30, importance_threshold=0.5)
    
    assert brain.storage.get(n1.id) is None
    assert brain.storage.get(n2.id) is not None

@pytest.mark.asyncio
async def test_resurfacer(brain):
    from zettel_memory.core.cortex import Resurfacer
    
    # 1. Setup Data
    from zettel_memory.core.models import Note
    # Old note
    n1 = Note(content="Old", embedding=[0.1]*768)
    n1.last_accessed = datetime.now() - timedelta(days=100)
    
    # Recent note
    n2 = Note(content="Recent", embedding=[0.1]*768)
    n2.last_accessed = datetime.now() # Just now
    
    brain.storage.add(n1)
    brain.storage.add(n2)
    brain.graph.add_node(n1.id)
    brain.graph.add_node(n2.id)
    
    # Mock retrieval to return both (simulating vector match)
    # We must mock retrieve to return [n1, n2] objects
    # But wait, Resurfacer calls retrieve(return_objects=True)
    # If we rely on real retrieve, it calls storage.query.
    # storage.query will return n1 and n2 if we mock it to.
    
    brain.storage.query = MagicMock(return_value=[n1, n2])
    
    # Mock get_query_embedding to satisfy retrieve
    brain._get_query_embedding = AsyncMock(return_value=[0.1]*768)
    
    resurfacer = Resurfacer(brain)
    
    # 2. Resurface with exclusion
    # context shouldn't matter as we mocked query result
    surfaced = await resurfacer.resurface("context", exclude_recent_minutes=5)
    
    # n2 should be excluded because it's recent
    assert len(surfaced) == 1
    assert surfaced[0].id == n1.id
    
    # 3. Verify retrieve was called with correct flags
    # We can check if stat update happened? No, retrieve called with update_stats=False
    # n1.last_accessed shouldn't change... but it's an object reference.
    # retrieve iterates and DOES NOT update it.
    # But n1.last_accessed is already set to 100 days ago.
    # If retrieve updated it, it would be NOW.
    # But checking side effects on object in memory is tricky if retrieve modifies it.
    
    # Better: check call args if we mock retrieve?
    # But we want to test integration.
    # If retrieve(update_stats=False) works, n1.last_accessed remains 100 days old.
    assert (datetime.now() - n1.last_accessed).days >= 100
