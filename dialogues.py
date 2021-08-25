import tkinter as tk
from tkinter import simpledialog
import tkinter.colorchooser
from abc import ABC, abstractmethod

def validate(var,vals,types):
    """This function checks if an input is valid by ensuring that does not have
    a restricted value and that it is of a specified type."""
    return bool(var not in vals and isinstance(var,types))

empties = ("",[],tuple(),None,0,{})

class InputDialogue(ABC):
    """InputDialogue is an abstract parent class for various input popup
    dialogues."""
    def __init__(self,instance):
        """This method defines common behaviour of input dialogues.
        From subclass.__init__(), call super().__init__(self) to reference the
        same popup window when creating the 'OK' button and blocking the code.

        Arguments:
            instance -- a subclass instance; i.e. self in subclass.__init__()"""
        self.results = "\x18"
        #Initialize result to cancel character in case the popup is closed.
        button_frame = tk.Frame(instance.top)
        instance.cancel_button = tk.Button(button_frame, text='Cancel', command=instance.cancel)
        instance.cancel_button.grid(row=0,column=0)
        instance.ok_button = tk.Button(button_frame, text='OK', command=instance.submit)
        instance.ok_button.grid(row=0,column=1)
        button_frame.grid(row=len(instance.rows),column=0)
        #After all the label/entry frames are packed, the button frame is
        #packed at the bottom. It holds the Cancel and OK buttons.

        #instance.top.protocol("WM_DELETE_WINDOW", instance.cancel)

        instance.top.grab_set()
        instance.top.wait_window()
        #These two lines are required for blocking the code until the dialogue
        #is submitted.

    @abstractmethod
    def save_input(self):
        """This method is used to save the input, obtained by calling the
        tk.Entry.get() method, to object attributes so that the input data can
        be accessed once the popup has been destroyed. Override this method
        when defining a subclass."""
        pass

    def cancel(self):
        """This method defines behaviour for clicking the 'Cancel' button. It
        saves a '\x18' string (Cancel control character) to the results."""
        self.results = "\x18"
        self.top.destroy()

    def submit(self):
        """This method defines behavoiur for clicking the 'OK' button. It saves
        the input and destroys the popup."""
        self.save_input()
        self.top.destroy()

class MultiEntryInput(InputDialogue):
    """This class defines an input dialogue that consists of one or more
    tk.Entry fields."""
    def __init__(self, parent, labels: list):
        """Arguments:
            parent -- the parent window, i.e. windows['main'] in mchroma.py
            labels -- a list of strings describing the entry fields"""
        top = self.top = tk.Toplevel(parent)

        self.labels = []
        self.entries = []
        self.rows = []
        for i, label in enumerate(labels):
            frame = tk.Frame(top)
            label = tk.Label(frame, text=f"{label}: ")
            entry = tk.Entry(frame)
            label.grid(row=0,column=0)
            entry.grid(row=0,column=1)
            frame.grid(row=i,column=0)
            #Pack the widget as a grid with one column, whose rows are frames
            #containing a label and an entry packed side by side.
            self.labels.append(label)
            self.entries.append(entry)
            self.rows.append(frame)
            #Save the elements in case they need to be referenced (e.g.
            #the save_input() method accesses self.entries).

        super().__init__(self)

    def save_input(self):
        self.results = []
        for entry in self.entries:
            value = entry.get()
            if value == "":
                self.results.append("\x18")
            else:
                self.results.append(value)

class EditChromatogram(InputDialogue):
    """This class defines an input dialogue specific to editing chromatogram
    metadata."""
    def __init__(self,parent,chromatogram):
        top = self.top = tk.Toplevel(parent)
        self.gram = chromatogram

        self.rows = [tk.Frame(self.top) for _ in range(5)]

        self.name = tk.Entry(self.rows[0])
        self.name.insert(0,self.gram.name)

        self.color_value = None #Temp container for updated color value.
        self.color = tk.Button(self.rows[0],text="\x09",bg=self.gram.color,
            command = self.select_color)

        self.active_var = tk.IntVar()
        self.active = tk.Checkbutton(self.rows[1], text="Active",
            var=self.active_var)
        if self.gram.active:
            self.active.select()

        self.hidden_var = tk.IntVar()
        self.hidden = tk.Checkbutton(self.rows[1], text="Visibile",
            var=self.hidden_var)
        if not self.gram.hidden:
            self.hidden.select()

        self.signal_scale = tk.Entry(self.rows[2])
        self.signal_scale.insert(0,str(self.gram.signal_scale))
        self.time_shift = tk.Entry(self.rows[3])
        self.time_shift.insert(0,str(self.gram.time_shift))
        self.time_scale = tk.Entry(self.rows[4])
        self.time_scale.insert(0,self.gram.time_scale)

        tk.Label(self.rows[0],text="Name: ").grid(row=0,column=0)
        self.name.grid(row=0,column=1)
        tk.Label(self.rows[0],text="Color: ").grid(row=0,column=2)
        self.color.grid(row=0,column=3)


        self.active.grid(row=0,column=0)
        self.hidden.grid(row=0,column=1)

        tk.Label(self.rows[2],text="Net signal scale: ").grid(row=0,column=0)
        self.signal_scale.grid(row=0,column=1)
        tk.Label(self.rows[2],text="x").grid(row=0,column=2)

        tk.Label(self.rows[3],text="Net time offset: ").grid(row=0,column=0)
        self.time_shift.grid(row=0,column=1)
        tk.Label(self.rows[3],text="min.").grid(row=0,column=2)

        tk.Label(self.rows[4],text="Net time scale: ").grid(row=0,column=0)
        self.time_scale.grid(row=0,column=1)
        tk.Label(self.rows[4],text="min/point").grid(row=0,column=2)

        for i,row in enumerate(self.rows):
            row.grid(row=i,column=0,sticky="w")

        super().__init__(self)


    def select_color(self):
        color = tk.colorchooser.askcolor(color=self.gram.color,
            title = f"Select color for {self.gram.name}")[1]
        if color is not None:
            self.color_value = color
            self.color.config(bg=color)

    def save_input(self):
        self.results={}
        self.results["name"] = self.name.get()
        if not validate(self.results["name"],empties,(str)):
            self.results["name"] = self.gram.name

        if self.color_value is None or not validate(self.color_value,empties,(str)):
            self.results["color"] = self.gram.color
        else:
            self.results["color"]=self.color_value

        self.results["active"] = bool(self.active_var.get())
        self.results["hidden"] = not bool(self.hidden_var.get())

        self.results["signal_scale"]=self.signal_scale.get()
        if not validate(self.results["signal_scale"],empties,(str))\
            or not self.results["signal_scale"].replace("-","").replace(".","").isnumeric():
            self.results["signal_scale"]=float(self.gram.signal_scale)
        else:
            self.results["signal_scale"]=float(self.signal_scale.get())

        self.results["time_shift"]=self.time_shift.get()
        if not validate(self.results["time_shift"],("",[],tuple(),None,{}),(str))\
            or not self.results["time_shift"].replace("-","").replace(".","").isnumeric():
            self.results["time_shift"]=float(self.gram.time_shift)
        else:
            self.results["time_shift"]=float(self.time_shift.get())

        self.results["time_scale"]=self.time_scale.get()
        if not validate(self.results["time_scale"],empties,(str))\
            or not self.results["time_scale"].replace("-","").replace(".","").isnumeric():
            self.results["time_scale"]=float(self.gram.time_scale)
        else:
            self.results["time_scale"]=float(self.time_scale.get())
