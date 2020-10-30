import subprocess

def install(name):
    subprocess.call(['pip', 'install', name])

def initialize():
    try:
        import tkinter
    except:
        install("tkinter")

    try:
        import pandas
    except:
        install("pandas")

    try:
        import plotly.express
    except:
        install("plotly")

    try:
        import tkinter.filedialog
    except:
        install("tkinter.filedialog")

    try:
        import copy
    except:
        install("copy")

    try:
        import ipywidgets
    except:
        install("ipywidgets")

    try:
        import numpy
    except:
        install("numpy")

    try:
        import pandastable
    except:
        install("pandastable")
        #Pandastable documentation
        #https://pandastable.readthedocs.io/en/latest/pandastable.html
        #
    try:
        import cefpython3
    except:
        install("cefpython3")
    try:
        import kaleido
    except:
        install("kaleido")
