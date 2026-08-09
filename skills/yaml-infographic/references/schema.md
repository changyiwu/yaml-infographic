# YAML Infographic 規格（Schema）

單張高資訊密度的畫布，使用 `yaml_infographic_v1`。不可加入 `slides`。

## 根層級區塊

- `document`：受眾、目的、關鍵訊息、語言。
- `canvas`：profile、長寬比、尺寸、安全區、閱讀方向。
- `design_system`：版本化的全域 profile，或明確的自訂覆寫。
- `information_architecture`：語意型態、資訊密度、閱讀路徑。
- `layout`：一種受控構圖，以及百分比表示的區塊（zone）。
- `sections`：依序排列的內容區塊。
- `data_integrity`：精確數字、引用出處、資料集。
- `accessibility`：替代文字、對比度、非顏色線索。
- `output`：baked 或 plate 的產物契約。
- `validation`：固定的驗證 profile；它不能關掉任何硬性檢查。

## section 契約

每個 section 都必須有 `id`、`order`、`role`、`layout_slot`、`core_point`、`visible_text`、`items`、`visual`、`evidence_refs` 與 `emphasis`。

- `id` 不可重複，`order` 從 1 開始連續編號。
- `primary` 強調最多只能出現一次。
- 可查證的數字要放進 `data_integrity.exact_numbers`，並以 ID 參照引用出處。
- 區塊一律用百分比；絕不可存入特定 agent 的絕對路徑。

## 風格 profile

`profile_ref` 接受兩種寫法：

- `global:<style_id>@<major.minor.patch>` — 具名且帶版本的 profile。`style_id` 為小寫加底線。`design_system.preset` 與 `preset_version` 必須重複填入同樣的 id 與版本。
- `explicit` — 內嵌的自訂風格，此時 `overrides` 不可為空。

`global:` 參照會把底線換成連字號後解析成 `<style_id>.yaml`，並依下列順序搜尋：

1. `~/.agents/visual-styles/<file>.yaml`
2. 本技能內附的 `assets/<file>.yaml`

解析到的 profile 必須宣告與參照相符的 `style.id` 與 `style.version`，外加一份 `palette`，且定義出每一個必要角色——`background`、`background_secondary`、`surface`、`text`、`keyword`、`highlight`——每個都是 `#RRGGBB` 格式。**驗證檢查的是結構，不是特定顏色**，所以只要每個角色都存在且格式正確，任何調色盤都可以用。

內附的 `tech_calm` 只是「其中一份 profile」，不是寫死的必要條件。

## 產出契約

- `baked`：`final_path` 與 `prompt_record`；不可有底圖、SVG 疊加層或 `overlay_blocks`。
- `plate`：`plate_path`、`overlay_path`、`final_path`、`prompt_record`、`background_text_policy: none`，以及非空的 `overlay_blocks`。
- 所有路徑都必須相對於專案，且不可含有 `..`。
