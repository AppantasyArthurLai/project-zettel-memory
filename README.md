# Zettel-Memory

> "Building the Agent's Second Brain."

**Zettel-Memory** is a lightweight, organic memory framework for AI Agents, inspired by the Niklas Luhmann's Zettelkasten method. Unlike traditional RAG (which acts like a static file cabinet), Zettel-Memory functions as a living organism—it grows, connects, forgets, and dreams.

## Core Philosophy

- **Atomicity**: Memories are automatically split into atomic concepts.
- **Connectivity**: Notes are auto-linked via an internal graph (NetworkX).
- **Organic Life**:
  - **Dreaming**: Background compaction of memories into insights.
  - **Forgetting**: Automatic pruning of irrelevant/unused memories over time.
  - **Resurfacing**: Proactive retrieval of old but relevant memories.

## Installation

### Prerequisites

- Python 3.9+
- A Google Gemini API Key

### Steps

1. **Install from PyPI** (Recommended)

   ```bash
   pip install zettel-memory
   ```

2. **Or Clone and Install** (For development)

   ```bash
   git clone https://github.com/AppantasyArthurLai/project-zettel-memory.git
   cd project-zettel-memory
   python3 -m venv .venv
   source .venv/bin/activate
   pip install .
   ```

3. **Configuration**
   Create a `.env` file in the root directory:
   ```bash
   GOOGLE_API_KEY=your_gemini_api_key_here
   MODEL_NAME=gemini-2.0-flash-exp
   ```

## Quick Start

```python
import asyncio
from zettel_memory.core.brain import ZettelBrain

async def main():
    # Initialize the Brain
    brain = ZettelBrain()

    # 1. Add Memory (Auto-atomized & Auto-linked)
    await brain.add_memory("""
        The Zettelkasten method emphasizes connecting ideas rather than just collecting them.
        It was popularized by Niklas Luhmann.
    """)

    # 2. Retrieve (Hybrid: Vector + Graph)
    results = await brain.retrieve("How should I organize notes?")
    print("Retrieval Results:", results)

    # 3. Resurfacing (Proactive Contextual Recall)
    # Surfaces old relevant memories while ignoring what you just discussed
    surfaced = await brain.resurfacer.resurface("Tell me about knowledge management systems.")
    print("Resurfaced Memories:", [n.content for n in surfaced])

if __name__ == "__main__":
    asyncio.run(main())
```

## Integration Patterns (Agentic Workflows)

Zettel-Memory is designed to be the **Hippocampus** (Long-term Memory) of your agent system. In a workflow (like LangGraph or CrewAI), it shouldn't be used by _every_ node, but rather by specific roles:

- **Planner / Manager Node**:
  - Queries `brain.retrieve(task_context)` at the start to load relevant history.
  - Decides direction based on past learnings.
- **Writer / Executor Node**:
  - Queries specific details when generating content.
- **Observer / Critic Node**:
  - Calls `brain.add_memory(observation)` to store new findings after an action is completed.

### Multi-tenancy (Serving Multiple Users)

If your system serves multiple users (e.g., a SaaS platform), you **MUST** isolate their memories. The implementation requires creating a separate brain instance (pointing to a separate path) for each user.

```python
def get_user_brain(user_id: str) -> ZettelBrain:
    # Each user gets their own isolated folder
    return ZettelBrain(storage_path=f"./brain_data/users/{user_id}")
```

**Why?**

- **Privacy**: User A should never traverse User B's graph.
- **Safety**: Isolating NetworkX graphs prevents in-memory cross-contamination.

**Best Practice**: Treat `ZettelBrain` as a **Shared Singleton** passed to these nodes.

> **Why Shared?**
> The power of Zettelkasten comes from "Cross-pollination". If the Planner has a separate database from the Reflector, the Planner will never learn from the Reflector's insights. They should share the same `storage_path` so that one node's output becomes another node's retrieval context.

## Architecture

| Component       | Responsibility                                   | Tech Stack       |
| :-------------- | :----------------------------------------------- | :--------------- |
| **ZettelBrain** | Main Interface & Orchestrator                    | Python (Async)   |
| **Storage**     | Vector Embedding Storage                         | ChromaDB         |
| **Graph**       | Knowledge Graph & Links                          | NetworkX         |
| **Cortex**      | Background Intelligence (Dream/Forget/Resurface) | Background Tasks |

## Development & Testing

Run the test suite to verify the installation:

```bash
# Run all tests with coverage
pytest --cov=zettel_memory --cov-report=term-missing tests/
```

## Build & Distribution

If you want to build a distribution package or use this library in other local projects without publishing to PyPI.

### 1. Build Package

```bash
pip install build twine
python -m build
# Generates ./dist/zettel_memory-0.1.0.tar.gz and .whl
```

### 2. Local Integration (Editable Install)

Recommended for development. Allows you to use Zettel-Memory in another project while keeping the code editable.

```bash
# In your other project's directory:
pip install -e /path/to/project-zettel-memory
```

### 3. Deploy to PyPI

```bash
twine upload dist/*
```

## License

MIT License. Created by Arthur & Gemini.
