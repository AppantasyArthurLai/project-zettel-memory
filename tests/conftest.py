import pytest
import os
import shutil
import asyncio
from unittest.mock import AsyncMock, MagicMock
from zettel_memory.core.brain import ZettelBrain
from zettel_memory.core.models import Note

@pytest.fixture
def temp_brain_dir(tmp_path):
    """Provides a unique temporary directory for each test."""
    d = tmp_path / "brain_data"
    d.mkdir()
    return str(d)

@pytest.fixture
def mock_genai(monkeypatch):
    """Mocks Google GenAI to avoid API calls."""
    mock_client = MagicMock()

    # Mock Models (Async)
    mock_files = MagicMock() 
    mock_models = MagicMock()
    
    # Mock embedding
    async def mock_embed(*args, **kwargs):
        res = MagicMock()
        # response.embeddings[0].values
        embedding_obj = MagicMock()
        embedding_obj.values = [0.1] * 768
        res.embeddings = [embedding_obj]
        return res
    
    mock_models.embed_content = AsyncMock(side_effect=mock_embed)
    
    # Mock generation (Async)
    async_generate = AsyncMock()
    async_generate.return_value.text = '{"notes": ["Note A", "Note B"], "links": [], "summary": "Insight Summary"}'
    mock_models.generate_content = async_generate

    mock_client.aio.models = mock_models

    # Patch google.genai.Client
    monkeypatch.setattr("google.genai.Client", lambda api_key: mock_client)
    
    return mock_client.aio.models

@pytest.fixture
def brain(temp_brain_dir, mock_genai):
    # Pass a dummy key so it validates
    b = ZettelBrain(api_key="dummy_key", storage_path=temp_brain_dir)
    # Monkeypatch inner async calls if needed, but mock_genai handles global calls
    # We also need to patch the internal _get_embedding which runs in executor if not fully mocked at module level
    return b
