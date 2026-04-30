
class TextItem:
    def __init__(self, item: dict, page: int):
        self.page: int = page
        self.text: str = str(item['text'])
        self.font: str = str(item['fontName']).removeprefix('g_d0_')
        self.font_size = int(item['fontSize'])

