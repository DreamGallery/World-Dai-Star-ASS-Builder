class ass_events(object):

    def __init__(self, Layer: int = 0, Start: str = "", End: str = "", Style: str = "", Name: str = "", MarginL: int = 0, MarginR: int = 0, MarginV: int = 0, Effect: str = "", Text: str = ""):
        self.Layer = Layer
        self.Start = Start
        self.End = End
        self.Style = Style
        self.Name = Name
        self.MarginL = MarginL
        self.MarginR = MarginR
        self.MarginV = MarginV
        self.Effect = Effect
        self.Text = Text

    def echo_dialogue(self) -> str:
        dialogue = 'Dialogue: %d,%s,%s,%s,%s,%d,%d,%d,%s,%s' %(self.Layer, self.Start, self.End, self.Style, self.Name, self.MarginL, self.MarginR, self.MarginV, self.Effect, self.Text)
        return dialogue
    
    @classmethod
    def echo_format(cls) -> str:
        _format = "Format:"
        for attribute in cls.__init__.__code__.co_varnames[1:]:
            _format = _format + f" {attribute},"
        _format = _format[:-1]
        return _format