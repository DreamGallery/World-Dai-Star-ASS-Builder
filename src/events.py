class ass_events(object):

    def __init__(self, layer: int = 0, start: str = "", end: str = "", style: str = "", name: str = "", marginL: int = 0, marginR: int = 0, marginV: int = 0, effect: str = "", text: str = ""):
        self.layer = layer
        self.start = start
        self.end = end
        self.style = style
        self.name = name
        self.marginL = marginL
        self.marginR = marginR
        self.marginV = marginV
        self.effect = effect
        self.text = text

    def echo_dialogue(self) -> str:
        dialogue = 'Dialogue: %d,%s,%s,%s,%s,%d,%d,%d,%s,%s' %(self.layer, self.start, self.end, self.style, self.name, self.marginL, self.marginR, self.marginV, self.effect, "")
        return dialogue
    
    @classmethod
    def echo_format(self) -> str:
        _format = "Format:"
        for attribute in self.__init__.__code__.co_varnames[1:]:
            _format = _format + f" {attribute},"
        _format = _format[:-2]
        return _format