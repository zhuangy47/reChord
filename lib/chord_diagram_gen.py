import sys
from PIL import image
TITLE_PADDING = 30

class Chord:
    '''
    Constructor for the Chord Diagram class
    inputs: 
        notes: [(<string # [1-6]>, fret #), ...]
        starting_fret: int
        barres: [(fret #, starting string, ending string)...]
        mute: []
        params: {
            padding: int
            fret_size: int
            line_thickness: int
        }
    '''
    def __init__(self, num_strings, notes: list[tuple[int, int]], starting_fret: int = 1, barres: list[tuple[int, int, int]] = [], mute: list[int] = [], title: str = "", params: dict = {}):
        self.num_strings = num_strings
        self.starting_fret = starting_fret
        self.notes = notes
        self.barres = barres
        self.title = title
        self.param = {}

    
    @starting_fret.setter
    def starting_fret(self, value):
        if (value < 1 or value > 100):
            raise ValueError(f"Starting fret is out of bounds [1-100]")
        self.starting_fret = value


    @notes.setter
    def notes(self, value):
        for string, fret in value:
            if (string < 1 or string > self.num_strings + 1):
                raise ValueError(f"Entry [{string}, {fret}] specifies a string that is out of bounds of {self.num_strings} strings")
            if (fret < 1 or fret > 100):
                raise ValueError(f"Entry [{string}, {fret}] specifies a negative fret or too high of a fret")
        self.notes = value

    @barres.setter
    def barres(self, value):
        for fret, starting_string, ending_string in value:
            if (fret < 1 or fret > 100):
                raise ValueError(f"Entry [{fret}, {starting_string}, {ending_string}] specifies a negative fret or too high of a fret")
            if (ending_string - starting_string <= 0):
                raise ValueError(f"Ending string number must be strictly greater than starting string number")
            if (ending_string > self.num_strings):
                raise ValueError(f"Ending string is too large; out of bounds: (max {self.num_strings})")
            if (starting_string < 1):
                raise ValueError(f"Starting string is too small, out of bounds: (min: 1)")
        self.barres = value

    @params.setter
    def params(self, value):
        self.padding = value.get("padding") or 30
        self.fret_spacing = value.get("fret_spacing") or 30
        self.string_spacing = value.get("string_spacing") or 20
        self.line_thickness = value.get("line_thickness") or 3
        self.top_line_thickness = 10 if self.line_thickness < 5 else 3 * self.line_thickness

    def get_max_fret_distance(self):
        min_fret = 101
        max_fret = -1
        for _, fret in self.notes:
            min_fret = min(min_fret, fret)
            max_fret = max(max_fret, fret)
        for fret, _, _ in self.barres:
            min_fret = min(min_fret, fret)
            max_fret = max(max_fret, fret)
        distance = max_fret - min_fret
        if (distance > 6):
            raise ValueError("Your hands aren't that big: fret distance is too big")
        return max_fret - min_fret
        
    def create_image(self):
        num_fret = max(4, self.get_max_fret_distance())
        height = TITLE_PADDING + 2 * self.padding + num_fret * self.fret_spacing + (num_fret) * self.line_thickness + self.top_line_thickness;
        if self.title == "":
            height = 2 * self.padding + num_fret * self.fret_size + (num_fret) * self.line_thickness + self.top_line_thickness
        width =  2 * self.padding + (self.num_strings - 1) * self.string_spacing + self.num_strings * self.line_thickness

        


    def 

