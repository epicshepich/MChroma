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

class Empty:
    def __init__(self):
        pass
    #empty class for making standalone objects

#================================================================
#INITIALIZE MATPLOTLIB GRAPH OBJECT
#================================================================
graph = Empty() #master object to store all relevant graphing variables
graph.fig = Figure(figsize=(5, 4), dpi=100)
graph.plot = graph.fig.add_subplot(111)
#graph.plot.xlabel("Time (min.)")


#================================================================
# INITIALIZE TKINTER GUI WINDOW
#================================================================
windows = {"main":tk.Tk()} # initialize
windows["main"].title("M|Chroma")

graph.canvas = FigureCanvasTkAgg(graph.fig, master=windows["main"])  # A tk.DrawingArea.
graph.canvas.draw()
graph.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


#================================================================
# DEFINE STATE OBJECT AND SAVE STATE FUNCTION FOR UNDO/REDO FUNCTIONALITIES
#================================================================
class State:
    chromatograms=[]
    active_chromatogram={}
state = State()
states=[]

def save_state():
    states.append(copy.deepcopy(state))

#================================================================
# DEFINE CHROMATOGRAM CLASS
#================================================================
class chromatogram:
    def __init__(self,raw_data):
        self.signal_series=raw_data
        self.time_scale=0.0016667
        self.time_series=[]
        for x in range(len(self.signal_series)):
            self.time_series.append(x*self.time_scale)
        self.derivative_series=[]
        for x in range(len(self.signal_series)-1):
            self.derivative_series.append(self.signal_series[x+1]-self.signal_series[x])#computes the right handed slope at any point
            self.derivative_series.append(0)#we need one more data point at the end so the lengths don't mismatch
    def plot(self):
        graph.plot.plot(self.time_series, self.signal_series)
        graph.canvas.draw()
    peaks=[]

#================================================================
# DEFINE PEAK CLASS
#================================================================
class peak:
    def __init__(self, start, end):
        self.time_bounds=[start, end]
        self.start_index=int(np.round(start/state.active_chromatogram.time_scale))
        self.end_index=int(np.round(end/state.active_chromatogram.time_scale))
        self.time_series=state.active_chromatogram.time_series[self.start_index:self.end_index+1]
        self.signal_series=state.active_chromatogram.signal_series[self.start_index:self.end_index+1]
        self.area_bb=sum(self.signal_series)
        self.height=max(self.signal_series)
        self.retention_time=self.time_series[self.signal_series.get_loc(self.height)]
        try:
            half_height_loop=0
            while self.signal_series[half_height_loop] < self.height/2:
                half_height_loop+=1
            self.half_height_left=self.time_series[copy.deepcopy(half_height_loop)]
            while self.signal_series[half_height_loop]>=self.height/2:
                half_height_loop+=1
            self.half_height_right=self.time_series[copy.deepcopy(half_height_loop)]
            self.width_hh=self.half_height_right-self.half_height_left
            self.plates=5.54*(self.retention_time/self.width_hh)*(self.retention_time/self.width_hh)
        except:
            print("Error computing half-height width")

    def add_to_table(self):
        pass
    def shade_under_curve(self):
        pass


#================================================================
# IMPORTING CHROMATOGRAMS
#================================================================
def import_chromatogram():
    try:
        temp_data = []
        with open(tk.filedialog.askopenfilename()) as reader:
            line = reader.readline()
            while line != '':  # The EOF char is an empty string
                #print(line, end='')
                try:
                    temp_data.append(int(line))
                except ValueError:
                    pass
                line = reader.readline()

        save_state
        chroma_temp=chromatogram(temp_data)
        chroma_temp.index=len(state.chromatograms)
        state.chromatograms.append(chroma_temp)
        chroma_temp.plot()
        update_plot()
        state.active_chromatogram=state.chromatograms[chroma_temp.index]
        update_peak_table()
    except FileNotFoundError:
        print("Please select a file!")

#================================================================
# PEAK PICKING
#================================================================
def on_click(event):
    if event.inaxes is not None:
        print(event.xdata,event.ydata)

graph.canvas.callbacks.connect('button_press_event', on_click)

def peak_pick():
#    try:
    """    peak_temp=peak(float(peak_start.get()),float(peak_end.get()))
        save_state
        state.active_chromatogram.peaks.append(peak_temp)
        peak_temp.add_to_table()
        update_peak_table()
        peak_temp.shade_under_curve()"""
#    except ValueError:
#        print("Input a numerical values for start and end time")
#    except:
#        print("Peak picking error")

#peak_pick_button = tk.Button(windows["main"],
#                        text = "Add peak",
#                        command = peak_pick)

#peak_start_label = tk.Label(text="Peak start")
#peak_end_label=tk.Label(text="Peak end")
#peak_start = tk.Entry()
#peak_end=tk.Entry()

#================================================================
# GUI PEAK TABLE
#================================================================

def update_peak_table():
    pass

#================================================================
# EXPORT PEAK TABLE TO CSV
#================================================================
def export_peaks():
    pass

#================================================================
# EXPORT PLOT
#================================================================
def export_plot():
    pass


#================================================================
# MENU BAR
#================================================================
menubar = tk.Menu(windows["main"])
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Open", command=import_chromatogram)
#filemenu.add_command(label="Export Peak Table", command=export_peaks)
#filemenu.add_command(label="Export Plot", command=export_plot)
#filemenu.add_separator()

menubar.add_cascade(label="File", menu=filemenu)

#================================================================
# PACK FRAME ELEMENTS
#================================================================
#plot_frame = tk.Frame(windows["main"], height=600, width=800)
#plot_frame.pack(side='top', fill='x')

#peak_pick_button.pack(side="top")
#peak_start_label.pack()
#peak_start.pack()
#peak_end_label.pack()
#peak_end.pack()
#table_frame.pack(fill='both', expand=True)





#================================================================
# KEEP WINDOW OPEN
#================================================================
def update_plot():
    pass

windows["main"].config(menu=menubar)
windows["main"].mainloop() # keep window open
