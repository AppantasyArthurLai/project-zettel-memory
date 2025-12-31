from datetime import datetime
from typing import List, Optional, Dict
import uuid
from pydantic import BaseModel, Field, ConfigDict

class Note(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    embedding: Optional[List[float]] = None
    metadata: Dict = Field(default_factory=dict)
    
    # Cortex fields
    importance: float = 1.0
    last_accessed: datetime = Field(default_factory=datetime.now)
    access_count: int = 0

    model_config = ConfigDict(arbitrary_types_allowed=True)
