import json
from src.read_ini import config

class ass_styles(object):
    def __init__(self, Name: str = "", Fontname: str = "", Fontsize: int = "", PrimaryColour: str = "", SecondaryColour: str = "", OutlineColour: str = "", BackColour: str = "", Bold: int = "", Italic: int = "", Underline: int = "", StrikeOut: int = "", ScaleX: int = "", ScaleY: int = "", Spacing: int = "", Angle: int = "", BorderStyle: int = "", Outline: int = "", Shadow: int = "", Alignment: int = "", MarginL: int = "", MarginR: int = "", MarginV: int = "", Encoding: int = ""):
        self.Name = Name
        self.Fontname = Fontname
        self.Fontsize = Fontsize
        self.PrimaryColour = PrimaryColour
        self.SecondaryColour = SecondaryColour
        self.OutlineColour = OutlineColour
        self.BackColour = BackColour
        self.Bold = Bold
        self.Italic = Italic
        self.Underline = Underline
        self.StrikeOut = StrikeOut
        self.ScaleX = ScaleX
        self.ScaleY = ScaleY
        self.Spacing = Spacing
        self.Angle = Angle
        self.BorderStyle = BorderStyle
        self.Outline = Outline
        self.Shadow = Shadow
        self.Alignment = Alignment
        self.MarginL = MarginL
        self.MarginR = MarginR
        self.MarginV = MarginV
        self.Encoding = Encoding

    def echo(self) -> str:
        style = 'Style: %s,%s,%d,%s,%s,%s,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d' %(self.Name, self.Fontname, self.Fontsize, self.PrimaryColour, self.SecondaryColour, self.OutlineColour, self.BackColour, self.Bold, self.Italic, self.Underline, self.StrikeOut, self.ScaleX, self.ScaleY, self.Spacing, self.Angle, self.BorderStyle, self.Outline, self.Shadow, self.Alignment, self.MarginL, self.MarginR, self.MarginV, self.Encoding)
        return style

    @classmethod
    def echo_format(cls) -> str:
        _format = "Format:"
        for attribute in cls.__init__.__code__.co_varnames[1:]:
            _format = _format + f"\u0020{attribute},"
        _format = _format[:-1]
        return _format
    

style_1 = ass_styles(*json.loads(config.get("ASS Style", "style_1")))
style_2 = ass_styles(*json.loads(config.get("ASS Style", "style_2")))
style_3 = ass_styles(*json.loads(config.get("ASS Style", "style_3")))