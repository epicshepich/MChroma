#https://stackoverflow.com/questions/57974532/why-cant-run-both-tkinter-mainloop-and-cefpython3-messageloop
import tkinter as tk
from tkinter import messagebox
from cefpython3 import cefpython as cef
import threading
import sys


def test_thread(frame):
    sys.excepthook = cef.ExceptHook
    window_info = cef.WindowInfo(frame.winfo_id())
    window_info.SetAsChild(frame.winfo_id(), rect)
    cef.Initialize()
    browser = cef.CreateBrowserSync(window_info, url='http://www.google.com')
    cef.MessageLoop()


def on_closing():
    print('closing')
    root.destroy()


root = tk.Tk()
root.geometry('800x600')
root.protocol('WM_DELETE_WINDOW', on_closing)
frame = tk.Frame(root, bg='blue', height=200)
frame2 = tk.Frame(root, bg='white', height=200)
frame.pack(side='top', fill='x')
frame2.pack(side='top', fill='x')

tk.Button(frame2, text='Exit', command=on_closing).pack(side='left')
tk.Button(frame2, text='Show something',
          command=lambda: messagebox.showinfo('TITLE', 'Shown something')).pack(side='right')

rect = [0, 0, 800, 200]
print('browser: ', rect[2], 'x', rect[3])

thread = threading.Thread(target=test_thread, args=(frame,))
thread.start()

root.mainloop()
