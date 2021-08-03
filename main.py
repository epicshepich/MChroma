#================================================================
# IMPORT MODULES
#================================================================
from chromatogram import Chromatogram, Peak
import save as save
import pandas as pd
import numpy as np
import tkinter as tk
import tkinter.filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import copy
import sys
import pathlib
path = pathlib.Path(__file__).parent.absolute()

from icecream import ic

class Empty:
    def __init__(self):
        pass
    #empty class for making standalone objects

#================================================================
#INITIALIZE GUI
#================================================================
windows = {"main":tk.Tk()} # initialize
windows["main"].title("M|Chroma")

graph = Empty() #master object to store all relevant graphing variables
graph.fig = Figure(figsize=(5, 2), dpi=100)#container for subplots
graph.plot = graph.fig.add_subplot(111)#subplot is the actual graph
#graph.plot.xlabel("Time (min.)")
graph.canvas = FigureCanvasTkAgg(graph.fig, master=windows["main"])
#TKinter object containing the MatPlotLib figure
graph.canvas.draw()
#this method updates the graph
#(note: graph does not automatically update when changed)
graph.toolbar = NavigationToolbar2Tk(graph.canvas, windows["main"])
graph.toolbar.update()


blank_gram = Chromatogram({"ID":"","data":[0,0]})
blank_gram.update()
#create a blank chromatogram solely for the purpose of extracting headers for
#the peak summary table
#I do it this way because if I change a field, I don't want to have to fix it
#in multiple places in the code
graph.table=graph.plot.table(
    cellText=[[""]*(len(blank_gram.peak_table.columns))],
    colLabels=blank_gram.peak_table.columns,loc="bottom")
#this should make the peak summary table below the subplot

def plot(gram):
    """This method takes a Chromatogram object as its argument and it draws
    the chromatogram the graph."""
    if not gram.hidden:
        graph.plot.plot(gram.time_series, gram.signal_series)
        graph.canvas.draw()


#================================================================
# SET UP HISTORY OBJECT FOR UNDO/REDO FUNCTIONALITY
#================================================================
class SaveState:
    """The SaveState class is used to create a deep copy of the chromatograms
    in their current state so that changes can be undone/redone
    """
    def __init__(self):
        self.chromatograms=[]
        self.active_index=0

    def active(self):
        """This method returns the active chromatogram"""
        return self.chromatograms[self.active_index]

    def __getitem__(self,i):
        """This method allows direct indexing into a SaveState object to access
        chromatograms in the list."""
        return self.chromatograms[i]

class History:
    """The History class is for the instantiation of a master object which
    contains the cache of SaveStates, as well as methods pertaining to changing
    the current SaveState."""

    def __init__(self):
        self.states=[SaveState()]
        self.present_index=0

    def save(self):
        """This method adds a new SaveState to the cache. The while statement
        is used to overwrite changes that have been undone prior to saving the
        new state."""
        while len(self.states)>self.present_index+1:
            self.states.pop()
        self.states.append(copy.deepcopy(self.states[self.present_index]))
        self.present_index+=1

    def present(self):
        """This method returns the presently displayed SaveState."""
        return self.states[self.present_index]

    def undo(self):
        """"This method returns to the previous SaveState in the cache."""
        if self.present_index>0:
            self.present_index-=1
            plot(self.present().active())
            self.update()
        else:
            print("Nothing to undo!")

    def redo(self):
        """This method returns to the next SaveState in the cache."""
        if self.present_index<len(self.states)-1:
            self.present_index+=1
            plot(self.present().active())
            self.update()
        else:
            print("Nothing to redo!")

    def update(self):
        """"This method is invoked to apply a new SaveState"""
        graph.plot.cla() #clears the plot
        for gram in self.present().chromatograms:
            plot(gram) #redraws each unhidden chromatogram

        ic(history.present().active())
        if not history.present().active().peak_table.empty:
            table_temp = history.present().active().peak_table
            #contraction for the next part
            graph.table=graph.plot.table(
                cellText=table_temp.values,
                colLabels=table_temp.columns,loc="bottom")
        else:
            graph.table=graph.plot.table(
                cellText=[[""]*(len(blank_gram.peak_table.columns))],
                colLabels=blank_gram.peak_table.columns,loc="bottom")
            #Make the table blank again when a peakless chromatogram is active


