#================================================================
# IMPORT MODULES
#================================================================
import modules
modules.initialize()
import tkinter as tk
import pandas as pd
import tkinter.filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#import plotly.express as px
import numpy as np
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
#INITIALIZE MATPLOTLIB GRAPH OBJECT
#================================================================
graph = Empty() #master object to store all relevant graphing variables
graph.fig = Figure(figsize=(5, 4), dpi=100)#container for subplots
graph.plot = graph.fig.add_subplot(111)#subplot is the actual graph
#graph.plot.xlabel("Time (min.)")


#================================================================
# INITIALIZE TKINTER GUI WINDOW
#================================================================
windows = {"main":tk.Tk()} # initialize
windows["main"].title("M|Chroma")

graph.canvas = FigureCanvasTkAgg(graph.fig, master=windows["main"])
#TKinter object containing the MatPlotLib figure
graph.canvas.draw()
#this method updates the graph
#(note: graph does not automatically update when changed)
graph.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


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
            self.present().active().plot()
            self.update()
        else:
            print("Nothing to undo!")

    def redo(self):
        """This method returns to the next SaveState in the cache."""
        if self.present_index<len(self.states)-1:
            self.present_index+=1
            self.present().active().plot()
            self.update()
        else:
            print("Nothing to redo!")

    def update(self):
        """"This method is invoked to apply a new SaveState"""
        graph.plot.cla() #clears the plot
        for gram in self.present().chromatograms:
            gram.plot() #redraws each unhidden chromatogram

history = History()

#================================================================
# DEFINE CHROMATOGRAM CLASS
#================================================================
class Chromatogram:
    """Chromatogram class is used to store all the information about a
    chromatogram: raw data, axis scale factors, peaks, etc.

    Parameters:
        raw_data - expects a list of integers corresponding to signal intensity
            in detector counts"""
    def __init__(self,raw_data):
        self.signal_series=raw_data
        self.time_scale=0.0016667#Number of data points recorded per minute
        self.time_series=[t*self.time_scale for t in range(len(self.signal_series))]
        #convert independent variable from data point # to time in minutes

        self.derivative_series=[self.signal_series[x+1]-self.signal_series[x]\
            for x in range(len(self.signal_series)-1)]
        #computes the right handed slope at any point
        self.derivative_series.append(0)
        #we need one more data point at the end so the lengths don't mismatch
        self.peaks=[]
        self.hidden=False
        #toggles display of chromatogram on graph

    def plot(self):
        """This method draws the chromatogram on the graph"""
        if not self.hidden:
            graph.plot.plot(self.time_series, self.signal_series)
            graph.canvas.draw()

    def reindex_peaks(self):
        """This method orders peaks from lowest rt to highest"""
        peak_order=[]
        peaks_temp=[]
        for peak_1 in self.peaks:
            peak_index = 0
            if len(self.peaks) <=1:
                break
            for peak_2 in self.peaks:
                if peak_1.retention_time>peak_2.retention_time:
                    peak_index+=1
                    #Assign each peak an index based on the order of its retention time
                elif peak_1.retention_time==peak_2.retention_time:
                    print("Error: Peaks should have distinct retention times!")
            peak_order.append(self.peak_index)
        for index in peak_order:
            peaks_temp.append(self.peaks[index])
            #reorder peaks based on their assigned indices
        self.peaks = peaks_temp #overwrite unsorted list with newly sorted list


