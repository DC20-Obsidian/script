from dc_types.text_frag import TextFrag
from utils.debug import eprint
import re
from dc_types.frag_list import FragList
from dc_types.pc_class import Class, Feature
from dc_types.proto_item import DCProtoItem
from utils.fixup_text import fixup_description, fixup_name
from utils.split import SplitBuilder, split_items_full


def parse_class(proto: DCProtoItem) -> Class:
    cl = Class()
    cl.page = proto.page
    cl.name = proto.name
    frags: FragList = proto.frags

    # Flavor Text
    cl.flavor_text = re.sub(
        r" \*{3}",
        "\n***",
        fixup_description(frags.markup_until(lambda frag: frag.font == "f27")),
    )

    # TODO Parse Class Table
    assert frags.match_next_regex(".* Class Table$")
    frags.discard_next()
    frags.discard_while(lambda frag: frag.font in ["f19"])  # Table Header
    frags.discard_while(lambda frag: frag.font in ["f22"])

    flavor2: str = fixup_description(  # This part is for Bard flavor text
        frags.markup_until(lambda frag: frag.font in ["f4", "f10"], min_one=False)
    )
    if flavor2:
        cl.flavor_text += f"\n{flavor2}"

    while frags.match_next(lambda frag: frag.font not in ["f3"]):
        next_section: str = frags.cat_while(
            lambda frag, _: frag.font in ["f4", "f10"]
        ).lower()

        if next_section == "startingequipment":
            starting_equipment(frags, cl)
        elif next_section.endswith("path"):
            combat_path(frags, cl)
        else:
            raise Exception(f"Unknown Section: {next_section}")

    # "____ Class Features"
    frags.discard_while(lambda frag: frag.font == "f3")
    class_features = FragList.slice_until(
        frags, lambda frag: frag.font == "f3" and frag.font_size >= 15
    )

    parse_class_features(class_features, cl)
    frags.discard_while(lambda frag: frag.font == "f3")
    parse_subclasses(frags, cl)

    return cl


def starting_equipment(frags: FragList, cl: Class):
    start_equip = FragList.slice_while(
        frags, lambda frag: frag.font in ["f21", "f7", "f5", "f14", "f11"]
    )
    starting_equipment_inner(start_equip, cl)


def starting_equipment_inner(frags: FragList, cl: Class):
    equipment_fonts: list[str] = ["f7", "f21"]
    if cl.name in ["Bard", "Cleric"]:
        equipment_fonts.append("f11")
    if cl.name not in ["Cleric", "Warlock"]:
        equipment_fonts.append("f14")

    prams = SplitBuilder(
        is_header=equipment_fonts,
    ).build()

    items: list[DCProtoItem] = split_items_full(frags, prams, "<none>")

    equip: dict[str, str] = {
        item.name.rstrip(" :"): fixup_description(item.frags.markup_rest().lstrip(" :"))
        for item in items
    }
    cl.starting_equipment = equip


def combat_path(frags: FragList, cl: Class):
    path = FragList.slice_while(
        frags, lambda frag: frag.font in ["f21", "f7", "f5", "f14", "f11", "f15"]
    )
    combat_path_inner(path, cl)


def combat_path_inner(frags: FragList, cl: Class):
    prams = SplitBuilder(
        is_header=["f7", "f21"],
    ).build()

    items: list[DCProtoItem] = split_items_full(frags, prams, "<none>")

    for item in items:
        match item.name:
            case (
                "Combat Training"
            ):  # TODO make ["All ____"] -> ["Light ____", "Heavy ____"]
                cl.combat_training = [
                    fixup_name(tr.strip(" :"), "combat training")
                    for tr in item.frags.cat_rest().split(",")
                ]
            case "Maneuvers" | "Stamina Points":
                cl.martial = True
            case "Stamina Regen":
                cl.stamina_regen = fixup_description(
                    item.frags.markup_rest().strip(" :")
                )
            case "Spell List":
                cl.spell_list = fixup_description(item.frags.markup_rest().strip(" :"))
            case "Spells Known" | "Mana Points":
                cl.spellcaster = True


def parse_class_features(frags: FragList, cl: Class):
    def is_level(name: str, frag: TextFrag) -> bool:
        return frag.font == "f4" and (
            (frag.text.startswith("Le") and name == "") or name != ""
        )

    level_split_prams = SplitBuilder(
        is_header=is_level,
    ).build()
    levels = split_items_full(frags, level_split_prams, "<none>")
    cl.debug = [level.name for level in levels]
    # cl.debug = [level.frags._frags[0:2] for level in levels]
    for level in levels:
        cl.features.extend(parse_class_level(level, cl))


def parse_class_level(proto: DCProtoItem, cl: Class) -> list[Feature]:
    lv_match = re.match("Level ?([0-9]+)", proto.name)
    assert lv_match
    level: int = int(lv_match.group(1))

    split_prams = SplitBuilder(
        is_header=["f3"],
    ).build()

    def parse_feature(proto: DCProtoItem, level: int) -> Feature:
        f = Feature()
        f.name = proto.name
        f.page = proto.page
        f.level = level
        f.description = fixup_description(proto.frags.markup_rest())
        return f

    features_proto: list[DCProtoItem] = split_items_full(
        proto.frags, split_prams, "features"
    )
    features: list[Feature] = [parse_feature(f, level) for f in features_proto]

    if level == 1: # Flavor Feature
        flavor_feature: Feature = features.pop(-1)
        flavor_name = re.match(r"([a-zA-Z -]+) \( ?Flavor", flavor_feature.name)
        eprint(flavor_feature.name)
        assert flavor_name
        flavor_feature.name = flavor_name.group(1)
        if cl.name == "Druid":
            flavor_feature.description = re.sub(
                " WILD FORM TEMPLATES SIDEBAR .*", "", flavor_feature.description
            )
        cl.flavor_feature = flavor_feature

    return [f for f in features if f.name not in ["Talent", "Path Progression", "Ancestry Points"]]


def parse_subclasses(frags: FragList, cl: Class):
    pass
