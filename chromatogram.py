"""This module defines the Chromatogram and Peak classes"""
import numpy as np
import pandas as pd
from icecream import ic

#================================================================
# SETTING SYSTEM PARAMETERS
#================================================================
NOISE_TOLERANCE = 50
SAMPLING_RATE = 10.000640

with open("settings.cfg","r") as settings:
    line = settings.readline()
    while line != "":
        if line.split(" ")[0] == "NOISE_TOLERANCE":
            NOISE_TOLERANCE = float(line.split(" ")[1])
        elif line.split(" ")[0] == "SMAPLING_RATE":
            SAMPLING_RATE = float(line.split(" ")[1])
        line = settings.readline()


#================================================================
# HANDY INPUT HANDLING FUNCTION
#================================================================
def validate(var,vals,types):
    """This function checks if an input is valid by ensuring that does not have
    a restricted value and that it is of a specified type."""
    return bool(var not in vals and isinstance(var,types))

empties = ("",[],tuple(),None,0,{})
#================================================================
# CHROMATOGRAM
#================================================================
class Chromatogram:
    """Chromatogram class is used to store all the information about a
    chromatogram: raw data, axis scale factors, peaks, etc.

    Parameters:
        raw_data - expects a list of integers corresponding to signal intensity
            in detector counts"""
    def __init__(self,**kwargs):
        self.raw_data = [point for point in kwargs["data"]]
        self.signal_series = [point for point in kwargs["data"]]
        self.baseline = [0 for point in kwargs["data"]]
        #Initialize raw_data and signal_series as separate memory objects
        #so that raw_data can be remembered when signal_series is changed by
        #normalization, etc.

        if "color" in kwargs and validate(kwargs["color"],empties,(str)):
            self.color = kwargs["color"]
        else:
            self.color = "#000000"
        #Set plotting color

        if "name" in kwargs and validate(kwargs["name"],empties,(str)):
            self.name = kwargs["name"]
        else:
            self.name = "unnamed chromatogram"
        #Set chromatogram name.

        if "sampling_rate" in kwargs and validate(kwargs["sampling_rate"],empties,(int,float)):
            self.time_scale = 1/(60*kwargs["sampling_rate"])
        else:
            self.time_scale=1/(60*SAMPLING_RATE)
        #Specify number of data points recorded per minute.

        self.time_series=[t*self.time_scale for t in range(len(self.signal_series))]
        #convert independent variable from data point # to time in minutes

        if "time_shift" in kwargs and validate(kwargs["time_shift"],empties,(int,float)):
            self.time_shift = kwargs["time_shift"]
        else:
            self.time_shift = 0
        #Variable to track net shift in time series

        if "signal_scale" in kwargs and validate(kwargs["signal_scale"],empties,(int,float)):
            self.signal_scale = kwargs["signal_scale"]
        else:
            self.signal_scale = 1 #Variable to track net scaling of signal series

        self.reference_peak = None #Peak used as reference for adjusting time.

        self.derivative_series=[self.signal_series[x+1]-self.signal_series[x]\
            for x in range(len(self.signal_series)-1)]
        #computes the right handed slope at any point
        self.derivative_series.append(0)
        #we need one more data point at the end so the lengths don't mismatch
        self.peaks = []
        self.hidden = False #Toggles display of chromatogram on graph.
        self.active = False
        self.peak_table=pd.DataFrame()

    def update_peak_table(self):
        """This method stores peak data in a Pandas DataFrame object in order to
        easily export it as CSV"""
        peaks_data = []
        for peak in self.peaks:
            peak_data = [
                peak.retention_index,
                peak.retention_time,
                peak.area,
                peak.height,
                peak.width_hh,
                peak.plates
                ]
            peaks_data.append(peak_data)

        self.peak_table=pd.DataFrame(peaks_data,
            columns=[
                "Retention Index",
                "Retention Time",
                "Area",
                "Height",
                "Width",
                "Plate Count"
                ])

    def reindex_peaks(self):
        """This method orders peaks from lowest rt to highest"""
        peak_order=[]
        peaks_temp=[]
        for peak_1 in self.peaks:
            peak_index = 0
            if len(self.peaks) <=1:
                peak_order=[0]
                #bug fix! without this line, peak_order is an empty table,
                #so nothing gets appended into peaks_temp, so the peak table
                #gets wiped by this function!
                break
            for peak_2 in self.peaks:
                if peak_1 is peak_2:
                    continue
                    #do not compare peak with itself
                if peak_1.retention_time>peak_2.retention_time:
                    peak_index+=1
                    #Assign each peak an index based on the order of its retention time
                elif peak_1.retention_time==peak_2.retention_time:
                    print("Error: Peaks should have distinct retention times!")
            peak_order.append(peak_index)
        for index in peak_order:
            peaks_temp.append(self.peaks[index])
            self.peaks[index].retention_index=len(peaks_temp)
            #reorder peaks based on their assigned indices
        self.peaks = peaks_temp #overwrite unsorted list with newly sorted list

    def __getitem__(self,i):
        """This method allows direct indexing into the chromatogram to access
        its peaks."""
        return self.peaks[i]

    def __repr__(self):
        pd.set_option("display.precision", 2)
        return f"Chromatogram {self.name} <{id(self)}>:\n{str(self.peak_table)}\n"

    def compute_derivative(self):
        """This method is used to calculate the first-derivative series from
        the signal series."""
        self.derivative_series=[self.signal_series[x+1]-self.signal_series[x]\
            for x in range(len(self.signal_series)-1)]
        #Computes the right handed slope at any point
        self.derivative_series.append(0)
        #we need one more data point at the end so the lengths don't mismatch

    def time2index(self,time):
        """This method converts a list of times to a list of corresponding data
        point indices."""
        output = None
        if isinstance(time,(list,tuple)):
            indices = []
            for t in time:
                indices.append(int(np.round((t-self.time_shift)/self.time_scale)))
                output = indices
        elif isinstance(time,(float,int)):
            output = int(np.round((time-self.time_shift)/self.time_scale))
        return output

    def index2time(self,index):
        """This method converts a list of data point indices to a list of
        time points."""
        output = None
        if isinstance(index,(list,tuple)):
            time = []
            for i in index:
                time.append(i*self.time_scale+self.time_shift)
            output = time
        elif isinstance(index,int):
            output = index*self.time_scale+self.time_shift
        return output

    def _update_peaks(self):
        """This method is used to update peaks when a chromatogram is
        manipulated (i.e. time series is shifted or signal series is scaled.)
        A new set of peaks is constructed based on the bounding point indices
        of the old peaks."""
        updated_peaks = []
        for peak in self.peaks:
            updated_peaks.append(Peak(self,[peak.i_0,peak.i_f],area_mode=peak.area_mode))
        self.peaks = updated_peaks

    def update(self):
        """This method is used to ensure that any changes to a chromatogram
        are reflected throughout."""
        self.compute_derivative()
        self.reindex_peaks()
        self.update_peak_table()

    def add_peak(self,bounds,area_mode="bb"):
        """This method is used to add a peak to the chromatogram."""
        self.peaks.append(Peak(self,bounds))
        self.update()

    def baseline_correct(self,bounds):
        """This method is used to correct the baseline of the chromatogram. It
        takes two points selected from the baseline as reference, and defines
        the new baseline as the line passing through both points.

        Arguments:
            bounds -- a list of indices [start, end]"""
        i_0, i_f = bounds #Bounding indices.
        t_0, t_f = self.index2time(bounds) #Bounding times.
        s_0 = self.signal_series[i_0] #Signal at first point
        s_f = self.signal_series[i_f] #Signal at second point
        slope = (s_f-s_0)/(i_f-i_0) #Slope of baseline
        self.baseline = [slope * (i_x-i_0) + s_0
            for i_x,_ in enumerate(self.signal_series)]
        #Signal values of baseline calculated with point slope form
        corrected_signals = [self.signal_series[i] - self.baseline[i]
            for i,_ in enumerate(self.signal_series)]
        self.signal_series = corrected_signals
        #Update signal series by subtracting baseline values
        self._update_peaks()
        self.update()

    def _update_time_series(self):
        """This method is used to apply changes to the time_scale and time_shift
        attributes to the time_series list."""
        self.time_series=[t*self.time_scale+self.time_shift for t in range(len(self.signal_series))]

    def shift_time(self, shift, set=False):
        """This method shifts the time series by a given amount of time.

        Arguments:
            shift -- the amount of time to shift by
            set -- when enabled, the time_shift attribute will be set to the
                shift; otherwise the shift will be applied cumulatively"""
        if set:
            self.time_shift = shift
        else:
            self.time_shift += shift

        self._update_time_series()
        self._update_peaks()
        self.update()

    def scale_signal(self, factor,set=False):
        """This method scales the signal series by a specified scale factor.

        Arguments:
            factor -- the factor to scale the signal by
            set -- when enabled, the signal_scale attribute will be set to the
                factor; otherwise the factor will be applied cumulatively"""
        if factor == 0:
            print("Cannot scale signal to 0 or data will be lost!")
        else:
            if set:
                self.signal_scale = factor
            else:
                self.signal_scale *= factor

            self.signal_series = [self.signal_scale*point for point in self.raw_data]

            self._update_peaks()
            self.update()

    def scale_time(self, factor, type="period",set=True):
        """This method changes the time scale factor.

        Arguments:
            factor -- the factor by which to scale the time series
            type -- the type of value the factor is, options are 'period' in
                units of minutes per point and 'frequency' in points per second.
            set -- when enabled, the time_scale attribute will be set to the
                factor; otherwise the factor will be applied cumulatively"
            """

        if type not in ("period","frequency"):
            print("Invalid argument: type must be 'period' or 'frequency'.")


        if validate(factor,empties,(int,float)):
            if type == "period":
                if set:
                    self.time_scale = factor
                else:
                    self.time_scale *= factor
            elif type == "frequency":
                if set:
                    self.time_scale = 1/(60*factor)
                else:
                    self.time_scale *= 1/(60*factor)
            self.time_series=[t*self.time_scale+self.time_shift for t in range(len(self.signal_series))]
        else:
            print("Invalid argument for Chromatogram.rescale_time()")

        self._update_peaks()
        self.update()

    def normalize(self, reference, dim="area", norm_to=1):
        """This method normalizes the signal series with respect to a reference
        peak.

        Positional Arguments:
            reference -- a peak object to use as a reference to normalize to

        Keyword Arguments:
            dim -- the quantity which is to be normalized. Valid options are
                'height' and 'area'.
            norm_to -- the target value of the height/area after normalization.

            With default kwargs, the chromatogram will be scaled such that the
            area of the reference integrates to 1.
            """
        if dim == "area":
            self.scale_signal(norm_to/reference.area,set=True)
        elif dim == "height":
            self.scale_signal(norm_to/reference.height,self=True)
        else:
            raise ValueError("Normalization dimension must be\
                 'area' or 'height!'") from None

    def shift_by_reference(self, reference):
        """This method shifts the time scale based on a reference peak."""
        self.shift_time(reference.retention_time,set=True)
        self.reference_peak = reference

    def detect_bounds(self, point):
        """This method finds the bounding indices of a feature (peak) from a
        single index within the peak by examining the first derivative.

        The location on the peak is detected (left, right, or plateau) and
        from there, the bounds are detected as points past the crest (plateau)
        whose first derivatives are zero (below the NOISE_TOLERANCE threshold)."""
        location = ""
        if abs(self.derivative_series[point]) < NOISE_TOLERANCE*self.signal_scale:
            location = "top"
        elif self.derivative_series[point] < 0:
            location = "right"
        else:
            location = "left"

        left = point
        right = point

        while True:
            left -= 1
            #Step through the feature backwards to find the left bound.
            if location == "left" and abs(self.derivative_series[left]) < NOISE_TOLERANCE*self.signal_scale:
                #Bound is found when the left tail reaches a plateau (zero derivative).
                break
            elif location == "left" and -self.derivative_series[left] > NOISE_TOLERANCE*self.signal_scale:
                #Bound is also found when the left tail finds the end of another
                #peak (negative derivative).
                break
            elif location == "top" and self.derivative_series[left] > NOISE_TOLERANCE*self.signal_scale:
                #The left tail is found when the top begins to to slope (positive derivative).
                location = "left"
                continue
            elif location == "right" and self.derivative_series[left] > NOISE_TOLERANCE*self.signal_scale:
                location = "left"
                #There may not be a top plateau, so the left tail is found when
                #derivative is positive while exploring the right tail.
                continue
            elif location == "right" and abs(self.derivative_series[left]) < NOISE_TOLERANCE*self.signal_scale:
                location = "top"
                #The top is found when the right tail gives way to a plateau.
                continue
            else:
                continue

        while True:
            right += 1
            #Step through the feature forwards to find the right bound.
            if location == "right" and abs(self.derivative_series[right]) < NOISE_TOLERANCE*self.signal_scale:
                #Bound is found when the right tail reaches a plateau (zero derivative).
                break
            elif location == "right" and self.derivative_series[right] > NOISE_TOLERANCE*self.signal_scale:
                #Bound is also found when the right tail finds the start of another
                #peak (positive derivative).
                break
            elif location == "top" and -self.derivative_series[right] > NOISE_TOLERANCE*self.signal_scale:
                #The right tail is found when the top begins to to slope (negative derivative).
                location = "right"
                continue
            elif location == "left" and -self.derivative_series[right] > NOISE_TOLERANCE*self.signal_scale:
                location = "right"
                #There may not be a top plateau, so the right tail is found when
                #derivative is negative while exploring the left tail.
                continue
            elif location == "left" and abs(self.derivative_series[right]) < NOISE_TOLERANCE*self.signal_scale:
                location = "top"
                #The top is found when the left tail gives way to a plateau.
                continue
            else:
                continue

        return [left,right]

    def one_point_peak(self,point):
        """This method adds a peak from a single index within the feature,
        using the detect_bounds() method to find the bounding indices of the
        peak."""
        self.add_peak(self.detect_bounds(point))


    def threshold_autopick(self,threshold,delta=200):
        """This method automatically picks peaks above a certain threshold"""
        features=[]
        #Keep track of the features above the threshold in this list.
        above_threshold = False
        temp_bounds = []
        for index,signal in enumerate(self.signal_series):
            if not above_threshold:
                if signal > threshold:
                    temp_bounds.append(index)
                    above_threshold = True
                    #When the signal first exceeds the threshold, define the
                    #start of a new feature.
            else:
                if signal < threshold:
                    temp_bounds.append(index)
                    above_threshold = False
                    features.append(temp_bounds)
                    #When the signal of a feature drops below the threshold,
                    #define the end of the feature and append it to the list of
                    #features.

        #Note: we could be done here if we only wanted to include the part of
        #the peaks that are above the threshold, but instead what we want is to
        #include the entirety of any peak whose maximum height is above the
        #threshold.
        for feature in temp_bounds:
            self.one_point_peak(feature[0])
            #Instead of reinveinting the wheel, peaks are made from the
            #detected features by using one_point_peak() to find their bounds.

    def load_dict(self,dictionary):
        """This method loads data from a dict of chromatogram data."""
        self.__dict__ = dictionary



