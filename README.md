# M|Chroma
An open-source software for the analysis of chromatograms.


## Getting Started
### Installation
Either clone the repository or download the .zip file and extract.


### Requirements
You will need to install Python >=3.8.0 to use this software. MChroma is not
compatible with Python 3.7, which does not support an extended Unicode charset.
M|Chroma is developed with Python 3.8.8, so that is the safest version to use.
Download Python 3.8.8 from:
[https://www.python.org/downloads/](https://www.python.org/downloads/).

Once Python is installed, run requirements.py to install the required packages.


### Running the Program
Start the software by running mchroma.py. Tutorial coming soon!

## Current Features
### Implemented Features
- Peak picking (from bounding points or from single point in peak)
- Automatic calculation of retention time, theoretical plate count, peak width
    peak area, and more
- Baseline correction
- Peak summary table exporting to .csv file
- Signal scaling


### Unimplemented/In-development Features
For a more detailed description of planned features, check out agenda.txt.
- Modified area calculations (base-valley, valley-base, and valley-valley)
- Time scale shifting/peak referencing
- Normalization
- Automatic peak picking by threshold


## Challenges, Bugs, and Other Complications
- Currently, this program only supports .asc files exported from Shimadzu
    CLASS-VP analysis software.
- Peak summary table is cut off. This can be manually fixed to some extent by
    adjusting the "bottom" parameter in the "Configure subplots" context of the
    plot menu.
- Edit>Undo/Redo feature is very buggy