#================================================================
# DEFINE PEAK CLASS
#================================================================
class Peak:
    """Peak class contains data about a given peak, including the subset of
    raw data and time series the peak contains, peak area, maximum height,
    half-height width, retention time, etc."""

    def __init__(self, bounds, area_mode="bb"):
        self.t_0 = bounds[0]#starting time and height of click
        self.t_f = bounds[1]#ending time and height of click
        self.i_0 = int(np.round(self.t_0/history.present().active().time_scale))
        self.i_f = int(np.round(self.t_f/history.present().active().time_scale))
        #indices of incident and final data points in the chromatogram raw data
        self.time_series = history.present().active().time_series[self.i_0:self.i_f+1]
        self.signal_series = history.present().active().signal_series[self.i_0:self.i_f+1]
        #subset of raw data contained in peak
        self.s_0 = self.signal_series[0]
        self.s_f = self.signal_series[-1]
        self.height = max(self.signal_series)

        self.area_modifiers = {
            "bb":0,
            "vv":sum([(self.s_f-self.s_0)/(self.t_f-self.t_0)*n\
                for n in range(len(self.time_series))]),
            "bv":sum([(0-self.s_0)/(self.t_f-self.t_0)*n\
                for n in range(len(self.time_series))]),
            "vb":sum([(self.s_f-0)/(self.t_f-self.t_0)*n\
                for n in range(len(self.time_series))])
        }
        #modifiers for different integration modes: base-base, valley-valley,
        #left base to right valley, right base to left valley
        #The modifiers are integrals of the lines connecting the bases/valleys

        self.areas={}
        for key in self.area_modifiers:
            self.areas[key]=sum(self.signal_series)-self.area_modifiers[key]
        #areas computed with each mode
        self.area = self.areas[area_mode]
        #area computed with the desired mode

        i_maxima = [index for index in range(len(self.time_series))\
            if self.signal_series[index] == self.height]
        #finds all time points with maximum signal in case detector caps out
        i_max=int(np.floor((len(i_maxima)-1)/2))
        #as an estimate, the middle of the peak is in the middle of the plateau
        self.retention_time=self.time_series[i_max]
        #the retention time occurs at the crest of the peak

        try:
            i_over_hh = [index for index in range(len(self.signal_series))\
                if self.signal_series[index]>self.height/2]
            #all indices for which the singal is > half the height
            self.width_hh=self.time_series[i_over_hh[-1]]\
                -self.time_series[i_over_hh[0]]
            #hh width is total duration of time for which the signal is
            #greater than half-height
            self.plates=5.54*(self.retention_time/self.width_hh)\
                *(self.retention_time/self.width_hh)
            #calculates the number of theoretical plates for a peak
        except:
            print("Error computing half-height width")

        #ic(self.retention_time)
        #ic(self.area)
        #ic(self.height)
        #ic(self.width_hh)
        #ic(self.plates)

#================================================================
# IMPORTING CHROMATOGRAMS
#================================================================
def import_chromatogram():
    try:
        temp_data = []
        with open(tk.filedialog.askopenfilename()) as reader:
            #use tk filedialog to select the chromatogram data file
            line = reader.readline()
            while line != '':  # The EOF char is an empty string
                try:
                    temp_data.append(int(line))
                    #assume any line that can be converted to an integer is
                    #a data point and anything that can't is metadata
                except ValueError:
                    pass
                line = reader.readline()

        history.save()
        history.present().chromatograms.append(Chromatogram(temp_data))
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
                #once a start and end point have been selected, a peak is born
                history.present().active().peaks.append(Peak(peak_bounds))
                #the new peak is added to the active chromatogram
                peak_bounds=[]
                picking=False
                #reset these temp variables for the next peak

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
menu.bar.add_cascade(label="File", menu=menu.file)
#this creates the "File" dropdown on the menu bar

menu.edit = tk.Menu(menu.bar, tearoff=0)
menu.edit.add_command(label="Undo", command=history.undo)
menu.edit.add_command(label="Redo", command=history.redo)
menu.bar.add_cascade(label="Edit", menu=menu.edit)
#this creates the "Edit" dropdown on the menu bar


#================================================================
# PACK FRAME ELEMENTS
#================================================================
peak_pick_button = tk.Button(windows["main"],text = "Add peak",
    command = peak_pick)
peak_pick_button.pack(side="top")


#================================================================
# KEEP WINDOW OPEN
#================================================================
windows["main"].config(menu=menu.bar)
windows["main"].mainloop() # keep window open
