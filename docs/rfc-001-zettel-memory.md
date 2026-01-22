# RFC-001: Zettel-Memory MVP

- **Author**: Arthur (Assisted by Gemini)
- **Status**: Released (v0.1.0)
- **Date**: 2025-12-31 (MVP Completed)

---

## 1. Summary (摘要)

本文件旨在定義 **"Zettel-Memory"** 的最小可行性產品 (MVP) 架構。這是一個專為 AI Agent 設計的輕量級、具備自我生長能力的記憶框架，其設計哲學源自卡片盒筆記法 (Zettelkasten)。

目標是創建一個開源 Python 庫，讓開發者能用極低的成本（3 行代碼）為自己的 Agent 掛載一個「第二大腦」。

## 2. Motivation (動機)

### 2.1 The Problem (問題)

- **Context Window 限制**：LLM 無法記住所有歷史對話，且長 Context 費用高昂、精度下降。
- **現有框架過重**：
  - **GraphRAG**：架構複雜，依賴重型 Graph DB，適合靜態知識庫檢索，不適合動態 Agent 記憶。
  - **MemGPT**：模擬 OS 過於複雜，且偏向「管理」而非「知識湧現」。
- **缺乏「遺忘」機制**：現有 Memory 多為「只進不出」，導致雜訊堆積，檢索準確度隨時間下降。

### 2.2 The Solution (解決方案)

打造一個 **"Agent's Obsidian"**：

- **Atomicity**：將記憶拆解為原子化的「卡片 (Note)」。
- **Linking**：透過雙向連結建立知識網絡，實現上下文關聯提取。
- **Emergence**：記憶庫隨互動自動生長，越用越聰明。

---

## 3. High-Level Design (高層設計)

### 3.1 核心概念 (Core Concepts)

系統由三個核心實體組成：

1.  **Note (卡片)**：記憶的最小單位。包含 `content`, `tags`, `timestamp`, `importance_score`。
2.  **Link (連結)**：卡片間的關係。包含 `source_id`, `target_id`, `relation_type`, `strength`。
3.  **Brain (大腦)**：負責管理存儲、檢索、遺忘邏輯的主控制器。
4.  **Cortex (皮質層)**：實現 Autonomous 能力的後台進程。
    - **Dreaming (做夢)**：閒置時自動重組、優化記憶連結。
    - **Resurfacing (浮現)**：根據情境主動推送相關舊記憶，而非等待查詢。

### 3.2 技術棧 (Tech Stack) - MVP

以 **社群主流** 與 **Developer Experience (DX)** 為最優先考量：

- **Framework**: `FastAPI` (AI 社群標準，天生支援 Async，適合高併發 Cortex 任務)。
- **Storage (Content)**: `ChromaDB` (Python 向量庫的社群首選，生態最豐富，安裝最簡單)。
- **Graph (Relations)**: `NetworkX` (純 Python 圖算法庫，零依賴。設計上保留介面未來可遷移至 `Neo4j`)。
- **Processor (Thought)**: `Gemini 3 Flash` (高頻、低成本的後台思考引擎)。
- **Logic**: 純 Python 3.10+。

---

## 4. API Specification (介面規範)

開發者只需與 `ZettelBrain` 類交互：

```python
class ZettelBrain:
    def __init__(self, llm_client, storage_path="./brain_data"):
        """初始化大腦"""
        pass

    def add_memory(self, content: str, context: dict = None) -> str:
        """
        1. 使用 LLM 將 content 拆解/總結為 Atomic Note
        2. 生成 Embedding
        3. 自動尋找並建立與現有 Note 的連結 (Auto-linking)
        4. 存入 DB
        5. 返回 note_id
        """
        pass

    def retrieve(self, query: str, top_k: int = 5) -> list[str]:
        """
        1. 向量檢索 (Vector Search) 找到相似卡片
        2. 圖譜遍歷 (Graph Traversal) 找到關聯卡片 (2-hop neighbors)
        3. 根據 importance_score 排序返回
        """
        pass

    def forget(self, threshold: float):
        """
        (可選) 觸發遺忘機制，根據原本的艾賓浩斯遺忘曲線或存取頻率，
        將低分卡片 '封存' 或 '刪除'。
        """
        pass
```

---

## 5. Implementation Strategy (實作策略)

### Phase 1: The Core (Week 1)

- 實現 `Note` 數據結構。
- 集成 `ChromaDB` 進行向量存儲。
- 實現最簡單的 `add_memory` (無自動連結) 和 `retrieve` (純向量)。

### Phase 2: The Graph (Week 2)

- 集成 `NetworkX`。
- 實現 LLM 驅動的 **Auto-linking**：在寫入新卡片時，讓 LLM 查詢舊卡片並決定是否建立連結。

### Phase 3: The Cortex (Week 3)

- 實現 **Background Worker** (基於 FastAPI BackgroundTasks)。
- 實現 **Dreaming**：定期觸發 Compaction，將碎片記憶合併為 Insight。
- 實現 **Resurfacing**：實作「主動浮現」邏輯，計算 Context 相關性並推送舊記憶。
- 實現 **Forgetting**：引入時間衰減與存取頻率算法。

---

## 6. Risks & Drawbacks (風險與缺點)

1.  **Latency (延遲)**：

    - **風險**：每次 `add_memory` 都要 LLM 進行拆解和連結判斷，可能會慢。
    - **對策**：使用 `Async` 非同步寫入，不阻塞主對話流程。

2.  **LLM Cost (成本)**：

    - **風險**：頻繁調用 LLM 整理記憶會消耗 Token。
    - **對策 (Flash-First Strategy)**：
      - 採用 **Gemini 3 Flash** (或 GPT-4o-mini) 作為默認的「後台整理模型」。
      - **哲學**：記憶只需 80% 準確度（抓到大意與關鍵字）即可發揮聯想作用，无需使用昂貴的 Pro 模型。
      - **效益**：極致的低延遲與低成本，支持高頻的大量記憶寫入。

3.  **Graph Complexity (圖複雜度)**：
    - **風險**：NetworkX 是內存圖庫，若節點破百萬可能會爆記憶體。
    - **對策**：MVP 階段假定是用於「個人」Agent，節點數在可控範圍。未來可遷移至 KuzuDB。

---

## 7. Future Work (未來展望)

- **Visualizer**: 提供一個類似 Obsidian 的前端圖譜視覺化介面。
- **Plugin System**: 允許開發者自定義 `ForgettingStrategy` 或 `LinkingStrategy`。
