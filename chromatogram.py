"""This module defines the Chromatogram and Peak classes"""

import numpy as np
import pandas as pd
from icecream import ic
#================================================================
# CHROMATOGRAM
#================================================================
class Chromatogram:
    """Chromatogram class is used to store all the information about a
    chromatogram: raw data, axis scale factors, peaks, etc.

    Parameters:
        raw_data - expects a list of integers corresponding to signal intensity
            in detector counts"""
    def __init__(self,params):
        self.signal_series=params["data"]
        self.ID=params["ID"]
        self.time_scale=0.0016667#Number of data points recorded per minute
        self.time_series=[t*self.time_scale for t in range(len(self.signal_series))]
        #convert independent variable from data point # to time in minutes

        self.derivative_series=[self.signal_series[x+1]-self.signal_series[x]\
            for x in range(len(self.signal_series)-1)]
        #computes the right handed slope at any point
        self.derivative_series.append(0)
        #we need one more data point at the end so the lengths don't mismatch
        self.peaks=[]
        self.hidden=False
        #toggles display of chromatogram on graph

    peak_table=pd.DataFrame()

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

    def update(self):
        self.reindex_peaks()
        self.update_peak_table()

#================================================================
# PEAK
#================================================================
class Peak:
    """Peak class contains data about a given peak, including the subset of
    raw data and time series the peak contains, peak area, maximum height,
    half-height width, retention time, etc."""

    def __init__(self, parent_gram, bounds, area_mode="bb"):
        self.t_0 = bounds[0]#starting time and height of click
        self.t_f = bounds[1]#ending time and height of click
        self.i_0 = int(np.round(self.t_0/parent_gram.time_scale))
        self.i_f = int(np.round(self.t_f/parent_gram.time_scale))
        #indices of incident and final data points in the chromatogram raw data
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

        #ic(self.retention_time)
        #ic(self.area)
        #ic(self.height)
        #ic(self.width_hh)
        #ic(self.plates)
