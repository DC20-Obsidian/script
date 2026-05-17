import re
from lib.fixup_text import fixup_description
from dc_types.text_frag import TextFrag
from dc_types.skill import Skill
from dc_types.proto_item import DCProtoItem


def parse_skill(proto: DCProtoItem) -> Skill:
    skill = Skill()
    skill.name = proto.name
    skill.page = proto.page
    frags = proto.frags

    attributes: list[str] = ["Might", "Agility", "Intelligence", "Charisma", "Prime"]
    skill.attribute = attributes[max(proto.section, 0)]

    use_fonts: list[str] = ["f7", "f21"]

    def frag_text(frag: TextFrag) -> str:
        return frag.text

    uses: list[str] = list(
        map(frag_text, filter(lambda f: f.font in use_fonts, frags._frags))
    )
    description = fixup_description(frags.markup_while(lambda _: True))

    # Nest/make lists see "Survival"
    description = re.sub(r"\n- ", "\n  - ", description)
    skill.description = re.sub(r" \*\*\*", "\n- ***", description)

    skill.uses = uses

    return skill
