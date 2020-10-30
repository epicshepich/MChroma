#================================================================
# IMPORT MODULES
#================================================================
import modules
modules.initialize()
import tkinter as tk
import pandas as pd
import plotly.express as px
import tkinter.filedialog as file
import plotly.graph_objects as go
import ipywidgets
import numpy as np
from pandastable import Table, TableModel
import copy
from cefpython3 import cefpython as cef#https://github.com/cztomczak/cefpython/blob/master/api/Browser.md#loadurl
import threading
import sys
import pathlib
path = pathlib.Path(__file__).parent.absolute()
import kaleido

#================================================================
#INITIALIZE PLOTLY GRAPH OBJECT
#================================================================
fig = go.FigureWidget()
fig.update_layout(showlegend=False)
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
    def create(self):
        self.raw_data=pd.read_csv(tk.filedialog.askopenfilename(),header=None,sep=" ",skiprows=13,names=[])
        self.time_scale=0.0016667
        self.signal_series=self.raw_data.index
        self.time_series=[]
        for x in range(len(self.signal_series)):
            self.time_series.append(x*self.time_scale)
        self.derivative_series=[]
        for x in range(len(self.signal_series)-1):
            self.derivative_series.append(self.signal_series[x+1]-self.signal_series[x])#computes the right handed slope at any point
            self.derivative_series.append(0)#we need one more data point at the end so the lengths don't mismatch
    def plot(self):
        fig.add_trace(go.Scatter(x=self.time_series, y=self.signal_series))
    peaks=[]
    peak_table=pd.DataFrame(columns=["Retention Index","Retention Time","Area","Height","Width","Plate Count"])

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
        state.active_chromatogram.peak_table=state.active_chromatogram.peak_table.append({'Retention Index' : 0 , 'Retention Time' : self.retention_time, 'Area' : self.area_bb, 'Height' : self.height, 'Width' : self.width_hh, 'Plate Count' : self.plates} , ignore_index=True)
    def shade_under_curve(self):
        fig.add_trace(go.Scatter(x=self.time_series, y=self.signal_series, fill='tozeroy')) # fill down to xaxis
        fig.add_trace(go.Scatter(
    x=[self.retention_time],
    y=[self.height],
    mode="markers+text",
    name="",
    text=[str(round(self.retention_time,2))+" min."],
    textposition="top center"
    ))
        fig.add_trace(go.Scatter(
        x=self.time_series,
        y=[0]*(len(self.signal_series)-1),
        mode="markers+text",
        name="",
        text=["{:.2e}".format(self.area_bb)],
        textposition="bottom center"
        ))
        #"{:.2e}".format(12300000)
        update_plot()
        #for now, this is as good as I can do

#================================================================
# INITIALIZE TKINTER GUI WINDOW
#================================================================
window = tk.Tk() # initialize

#try:
#    window.lift()
#    window.wm_attributes("-topmost", True) #Keep Tkinter window on top of other windows
#except:
#    print("Error lifting window to top")

#================================================================
# IMPORTING CHROMATOGRAMS
#================================================================
def import_chromatogram():
    save_state
    chroma_temp=chromatogram()
    chroma_temp.index=len(state.chromatograms)
    state.chromatograms.append(chroma_temp)
    chroma_temp.create()
    chroma_temp.plot()
    update_plot()
    state.active_chromatogram=state.chromatograms[chroma_temp.index]
    update_peak_table()

#================================================================
# PEAK PICKING
#================================================================
def peak_pick():
#    try:
        peak_temp=peak(float(peak_start.get()),float(peak_end.get()))
        save_state
        state.active_chromatogram.peaks.append(peak_temp)
        peak_temp.add_to_table()
        update_peak_table()
        peak_temp.shade_under_curve()
#    except ValueError:
#        print("Input a numerical values for start and end time")
#    except:
#        print("Peak picking error")

peak_pick_button = tk.Button(window,
                        text = "Add peak",
                        command = peak_pick)

