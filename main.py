import tkinter as tk
from tkinter import filedialog, simpledialog, ttk
from PIL import Image, ImageTk
import os
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import lib.chord_diagram_gen as cg
import json

BUTTON_STYLE = {
    "font": ("Helvetica", 12, "bold"),
    "bg": "coral",
    "fg": "white",
    "activebackground": "tomato",
    "activeforeground": "white",
    "bd": 2,
    "relief": tk.RAISED,
}

class ReChord(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("ReChord")
        self.geometry("800x600")
        self.iconbitmap("logo.ico")

        self.canvas = tk.Canvas(self, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.on_resize)

        self.button_frame = tk.Frame(self)
        self.button_frame.pack(side=tk.TOP, pady=10)

        self.edit_button = tk.Button(self.button_frame, text="Add/Remove Chords from Canvas", command=self.open_edit_popup, **BUTTON_STYLE)
        self.edit_button.pack(side=tk.LEFT, padx=10)

        self.create_button = tk.Button(self.button_frame, text="Create Chord Diagrams", command=self.open_create_popup, **BUTTON_STYLE)
        self.create_button.pack(side=tk.LEFT, padx=10)
        
        self.delete_button = tk.Button(self.button_frame, text="Delete", command=self.open_delete_popup, **BUTTON_STYLE)
        self.delete_button.pack(side=tk.LEFT, padx=10)

        self.save_button = tk.Button(self.button_frame, text="Save", command=self.open_save_popup, **BUTTON_STYLE)
        self.save_button.pack(side=tk.LEFT, padx=10)

        self.load_button = tk.Button(self.button_frame, text="Load", command=self.open_load_popup, **BUTTON_STYLE)
        self.load_button.pack(side=tk.LEFT, padx=10)

        self.chord_images = []
        self.chord_names = []
        self.next_x = 0
        self.next_y = 0
        self.canvas_width = 800

    def on_resize(self, event):
        self.canvas_width = event.width
        self.reposition_chords()

    def reposition_chords(self):
        self.canvas.delete("all")
        self.next_x = 0
        self.next_y = 0
        for chord_image in self.chord_images:
            svg_width = chord_image.width()
            svg_height = chord_image.height()

            if self.next_x + svg_width > self.canvas_width:
                self.next_x = 0
                self.next_y += svg_height

            self.canvas.create_image(self.next_x + svg_width / 2, self.next_y + svg_height / 2, image=chord_image)
            self.next_x += svg_width

    def open_edit_popup(self):
        popup = EditPopup(self)
        self.wait_window(popup)

    def open_create_popup(self):
        popup = CreatePopup(self)
        self.wait_window(popup)

    def open_delete_popup(self):
        popup = DeletePopup(self)
        self.wait_window(popup)

    def open_save_popup(self):
        popup = SavePopup(self)
        self.wait_window(popup)

    def open_load_popup(self):
        popup = LoadPopup(self)
        self.wait_window(popup)

    def add_svg_to_canvas(self, svg_path, chord_name):
        try:
            drawing = svg2rlg(svg_path)
            if drawing is None:
                raise ValueError(f"Unable to read SVG file: {svg_path}")
            
            png_data = renderPM.drawToPIL(drawing)
            chord_image = ImageTk.PhotoImage(png_data)

            svg_width = drawing.width
            svg_height = drawing.height

            # wrap logic
            if self.next_x + svg_width > self.canvas_width:
                self.next_x = 0
                self.next_y += svg_height

            self.canvas.create_image(self.next_x + svg_width / 2, self.next_y + svg_height / 2, image=chord_image)
            self.chord_images.append(chord_image)  
            self.chord_names.append(chord_name)

            self.next_x += svg_width
        except Exception as e:
            print(f"Error adding SVG to canvas: {e}")

    def remove_chord(self, index):
        if 0 <= index < len(self.chord_images):
            self.chord_images.pop(index)
            self.chord_names.pop(index)
            self.reposition_chords()

    def remove_all_chords(self):
        self.chord_images.clear()
        self.chord_names.clear()
        self.reposition_chords()

    def move_chord_up(self, index):
        if 1 <= index < len(self.chord_images):
            self.chord_images[index], self.chord_images[index-1] = self.chord_images[index-1], self.chord_images[index]
            self.chord_names[index], self.chord_names[index-1] = self.chord_names[index-1], self.chord_names[index]
            self.reposition_chords()

    def move_chord_down(self, index):
        if 0 <= index < len(self.chord_images) - 1:
            self.chord_images[index], self.chord_images[index+1] = self.chord_images[index+1], self.chord_images[index]
            self.chord_names[index], self.chord_names[index+1] = self.chord_names[index+1], self.chord_names[index]
            self.reposition_chords()

class EditPopup(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self.title("ReChord: Edit Canvas")
        self.geometry("850x600")

        # file list frame
        self.left_frame = tk.Frame(self)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # file list label
        self.file_list_label = tk.Label(self.left_frame, text="Available Chord Diagrams")
        self.file_list_label.pack(pady=10)

        # file list
        self.svg_listbox = tk.Listbox(self.left_frame)
        self.svg_listbox.pack(fill=tk.BOTH, expand=True)
        self.svg_listbox.bind("<<ListboxSelect>>", self.preview_svg)

        # canvas chords frame
        self.right_frame = tk.Frame(self)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # canvas chords label
        self.chord_list_label = tk.Label(self.right_frame, text="Current Chords")
        self.chord_list_label.pack(pady=10)

        # canvas chords
        self.chord_listbox = tk.Listbox(self.right_frame, width=15) 
        self.chord_listbox.pack(fill=tk.BOTH, expand=True)
        self.chord_listbox.bind("<<ListboxSelect>>", self.preview_svg)

        self.button_frame = tk.Frame(self.right_frame)
        self.button_frame.pack(fill=tk.X, pady=10)

        self.add_button = tk.Button(self.button_frame, text="Add", command=self.add_chord, **BUTTON_STYLE)
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.remove_button = tk.Button(self.button_frame, text="Remove", command=self.remove_chord, **BUTTON_STYLE)
        self.remove_button.pack(side=tk.LEFT, padx=5)

        self.remove_all_button = tk.Button(self.button_frame, text="Remove All", command=self.remove_all_chords, **BUTTON_STYLE)
        self.remove_all_button.pack(side=tk.LEFT, padx=5)

        self.move_up_button = tk.Button(self.button_frame, text="Move Up", command=self.move_chord_up, **BUTTON_STYLE)
        self.move_up_button.pack(side=tk.LEFT, padx=5)

        self.move_down_button = tk.Button(self.button_frame, text="Move Down", command=self.move_chord_down, **BUTTON_STYLE)
        self.move_down_button.pack(side=tk.LEFT, padx=5)

        self.close_button = tk.Button(self.button_frame, text="Close", command=self.destroy, **BUTTON_STYLE)
        self.close_button.pack(side=tk.LEFT, padx=5)

        self.preview_canvas = tk.Canvas(self, width=200, height=200)
        self.preview_canvas.pack(pady=10)

        self.load_svgs()
        self.load_current_chords()

    def load_svgs(self):
        svg_dir = './tmp/svg'
        self.svgs = [f for f in os.listdir(svg_dir) if f.endswith('.svg')]
        for svg in self.svgs:
            self.svg_listbox.insert(tk.END, svg)

    def load_current_chords(self):
        self.chord_listbox.delete(0, tk.END)
        for chord_name in self.master.chord_names:
            self.chord_listbox.insert(tk.END, chord_name)

    def preview_svg(self, event):
        selected_index = self.svg_listbox.curselection()
        if not selected_index:
            return

        selected_svg = self.svgs[selected_index[0]]
        svg_path = os.path.join('./tmp/svg', selected_svg)
        try:
            drawing = svg2rlg(svg_path)
            if drawing is None:
                raise ValueError(f"Unable to read SVG file: {svg_path}")
            png_data = renderPM.drawToPIL(drawing)
            self.preview_image = ImageTk.PhotoImage(png_data)
            self.preview_canvas.create_image(100, 100, image=self.preview_image)
        except Exception as e:
            print(f"Error previewing SVG: {e}")

    def add_chord(self):
        selected_index = self.svg_listbox.curselection()
        if not selected_index:
            return

        selected_svg = self.svgs[selected_index[0]]
        svg_path = os.path.join('./tmp/svg', selected_svg)
        chord_name = os.path.splitext(selected_svg)[0]

        self.master.add_svg_to_canvas(svg_path, chord_name)
        self.load_current_chords()

    def remove_chord(self):
        selected_index = self.chord_listbox.curselection()
        if not selected_index:
            return

        chord_index = selected_index[0]
        self.master.remove_chord(chord_index)
        self.load_current_chords()

    def remove_all_chords(self):
        self.master.remove_all_chords()
        self.load_current_chords()

    def move_chord_up(self):
        selected_index = self.chord_listbox.curselection()
        if not selected_index or selected_index[0] == 0:
            return

        chord_index = selected_index[0]
        self.master.move_chord_up(chord_index)
        self.load_current_chords()
        self.chord_listbox.select_set(chord_index - 1)

    def move_chord_down(self):
        selected_index = self.chord_listbox.curselection()
        if not selected_index or selected_index[0] == len(self.master.chord_names) - 1:
            return

        chord_index = selected_index[0]
        self.master.move_chord_down(chord_index)
        self.load_current_chords()
        self.chord_listbox.select_set(chord_index + 1)

class DeletePopup(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self.title("ReChord: Delete SVG Files")
        self.geometry("850x600")

        self.svg_listbox = tk.Listbox(self)
        self.svg_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.button_frame = tk.Frame(self)
        self.button_frame.pack(pady=10)

        self.delete_button = tk.Button(self.button_frame, text="Delete Selected", command=self.delete_selected, **BUTTON_STYLE)
        self.delete_button.pack(side=tk.LEFT, padx=10)

        self.close_button = tk.Button(self.button_frame, text="Close", command=self.destroy, **BUTTON_STYLE)
        self.close_button.pack(side=tk.LEFT, padx=10)

        self.load_svgs()

    def load_svgs(self):
        svg_dir = './tmp/svg'
        self.svgs = [f for f in os.listdir(svg_dir) if f.endswith('.svg')]
        for svg in self.svgs:
            self.svg_listbox.insert(tk.END, svg)

    def delete_selected(self):
        selected_index = self.svg_listbox.curselection()
        if not selected_index:
            return

        selected_svg = self.svgs[selected_index[0]]
        svg_path = os.path.join('./tmp/svg', selected_svg)
        try:
            os.remove(svg_path)
            self.svg_listbox.delete(selected_index)
            self.svgs.pop(selected_index[0])
        except Exception as e:
            print(f"Error deleting SVG file: {e}")

class SavePopup(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self.title("ReChord: Save Chords")
        self.geometry("400x200")

        self.label = tk.Label(self, text="Enter filename:")
        self.label.pack(pady=10)

        self.filename_entry = tk.Entry(self)
        self.filename_entry.pack(pady=10)

        self.button_frame = tk.Frame(self)
        self.button_frame.pack(pady=10)

        self.save_button = tk.Button(self.button_frame, text="Save", command=self.save_file, **BUTTON_STYLE)
        self.save_button.pack(side=tk.LEFT, padx=10)

        self.cancel_button = tk.Button(self.button_frame, text="Cancel", command=self.destroy, **BUTTON_STYLE)
        self.cancel_button.pack(side=tk.LEFT, padx=10)

    def save_file(self):
        filename = self.filename_entry.get()
        if not filename:
            return

        save_data = {
            "chord_names": self.master.chord_names
        }

        save_path = os.path.join('./save', f"{filename}.json")
        try:
            with open(save_path, 'w') as f:
                json.dump(save_data, f)
            self.destroy()
        except Exception as e:
            print(f"Error saving file: {e}")

class LoadPopup(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self.title("ReChord: Load Saved Chords")
        self.geometry("850x600")

        self.save_listbox = tk.Listbox(self)
        self.save_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.button_frame = tk.Frame(self)
        self.button_frame.pack(pady=10)

        self.load_button = tk.Button(self.button_frame, text="Load Save", command=self.load_selected, **BUTTON_STYLE)
        self.load_button.pack(side=tk.LEFT, padx=10)

        self.close_button = tk.Button(self.button_frame, text="Close", command=self.destroy, **BUTTON_STYLE)
        self.close_button.pack(side=tk.LEFT, padx=10)

        self.load_saves()

    def load_saves(self):
        save_dir = './save'
        self.saves = [f for f in os.listdir(save_dir) if f.endswith('.json')]
        for save in self.saves:
            self.save_listbox.insert(tk.END, save)

    def load_selected(self):
        selected_index = self.save_listbox.curselection()
        if not selected_index:
            return

        selected_save = self.saves[selected_index[0]]
        save_path = os.path.join('./save', selected_save)
        try:
            with open(save_path, 'r') as f:
                save_data = json.load(f)
                self.master.remove_all_chords()
                for chord_name in save_data["chord_names"]:
                    svg_path = os.path.join('./tmp/svg', f"{chord_name}.svg")
                    if os.path.exists(svg_path):
                        self.master.add_svg_to_canvas(svg_path, chord_name)
            self.destroy()
        except Exception as e:
            print(f"Error loading save: {e}")

class CreatePopup(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self.title("ReChord: Create Chord Diagrams")
        self.geometry("850x600")

        self.chord_name_var = tk.StringVar()
        self.starting_fret_var = tk.IntVar()
        self.num_strings_var = tk.IntVar()
        self.num_frets_var = tk.IntVar()

        self.starting_fret_var.set(1)
        self.num_strings_var.set(6)
        self.num_frets_var.set(4)

        self.create_widgets()

    def create_widgets(self):
        instructions_label = tk.Label(self, text="Use 'b' for barre, 'n' for dot\n'x' for muted", font=("Helvetica", 10))
        instructions_label.pack(pady=(10, 0))

        main_frame = tk.Frame(self, relief=tk.SOLID)
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        left_frame = tk.Frame(main_frame, relief=tk.SOLID)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        control_frame = tk.Frame(left_frame)
        control_frame.pack(fill=tk.X, pady=10, padx=10)

        tk.Label(control_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Entry(control_frame, textvariable=self.chord_name_var, width=7).grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(control_frame, text="Starting Fret:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        tk.Spinbox(control_frame, from_=1, to=20, textvariable=self.starting_fret_var, width=3).grid(row=1, column=1, padx=5, pady=5, sticky="w")

        tk.Label(control_frame, text="Number of Strings:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        tk.Spinbox(control_frame, from_=4, to=6, textvariable=self.num_strings_var, width=3).grid(row=2, column=1, padx=5, pady=5, sticky="w")

        tk.Label(control_frame, text="Number of Frets:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        tk.Spinbox(control_frame, from_=4, to=6, textvariable=self.num_frets_var, width=3).grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # Muted
        self.muted_label = tk.Label(left_frame, text="Muted:", font=("Helvetica", 10))
        self.muted_label.pack(pady=(10, 0))

        self.muted_frame = tk.Frame(left_frame)
        self.muted_frame.pack(pady=5, padx=10)

        # Notes Grid
        self.notes_label = tk.Label(left_frame, text="Notes:", font=("Helvetica", 10))
        self.notes_label.pack(pady=(10, 0))

        self.grid_frame = tk.Frame(left_frame)
        self.grid_frame.pack(pady=5, padx=10)

        self.error_label = tk.Label(left_frame, text="", font=("Helvetica", 10), fg="red")
        self.error_label.pack()

        right_frame = tk.Frame(main_frame, relief=tk.SOLID)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.preview_label = tk.Label(right_frame, text="Preview: ", font=("Helvetica", 10))
        self.preview_label.pack()

        self.preview_canvas = tk.Canvas(right_frame, width=400, height=300)
        self.preview_canvas.pack(pady=10, padx=10)

        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        self.preview_button = tk.Button(button_frame, text="Preview", command=self.preview_chord, **BUTTON_STYLE)
        self.preview_button.pack(side=tk.LEFT, padx=10)

        self.create_button = tk.Button(button_frame, text="Create", command=self.create_chord, **BUTTON_STYLE)
        self.create_button.pack(side=tk.LEFT, padx=10)

        self.cancel_button = tk.Button(button_frame, text="Cancel", command=self.destroy, **BUTTON_STYLE)
        self.cancel_button.pack(side=tk.RIGHT, padx=10)

        self.num_strings_var.trace_add("write", self.update_grid)
        self.num_frets_var.trace_add("write", self.update_grid)

        self.update_grid()

    def update_grid(self, *args):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        for widget in self.muted_frame.winfo_children():
            widget.destroy()

        num_frets = self.num_frets_var.get()
        num_strings = self.num_strings_var.get()

        self.entries = []
        for fret in range(num_frets):
            row_entries = []
            for string in range(num_strings):
                entry = tk.Entry(self.grid_frame, width=3) 
                entry.grid(row=fret, column=string, padx=2, pady=2)
                row_entries.append(entry)
            self.entries.append(row_entries)

        self.muted_entries = []
        for string in range(num_strings):
            entry = tk.Entry(self.muted_frame, width=3)
            entry.grid(row=0, column=string, padx=2, pady=2)
            self.muted_entries.append(entry)

        self.update_window_size()

    def update_window_size(self):
        self.update_idletasks()
        width = 500
        height = self.grid_frame.winfo_reqheight() + self.muted_frame.winfo_reqheight() + 400
        self.geometry(f"{width}x{height}")

    def create_chord(self):
        title = self.chord_name_var.get()
        starting_fret = self.starting_fret_var.get()
        num_strings = self.num_strings_var.get()
        num_frets = self.num_frets_var.get()

        chord_data = {
            "title": title,
            "starting_fret": starting_fret,
            "num_strings": num_strings,
            "num_frets": num_frets,
            "grid": [[entry.get() for entry in row] for row in self.entries],
            "muted": [entry.get() for entry in self.muted_entries]
        }

        if not self.validate_chord_data(chord_data["grid"]):
            self.error_label.config(text="Input validation failed:\nOnly 'b' or 'n' allowed in notes")
            return
        
        if not self.validate_muted_data(chord_data["muted"]):
            self.error_label.config(text="Input validation failed:\nOnly 'x' allowed in notes")
            return


        barres = self.get_barres(chord_data["grid"], starting_fret, num_strings)
        notes = self.get_notes(chord_data["grid"], starting_fret)
        mutes = self.get_muted(chord_data["muted"])

        success, error = self.create_chord_svg(num_strings, chord_data["title"], starting_fret, notes, barres, mutes)

        if (not success):
            self.error_label.config(text=error)
            return
        
        self.destroy()

    def validate_chord_data(self, grid):
        for row in grid:
            for value in row:
                if value not in ['b', 'n', '']:
                    return False
        return True
    
    def validate_muted_data(self, muted):
        for value in muted:
            if value not in ['x', '']:
                return False
        return True

    def get_barres(self, grid, starting_fret, num_strings):
        barres = []

        for fret_index, row in enumerate(grid):
            in_sequence = False
            starting_string = -1
            ending_string = -1
            for string_index, cell in enumerate(reversed(row)):
                if (cell == 'b' and not in_sequence):
                    starting_string = string_index + 1
                    in_sequence = True
                if ( ( (cell == '') or (string_index == num_strings - 1) ) and in_sequence ):
                    ending_string = string_index
                    barres.append((starting_fret + fret_index, starting_string, ending_string))

        return barres
    
    def get_muted(self, muted):
        mutes = []
        for string_index, string in enumerate(reversed(muted)):
            if (string == 'x'):
                mutes.append(string_index + 1)
        return mutes
    
    def get_notes(self, grid, starting_fret):
        notes = []
        for fret_index, row in enumerate(grid):
            for string_index, cell in enumerate(reversed(row)):
                if (cell == 'n'):
                    notes.append((string_index + 1, starting_fret + fret_index))
        return notes
    
    def create_chord_svg(self, num_strings, title, starting_fret, notes, barres, mute):
        try:
            new_chord = cg.Chord(num_strings, title, starting_fret, notes, barres, mute)
            new_chord.create_image()
            return True, ""
        except Exception as error:
            print(error)
            return False, error

    def preview_chord(self):
        title = self.chord_name_var.get()
        starting_fret = self.starting_fret_var.get()
        num_strings = self.num_strings_var.get()
        num_frets = self.num_frets_var.get()

        chord_data = {
            "title": title,
            "starting_fret": starting_fret,
            "num_strings": num_strings,
            "num_frets": num_frets,
            "grid": [[entry.get() for entry in row] for row in self.entries],
            "muted": [entry.get() for entry in self.muted_entries]
        }

        if not self.validate_chord_data(chord_data["grid"]):
            self.error_label.config(text="Input validation failed:\nOnly 'b' or 'n' allowed in notes")
            return
        
        if not self.validate_muted_data(chord_data["muted"]):
            self.error_label.config(text="Input validation failed:\nOnly 'x' allowed in notes")
            return

        barres = self.get_barres(chord_data["grid"], starting_fret, num_strings)
        notes = self.get_notes(chord_data["grid"], starting_fret)
        mutes = self.get_muted(chord_data["muted"])

        success, error = self.create_chord_svg(num_strings, chord_data["title"], starting_fret, notes, barres, mutes)

        if not success:
            self.error_label.config(text=error)
            return

        # Preview SVG
        if not title:
            title = "new_chord"
        svg_path = f"./tmp/svg/{title}.svg"
        try:
            drawing = svg2rlg(svg_path)
            if drawing is None:
                raise ValueError(f"Unable to read SVG file: {svg_path}")
            png_data = renderPM.drawToPIL(drawing)
            self.preview_image = ImageTk.PhotoImage(png_data)
            self.preview_canvas.create_image(100, 100, image=self.preview_image)
            os.remove(svg_path)
        except Exception as e:
            print(f"Error previewing SVG: {e}")

if __name__ == "__main__":
    app = ReChord()
    app.mainloop()
