# yaml-infographic（專案藍圖）

> 本檔為跨 Agent 通用的專案藍圖（AGENTS.md 開放標準）。任何 Agent 的每個 session 都應先讀本檔＋`handoff.md`。
> Claude Code 不讀 `agents.md`，改由 `CLAUDE.md` 的 `@agents.md` import 本檔；Claude 專屬規範寫在 `CLAUDE.md`。

## 專案簡介

用一份結構化 YAML 先固定資訊架構、版型、精確資料與視覺規則，再生成風格一致的單張資訊圖表的 Agent 技能專案。技能本體可安裝到 Codex、Claude、OpenCode、Antigravity 四種 Agent。

本專案的程式與文件源自三師爸 Sense Bar 的 `mathruffian-dot/yaml-infographic`（MIT），現正改造成自己的版本：解開寫死的視覺風格、換上自有的黃金樣張與調色盤，並修掉上游的若干程式問題。已與上游脫離 fork 關係，是獨立 repo。

## 關鍵時程

<!-- 目前沒有對外時程 -->

## 目標與路線圖

- [x] 階段一：法律與身分歸屬
  - [x] `LICENSE` 增列自己的著作權行（**保留**三師爸原行）
  - [x] `README.md` 安裝指令改指向本 repo，並新增〈出處與授權〉
- [ ] 階段二：解開風格鎖
  - [x] `validate_spec.py` 移除硬編碼調色盤，改成讀 YAML 做自我一致性檢查
  - [ ] 新增自有風格 profile，`tech_calm` 降為範例
  - [ ] 產出自己的黃金樣張，取代 `channel-style-tech-calm.png`
- [x] 階段三：修正程式問題
  - [x] `compile_prompt.py` 實際讀取 style YAML 的 `typography` 與 `emphasis`
  - [x] `compile_prompt.py` 補 `sys.exit(main())`、清掉 palette fallback 死碼
  - [x] `validate_spec.py` 的 YAML 載入包 try／except
  - [x] `validate_repo.py` 機密掃描改成符合本機環境
  - [x] `.gitattributes` 首行補 `eol=lf`
- [x] 階段四：文件一致性
  - [x] 統一 SKILL.md 與 README 的 script 路徑寫法，改成安裝後真的可用的形式

## 資料夾結構

```text
agents.md                              專案藍圖（本檔）
handoff.md                             交接檔（不進 git）
CLAUDE.md                              Claude Code 橋接檔
README.md                              對外說明與安裝指引
LICENSE                                MIT（程式與文件）
LICENSE-ASSETS.md                      素材授權說明
requirements.txt                       Python 相依套件
.github/workflows/validate.yml         Ubuntu／Windows 自動驗證
examples/                              可直接改寫的 YAML 範例
  process-baked/spec.yaml              1:1 流程圖／baked
  comparison-plate/spec.yaml           4:5 比較圖／plate
skills/yaml-infographic/               技能本體（安裝器複製的就是這層）
  SKILL.md                             技能主文件與工作流程
  agents/openai.yaml                   Codex 介面設定
  assets/tech-calm.yaml                風格 profile
  assets/channel-style-tech-calm.png   黃金樣張
  assets/infographic-spec-template.yaml  spec 範本
  references/                          schema／版型庫／提示詞／驗收
  scripts/validate_spec.py             規格驗證
  scripts/compile_prompt.py            提示詞編譯
  scripts/verify_output.py             產物驗收
tests/test_skill.py                    正向與負向測試
tools/install.ps1                      四種 Agent 安裝器
tools/validate_repo.py                 Repo 完整性驗證
```

## 專案專屬規則

**授權（不可違反）**
- `LICENSE` 的 `Copyright (c) 2026 三師爸 Sense Bar` 一行**永遠保留**。MIT 要求副本必須包含原始著作權聲明，自己的署名只能**增行**，不能取代。
- 沿用或改作上游素材（尤其 `channel-style-tech-calm.png`）時，`LICENSE-ASSETS.md` 的來源說明要同步維持正確。

**驗證**
- 任何改動後必須跑 `python .\tools\validate_repo.py`，要看到 `REPO VALID` 才算完成。它會連帶跑 `examples/` 的規格驗證與 `tests/test_skill.py` 的 11 項正負向測試。
- 改 `validate_spec.py` 的規則時，對應的負向測試要一起改，不要讓測試跟著規則一起放寬。

**內容邊界**
- repo 內任何文字檔都不要寫本機絕對路徑（使用者家目錄開頭的 Windows 路徑）；`tools/validate_repo.py` 會掃描並擋下。注意它掃的是**整個資料夾**而非 git 索引，所以連不進版控的 `handoff.md` 也會被擋。
- 本 repo 為**公開**：commit 前確認沒有金鑰、個資或未公開素材。

**技能語意**
- 這個技能只產出「單張畫布」，不是簡報。`spec.yaml` 不可出現 `slides` 區塊。
- 繁體中文、精確數字、圖表、日期與公式一律走 `plate` 模式（無字底圖＋原生文字疊加），避免 AI 生圖寫錯字。

## 同步層級（本專案初始化至第 3 層級）

| 層級 | 平台 | 位置 | 讀取時機 |
|------|------|------|---------|
| L1 | 本地（GDrive） | `agents.md`＋`handoff.md`（不進 git，只走雲端硬碟）＋`CLAUDE.md`（橋接） | 每個 session |
| L2 | GitHub | [changyiwu/yaml-infographic](https://github.com/changyiwu/yaml-infographic)（公開） | 指定時 |
| L3 | Obsidian | `yaml-infographic/專案工作流程.md` | 有需要時 |

## 三個檔案的職責（依「時效性」分家，不是依「詳細程度」）

| 檔案 | 時效 | 寫入方式 | 放什麼 |
|------|------|---------|--------|
| `handoff.md` | **只對下一個 session 有效**，過期即丟 | 每次收工**整份重寫** | 做到哪、下一步、**這次**的暫時 workaround |
| `agents.md`（本檔） | **長期有效**，每個 session 都適用 | 只有規則本身變了才改 | 目標、路線圖、常設規則、結構 |
| Obsidian（L3）／`git log` | **歷史**：發生過什麼、為什麼 | 只增不刪 | 決策紀錄、踩坑完整版、逐次進度 |

驗收標準：**`handoff.md` 整份刪掉，不應損失任何長期資訊**——會的話代表該升級進本檔卻沒升級。

**本檔不要出現的東西**（會無限膨脹，且開工每次都要重讀）：
- ❌ `## 最近進度`／逐次工作紀錄 → 有 L3 寫 Obsidian「🗓️ 最近更動紀錄」；沒有就靠 `git log`（所以 commit 訊息要寫「做什麼＋為什麼」）
- ❌ 決策記錄、取捨理由、踩坑經過的完整版 → Obsidian「決策紀錄」「🕳️ 踩坑筆記」
- ✅ 只留「結論式的規則」：踩過的坑收斂成一條**祈使句**寫進〈工作約定〉或〈專案專屬規則〉，理由那一大段留在 Obsidian

## 工作約定
- 任何 Agent、任何電腦：**開工先讀 `handoff.md`，收工必更新 `handoff.md`**
- `handoff.md` **不進 git**（含真實電腦名與本機絕對路徑），已列入 `.gitignore`，跨電腦靠雲端硬碟同步——不要把它加回版控
- 修改共用檔案前先讀最新內容，避免覆蓋其他 Agent 的變更
- 所有回應與文件使用繁體中文
- 修改前先確認計畫，優先保留原有資料結構
