[![made-for-Obsidian](https://img.shields.io/badge/Made%20for-Obsidian-7c3aed.svg?logo=obsidian)](https://obsidian.md)  
[![Static Badge](https://img.shields.io/badge/Made%20with%20-%20DC20%20-%20%233a1068)](https://thedungeoncoach.com/pages/dc20)

[![Git](https://img.shields.io/badge/Git-F05032?logo=git&logoColor=fff)](https://git-scm.com/)
[![made-with-Markdown](https://img.shields.io/badge/Markdown-1f425f.svg?logo=markdown)](https://commonmark.org)
[![JSON](https://img.shields.io/badge/JSON-000?logo=json&logoColor=fff)](https://www.json.org/)  
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](https://www.python.org/)
[![Ruff](https://custom-icon-badges.demolab.com/badge/Ruff-261230.svg?logo=ruff-logo)](https://docs.astral.sh/ruff/)
[![ty](https://custom-icon-badges.demolab.com/badge/ty-261230.svg?logo=ty-astral-logo)](https://docs.astral.sh/ty/)  
[![Hugo](https://img.shields.io/badge/Hugo-FF4088?logo=hugo&logoColor=fff)](https://gohugo.io/)
[![Cloudflare](https://img.shields.io/badge/Cloudflare%20Pages-F38020?logo=Cloudflare&logoColor=white)](https://pages.cloudflare.com/)  

# FAQ
## What is this?
This is a script to convert the DC20 TTRPG PDF into JSON and Obsidian flavored markdown.

## How do I access the output?
Use the website to unlock and download the zip archive. [website](https://dc20obsidain.pages.dev/) (TODO include link to website) It requires owning a copy of the PDF to unlock, so if you don't own a copy, go ahead and buy one [here](https://thedungeoncoach.com/products/dc20-core-rules).

## Is there a free version?
Yes, Alan (AKA the Dungeon Coach) has graciously permitted us to share the player options for levels 1-2.
*(Note: while the code in this repository is open source, DC20, both the source PDF and the output of this script, including the free section, is proprietary. Any questions regarding this should be directed to Alan thedungeoncoach@thedungeoncoach.com, or one of his [discord moderators](https://discord.gg/8yCwh6ZVq7))*

## What is the project status/roadmap?
- [X] spells
	- [X] tags
	- [X] schools
	- [X] sources
- [X] maneuvers
	- [X] maneuvers types
- [X] conditions
	- [ ] overlapping conditions?
- [X] ancestries
- [X] talents
- [X] the Wild Magic Table
- [ ] classes
	- [ ] subclasses
- [ ] actions
- [ ] damage types
- [ ] attributes
	- [ ] saves
	- [ ] skills
	- [ ] trades
	- [ ] languages
- [ ] equipment
	- [ ] weapons
		- [ ] styles
		- [ ] properties
	- [ ] shields
	- [ ] armor
	- [ ] spell focuses
- [ ] character sheets
- [ ] monster stat blocks
- [ ] Magazine content
	- [ ] Monsters
	- [ ] Magic items
	- [ ] ancestries
	- [ ] classes
		- [ ] Psion
		- [ ] Articicer
		- [ ] Summoner



## What is the difference between the locked and unlocked versions?
The free/publicly available version is missing the following:
- **Spells with a base MP cost of 2 or more**
	-  Banish, Gravity Shift, Increase Gravity, Time Stop, Confusion, Slumber, Revivify, Disintegrating Beam, Disintegrate
- **Maneuvers with a base SP cost of 2 or more**
	- Sunder Strike
- **Talents with a level requirement of 3 or more**
	- Unfathomable Strength, Expanded Repertoire, Helping Hands, Champion's Resolve, Disciplined Combatant, Bountiful Blessings, Divine Cleanse, Seize Momentum, Coordinated Command, Wild Form Expansion, Nature's Vortex, Pack Leader, Big Game Hunter, Internal Damage, Steel Fist, Unseen Ambusher, Sinister Shot, Greater Innate Power, Font of Magic, Sling-blade, Adaptive Bond, Pact Bane, Warlock Subcontract, Crowned Sigil, Overly Prepared Spellcaster, Adept Multiclass, Expert Multiclass, Master Multiclass
- **Monsters**
- **Magazine Content** (This will be locked behind their respective magazines)

# Development
## Adding a new Item Type

- Add the type to `dc_types/`, inheriting from `Item` (dc_types/item)
  - implement `__init__`, `from_json`, `markdown`, `get_default_page_range`, `get_save_file`, and `markdown_path`
- Add to the `dc_obj_decoder` function in `dc_types/serde.py`
- Add a parser to `parsers/`
- Add to the `get_type` function in `main.py`

### Debugging
- Make sure you have the correct set of pages
- Make sure the proto items are split correctly
  - `./main.py --type <type> --all --print --raw | jq '.[].name'`
	  - Lists all proto item names
  - `./main.py --type <type> --all --print --raw | jq '.[].frags | .[0:3] + .[-4:-1]`
	  - This shows the first and last three fragments in all proto items
- View unprocessed fragments
  - Add an early return to your parser
  - `./main.py --type <type> --all --print --raw -u | jq '.[0].frags[0:<number of fragment to view>]'`

## Development Tools
- `git`: version control
- `ruff`: python formatter/linter
- `ty`: python type checker
- `jq`: JSON utility
- `fx`: JSON pager
- ripgrep: find
- `sd`: find and replace
- `typos`: spell checker
- obsidian: view final output
- `fzf`: Fuzzy finder, used for `stats.sh`


# Note
This software is distributed separately form the input/output documents for legal reasons. Copy or symlink the dc-obsidian directory into this one in order to run this software.
**DO NOT include the input/output file(s) in commits/pull requests**

# Input
The input file is in the encrypted zip file included on the website, unlock it with `unlock.html` using the source PDF as the key file. You shouldn't have to generate it manually, but the instructions are below if you need them.

## Generating the input files from the PDF
**Note: I have only tested this on Linux so your mileage may vary**

To create to required JSON file install https://github.com/run-llama/liteparse and run:
***NOTE the presence of the `--no-ocr` argument***
```sh
cd <path to project>
mkdir -p dc-obsidian/json

lit parse --no-ocr --output dc-obsidian/json/dc20_0.10.5_pdf_orig.json --format json "DC20 RPG 0.10.5 Beta v1.0.pdf"

cat dc-obsidian/json/dc20_0.10.5_pdf_orig.json | jq '.pages | map(del(.boundingBoxes) | .textItems = (.textItems | map(del(.confidence))))' > ./dc-obsidian/json/dc20_0.10.5_pdf_filtered.json
```
