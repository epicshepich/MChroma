import tkinter as tk
from tkinter import simpledialog
from abc import ABC, abstractmethod

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
        button_frame.grid(row=len(instance.frames),column=0)
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
        self.frames = []
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
            self.frames.append(frame)
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
