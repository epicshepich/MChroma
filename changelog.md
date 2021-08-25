## Edit Dialogue Update
- Discovered compatibility issue with Python 3.7.3
- Updated legend header
- **Created dialogue EditChromatogram which is used for editing Chromatogram
    object metadata via the UI**
- Added edit buttons to legend, which use EditChromatogram dialogues
- Added Edit>Chromatogram toolbar item that opens an EditChromatogram dialogue
    for the active chromatogram
- Created method Chromatogram.scale_time, which allows the time_scale
    attribute to be changed (and reflects the changes throughout the code)
- Added "set" keyword to Chromatogram.scale_signal, Chromatogram.scale_time,
    and Chromatogram.shift_time methods which specifies whether the shift/scale
    factor is to be treated as net or cumulative.
- Added sample chromatograms to new folder "sample data" for testing



## Color Update II
- Allow loading multiple chromatograms from the file selection dialogue
- Added SAMPLING_RATE parameter to settings.cfg specifying the default sampling
    rate in Hz
- Importing chromatogram reads sampling rate from data file (if present), or falls
    back on default
- Added contingencies in Chromatogram class to handle missing/invalid arguments
- Added header to legend
- Added color selection buttons to legend


## Color Update
- Chromatogram.color attribute is assigned at construction so that chromatograms
    can be consistently plotted with the same color
- Specified list of default colors in settings.cfg
- Made graph resizable again


## Legendary Update
- Added cancel button to InputDialogue objects
- Added handling for aborted dialogue operations using the cancel control
    character "\x18"
- Added file settings.cfg for system parameters (such as NOISE_TOLERANCE)
- Used tkinter.Frame objects and the .grid() method to beautify input dialogues
- **Added chromatogram legend to left of graph that allows toggling chromatogram visibility and changing the active chromatogram**


## Input Dialogue Update
- Added input dialogue classes in new file dialogues.py:
    - Abstract base class InputDialogue
    - MultiEntryInput, a class defining a popup containing one or more
        tkinter.Entry fields.
- Implemented MultiEntryInput in Analysis>Scale Signal menu action.


## Peak Bounds Update
- Added \_\_repr__() method to peak class
- Reformatted changelog and agenda as markdown (.md) files
- Changed peak table display precision to 2
- Reformatted Chromatogram and Peak methods to take indices as arguments
    instead of times
- Added methods Chromatogram.time2index() and Chromatogram.index2time() to
    streamline conversions
- Used calls of active_chroma().time2index() in peak picking logic of
    mchroma.py
- Added method Chromatogram.detect_bounds() to find the bounding indices of a
    peak feature from a point within the feature.
- Added method Chromatogram.one_point_peak() to add a peak from a single index
    using the detect_bounds() method.
- One point picking works!
- Method one_point_peak() implemented in threshold_autopick(), but the feature
    is yet untested.


## README/Changelog Update
- Changed name of main script from "main.py" to "mchroma.py"
- Changed name of "install.py" to "requirements.py"'
- Replaced "README.txt" with reformatted "README.md"
- Created changelog
- Removed "Add Peak" button
- Moved icon files to new "images/icon" folder
