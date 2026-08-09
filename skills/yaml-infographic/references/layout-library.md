# 受控資訊圖表版型庫

依**資訊關係**選擇，不是依裝飾效果選擇。

| 資訊型態 | 版型 ID | 內容容量 |
|---|---|---|
| `focus` | `focus_hero` | 一個主張搭配一個焦點視覺 |
| `metric` | `single_metric` | 一個主要數字，最多三項輔助事實 |
| `process` | `process_steps` | 三到七個有序項目 |
| `cycle` | `cycle_loop` | 三到六個節點 |
| `comparison` | `comparison_split`、`matrix_quadrant` | 兩組各二到五項，或剛好四格 |
| `timeline` | `timeline` | 三到八個事件 |
| `hierarchy` | `hierarchy_tree` | 二到四層，最多九個節點 |
| `classification` | `classification_grid` | 四到八組 |
| `cause_effect` | `cause_effect_chain` | 三到七個節點 |
| `relationship` | `relationship_map` | 最多八個節點 |
| `data` | `data_story` | 一張主圖表、若干輔助事實、一個結論 |
| `list` | `ranked_list`、`checklist` | 三到八個項目 |
| `anatomy` | `anatomy_callout` | 一個主體，三到八個標註 |
| `story` | `modular_story` | 每個生成區塊三到六個模組 |

極長的長圖用 `modular_story`，並逐區塊生成底圖。換長寬比時要**重新構圖**，不要把某個版型硬裁成另一個版型。
