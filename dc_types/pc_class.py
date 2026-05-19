from pathlib import Path
from typing import Optional, Self

from dc_types.frag_list import FragList
from dc_types.item import Item
from dc_types.proto_item import DCProtoItem
from dc_types.text_frag import TextFrag
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
        self.debug = None

    @classmethod
    def from_json(cls, d: dict) -> Self:
        raise

    def markdown(self) -> str:
        raise

    @classmethod
    def get_default_page_range(cls) -> slice:
        return slice(209 - 1, 267)

    @classmethod
    def get_save_file(cls, data_folder: Path, version: str) -> Path:
        return data_folder / f"classes_{version}.json"

    def markdown_path(self, prefix: Path) -> Path:
        raise

    @classmethod
    def split(cls, frags: FragList) -> list[DCProtoItem]:
        prams = SplitBuilder(
            is_header=_is_header,
        ).build()
        return split_items_full(frags, prams, "classes")

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
        self.description: str = ""

    @classmethod
    def from_json(cls, d: dict) -> Self:
        raise

    @classmethod
    def split(cls, frags: FragList) -> list[DCProtoItem]:
        raise

    def markdown_path(self, prefix: Path) -> Path:
        raise

    def markdown(self) -> str:
        raise


class Subclass(Item):
    _type: str = "subcalss"
    def __init__(self):
        self._type: str = "subclass"
        self.name: str = ""
        self.page: int = -1
        self.flavor_feature: Optional[Feature] = None
        self.features: list[Feature] = []

    @classmethod
    def from_json(cls, d: dict) -> Self:
        raise

    @classmethod
    def split(cls, frags: FragList) -> list[DCProtoItem]:
        raise

    def markdown_path(self, prefix: Path) -> Path:
        raise

    def markdown(self) -> str:
        raise
