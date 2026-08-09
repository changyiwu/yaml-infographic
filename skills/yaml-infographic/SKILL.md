---
name: yaml-infographic
description: 用一份結構化的 YAML 資訊架構搭配版本化的全域視覺風格，生成風格一致的單張資訊圖表（infographic）。當使用者要求資訊圖表、資訊長圖、社群長圖、流程圖、比較圖、時間軸、數據故事、檢查清單、構造解說圖，或要求用 YAML 規劃一張 1:1、4:5、9:16、16:9、A4 比例的單張圖片時使用。支援 baked（文字直接生在圖上）與 plate（無字底圖＋精確可編輯文字疊加）兩種模式。
---

# YAML Infographic

用一份通過驗證的 YAML 契約，生成一張完整的資訊圖表。**全域視覺識別**與**單張畫布的資訊架構**要分開管理。

## 預設值

- 走 `yaml_spec` 規劃流程，並使用內附的版本化風格 profile 之一，除非使用者明確指定其他風格。依發佈場合挑選：紙本講義與明亮教室用 `global:paper_warm@1.2.0`；暗房螢幕與社群貼文用 `global:tech_calm@1.0.0`。
- 繁體中文、精確數字、圖表、日期、引用出處、公式、地圖，或日後還要改的內容，一律預設用 `plate`。
- 只有在「低密度視覺敘事、文案短、且沒有精確性要求的資料」時才用 `baked`。
- 產出的是**單張畫布，不是簡報**。不可建立 `slides` 區塊。
- 所有產物都放在當前專案目錄底下。

## 全域風格

`global:<style_id>@<version>` 這個參照會依下列順序解析到 `<style-id>.yaml`：

1. `%USERPROFILE%\.agents\visual-styles\<style-id>.yaml`
2. 本技能內附的 `assets/<style-id>.yaml`

內附的 profile：

| 參照 | 檔案 | 視覺樣貌 | 黃金樣張 |
|---|---|---|---|
| `global:paper_warm@1.2.0`（預設） | `paper-warm.yaml` | 厚實的模切貼紙浮在溫暖漸層紙底上，底圖散布稀疏的低對比小物件；墨灰色文字、琥珀色關鍵字、紅色只留給唯一的最高層級強調 | `paper-warm-sample.png` |
| `global:tech_calm@1.0.0` | `tech-calm.yaml` | 近黑色塊面、冰白文字、橘色關鍵字、黃色只留給唯一的最高層級強調 | `channel-style-tech-calm.png` |

任何 profile 只要宣告了對得上的 `style.id`、`style.version`，以及一份完整的 `palette`，就同樣有效——驗證器沒有寫死任何特定調色盤。

**spec 一定要配自己那份 profile 的樣張。**拿暖紙風的 spec 去指近黑色的樣張（或反過來），等於餵給生圖模型一張跟自己提示詞打架的參考圖。

`assets/channel-style-tech-calm.png` 可作為內附的黃金樣張後備。使用時要維持近黑色塊面、冰白文字、橘色關鍵字與訊號線，黃色只用於唯一的最高優先強調。使用者或專案明確指定的風格，優先於預設 profile。

## 工作流程

所有指令都在放著 `spec.yaml` 的專案目錄下執行。`<SKILL_DIR>` 是本技能的安裝位置——例如 Claude Code 是 `%USERPROFILE%\.claude\skills\yaml-infographic`，Codex 是 `%USERPROFILE%\.codex\skills\yaml-infographic`。若是直接在原始碼 repo 裡工作，`<SKILL_DIR>` 就是 `skills\yaml-infographic`。

1. 定義受眾、目的、單一關鍵訊息、發佈場合，以及所需的長寬比。
2. 從 `assets/infographic-spec-template.yaml` 複製出 `spec.yaml`。
3. 從 `references/layout-library.md` 選出資訊關係，以及對應的版型。
4. 把**精確事實**與**裝飾性文案**分開。統計數字、日期、百分比、金額，以及任何外部可查證的主張，都要附上出處。
5. 生成前先驗證：

   ```powershell
   python <SKILL_DIR>\scripts\validate_spec.py --spec .\spec.yaml
   ```

6. 編譯並存下圖片提示詞：

   ```powershell
   python <SKILL_DIR>\scripts\compile_prompt.py --spec .\spec.yaml
   ```

7. 用內建生圖能力產生視覺。`plate` 模式要先生成**無字底圖**，之後再疊上精確文字、圖表或公式。
8. 用原圖尺寸與社群縮圖尺寸各檢查一次。文字太小或寫錯的區域要重生或重組，不要將就。
9. 驗收宣告的產出：

   ```powershell
   python <SKILL_DIR>\scripts\verify_output.py --spec .\spec.yaml --project-root .
   ```

10. 回報 YAML、提示詞紀錄、最終圖片、來源底圖或疊加層、模式、尺寸，以及風格 profile 版本。

## 產出規範

- `baked`：一張最終的 PNG／JPG／WebP；不可有 `overlay_blocks`。只有在「所有可見文字都可以安全地被重新生成」時才用。
- `plate`：一張無字底圖、一張最終點陣圖、一份 SVG 疊加層原始檔，以及非空的 `overlay_blocks`。
- **不要宣稱生圖產生了可編輯的 SVG。**plate 模式下，SVG 裡裝的是原生的疊加文字、圖表與向量圖形；AI 生成的底圖始終是點陣素材。
- 極高或極密的資訊圖表要拆成區塊（zone），逐區生成底圖，再在本機合成。

## 精確性規範

- 圖表、表格、公式、座標軸、地圖、比例尺與精確幾何，一律在 plate 模式下以原生方式繪製。
- 精確數字要存進 `data_integrity.exact_numbers`，不可只寫在可見文案裡。
- 每一個依賴外部來源的精確數字，都必須有可解析的引用出處。
- 每張畫布只保留一個 `primary` 強調，黃色才能維持「真正的優先訊號」這個語意。
- 必須提供完整的替代文字（alt text），且絕不可把顏色當成唯一的辨識線索。

## 參考文件

- 撰寫或修改 YAML 前，先讀 `references/schema.md`。
- 選擇構圖前，先讀 `references/layout-library.md`。
- 生圖前，先讀 `references/prompting.md`。
- 交付前，先讀 `references/validation.md`。
