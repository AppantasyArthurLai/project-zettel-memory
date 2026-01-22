# Zettel-Memory (卡片盒記憶)

> "打造 AI Agent 的第二大腦。"

**Zettel-Memory** 是一個專為 AI Agent 設計的輕量級、有機記憶框架，靈感來自 Niklas Luhmann (盧曼) 的卡片盒筆記法 (Zettelkasten)。不同於傳統的 RAG (就像一個靜態的檔案櫃)，Zettel-Memory 像是一個有生命的有機體——它會生長、連結、遺忘，甚至會做夢。

## 核心哲學 (Core Philosophy)

- **原子性 (Atomicity)**: 所有記憶會自動被拆解為原子級別的概念單元。
- **連結性 (Connectivity)**: 筆記之間會透過內部的圖譜 (NetworkX) 自動建立連結。
- **有機生命 (Organic Life)**:
  - **做夢 (Dreaming)**: 背景程序會將零散的記憶壓縮 (Compact) 成新的洞見。
  - **遺忘 (Forgetting)**: 根據時間衰減與重要性，自動修剪不再使用的記憶。
  - **浮現 (Resurfacing)**: 根據當下情境，主動浮現古老但相關的記憶。

## 安裝指南 (Installation)

### 前置需求

- Python 3.9+
- Google Gemini API Key

### 步驟

1. **從 PyPI 安裝** (推薦)

   ```bash
   pip install zettel-memory
   ```

2. **Clone 與安裝** (開發用)

   ```bash
   git clone https://github.com/AppantasyArthurLai/project-zettel-memory.git
   cd project-zettel-memory
   python3 -m venv .venv
   source .venv/bin/activate
   pip install .
   ```

3. **設定環境變數**
   在專案根目錄建立 `.env` 檔案：
   ```bash
   GOOGLE_API_KEY=your_gemini_api_key_here
   MODEL_NAME=gemini-2.0-flash-exp
   ```

## 快速開始 (Quick Start)

```python
import asyncio
from zettel_memory.core.brain import ZettelBrain

async def main():
    # 初始化大腦
    brain = ZettelBrain()

    # 1. 新增記憶 (自動原子化拆解 + 自動連結)
    await brain.add_memory("""
        卡片盒筆記法 (Zettelkasten) 強調的是連結想法，而不僅僅是收集它們。
        這個方法是由社會學家 Niklas Luhmann 發揚光大的。
    """)

    # 2. 檢索 (混合模式: 向量搜尋 + 圖譜擴展)
    results = await brain.retrieve("我該如何組織筆記？")
    print("檢索結果:", results)

    # 3. 主動浮現 (Resurfacing - 基於情境的主動喚回)
    # 系統會浮現「相關」但在當前對話中尚未被提及的舊記憶
    surfaced = await brain.resurfacer.resurface("跟我聊聊知識管理系統。")
    print("浮現的舊記憶:", [n.content for n in surfaced])

if __name__ == "__main__":
    asyncio.run(main())
```

## 整合模式 (Integration Patterns)

在 Agentic Workflow (如 LangGraph, CrewAI) 中，Zettel-Memory 被設計為系統的 **"海馬迴" (長期記憶中樞)**。它不需要被 _每一個_ LLM 節點調用，而是應該掛載在特定的角色上：

- **規劃者 (Planner Node)**:
  - 在任務開始時調用 `retrieve(context)`，提取相關的歷史經驗。
  - 避免重蹈覆轍，或根據過去的偏好制定計畫。
- **執行者 (Executor Node)**:
  - 寫入新資訊時調用 `add_memory(result)`。
- **觀察者 (Observer Node)**:
  - 在對話/任務結束時，將關鍵洞察寫入記憶。

### 多租戶應用 (Multi-tenancy)

如果您的系統要服務多位使用者 (例如 SaaS 服務)，您 **必須** 將他們的記憶完全隔離。
這需要為每位使用者實例化一個指向不同路徑的 Brain。

```python
def get_user_brain(user_id: str) -> ZettelBrain:
    # 每個使用者擁有自己的資料夾，確保隱私絕對隔離
    return ZettelBrain(storage_path=f"./brain_data/users/{user_id}")
```

**原因**:

- **隱私 (Privacy)**: A 用戶的檢索絕對不能 Query 到 B 用戶的向量或圖譜。
- **安全 (Safety)**: 物理隔離 (不同資料夾) 比邏輯隔離 (Metadata Filter) 更安全且容錯率更高。

**最佳實踐**: 將 `ZettelBrain` 實例視為一個 **Shared Singleton (共享單例)**。

> **為什麼要共用資料庫？**
> Zettelkasten 的核心威力在於「知識的交叉傳播 (Cross-pollination)」。
> 如果規劃者 (Planner) 與 反思者 (Reflector) 擁有不同的資料庫，那麼規劃者就永遠無法「學到」反思者總結出的教訓。
> 不同的節點應該共用同一個 `storage_path`，這樣 A 節點寫入的洞見，才能被 B 節點在未來的某個時刻檢索出來 (Resurfacing)。

## 系統架構 (Architecture)

| 組件 (Component) | 職責 (Responsibility)            | 技術棧 (Tech Stack) |
| :--------------- | :------------------------------- | :------------------ |
| **ZettelBrain**  | 主要介面與協調者 (Orchestrator)  | Python (Async)      |
| **Storage**      | 向量嵌入儲存 (以 embedding 為主) | ChromaDB            |
| **Graph**        | 知識圖譜與連結                   | NetworkX            |
| **Cortex**       | 背景智慧 (做夢/遺忘/浮現)        | Background Tasks    |

### 技術實作細節 (Technical Implementation Details)

- **Embedding Model**: 我們預設使用 **Google Gemini `text-embedding-004`**。
  - _原因_: 相比於 Chroma 預設的本地模型 (`all-MiniLM`)，Gemini 對於多語言與複雜語意的理解能力更強。
  - _代價_: 這會產生少許 API 費用與網路延遲。
- **圖譜持久化 (Graph Persistence)**:
  - NetworkX 雖然在記憶體中運算，但所有的變更 (Add Node/Edge) 都會**即時**寫入硬碟 (`graph.graphml`)。
  - 即使程式重啟，圖譜結構也不會消失。但在高併發 (High Concurrency) 寫入時需注意檔案鎖定問題。

## 開發與測試 (Development)

執行測試套件以驗證安裝是否正確：

```bash
# 執行所有測試並產出覆蓋率報告
pytest --cov=zettel_memory --cov-report=term-missing tests/
```

## 建置與發布 (Build & Distribution)

如果您想要自行打包，或是在本機的其他專案中引用此庫。

### 1. 打包 (Build Package)

```bash
pip install build twine
python -m build
# 執行後會於 ./dist/ 產生 .tar.gz 與 .whl 檔案
```

### 2. 本機整合 (Editable Install)

推薦開發使用。這讓您可以在其他專案中直接引用 Zettel-Memory，且這邊的程式碼修改會即時生效。

```bash
# 在您的另一個專案目錄下執行：
pip install -e /path/to/project-zettel-memory
```

## 授權 (License)

MIT License. Created by Arthur & Gemini.
