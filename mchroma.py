#================================================================
# IMPORT MODULES
#================================================================
from chromatogram import Chromatogram, Peak
import dialogues as tkd
import save as save
import pandas as pd
import numpy as np
import tkinter as tk
import tkinter.filedialog
import tkinter.colorchooser
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
    #Empty class for making standalone objects.

#================================================================
#INITIALIZE GUI
#================================================================
windows = {"main":tk.Tk()} # initialize
windows["main"].title("M|Chroma")

graph = Empty() #master object to store all relevant graphing variables

graph.frame = tk.Frame(master = windows["main"])

graph.fig = Figure(figsize=(5, 2), dpi=100)#container for subplots
graph.plot = graph.fig.add_subplot(111)#subplot is the actual graph
#graph.plot.xlabel("Time (min.)")
graph.canvas = FigureCanvasTkAgg(graph.fig, master=graph.frame)
#TKinter object containing the MatPlotLib figure
graph.canvas.draw()
#This method updates the graph.
#(note: graph does not automatically update when changed)
graph.toolbar = NavigationToolbar2Tk(graph.canvas, graph.frame)
graph.toolbar.update()


blank_gram = Chromatogram(data=[0,0])
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
        graph.plot.plot(gram.time_series, gram.signal_series, color=gram.color)
        graph.canvas.draw()

#================================================================
#INITIALIZE COLOR PALETTE
#================================================================
graph.colors = []
"""with open("rgb.txt","r") as reader:
    #Read XKCD colors in order as default chromatogram colors.
    line = reader.readline()
    while line != "":
        line = reader.readline().replace("\n","")
        color = line.split("	") #Names and colors delimited by tabs
        #There's a mysterious "" that gets saved in the split. Might be a
        #carriage return, but idk.
        if len(color) == 3:
            graph.colors.append(color[1])"""
with open("settings.cfg","r") as reader:
    line = reader.readline()
    while line != "":
        if "DEFAULT_COLORS" in line:
            graph.colors = line.replace("DEFAULT_COLORS ","").split(" ")
            break
        line = reader.readline()

graph.color_index = 0


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
        for gram in history.present().chromatograms:
            gram.active = False
        history.present().active().active = True
        #Ensure that only one chromatogram is active.

        graph.plot.cla() #Clears the plot.
        graph.canvas.draw() #Redraws plot as blank.
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
        repack_legend()


history = History()

def active_chroma():
    """This function streamlines referencing the active chromatogram."""
    return history.present().active()


#================================================================
# IMPORTING CHROMATOGRAMS
#================================================================
def import_chromatogram():
    try:
        paths = tk.filedialog.askopenfilename(multiple=True)
        #Use tk filedialog to select the chromatogram data file(s) as a tuple.
        for path in paths:
            temp_data = []
            temp_name = ""
            temp_rate = ""
            if graph.color_index < len(graph.colors):
                temp_color = graph.colors[graph.color_index]
            else:
                temp_color = "#000000"
                #Once default colors are exhausted, default chromatogram color
                #will be black.

            with open(path) as reader:
                line = reader.readline()
                while line != '':  # The EOF char is an empty string
                    if line.replace("\n","").replace("-","").isnumeric():
                        #Treat line as data point if it is just a number.
                        #Note: remove minus sign because isnumeric doesn't
                        #recognize negative numbers.
                        temp_data.append(int(line))
                    elif "Sample ID" in line:
                        temp_name=line.replace("Sample ID: ","").replace("\n","")
                        #Assign chromatogram name as the sample ID the data file.
                    elif "Sampling Rate" in line:
                        temp_rate = float(line.replace("Sampling Rate: ","").replace(" Hz\n",""))
                    line = reader.readline()
                    #Move on to the next line.

                if temp_name == "":
                    temp_name = path.split("/")[-1].replace(".dat.asc","")
                    #Fallback chromatogram name is file name without extension.

            history.save()
            history.present().chromatograms.append(Chromatogram(
                data=temp_data,
                name=temp_name,
                color=temp_color,
                sampling_rate = temp_rate
                ))
            #Create new chromatogram in current SaveState.
            graph.color_index +=1
            #Change the color of the next loaded chromatogram.
            history.present().active_index=len(history.present().chromatograms)-1
            #Set the new chromatogram as active for analysis
            history.update()
            #update plots
    except FileNotFoundError:
        print("Please select a file!")

