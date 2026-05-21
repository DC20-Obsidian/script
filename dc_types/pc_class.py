import re
from pathlib import Path
from typing import Optional, Self

from dc_types.frag_list import FragList
from dc_types.item import Item
from dc_types.proto_item import DCProtoItem
from dc_types.text_frag import TextFrag
from utils.frontmatter import fmt_bool, list_to_yaml
from utils.split import SplitBuilder, split_items_full


class Class(Item):
    _type: str = "class"

    def __init__(self):
        self._type: str = "class"
        self.page: int = -1
        self.name: str = ""
        self.flavor_text: str = ""
        self.starting_equipment: dict[str, str] = {}
        self.martial: bool = False
        self.spellcaster: bool = False
        self.combat_training: list[str] = []
        self.stamina_regen: Optional[str] = None
        self.spell_list: Optional[str] = None

        self.flavor_feature: Optional[Feature] = None
        self.features: list[Feature] = []
        self.subclasses: list[Subclass] = []
        # self.debug = None

    @classmethod
    def from_json(cls, d: dict) -> Self:
        cl = cls()
        cl.page = int(d["page"])
        cl.name = d["name"]
        cl.flavor_text = d["flavor_text"]
        cl.starting_equipment = d["starting_equipment"]
        cl.martial = bool(d["martial"])
        cl.spellcaster = bool(d["spellcaster"])
        cl.combat_training = d["combat_training"]
        cl.stamina_regen = d["stamina_regen"]
        cl.spell_list = d["spell_list"]

        cl.flavor_feature = d["flavor_feature"]
        cl.features = d["features"]
        cl.subclasses = d["subclasses"]
        return cl

    def markdown(self) -> str:
        assert self.flavor_feature
        args = {
            "page": self.page,
            "name": self.name,
            "flavor_text": self.flavor_text,
            "starting_equipment": fmt_starting_equipment(self.starting_equipment),
            "martial": fmt_bool(self.martial),
            "spellcaster": fmt_bool(self.spellcaster),
            "combat_training": list_to_yaml(self.combat_training),
            "stamina_regen": fmt_optional(self.stamina_regen, "Stamina Regen"),
            "spell_list": fmt_optional(self.spell_list, "Spell List"),
            "flavor_feature": f"![[{self.flavor_feature.markdown_path()}|{self.flavor_feature.name}]]",
            "features": fmt_features(self.features),
            "subclasses": self.subclasses,
        }
        return class_template.format_map(args)

    @classmethod
    def get_default_page_range(cls) -> slice:
        return slice(209 - 1, 267)

    @classmethod
    def get_save_file(cls, data_folder: Path, version: str) -> Path:
        return data_folder / f"classes_{version}.json"

    def markdown_path(self, prefix: Path = Path("")) -> Path:
        return prefix / f"Classes/{self.name}/{self.name}.md"

    @classmethod
    def split(cls, frags: FragList) -> list[DCProtoItem]:
        prams = SplitBuilder(
            is_header=_is_header,
        ).build()
        return split_items_full(frags, prams, "classes")

    def save_subitems(self, prefix: Path):
        assert self.flavor_feature

        for feature in self.features:
            feature.save_self(prefix)

        self.flavor_feature.save_self(prefix)

        for subclass in self.subclasses:
            subclass.save_self(prefix)
            subclass.save_subitems(prefix)


def _is_header(name: str, frag: TextFrag) -> bool:
    if name:
        return frag.font in ["f3"]
    else:
        return frag.font in ["f3"] and frag.font_size > 25


