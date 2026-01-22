# 編譯、發布與本機整合指南 (Deployment Guide)

本文件說明如何將 **Zettel-Memory** 打包、發布，以及如何在您本機的其他專案中直接引用它。

## 1. 建置與打包 (Build)

Python 專案的「編譯」主要是指將原始碼打包成發布格式 (Source Distribution 與 Wheel)。

### 前置準備

安裝打包工具：

```bash
pip install build twine
```

### 執行打包

在專案根目錄執行：

```bash
python -m build
```

執行後會自動產生 `dist/` 目錄，內容包含：

- `zettel_memory-0.1.0.tar.gz` (原始碼包)
- `zettel_memory-0.1.0-py3-none-any.whl` (Wheel 安裝包)

---

## 2. 部署 (發布至 PyPI)

若要讓全世界都能透過 `pip install zettel-memory` 安裝您的套件，需將其上傳至 Python Package Index (PyPI)。

### 步驟

1. **檢查套件完整性** (建議):

   ```bash
   twine check dist/*
   ```

2. **上傳至 PyPI**:
   ```bash
   twine upload dist/*
   ```
   _您需要擁有 PyPI 帳號以及 API Token。_

---

## 3. 本機整合 (在其他專案中使用)

如果您有另一個專案（例如 `MyAgentBot`）正在開發中，想要直接使用本機上的 `zettel-memory`，而不想先發布到 PyPI，可以使用 **Editable Install** 或 **Local Path Install**。

### 方法 A: 可編輯安裝 (Editable Install) - 推薦開發使用

這種方式會建立類似「捷徑」的參照。您在 `zettel-memory` 專案中修改的任何程式碼，會**即時**反映在其他專案中，無需重新安裝。

1. 進入您的另一個專案目錄：
   ```bash
   cd ~/Develop/MyAgentBot
   source .venv/bin/activate
   ```
2. 使用 `-e` 參數進行安裝 (路徑請改為您實際的存放路徑)：
   ```bash
   pip install -e /Users/arthur/Develop/project-zettel-memory
   ```

### 方法 B: 路徑安裝 (Path Install) - 穩定測試用

這種方式會將目前的程式碼複製一份安裝進去。如果您修改了 `zettel-memory`，必須重新執行安裝指令才會更新。

```bash
pip install /Users/arthur/Develop/project-zettel-memory
```

### 驗證安裝

在您的另一個專案中執行 Python：

```python
import zettel_memory
print(zettel_memory.__file__)
# 輸出應指向您的原始碼路徑: /Users/arthur/Develop/project-zettel-memory/zettel_memory/__init__.py
```
