# Manual fixups
## Spell names
-
# Spell descriptions
- Find Famillar

To create to required json file install https://github.com/run-llama/liteparse and run:
```sh
cd <path to project>
mkdir -p dc-obsidian/json
lit parse --no-ocr --output dc-obsidian/json/dc20_0.10.5_pdf_orig.json --format json "DC20 RPG 0.10.5 Beta v1.0.pdf"
cat dc-obsidian/json/dc20_0.10.5_pdf_orig.json | jq '.pages | map(del(.boundingBoxes) | .textItems = (.textItems | map(del(.x,.y,.width,.height,.confidence))))' > ./dc-obsidian/json/dc20_0.10.5_pdf_filtered.json
```
**Note the presence of the `--no-ocr` argument**

# Note
This software is distributed separately form the input/output documents for legal reasons. Copy the dc-obsidian directory into this one in order to run this software
