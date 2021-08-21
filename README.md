# M|Chroma
An open-source software for the analysis of chromatograms.


## Getting Started
### Installation
Either clone the repository or download the .zip file and extract.


### Requirements
You will need to install Python to use this software. M|Chroma is developed
with Python 3.8.8, so that is the safest version to use, but it has been tested
with Python 3.7 with no issues. Download Python 3.8.8 from:
[https://www.python.org/downloads/](https://www.python.org/downloads/).

You should then install the required packages by running requirements.py.


### Running the Program
Start the software by running mchroma.py. Tutorial coming soon!

## Current Features
### Implemented Features
- Peak picking (from bounding points or from single point in peak)
- Automatic calculation of retention time, theoretical plate count, peak width
    peak area, and more
- Baseline correction
- Peak summary table exporting to .csv file


### Unimplemented/In-development Features
For a more detailed description of planned features, check out agenda.txt.
- Modified area calculations (base-valley, valley-base, and valley-valley)
- Time scale shifting/peak referencing
- Signal scaling/normalization
- Automatic peak picking by threshold


## Challenges, Bugs, and Other Complications
- Currently, this program only supports .asc files exported from Shimadzu
    CLASS-VP analysis software.
- Peak summary table is cut off. This can be manually fixed to some extent by
    adjusting the "bottom" parameter in the "Configure subplots" context of the
    plot menu.
- Edit>Undo/Redo feature is very buggy