peak_start_label = tk.Label(text="Peak start")
peak_end_label=tk.Label(text="Peak end")
peak_start = tk.Entry()
peak_end=tk.Entry()

#================================================================
# GUI PEAK TABLE
#================================================================
empty_peak_table=pd.DataFrame(columns=["Retention Index","Retention Time","Area","Height","Width","Plate Count"])
empty_peak_table=empty_peak_table.append({'Retention Index' : 0 , 'Retention Time' : 0, 'Area' : 0, 'Height' : 0, 'Width' : 0, 'Plate Count' : 0} , ignore_index=True)
table_frame = tk.Frame(window)
peak_table=Table(table_frame)

def update_peak_table():
    peak_table.model.df=state.active_chromatogram.peak_table
    peak_table.model.df=peak_table.model.df.append({'Retention Index' : "Retention Index" , 'Retention Time' : "Retention Time", 'Area' : "Area", 'Height' : "Height", 'Width' : "Width", 'Plate Count' : "Plate Count"} , ignore_index=True)
    peak_table.adjustColumnWidths()#This method only resizes based on column values, not column headers
    #so, I append a row with column headers as the values to resize based on, and then replace this temp table with the real one
    peak_table.redraw()
    peak_table.model.df=state.active_chromatogram.peak_table
    peak_table.redraw()

peak_table.model.df=empty_peak_table
peak_table.show()

#================================================================
# EXPORT PEAK TABLE TO CSV
#================================================================
def export_peaks():
    filepath = tk.filedialog.asksaveasfilename(
        defaultextension="csv",
        filetypes=[("Comma-Separated Values", "*.csv"), ("All Files", "*.*")],
    )
    state.active_chromatogram.peak_table.to_csv(str(filepath), index = False, header=True)

#================================================================
# EXPORT PLOT
#================================================================
def export_plot():
    filepath = tk.filedialog.asksaveasfilename(
        defaultextension="pdf",
        filetypes=[("PDF File", "*.pdf"), ("PNG Image", "*.png"), ("Vector Graphic", "*.svg"), ("HTML Page", "*.html"), ("All Files", "*.*")],
    )
    if str(filepath).find(".html") != -1:
        fig.write_html(str(filepath), auto_open=False)
    else:
        fig.write_image(str(filepath))


#================================================================
# MENU BAR
#================================================================
menubar = tk.Menu(window)
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Open", command=import_chromatogram)
filemenu.add_command(label="Export Peak Table", command=export_peaks)
filemenu.add_command(label="Export Plot", command=export_plot)
#filemenu.add_separator()

menubar.add_cascade(label="File", menu=filemenu)

#================================================================
# PACK FRAME ELEMENTS
#================================================================
plot_frame = tk.Frame(window, height=500, width=800)
plot_frame.pack(side='top', fill='x')

peak_pick_button.pack(side="top")
peak_start_label.pack()
peak_start.pack()
peak_end_label.pack()
peak_end.pack()
table_frame.pack(fill='both', expand=True)


#================================================================
# KEEP WINDOW OPEN AND HANDLE CHROMIUM BROWSER
#================================================================
def test_thread(frame):
    sys.excepthook = cef.ExceptHook
    window_info = cef.WindowInfo(plot_frame.winfo_id())
    window_info.SetAsChild(plot_frame.winfo_id(), [0, 0, 800, 500])
    cef.Initialize()
    global browser
    #browser = cef.CreateBrowserSync(window_info, url='file:///'+str(path).replace("\\", "/")+'/gram.html')
    browser = cef.CreateBrowserSync(window_info, url='')
    #print('file:///'+str(path).replace("\\", "/")+'/gram.html')
    cef.MessageLoop()

thread = threading.Thread(target=test_thread, args=(plot_frame,))
thread.start()

def update_plot():
    fig.write_html('gram.html', auto_open=False)
    browser.LoadUrl('file:///'+str(path).replace("\\", "/")+'/gram.html')

window.config(menu=menubar)
window.mainloop() # keep window open
cef.Shutdown()
