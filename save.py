"""This module is used for saving and loading data"""
import tkinter as tk
import tkinter.filedialog
import pandas as pd
from icecream import ic

#================================================================
# EXPORT PEAK TABLE TO CSV
#================================================================
def export_peaks(params):
    try:
        filepath = tk.filedialog.asksaveasfilename(
            defaultextension="csv",
            filetypes=[
                ("Comma-Separated Values", "*.csv"),
                ("All Files", "*.*")],
            )
        #open a filedialog to pick output file name and destination
        peak_tables = [gram.peak_table for gram in params["chromatograms"]]
        table_temp = pd.concat(peak_tables,
            keys=[gram.name for gram in params["chromatograms"]])
        #concatenate all peak summary tables into one data frame indexed by
        #chromatogram names
        table_temp.to_csv(str(filepath), index = False, header=True)
    except ValueError:
        print("Peak summary export operation aborted!")
