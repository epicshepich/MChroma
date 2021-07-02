#I don't need threading anymore with the use of window.update() and browser.MessageLoopWork()
#however, it seems like I still can't get clienthandlers to work

#================================================================
# IMPORT MODULES
#================================================================
import tkinter as tk
from cefpython3 import cefpython as cef#https://github.com/cztomczak/cefpython/blob/master/api/Browser.md#loadurl
import threading
import sys
import pathlib
path = pathlib.Path(__file__).parent.absolute()
import time

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


sys.excepthook = cef.ExceptHook
window_info = cef.WindowInfo(plot_frame.winfo_id())
window_info.SetAsChild(plot_frame.winfo_id(), [0, 0, 800, 600])
cef.Initialize()
global browser
browser = cef.CreateBrowserSync(window_info, url='file:///'+str(path).replace("\\", "/")+'/gram.html')

class LoadHandler(object):
    def OnLoadingStateChange(self, Browser, is_loading, **_):
        print("boss please")
        if not is_loading:
            Browser.ExecuteJavascript("document.getElementsByName('q')[0].value = 24")
            print("This works")

browser.SetClientHandler(LoadHandler)

    #
def jimsloop():
    while True:
        cef.MessageLoopWork()
        window.update()
        window.update_idletasks()
        time.sleep(0.01)

jimsloop()
#cef.Shutdown()
