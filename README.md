# YAML Infographic

用一份結構化 YAML，先固定資訊架構、版型、精確資料與視覺規則，再生成一致的單張資訊圖表。

![紙感立體貼紙風格黃金樣板](skills/yaml-infographic/assets/paper-warm-sample.png)

內建兩種風格 profile。上圖為預設的「紙感立體貼紙」（`paper_warm`）：厚實圓角貼紙浮起於暖紙底，適合列印講義與明亮教室；下圖為「科技沉穩」（`tech_calm`，隨原始著作附帶），適合暗室螢幕與社群貼文。

![科技沉穩風格黃金樣板](skills/yaml-infographic/assets/channel-style-tech-calm.png)

## 核心能力

- 單張資訊圖表，不是多頁簡報。
- 支援 `1:1`、`4:5`、`9:16`、`16:9`、A4 直式與橫式。
- 支援流程、比較、時間軸、數據故事、分類、階層、因果、清單與解剖標註。
- 內建兩種可切換的風格 profile，調色盤不寫死在驗證器裡，可自行新增。
- 支援精確資料、來源引用、替代文字與色彩以外的辨識提示。
- YAML、提示詞紀錄與成品輸出皆可驗證。

## `baked` 與 `plate`

| 模式 | 適合情境 | 輸出方式 |
|---|---|---|
| `baked` | 文字少、低密度、視覺敘事為主 | 文字直接生成在圖片中 |
| `plate` | 繁體中文、數字、圖表、日期、公式或之後要修改 | 先生成無字底圖，再以 SVG／原生文字疊加 |

精確內容預設使用 `plate`，避免 AI 生圖造成錯字或數字失真。

## 安裝

### Codex 一行安裝

```powershell
python "$HOME\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" `
  --repo changyiwu/yaml-infographic `
  --path skills/yaml-infographic
```

### Codex、Claude、OpenCode、Antigravity／Gemini

先下載 Repo：

```powershell
git clone https://github.com/changyiwu/yaml-infographic.git
Set-Location .\yaml-infographic
```

再選擇要安裝的 Agent：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\install.ps1 -Agent codex
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\install.ps1 -Agent claude
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\install.ps1 -Agent opencode
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\install.ps1 -Agent antigravity
```

一次安裝到四個 Agent：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\install.ps1 -Agent all
```

若目標已存在，可加上 `-Force`。安裝器會先把舊版本移到帶時間戳記的備份資料夾，不會直接刪除。

## 五分鐘 Quick Start

安裝 Python 相依套件：

```powershell
python -m pip install -r .\requirements.txt
```

複製 YAML 樣板：

```powershell
Copy-Item .\skills\yaml-infographic\assets\infographic-spec-template.yaml .\spec.yaml
```

依題目修改 `spec.yaml` 後，先驗證再編譯提示詞（以下為在本 Repo 內操作；**安裝後**改用技能目錄的路徑，見 [SKILL.md](skills/yaml-infographic/SKILL.md)）：

```powershell
python .\skills\yaml-infographic\scripts\validate_spec.py --spec .\spec.yaml
python .\skills\yaml-infographic\scripts\compile_prompt.py --spec .\spec.yaml
```

接著把產生的 prompt record 交給 Codex／ChatGPT 的圖片生成功能。完成圖片與必要的 SVG 疊加後執行：

```powershell
python .\skills\yaml-infographic\scripts\verify_output.py --spec .\spec.yaml --project-root .
```

> 這個 Repo 的 Python 工具負責規格驗證、提示詞編譯與輸出驗收，不會自行呼叫圖片 API。正式生圖仍需要支援圖片生成的 AI 工具或訂閱功能。

## 工作流程

```text
需求與比例
    ↓
資訊架構 YAML
    ↓
規格驗證
    ↓
提示詞編譯
    ↓
AI 圖片生成
    ↓
文字／數據疊加（plate）
    ↓
尺寸與產物驗收
```

## 範例

- [1:1 流程圖／baked](examples/process-baked/spec.yaml)
- [4:5 比較圖／plate](examples/comparison-plate/spec.yaml)

## 專案結構

```text
skills/yaml-infographic/   技能本體
examples/                  可直接改寫的 YAML 範例
tests/                     正向與負向測試
tools/install.ps1          四種 Agent 安裝器
tools/validate_repo.py     Repo 完整性驗證
.github/workflows/         Windows／Ubuntu 自動測試
```

## 本機驗證

```powershell
python .\tools\validate_repo.py
```

測試不會呼叫任何圖片 API，也不需要 API Key。

## 出處與授權

本專案是**改作版本，不是原創**。

| 項目 | 內容 |
|---|---|
| 原作者 | 三師爸 Sense Bar（[mathruffian-dot](https://github.com/mathruffian-dot)） |
| 原始著作 | [mathruffian-dot/yaml-infographic](https://github.com/mathruffian-dot/yaml-infographic)，MIT |
| 本 Repo | `changyiwu/yaml-infographic`，由 changyiwu 修改與維護 |

YAML 設計合約、資訊架構路由、`baked`／`plate` 雙模式與黃金樣張機制等核心設計，皆由原作者提出。

程式、文件與 YAML 採 [MIT License](LICENSE)，原始著作權聲明完整保留，不可刪改。示範圖片與風格資產說明見 [LICENSE-ASSETS.md](LICENSE-ASSETS.md)。