#================================================================
# PEAK PICKING
#================================================================
picking = {
    "n":0,
    "mode":"",
    "points":[]
    }

def on_click(event):
    global picking
    if picking["n"] > 0 and event.inaxes is not None:
        #Only handle clicks on the subplot while peak picking.
        picking["points"].append(event.xdata)
        if len(picking["points"]) == picking["n"]:
            #When the desired number of points have been picked, we can
            #pass them on to whatever function needs them.
            if picking["mode"] == "peak_bounds":
                #Pick a peak from a starting and ending point.
                picking["points"].sort()
                active_chroma().add_peak(active_chroma().time2index(picking["points"]))
            elif picking["mode"] == "peak_crest":
                #Pick a peak from a high point.
                active_chroma().one_point_peak(active_chroma().time2index(picking["points"][0]))
                pass
            elif picking["mode"] == "baseline":
                #Correct the baseline from two points picked on the baseline.
                picking["points"].sort()
                active_chroma().baseline_correct(active_chroma().time2index(picking["points"]))
            history.update()
            #Update the GUI's graph and table.
            picking["points"] = []
            picking["n"] = 0
            picking["mode"] = ""
            #Empty these variables to wait for the next picking event.

graph.canvas.callbacks.connect('button_press_event', on_click)
#set on_click as the click event handler for the canvas

def peak_from_bounds():
    """This function toggles 2-point peak picking mode, in which a peak is
    defined from its starting and ending points."""
    global picking
    picking["n"] = 2
    picking["mode"] = "peak_bounds"

def peak_from_crest():
    """This function toggles 1-point peak picking mode, in which a peak is
    found from a high point in the peak."""
    global picking
    picking["n"] = 1
    picking["mode"] = "peak_crest"

def pick_baseline():
    """This function toggles point picking for baseline correction."""
    global picking
    picking["n"] = 2
    picking["mode"] = "baseline"


#================================================================
# ANALYSIS FUNCTIONS
#================================================================
def scale_signal():
    windows["scale signal popup"] = tkd.MultiEntryInput(windows["main"],["Scale factor"])
    scale_factor = windows["scale signal popup"].results[0]
    if scale_factor == "\x18":
        print("Scale operation aborted.")
    else:
        active_chroma().scale_signal(float(scale_factor))
        history.update()




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
#This creates the "File" dropdown on the menu bar.

menu.edit = tk.Menu(menu.bar, tearoff=0)
menu.edit.add_command(label="Chromatogram", command=lambda:edit_chromatogram(history.present().active_index))
menu.edit.add_command(label="Undo", command=history.undo)
menu.edit.add_command(label="Redo", command=history.redo)
menu.bar.add_cascade(label="Edit", menu=menu.edit)
#This creates the "Edit" dropdown on the menu bar.

menu.peak = tk.Menu(menu.bar, tearoff=0)
menu.peak.add_command(label="Pick from bounds", command=peak_from_bounds)
menu.peak.add_command(label="Pick from a point", command=peak_from_crest)
#menu.peak.add_command(label="Threshold autopick", command=threshold_autopick)
menu.bar.add_cascade(label="Peak", menu=menu.peak)
#This creates the "Peak" dropdown on the menu bar.

menu.analysis = tk.Menu(menu.bar, tearoff=0)
menu.analysis.add_command(label="Baseline correct", command=pick_baseline)
menu.analysis.add_command(label="Scale signal", command=scale_signal)
menu.bar.add_cascade(label="Analysis", menu=menu.analysis)
#This creates the "Analysis" dropdown on the menu bar.


windows["main"].iconbitmap('images/icon/mchroma.ico')
#Set icon on window


#================================================================
# CHROMATOGRAM LEGEND
#================================================================
legend = Empty()
#Container for variables related to the legend.
legend.frame = tk.Frame(windows["main"])
#Master container for legend widgets.
legend.radio_frame = tk.Frame(legend.frame)
#Container for radio buttons to select active chromatogram.
legend.check_frame = tk.Frame(legend.frame)
#Container for check buttons to toggle chromatogram visibility.
legend.radio_var = tk.IntVar()