class Feature(Item):
    _type: str = "feature"

    def __init__(self):
        self._type: str = "feature"
        self.name: str = ""
        self.page: int = -1
        self.level: int = -1
        self.is_flavor: bool = False
        self.description: str = ""
        self.class_name: str = ""
        self.subclass: Optional[str] = None

    @classmethod
    def from_json(cls, d: dict) -> Self:
        f = cls()
        f.name = d["name"]
        f.page = d["page"]
        f.level = d["level"]
        f.is_flavor = d["is_flavor"]
        f.description = d["description"]
        f.class_name = d["class_name"]
        f.subclass = d["subclass"]
        return f

    @classmethod
    def split(cls, frags: FragList) -> list[DCProtoItem]:
        raise

    def markdown_path(self, prefix: Path = Path("")) -> Path:
        if self.subclass:
            return (
                prefix
                / f"Classes/{self.class_name}/Subclasses/{self.subclass}/Features/{self.name}.md"
            )
        else:
            return prefix / f"Classes/{self.class_name}/Features/{self.name}.md"

    def markdown(self) -> str:
        # If no subclass link to class else link to subclass
        class_name: str = self.class_name
        class_name = (
            f'"[[Classes/{class_name}/{class_name}|{class_name}]]"'
            if not self.subclass
            else class_name
        )
        subclass = self.subclass
        subclass: str = (
            f'"[[Classes/{self.class_name}/Subclasses/{subclass}/{subclass}|{subclass}]]"'
            if subclass
            else "null"
        )
        args = {
            "name": self.name,
            "page": self.page,
            "level": self.level,
            "is_flavor": fmt_bool(self.is_flavor),
            "description": self.description,
            "class_name": class_name,
            "subclass": subclass,
        }
        return feature_template.format_map(args)

    def fixup(self) -> Self:
        if self.name == "Subclass":
            self.description = re.sub(
                r"\*\*([a-zA-z -]+)\*\*", r"**(\1)**", self.description
            )
        return self


class Subclass(Item):
    _type: str = "subcalss"

    def __init__(self):
        self._type: str = "subclass"
        self.name: str = ""
        self.page: int = -1
        self.flavor_feature: Optional[Feature] = None
        self.features: list[Feature] = []
        self.class_name: str = ""

    @classmethod
    def from_json(cls, d: dict) -> Self:
        subclass = cls()
        subclass.name = d["name"]
        subclass.page = d["page"]
        subclass.flavor_feature = d["flavor_feature"]
        subclass.features = d["features"]
        subclass.class_name = d["class_name"]
        return subclass

    @classmethod
    def split(cls, frags: FragList) -> list[DCProtoItem]:
        raise

    def markdown_path(self, prefix: Path = Path("")) -> Path:
        return (
            prefix / f"Classes/{self.class_name}/Subclasses/{self.name}/{self.name}.md"
        )

    def save_subitems(self, prefix: Path):
        assert self.flavor_feature
        self.flavor_feature.save_self(prefix)
        for feature in self.features:
            feature.save_self(prefix)

    def markdown(self) -> str:
        assert self.flavor_feature
        args: dict = {
            "name": self.name,
            "page": self.page,
            "flavor_feature": f"![[{self.flavor_feature.markdown_path()}|{self.flavor_feature.name}]]",
            "features": fmt_features(self.features),
            "class_name": self.class_name,
        }
        return subclass_template.format_map(args)


class_template: str = """---
name: {name}
page: {page}
martial: {martial}
spellcaster: {spellcaster}
combat_training:
{combat_training}
---
## Flavor
{flavor_text}

## Starting Equipment
{starting_equipment}
{stamina_regen}{spell_list}
# Flavor Feature
{flavor_feature}

# Class Features
{features}
"""


def fmt_starting_equipment(equip: dict[str, str]) -> str:
    text = ""
    for k in equip:
        text += f"- **{k}:** {equip[k]}\n"
    return text


def fmt_optional(text: Optional[str], header: str) -> str:
    if not text:
        return ""
    return f"## {header}\n{text}\n"


def fmt_features(features: list[Feature]) -> str:
    text: str = ""
    prev_level: int = 0
    for feature in features:
        if feature.level != prev_level:
            text += f"## Level {feature.level}\n"
            prev_level = feature.level
        text += f"![[{feature.markdown_path()}]]\n\n"
    return text


feature_template: str = """---
name: {name}
page: {page}
level: {level}
is_flavor: {is_flavor}
class_name: {class_name}
subclass: {subclass}
---
{description}
"""

subclass_template: str = """---
name: {name}
page: {page}
class_name: "[[Classes/{class_name}/{class_name}|{class_name}]]"
---
# Flavor Feature
{flavor_feature}

# Features
{features}
"""