history = History()

def active_chroma():
    """This function streamlines referencing the active chromatogram."""
    return history.present().active()


#================================================================
# IMPORTING CHROMATOGRAMS
#================================================================
def import_chromatogram():
    try:
        temp_data = []
        temp_ID = ""
        with open(tk.filedialog.askopenfilename()) as reader:
            #use tk filedialog to select the chromatogram data file
            line = reader.readline()
            while line != '':  # The EOF char is an empty string
                try:
                    temp_data.append(int(line))
                    #assume any line that can be converted to an integer is
                    #a data point and anything that can't is metadata
                except ValueError:
                    if line.find("Sample ID") > -1:
                        temp_ID=line.replace("Sample ID: ","")
                    #set the chromatogram ID as the sample ID from the file
                line = reader.readline()
                #move on to the next line

        history.save()
        history.present().chromatograms.append(Chromatogram({
            "data":temp_data,
            "ID":temp_ID
            }))
        #create new chromatogram in current SaveState
        #history.present().active().index=len(history.present().chromatograms-1)
        history.present().active_index=len(history.present().chromatograms)-1
        #set the new chromatogram as active for analysis
        history.update()
        #update plots
    except FileNotFoundError:
        print("Please select a file!")

#================================================================
# PEAK PICKING
#================================================================
picking = False
peak_bounds = []

def on_click(event):
    global picking,peak_bounds
    #without this line, the function treats these as undeclared local variables
    #when they show up
    if event.inaxes is not None:
        #only handle clicks on the subplot
        #print(event.xdata,event.ydata)
        if picking:
            #only handle clicks while peak picking
            peak_bounds.append(event.xdata)
            if len(peak_bounds)==2:
                active_chroma().add_peak(peak_bounds)
                #Once a start and end point have been selected, a peak is born.
                history.update()
                #Update the GUI's graph and table.
                peak_bounds=[]
                picking=False
                #Reset these temp variables for the next peak.

graph.canvas.callbacks.connect('button_press_event', on_click)
#set on_click as the click event handler for the canvas

def peak_pick():
    """This method toggles peak picking mode"""
    global picking
    picking = not picking


#================================================================
# MENU BAR
#================================================================
menu = Empty()
#creates master object "menu"

menu.bar = tk.Menu(windows["main"])
#this creates the menu bar

menu.file = tk.Menu(menu.bar, tearoff=0)
menu.file.add_command(label="Open", command=import_chromatogram)

menu.file.add_command(label="Export Peak Table",
    command=lambda : save.export_peaks({
        "chromatograms":history.present().chromatograms
    }))
menu.bar.add_cascade(label="File", menu=menu.file)
#this creates the "File" dropdown on the menu bar

menu.edit = tk.Menu(menu.bar, tearoff=0)
menu.edit.add_command(label="Undo", command=history.undo)
menu.edit.add_command(label="Redo", command=history.redo)
menu.bar.add_cascade(label="Edit", menu=menu.edit)
#this creates the "Edit" dropdown on the menu bar

windows["main"].iconbitmap('mchroma.ico')
#Set icon on window



#================================================================
# PACK FRAME ELEMENTS
#================================================================
peak_pick_button = tk.Button(windows["main"],text = "Add peak",
    command = peak_pick)
peak_pick_button.pack(side="top")

graph.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
#Packs the MatPlotLib graph


#================================================================
# KEEP WINDOW OPEN
#================================================================
windows["main"].config(menu=menu.bar)
windows["main"].mainloop() # keep window open
