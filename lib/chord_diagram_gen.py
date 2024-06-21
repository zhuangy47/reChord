import sys
import svgwrite
# from PIL import image
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
    def __init__(self, num_strings, notes: list[tuple[int, int]] = [], starting_fret: int = 1, barres: list[tuple[int, int, int]] = [], mute: list[int] = [], title: str = "new_chord", params: dict = {}):
        self.num_strings = num_strings
        self.starting_fret = starting_fret
        self.mute = mute
        self.notes = notes
        self.barres = barres
        self.title = title
        self.params = params

    @property
    def num_strings(self):
        return self._num_strings
    
    @num_strings.setter
    def num_strings(self, value):
        self._num_strings = value

    @property
    def starting_fret(self):
        return self._starting_fret
    
    @starting_fret.setter
    def starting_fret(self, value):
        if (value < 1 or value > 100):
            raise ValueError(f"Starting fret is out of bounds [1-100]")
        self._starting_fret = value

    @property
    def mute(self):
        return self._mute
    
    @mute.setter
    def mute(self, value):
        for val in value:
            if (value < 1 or value > self.num_strings):
                raise ValueError(f"String to mute {val} is out of bounded")
        self._mute = value
    @property
    def notes(self):
        return self._notes

    @notes.setter
    def notes(self, value):
        for string, fret in value:
            if (string < 1 or string > self.num_strings + 1):
                raise ValueError(f"Entry [{string}, {fret}] specifies a string that is out of bounds of {self.num_strings} strings")
            if (fret < 1 or fret > 100):
                raise ValueError(f"Entry [{string}, {fret}] specifies a negative fret or too high of a fret")
        self._notes = value

    @property
    def title(self):
        return self._title
    
    @title.setter
    def title(self, value):
        self._title = value or "tmp"

    @property
    def barres(self):
        return self._barres
    
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
        self._barres = value


    @property
    def params(self):
        return self._params
    
    @params.setter
    def params(self, value):
        self._params = {}
        self._params["padding"] = value.get("padding") or 30
        self._params["fret_spacing"] = value.get("fret_spacing") or 30
        self._params["string_spacing"] = value.get("string_spacing") or 20
        self._params["line_thickness"] = value.get("line_thickness") or 3
        self._params["top_line_thickness"] = 10 if self._params["line_thickness"] < 5 else 3 * self._params["line_thickness"]

    def get_max_fret_distance(self):
        min_fret = 101
        max_fret = -1
        for _, fret in self._notes:
            min_fret = min(min_fret, fret)
            max_fret = max(max_fret, fret)
        for fret, _, _ in self._barres:
            min_fret = min(min_fret, fret)
            max_fret = max(max_fret, fret)
        distance = max_fret - min_fret
        if (distance > 6):
            raise ValueError("Your hands aren't that big: fret distance is too big")
        return max_fret - min_fret
        
    def create_image(self):
        num_fret = max(4, self.get_max_fret_distance())
        diagram_width = (self.num_strings - 1) * self.params["string_spacing"] + self.num_strings * self.params["line_thickness"]
        diagram_height = num_fret * self.params["fret_spacing"] + (num_fret) * self.params["line_thickness"] + self.params["top_line_thickness"]
        height = TITLE_PADDING + 2 * self.params["padding"] + diagram_height;
        if self._title == "":
            height = 2 * self.params["padding"] + diagram_height
        width =  2 * self.params["padding"] + diagram_width
        print(width, height)
        chord_svg = svgwrite.Drawing(f"{self.title}.svg", (width, height))
        chord_svg.add(chord_svg.rect(insert = (0, 0), size = (width, height), fill = "white", stroke = "white"))
        chord_svg.add(chord_svg.line(start = (self.params["padding"], self.params["padding"] + TITLE_PADDING), end = (self.params["padding"] + diagram_width, self.params["padding"] + TITLE_PADDING), stroke="black", stroke_width=self.params["top_line_thickness"]))
        chord_svg.save()


if __name__ == "__main__":
    # chord_svg = svgwrite.Drawing(f"test.svg", (1000, 1000))
    # chord_svg.add(chord_svg.rect(insert=(0, 0), size=(1000, 1000), fill="white", stroke="black"))
    # chord_svg.add(chord_svg.rect(insert=(100, 100), size=(100, 100), fill="red", stroke="black"))
    
    # chord_svg.save()
    test = Chord(6)
    test.create_image()
