# 開源專案維護與管理最佳實踐 (Best Practices)

這份文件為專案維護者 (Maintainer) 提供了關於版本控制、發布流程與社群管理的標準作業程序 (SOP)。

## 1. 分支策略 (Branching Strategy)

對於中小型開源專案，推薦使用 **GitHub Flow** 或簡化的 **Git Flow**：

- **`main`**: 永遠保持可部署/可發布的穩定狀態。
- **`dev`** (可選): 如果開發變動頻繁，可作為下一個版本的集結地。
- **`feature/xxx`**: 開發新功能的分支。
- **`fix/xxx`**: 修復 Bug 的分支。

### 貢獻流程 (Contribution Workflow)

1. Fork 專案。
2. 開法者在自己的分支 (`feature/new-idea`) 進行開發。
3. 提交 **Pull Request (PR)** 到 `main`。
4. **CI (Continuous Integration)** 自動執行測試。
5. Maintainer 進行 Code Review。
6. Merge (推薦使用 `Squash and Merge` 以保持 Git History 整潔)。

## 2. 版本號管理 (Versioning)

嚴格遵守 **[Semantic Versioning 2.0.0 (SemVer)](https://semver.org/)**：
`MAJOR.MINOR.PATCH` (例如 `0.1.0`)

- **MAJOR**: 當你做了不兼容的 API 修改 (Breaking Changes)。
- **MINOR**: 當你做了向下兼容的功能性新增 (New Features)。
- **PATCH**: 當你做了向下兼容的問題修正 (Bug Fixes)。

## 3. 自動化與 CI/CD (Automation)

現代開源專案強烈依賴自動化工具。推薦使用 **GitHub Actions**。

### 推薦的工作流 (Workflows)

1.  **Test (CI)**:

    - **觸發**: Push to `main` 或 Pull Request。
    - **動作**: 安裝依賴 -> Lint (Black/Isort) -> Run Tests (Pytest)。
    - **目的**: 確保壞掉的程式碼永遠進不了 `main`。

2.  **Publish (CD)**:
    - **觸發**: 當 Release 被發布 (Created a Release)。
    - **動作**:
      1. Build (`python -m build`)
      2. Publish to PyPI (`twine upload`)
    - **目的**: 一鍵發布，避免人工打包錯誤。

## 4. 發布流程 (Release Process)

當準備好發布新版本 (例如 `v0.2.0`) 時的標準步驟：

1.  **更新版本號**: 修改 `pyproject.toml` 中的 `version = "0.2.0"`。
2.  **更新 Changelog**: 在 `CHANGELOG.md` (如有) 或 Release Note 中紀錄變更。
3.  **Commit & Push**: 標記為 "Bump version to 0.2.0"。
4.  **建立 GitHub Release**:
    - Tag: `v0.2.0`
    - Title: `v0.2.0 - 新功能名稱`
    - Description: 列出變更點，感謝貢獻者。
5.  **觸發 CD**: GitHub Actions 會自動看到新 Release 並將套件推送到 PyPI。

## 5. 專案管理 (Management)

- **README**: 這是專案的門面。保持最新，範例必須能跑。
- **Issues**: 使用 Labels (如 `bug`, `enhancement`, `good first issue`) 來分類。
- **Discussions**: 開啟 GitHub Discussions 讓使用者問問題，保持 Issues 只專注於 Bug 和具體功能請求。
- **Security**: 設定 `SECURITY.md` 告知如何回報漏洞 (通常是指向 email 而非公開 issue)。

---

_遵循這些實踐，能讓您的專案看起來更專業，並吸引更多高質量的貢獻者。_
