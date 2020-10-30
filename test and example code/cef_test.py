#https://pythonprogramming.altervista.org/python-goes-to-the-web-cefpython-and-tkinter/amp/
from cefpython3 import cefpython as cef
import platform
import sys
import tkinter as tk


def open_link(url):
    print(url)
    root.destroy()
    sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
    cef.Initialize()
    cef.CreateBrowserSync(url=url,
        window_title=url)
    cef.MessageLoop()
    main()

def main():
    global root
    root = tk.Tk()
    root.geometry("400x100")
    l = tk.Label(root, text="Press Enter to browse Internet", fg="blue", font="Arial 20")
    l.pack(fill=tk.X)
    v = tk.StringVar()
    e = tk.Entry(root, textvariable=v, font="Arial 14")
    e.pack(fill=tk.X)
    v.set("https://www.google.com/")
    e.focus()
    e.bind("<Return>", lambda x: open_link(e.get()))
    root.mainloop()
    cef.Shutdown()


if __name__ == '__main__':
    main()