#================================================================
# PEAK
#================================================================
class Peak:
    """Peak class contains data about a given peak, including the subset of
    raw data and time series the peak contains, peak area, maximum height,
    half-height width, retention time, etc."""

    def __init__(self, parent_gram, bounds, area_mode="bb"):
        """Peak object is defined by its parent chromatogram and its
        bounding indices."""
        self.i_0, self.i_f = bounds
        #Indices of incident and final data points in the chromatogram raw data.
        self.t_0, self.t_f = parent_gram.index2time(bounds)
        #Starting and ending time of peak feature.
        self.time_series = parent_gram.time_series[self.i_0:self.i_f+1]
        self.signal_series = parent_gram.signal_series[self.i_0:self.i_f+1]
        #subset of raw data contained in peak
        self.s_0 = self.signal_series[0]
        self.s_f = self.signal_series[-1]
        self.height = max(self.signal_series)
        self.retention_index = 0

        self.area_modifiers = {
            "bb":0,
            "vv":sum([(self.s_f-self.s_0)/(self.t_f-self.t_0)*n\
                for n in range(len(self.time_series))]),
            "bv":sum([(0-self.s_0)/(self.t_f-self.t_0)*n\
                for n in range(len(self.time_series))]),
            "vb":sum([(self.s_f-0)/(self.t_f-self.t_0)*n\
                for n in range(len(self.time_series))])
        }
        #modifiers for different integration modes: base-base, valley-valley,
        #left base to right valley, right base to left valley
        #The modifiers are integrals of the lines connecting the bases/valleys

        self.areas={}
        for key in self.area_modifiers:
            self.areas[key]=sum(self.signal_series)-self.area_modifiers[key]
        #areas computed with each mode
        self.area = self.areas[area_mode]
        self.area_mode = area_mode
        #area computed with the desired mode

        i_maxima = [index for index in range(len(self.time_series))\
            if self.signal_series[index] == self.height]
        #finds all time points with maximum signal in case detector caps out
        i_max=int(np.floor((len(i_maxima)-1)/2))
        #as an estimate, the middle of the peak is in the middle of the plateau
        self.retention_time=self.time_series[i_max]
        #the retention time occurs at the crest of the peak

        try:
            i_over_hh = [index for index in range(len(self.signal_series))\
                if self.signal_series[index]>self.height/2]
            #all indices for which the singal is > half the height
            self.width_hh=self.time_series[i_over_hh[-1]]\
                -self.time_series[i_over_hh[0]]
            #hh width is total duration of time for which the signal is
            #greater than half-height
            self.plates=5.54*(self.retention_time/self.width_hh)\
                *(self.retention_time/self.width_hh)
            #calculates the number of theoretical plates for a peak
        except:
            print("Error computing half-height width")

    def __repr__(self):
        return f"Peak object <{id(self)}>"
