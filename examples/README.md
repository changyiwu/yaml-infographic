# YAML 範例

這裡的範例只保存可公開、可改寫的 `spec.yaml`，不保存本機 prompt record、生成圖片或絕對路徑。

- `process-baked`：1:1 五步流程圖，適合短文案的純圖片生成。
- `comparison-plate`：4:5 左右比較圖，文字與精確內容由 SVG 疊加。

驗證範例：

```powershell
python .\skills\yaml-infographic\scripts\validate_spec.py --spec .\examples\process-baked\spec.yaml
python .\skills\yaml-infographic\scripts\validate_spec.py --spec .\examples\comparison-plate\spec.yaml
```
