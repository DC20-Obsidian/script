# Manual fixups
## Spell names
-
# Spell descriptions
- Find Familar

To create to required json file install https://github.com/run-llama/liteparse and run:
```sh
lit parse --no-ocr --output dc20_0.10beta.orig.json --format json "DC20 RPG 0.10 Beta v1.0.pdf"
cat dc20_0.10.5beta.orig.json | jq '.pages | map(del(.boundingBoxes) | .textItems = (.textItems | map(del(.x,.y,.width,.height,.confidence))))' > dc20_0.10.5beta.json
```
**Note the presence of the `--no-ocr` argument**
