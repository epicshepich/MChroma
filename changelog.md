
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