legend.checks = []
legend.check_vars = []
legend.radios = []

def toggle_gram(i):
    chromatogram = history.present().chromatograms[i]

    chromatogram.hidden = not bool(legend.check_vars[i].get())

    history.update()


def change_active(i):
    """This method assigns the active chromatogram."""
    history.present().active_index = i
    history.update()

def change_color(i):
    """This function changes the color attribute of a chromatogram."""
    chromatogram = history.present().chromatograms[i]
    color = tk.colorchooser.askcolor(color=chromatogram.color,
                      title = f"Select color for {chromatogram.name}")[1]
    if color is not None:
        chromatogram.color = color
    history.update()

def edit_chromatogram(i):
    """This function opens the edit chromatogram dialogue."""
    gram = history.present().chromatograms[i]
    windows["edit gram popup"] = tkd.EditChromatogram(windows["main"],gram)
    results = windows["edit gram popup"].results
    if "\x18" in results:
        print("Edit chromatogram operation aborted.")
    else:
        gram.name = results["name"]
        gram.hidden = results["hidden"]
        gram.color = results["color"]
        gram.scale_signal(results["signal_scale"],set=True)
        gram.scale_time(results["time_scale"],type="period",set=True)
        gram.shift_time(results["time_shift"],set=True)

        if results["active"]:
            history.present().active_index=i

        history.update()




def repack_legend():
    """This method updates the legend when new chromatograms are
    added."""
    for widget in legend.frame.winfo_children():
        widget.destroy()
        #Clear the legend frame.

    legend.radio_var.set(history.present().active_index)

    legend.checks = []
    legend.check_vars = []
    legend.radios = []
    #legend.toggle_funcs = [lambda : toggle_gram(m) for m,_ in enumerate(history.present().chromatograms)]
    tk.Label(legend.frame,text="📌").grid(row=0,column=0)
    tk.Label(legend.frame,text="👁").grid(row=0,column=1)
    tk.Label(legend.frame,text="Color").grid(row=0,column=2)
    tk.Label(legend.frame,text="Chromatogram").grid(row=0,column=3)
    tk.Label(legend.frame,text="Edit").grid(row=0,column=4)
    for i,chromatogram in enumerate(history.present().chromatograms):
        check_var = tk.IntVar()
        legend.check_vars.append(check_var)

        radio = tk.Radiobutton(legend.frame,var=legend.radio_var,value=i,
            command = lambda:change_active(legend.radio_var.get()))
        check = tk.Checkbutton(legend.frame,
            var=check_var, command = lambda n = i:toggle_gram(n))
            #That n=i line is essential, otherwise all commands take the last
            #value of n as their argument.
        color_button = tk.Button(legend.frame,text="\x09",bg=chromatogram.color,
            command = lambda p=i:change_color(p))
        name = tk.Label(legend.frame,text=chromatogram.name)

        edit_button = tk.Button(legend.frame,text="🖉",
            command = lambda q=i:edit_chromatogram(q))

        if not chromatogram.hidden:
            check.select()
            #Box is checked if chromatogram is unhidden.

        radio.grid(row=i+1,column=0)
        check.grid(row=i+1,column=1)
        color_button.grid(row=i+1,column=2)
        name.grid(row=i+1,column=3,sticky="w")
        edit_button.grid(row=i+1,column=4)
        legend.checks.append(check)





#================================================================
# PACK FRAME ELEMENTS
#================================================================
graph.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
#Packs the MatPlotLib graph
graph.frame.grid(row=0,column=0,sticky="nsew")
legend.frame.grid(row=0,column=1)
windows["main"].columnconfigure(0, weight=1)
windows["main"].rowconfigure(0, weight=1)
#Weight=1 assigns excess space to that portion of the grid; however, the cells
#will not expand unless their sticky argument is specified.



#================================================================
# KEEP WINDOW OPEN
#================================================================
windows["main"].config(menu=menu.bar)
windows["main"].mainloop() # keep window open
