## GENERAL NOTES / KEY FEATURES
- Figure out how to integrate dialogues with point picking
- Use numpy for chromatogram data (?)
- Fix peaks table
    - https://pandas.pydata.org/docs/reference/api/pandas.plotting.table.html
    - https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.table.html
    - Probably going to need to decouple from window
- Add functionality for editing chromatogram names
- py2exe (?)
    - Ideally I want something that can install a version of python then run
        requirements.py
- Create custom exceptions
    - Warnings for bad inputs?
- Test chromatogram shifting/referencing
- Test threshold autopicking
- Version numbering


## ERROR HANDLING
- Add some bug-proofing logic to one-point picking (what if the user selects a
    valley or a featureless region)


## QUALITY OF LIFE FEATURES
- Keyboard shortcuts
- Chain peak picking
- Allow deleting/editing picked peaks
- Update peaks by changing values on table
- Still allow manually setting peak bounds
- Help menu
- Settings menu
- Add support for other types of data file (though I would need a sample to inspect)


## UI FEATURES
- Add tooltips
- Change chromatogram order in stack
- Add a text box for printed output
- Add a crosshair cursor
    - https://stackoverflow.com/questions/63195460/how-to-have-a-fast-crosshair-mouse-cursor-for-subplots-in-matplotlib
- Dialog menus
    - Add dialogue options for all currently available analysis/peak methods
    - Add radio button subclass for methods like Chromatogram.normalize()
    - Custom class for peak picking (bounds, area mode)
    - Add title argument to dialogue class
    - http://www.java2s.com/Code/Python/GUI-Tk/Popupdialogbuildadialog.htm
- Label peak retention time and area on figure
- Highlight picked peaks (maybe plot them as separate objects with a fixed color)
- Use icons for buttons (steal them from MestReNova?)
- Color (links for reference)
    - https://stackoverflow.com/questions/42697933/colormap-with-maximum-distinguishable-colours
    - https://projects.susielu.com/viz-palette


## ANALYTICAL FEATURES
- Capacity factor
- Read time scale from data file
- Chromatogram signal addition and subtraction (remove reference peaks)
- Noise and S/N ratio


## SAVING/LOADING CHROMATOGRAMS
- JSON?
- Default file names
- Export plot and table to PDF
- Create a standard for saving data (similar to ascii data but with peak data, offset, scale, etc saved as well)
    - There might be a module that easily saves/loads variables
    - In that case, just export the history object and load it back in?

- plt.savefig('D:\\mpl_logo_with_title.png', dpi=dpi)


## SETTINGS
- Default time scale
- Data reader behavior
- Chromatogram colors
- Default integration mode
- Error logging
- Choose derivative calculation mode (left slope, right slope, lr average)


## KNOWN BUGS
- "instance.top.protocol("WM_DELETE_WINDOW", instance.cancel)" in dialogues.py
    does not result in instance.cancel() being called on closing out of the popup.
- When trying to undo importing the first chromatogram:
        Exception in Tkinter callback
        Traceback (most recent call last):
        File "C:\ProgramData\Anaconda3\lib\tkinter\__init__.py", line 1892, in __call__
        return self.func(*args)
        File "C:\Users\epics\Documents\Code\MChroma\MChroma\main.py", line 89, in undo
        self.present().active().plot()
        File "C:\Users\epics\Documents\Code\MChroma\MChroma\main.py", line 61, in active
        return self.chromatograms[self.active_index]
        IndexError: list index out of range

- Figure scaling is really gimpy: the peak table gets cut off, and resizing the
    window seems to resize the plot more than the table.
