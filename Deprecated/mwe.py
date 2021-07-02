#================================================================
# IMPORT MODULES
#================================================================
import modules
modules.initialize()
import tkinter as tk
import pandas as pd
import tkinter.filedialog as file
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
#import ipywidgets
import numpy as np
#from pandastable import Table, TableModel
import copy
from cefpython3 import cefpython as cef#https://github.com/cztomczak/cefpython/blob/master/api/Browser.md#loadurl
import threading
import sys
import pathlib
path = pathlib.Path(__file__).parent.absolute()
import kaleido

#================================================================
# INITIALIZE TKINTER GUI WINDOW
#================================================================
window = tk.Tk() # initialize
window.title("M|Chroma")

#================================================================
# PACK FRAME ELEMENTS
#================================================================
plot_frame = tk.Frame(window, height=600, width=800)
plot_frame.pack(side='top', fill='x')

#table_frame.pack(fill='both', expand=True)

#================================================================
# JAVASCRIPT EVENT HANDLING
#================================================================
#JS_script = """
#thegraph = document.getElementsByClassName("plotly-graph-div js-plotly-plot")[0]
#thegraph.on('plotly_click', function(eventData){
#alert("Gotcha")
#}
#);
#"""
JS_script="document.body.innerHTML=''"
#================================================================
# KEEP WINDOW OPEN AND HANDLE CHROMIUM BROWSER
#================================================================
#def lethal_interjection():
#    pass

#def lethal_click_handler
def lethal_message_handler(self, browser, message, **kwargs):
    "Browser console interface"
    #self.chrome.console.append(message)
    print(message)



def test_thread(frame):
    sys.excepthook = cef.ExceptHook
    window_info = cef.WindowInfo(plot_frame.winfo_id())
    window_info.SetAsChild(plot_frame.winfo_id(), [0, 0, 800, 600])
    cef.Initialize()
    global browser
    #browser = cef.CreateBrowserSync(window_info, url='file:///'+str(path).replace("\\", "/")+'/gram.html')
    browser = cef.CreateBrowserSync(window_info, url='file:///'+str(path).replace("\\", "/")+'/gram.html')

    class LoadHandler(object):
        def OnLoadingStateChange(self, Browser, is_loading, **_):
            print("boss please")
            if not is_loading:
                Browser.ExecuteJavascript("document.getElementsByName('q')[0].value = 24")
                print("This works")

    browser.SetClientHandler(LoadHandler)
    #print('file:///'+str(path).replace("\\", "/")+'/gram.html')
    #browser.ExecuteJavascript(JS_script)
    cef.MessageLoop()
    #


thread = threading.Thread(target=test_thread, args=(plot_frame,))
thread.start()

window.mainloop() # keep window open
cef.Shutdown()
