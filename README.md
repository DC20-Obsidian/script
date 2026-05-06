# Manual fixups
## Spell names
-
# Spell descriptions
- Find Famillar

# Generating the input files from the PDF

To create to required json file install https://github.com/run-llama/liteparse and run:
```sh
cd <path to project>
mkdir -p dc-obsidian/json
lit parse --no-ocr --output dc-obsidian/json/dc20_0.10.5_pdf_orig.json --format json "DC20 RPG 0.10.5 Beta v1.0.pdf"
cat dc-obsidian/json/dc20_0.10.5_pdf_orig.json | jq '.pages | map(del(.boundingBoxes) | .textItems = (.textItems | map(del(.x,.y,.width,.height,.confidence))))' > ./dc-obsidian/json/dc20_0.10.5_pdf_filtered.json
```
**Note the presence of the `--no-ocr` argument**

# Adding a new Item Type

- Add the type to `dc_types/`, inheriting from `Item` (dc_types/item)
  - impliment `__init__`, `from_json`, `markdown`, `get_default_page_range`, `get_save_file`, and `markdown_path`
- Add to the `dc_obj_decoder` function in `dc_types/serde.py`
- Add a parser to `parsers/`
- Add to the `get_type` function in `main.py`

## Debugging
- Make sure you have the correct set of pages
- Make sure the proto items are split correctly
  - `./main.py --type <type> --all --print --raw | jq '.[].name'`
- View unprocessed fragments
  - Add an early return to your parser
  - `./main.py --type <type> --all --print --raw -u | jq '.[0].frags[0:<number of fragment to view>]'`

## Development Tools
- `ruff`: python formater/linter
- `ty`: python type checker
- `jq`: JSON utility
- `fx`: JSON pager
- ripgrep: find
- `sd`: find and replace
- `typos`: spell checker
- obsidian: view final output


# Note
This software is distributed separately form the input/output documents for legal reasons. Copy the dc-obsidian directory into this one in order to run this software
