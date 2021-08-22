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
        instance.ok = tk.Button(instance.top, text='OK', command=instance.submit)
        instance.ok.pack()

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

    def submit(self):
        """This method saves the input and destroys the popup. Called when the
        'OK' button is clicked."""
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
        for label in labels:
            self.labels.append(tk.Label(top, text=f"{label}: "))
            self.labels[-1].pack()
            self.entries.append(tk.Entry(top))
            self.entries[-1].pack()

        super().__init__(self)

    def save_input(self):
        self.results = []
        for entry in self.entries:
            self.results.append(entry.get())
