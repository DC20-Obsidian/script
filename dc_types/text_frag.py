
class TextFrag:
    def __init__(self, fragment: dict, page: int):
        self.page: int = page
        self.text: str = str(fragment['text'])
        self.font: str = str(fragment['fontName']).removeprefix('g_d0_')
        self.font_size = int(fragment['fontSize'])

