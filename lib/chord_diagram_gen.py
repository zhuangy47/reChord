import sys
import svgwrite

TITLE_PADDING = 15

class Chord:
    '''
    Constructor for the Chord Diagram class
    inputs: 
        num_strings: int
        title: str
        starting_fret: int
        notes: [(<string #>, fret #), ...]
        barres: [(fret #, starting string #, ending string #), ...]
        mute: [(list of string # to be marked muted)] 
        params: {
            padding: int
            fret_spacing: int
            line_thickness: int
            string_spacing: int
            top_line_thickness: int
        }
    '''
    def __init__(self, num_strings, title: str = "", starting_fret: int = 1, notes: list[tuple[int, int]] = [], barres: list[tuple[int, int, int]] = [], mute: list[int] = [], params: dict = {}):
        self.num_strings = num_strings
        self.starting_fret = starting_fret
        self.muted_strings = mute
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
    def muted_strings(self):
        return self._muted_strings
    
    @muted_strings.setter
    def muted_strings(self, value):
        for val in value:
            if (val < 1 or val > self.num_strings):
                raise ValueError(f"String to mute {val} is out of bounded")
        self._muted_strings = value

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
        if value == "":
            self._title = "test"
        else:
            self._title = value 

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
        self._params["markers_spacing"] = 25
        self._params["padding"] = value.get("padding") or 30
        self._params["fret_spacing"] = value.get("fret_spacing") or 30
        self._params["string_spacing"] = value.get("string_spacing") or 20
        self._params["line_thickness"] = value.get("line_thickness") or 3
        self._params["top_line_thickness"] = value.get("top_line_thickness") or 10 if self._params["line_thickness"] < 5 else 3 * self._params["line_thickness"]

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
    
    def get_open_strings(self):
        to_ret = set(range(1, self.num_strings + 1))
        for string, _ in self.notes:
            if string in to_ret:
                to_ret.discard(string)
        for barre_range in self.barres:
            for string in range(barre_range[1], barre_range[2] + 1):
                if string in to_ret:
                    to_ret.discard(string)
        for muted in self.muted_strings:
            if muted in to_ret:
                to_ret.discard(muted)
        return to_ret

    def draw_mute_symbol(self, chord_svg, string_number):
        index = abs(self.num_strings - string_number)
        y_start = TITLE_PADDING + self.params["padding"] + self.params["markers_spacing"] / 2
        center = (self.params["padding"] + index * (self.params["string_spacing"] + self.params["line_thickness"]) + self.params["line_thickness"] / 2, y_start)
        chord_svg.add(chord_svg.line(
            start = (center[0] - self.params["markers_spacing"] / 3, center[1] - self.params["markers_spacing"] / 3),
            end = (center[0] + self.params["markers_spacing"] / 3, center[1] + self.params["markers_spacing"] / 3),
            stroke_width = self.params["line_thickness"],
            stroke = "black"
        ))
        chord_svg.add(chord_svg.line(
            start = (center[0] + self.params["markers_spacing"] / 3, center[1] - self.params["markers_spacing"] / 3),
            end = (center[0] - self.params["markers_spacing"] / 3, center[1] + self.params["markers_spacing"] / 3),
            stroke_width = self.params["line_thickness"],
            stroke = "black"
        ))

    def draw_note(self, chord_svg, string, fret):
        string_index = abs(self.num_strings - string)
        fret_index = fret - self.starting_fret
        x_pos = self.params["padding"] + string_index * (self.params["string_spacing"] + self.params["line_thickness"]) + self.params["line_thickness"] / 2
        y_pos = TITLE_PADDING + self.params["padding"] + self.params["markers_spacing"] + self.params["top_line_thickness"] + fret_index * (self.params["line_thickness"] + self.params["fret_spacing"]) + self.params["fret_spacing"] / 2
        chord_svg.add(chord_svg.circle(
            center = (x_pos, y_pos),
            r = self.params["markers_spacing"] / 2.5 / 1.75
        ))
        
    def create_image(self):
        num_frets = max(4, self.get_max_fret_distance())
        diagram_width = (self.num_strings - 1) * self.params["string_spacing"] + self.num_strings * self.params["line_thickness"]
        diagram_height = num_frets * self.params["fret_spacing"] + (num_frets - 1) * self.params["line_thickness"] + self.params["top_line_thickness"]
        height = TITLE_PADDING + 2 * self.params["padding"] + diagram_height + self.params["markers_spacing"];
        if self._title == "":
            height = 2 * self.params["padding"] + diagram_height + self._params["markers_spacing"]
        width =  2 * self.params["padding"] + diagram_width 

        chord_svg = svgwrite.Drawing(f"./tmp/svg/{self.title}.svg", (width, height))
        
        # White Canvas
        chord_svg.add(chord_svg.rect(insert = (0, 0), size = (width, height), fill = "white", stroke = "white"))
        
        # Top Line (Rectangle)
        chord_svg.add(chord_svg.rect(
            insert = (self.params["padding"], self.params["padding"] + TITLE_PADDING + self.params["markers_spacing"]),
            size = (diagram_width, self.params["top_line_thickness"]),
            stroke = "black",
            fill = "black",
            stroke_width = 0
        ))
        
        # Strings
        for string in range(self.num_strings):
            x_offset = string * self.params["string_spacing"] + string * self.params["line_thickness"]
            chord_svg.add(chord_svg.rect(
                insert = (x_offset + self.params["padding"], TITLE_PADDING + self.params["padding"] + self._params["markers_spacing"]),
                size = (self.params["line_thickness"], diagram_height),
                stroke_width = 0,
                stroke = "black",
                fill = "black"
                )
            )

        # Frets
        for fret in range(num_frets):
            y_offset = TITLE_PADDING + self.params["padding"] + self._params["markers_spacing"] + self.params["top_line_thickness"] + self.params["fret_spacing"] + fret * (self.params["line_thickness"] + self.params["fret_spacing"])
            chord_svg.add(chord_svg.rect(
                insert = (self.params["padding"], y_offset),
                size = (diagram_width,self.params["line_thickness"]),
                stroke_width = 0,
                stroke = "black",
                fill = "black"
            ))

        # Open String Symbols
        for open_string in self.get_open_strings():
            index = abs(self.num_strings - open_string)
            y_start = TITLE_PADDING + self.params["padding"] + self.params["markers_spacing"] / 2
            chord_svg.add(chord_svg.circle(
                center = (self.params["padding"] + index * (self.params["string_spacing"] + self.params["line_thickness"]) + self.params["line_thickness"] / 2, y_start),
                r = self.params["markers_spacing"] / 3
            ))
            chord_svg.add(chord_svg.circle(
                center = (self.params["padding"] + index * (self.params["string_spacing"] + self.params["line_thickness"]) + self.params["line_thickness"] / 2, y_start),
                r = self.params["markers_spacing"] / 3 - self.params["line_thickness"],
                fill = "white"
            ))

        # Mute Symbols
        for muted_string in self.muted_strings:
            self.draw_mute_symbol(chord_svg, muted_string)
        

        # Barre Chord
        for barre in self.barres:
            total_top_padding = TITLE_PADDING + self.params["padding"] + self.params["markers_spacing"] + self.params["top_line_thickness"]
            fret_index = barre[0] - self.starting_fret
            y_offset = total_top_padding + fret_index * (self.params["fret_spacing"] + self.params["line_thickness"]) + self.params["fret_spacing"] / 2
            ending_index = self.num_strings - barre[1]
            starting_index = self.num_strings - barre[2]
            chord_svg.add(chord_svg.line(
                start = (self.params["padding"] + starting_index * (self.params["string_spacing"] + self.params["line_thickness"]), y_offset),
                end = (self.params["padding"] + ending_index * (self.params["string_spacing"] + self.params["line_thickness"]) + self.params["line_thickness"], y_offset),
                stroke_width = self.params["fret_spacing"] / 2.5,
                stroke = "black"
            ))
            self.draw_note(chord_svg, barre[1], barre[0])
            self.draw_note(chord_svg, barre[2], barre[0])

        # Notes
        for string, fret in self.notes:
            self.draw_note(chord_svg, string, fret)

        # Starting Fret
        if self.starting_fret != 1:
            total_top_padding = TITLE_PADDING + self.params["padding"] + self.params["markers_spacing"] + self.params["top_line_thickness"]
            y_start = total_top_padding + self.params["fret_spacing"] / 1.5
            chord_svg.add(chord_svg.text(
                text = self.starting_fret,
                font_size = TITLE_PADDING,
                font_family = "Helvetica",
                insert=(self.params["padding"] + diagram_width + self.params["fret_spacing"] / 4, y_start),
                text_anchor = "start"
            ))
 
        # Title
        title_y_offset = self.params["padding"] + TITLE_PADDING / 1.5
        chord_svg.add(chord_svg.text(
            text = self.title,
            font_size = TITLE_PADDING * 1.5,
            font_family = "Helvetica",
            insert=(width / 2, title_y_offset),
            text_anchor = "middle"
        ))

        chord_svg.save()




if __name__ == "__main__":
    test = Chord(6, 
                 title = "F", 
                 notes = [(5, 3), (4, 3)], 
                 mute=[3], 
                 barres = [(1, 1, 2)],
                 params={"top_line_thickness": 10}
                 )
    test = Chord(6, 
                 title = "F# minor",
                 starting_fret = 2 ,
                 notes = [(5, 4), (4, 4)], 
                 barres = [(2, 1, 6)],
                 params={"top_line_thickness": 10}
                 )
    test.create_image()
