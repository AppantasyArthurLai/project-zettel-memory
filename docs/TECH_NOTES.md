# Technical Notes & Architectural Decisions

**Date:** 2025-12-31
**Topic:** Embedding Models & Graph Persistence

## 1. Embedding Model Strategy

**Decision:** Use **Google Gemini `text-embedding-004`**.

- **Rationale**:

  - **Semantic Depth**: Superior understanding of abstract concepts and complex logic compared to smaller local models (e.g., `all-MiniLM-L6-v2`).
  - **Multi-language**: Excellent performance on mixed English/Traditional Chinese (zh-TW) content, which is critical for this project's target audience.
  - **Context Window**: Supports larger input tokens, which is beneficial when summarizing or atomizing larger notes.

- **Trade-offs**:

  - **Latency**: Requires meaningful network RTT (~200-500ms) compared to local CPU/GPU inference (<50ms).
  - **Cost**: Incurs API usage costs, though `text-embedding-004` is relatively inexpensive.

- **Future Work**:
  - Consider adding a `EMBEDDING_PROVIDER` config to allow users to opt-in for local execution (using `chromadb.utils.embedding_functions`) for offline or zero-cost scenarios.

## 2. Graph Persistence Mechanism

**Decision:** **Instant Disk Persistence** (Write-through).

- **Architecture**:

  - To keep the codebase lightweight ("The 3-Line Rule"), we avoid heavy graph databases like Neo4j.
  - We use `NetworkX` (In-Memory) for graph traversal algorithms.
  - **Persistence**: Every modification methods (`add_node`, `add_edge`, `remove_node`) in `NetworkXStorage` immediately triggers a `self.save()` call.
  - **Format**: `GraphML` (`graph.graphml`). This is a standard XML-based format supported by Gephi and other viz tools.

- **Concurrency & Safety**:
  - **Single User**: Safe. The file write is atomic enough for typical agentic loops.
  - **Multi-tenancy**: **CRITICAL**. Because we write to a single file, multiple concurrent processes writing to the same `graph.graphml` will cause race conditions or corruption.
  - **Mitigation**: As documented in `README`, strict **Physical Isolation** via `storage_path` (one folder per user) is mandatory for SaaS deployments.

## 3. Deployment Context

- **PyPI Release**: v0.1.1
- **Documentation**: Deployment guides have been consolidated into `README.md` to keep the repo self-contained, while detailed internal docs remain in `docs/` (which is git-ignored).
