#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created:
    on Fri Dec 30 18:11:45 2022

Contains:
    All functions working on or creating histograms, densities and distributions

Author:
    robin
"""



import numpy as np
import pandas as pd

#for distribution-fitting
import warnings
import scipy.stats as st
#import statsmodels.api as sm
from scipy.stats._continuous_distns import _distn_names

#for faster fitting
from multiprocessing import Pool




# getJumps ( dictionary: rawdata ) = dictionary: jumps
##############################################################################
# :
# 
# histogram:  dictionary containing objects named after red in stock-data with ordered vectors
# close_i /= open_i+1
def getJumps( rawdata ):  # _ between the name of the stock/datafile and the data is needes in the plotfunction below!
    jumps = {}  #contains all kind of evaluable jumps.
    
    for index in rawdata: #iterates over index - an element of dictionary rawdata
       #nameofstock = index.replace("stock_", "")     
       
       # afternoon-Morning
       #_______________________________________________________________________
       closeopen =   rawdata[index]['Close'] - rawdata[index]['Open'] 
       
       # afternoon-next morning. Because shifting fills first column with NaN, one has to remove it via .dropna()
       #_______________________________________________________________________       
       openclose = rawdata[index]['Open']  - rawdata[index]['Close'].shift(1) 
       openclose = openclose.dropna() 
       
       # Transforms upper subtractions into numpy-array, combines them
       #_______________________________________________________________________       
       jumps[ index ] = np.concatenate((  closeopen.to_numpy(), openclose.to_numpy()  ))                      

    return jumps







# maximalJumps ( dictionary: jumps ) = dictionary: maxjumps
##############################################################################
# jumps: cictionary with unsorted jumps of charts. 

def maximalJumps( jumps ):
    maxjumps  = {}  #contains all kind of evaluable jumps.

    jumparray = []
       
    for index in jumps:                        # sum jumps up as long as sign doesnt change. 

        indexsize = np.size( jumps[ index ] )
        
        oldsign   = np.sign( jumps[ index ][0] )
        oldjump   =          jumps[ index ][0]
        
        for i in range( 1, indexsize ):      
            
            if np.sign( jumps[ index ][ i ] ) == oldsign:       # sum jumps up as long as sign doesnt change.  expects strictly monotonous changing series
                #print("huhuhuhuhuhu")
                oldjump  += jumps[index][i]  
            else:
                jumparray.append( oldjump )    #if sign of jumps change: write actual sum into maxjumps[index]    
                oldjump  = jumps[ index ][ i ] # initialize new
                oldsign   = np.sign( jumps[index][i] ) # set new sign
                
        maxjumps[ index ] = np.array( jumparray )
        
        oldjump = 0 # and start new summation
           
        #print( maxjumps[index] )
        
    return maxjumps

        






# makeHistogram ( dictionary: jumps ) = dictionary: data
##############################################################################
# :
# 
# histogram:  dictionary containing objects named after red in stock-data with ordered vectors
# close_i /= open_i+1
def makeHistogram( jumps ):  # _ between the name of the stock/datafile and the data is needes in the plotfunction below!
    histogram = {} #total histogram
    histpos   = {} #histogram of positive jumps
    histneg   = {} #histogram of negative jumps
    
    for index in jumps: #iterates over index - an element of dictionary rawdata     
       # Makes histogram of all jumps. 
       #_______________________________________________________________________       
       histogram[ index ] = jumps[ index ]#np.sort( jumps[ index ])
       
       # Makes histogram of all positive jumps
       #_______________________________________________________________________      
       histpos[ index ] = histogram[ index ][ histogram[ index ]>=0 ]
              
       # Makes histogram of all negative jumps
       #_______________________________________________________________________       
       histneg[ index ] = histogram[ index ][ histogram[ index ]<=0 ]                   

    return histogram, histpos, histneg










# makeHistogram ( dictionary: charts ) = dictionary: singlekeyvalues
##############################################################################
def determineValues( charts ):
    singlekeyvalues = {}
    
    for index in charts:   
           singlekeyvalues[ index ]       = { 
                                              "minimum":      np.min(    charts[ index ] ), 
                                              "maximum":      np.max(    charts[ index ] ), 
                                              "median":       np.median( charts[ index ] ), 
                                              "mean":         np.mean(   charts[ index ] ),           #expectancy
                                              "deviation":    np.std(    charts[ index ] ),           #standard deviation
                                              "variance":     np.std(    charts[ index ] )**2 ,       #secondmoment
                                              "thirdmoment":  st.moment( charts[ index ], moment=3 ), #  
                                              "fourthmoment": st.moment( charts[ index ], moment=4 )  #kurtosis                                              
                                              }
    return singlekeyvalues





# fitDistribution ( data, real: minimum, real: maximum, real: binwidth, ax=None )
##############################################################################
# Model data by finding best fit distribution to data
 
def fitDistribution(data, minimum, maximum, binwidth=20):#, ax=None):
    print("\n\nStart fitting process:\n")
    
    # Get histogram of original data
    y, x = np.histogram(
                         data,  
                         bins = range( 
                                       int(minimum), 
                                       int(maximum), 
                                       binwidth 
                                       ),  
                         density=True
                         )
    
    x = (x + np.roll(x, -1))[:-1] / 2.0

    # Best holders
    bestdistributions = []

    # Estimate distribution parameters from data
    for ii, distribution in enumerate([d for d in _distn_names if not d in ['levy_stable', 'studentized_range']]):
        print( "   " + "{:>3} / {:<3}: {}".format( ii+1, len(_distn_names), distribution ))

        distribution = getattr(st, distribution)
        #print(type(data))
        #params = distribution.fit(data)
        # Try to fit the distribution
        try:
            # Ignore warnings from data that can't be fit
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore')
                #print("1")
                # fit dist to data
                params = distribution.fit(data)
                #print(params)
                # Separate parts of parameters
                arg   = params[:-2]
                loc   = params[-2]
                scale = params[-1]
                
                # Calculate fitted PDF and error with fit in distribution
                pdf   = distribution.pdf(x, loc=loc, scale=scale, *arg)
                sse   = np.sum(np.power(y - pdf, 2.0))
# for testing purposes                
#                if ii >= 5:
#                    return sorted(bestdistributions, key=lambda x:x[2])
#                    break
#"""                
                # if axis pass in add to plot
#                try:
#                    if ax:
#                        pd.Series(pdf, x).plot(ax=ax)
#                    end
#                except Exception:
#                    pass

                # identify if this distribution is better
                bestdistributions.append((distribution, params, sse))

        except Exception:
            print(Exception)
            pass

    return sorted(bestdistributions, key=lambda x:x[2])





# makeDensity ( data, real: minimum, real: maximum, real: binwidth, ax=None ) = 
###############################################################################
# :

def makeDensity( dist, params, minimum, maximum, size=1000 ):
    #Generate distributions's Probability Distribution Function """

    # Separate parts of parameters
    arg   = params[:-2]
    loc   = params[-2]
    scale = params[-1]

    # Get sane start and end points of distribution
    start = minimum#max(dist.ppf(0, *arg, loc=loc, scale=scale) if arg else dist.ppf(0, loc=loc, scale=scale), minimum)
    end   = maximum#min(dist.ppf(1, *arg, loc=loc, scale=scale) if arg else dist.ppf(1, loc=loc, scale=scale), maximum)
    
    # Get quantiles of distribution
    q99   = dist.ppf(0.99, *arg, loc=loc, scale=scale) if arg else dist.ppf(0.99, loc=loc, scale=scale)
    q90   = dist.ppf(0.90, *arg, loc=loc, scale=scale) if arg else dist.ppf(0.90, loc=loc, scale=scale)   
    q75   = dist.ppf(0.75, *arg, loc=loc, scale=scale) if arg else dist.ppf(0.75, loc=loc, scale=scale)
    q50   = dist.ppf(0.50, *arg, loc=loc, scale=scale) if arg else dist.ppf(0.50, loc=loc, scale=scale)
    q25   = dist.ppf(0.25, *arg, loc=loc, scale=scale) if arg else dist.ppf(0.25, loc=loc, scale=scale)
    q10   = dist.ppf(0.10, *arg, loc=loc, scale=scale) if arg else dist.ppf(0.10, loc=loc, scale=scale)
    
    # Build PDF and turn into pandas Series
    x     = np.linspace(start, end, size)
    y     = dist.pdf(x, loc=loc, scale=scale, *arg)
    pdf   = pd.Series(y, x)

    return pdf, q99, q90, q75, q50, q25, q10


""" Old structure with too specific-hardcodes names. Now computable trough determineValues( histpos / histneg / histogram )
       # computes single key datas for analyzing  jumps
       #_______________________________________________________________________      
       jumps[ nameofstock+"_values" ]     = {   
                                              "minimum":      np.min(jumps[ nameofstock+"_combination" ]), 
                                              "maximum":      np.max(jumps[ nameofstock+"_combination" ]), 
                                              "median":       np.median(jumps[ nameofstock+"_combination" ]), 
                                              "mean":         np.mean(jumps[ nameofstock+"_combination" ]),  #expectancy
                                              "deviation":    dev,  #standard deviation
                                              "variance":     dev**2, #secondmoment
                                         
                                              "minimum_pos":      np.min(jumps[ nameofstock+"_histogram_positive" ]), 
                                              "maximum_pos":      np.max(jumps[ nameofstock+"_histogram_positive" ]), 
                                              "median_pos":       np.median(jumps[ nameofstock+"_histogram_positive" ]), 
                                              "mean_pos":         np.mean(jumps[ nameofstock+"_histogram_positive" ]),  #expectancy
                                              "deviation_pos":    dev,  #standard deviation
                                              "secondmoment_pos": dev**2, #variance
                                              
                                              "minimum_neg":      np.min(jumps[ nameofstock+"_histogram_negative" ]), 
                                              "maximum_neg":      np.max(jumps[ nameofstock+"_histogram_negative" ]), 
                                              "median_neg":       np.median(jumps[ nameofstock+"_histogram_negative" ]), 
                                              "mean_neg":         np.mean(jumps[ nameofstock+"_histogram_negative" ]),  #expectancy
                                              "deviation_neg":    dev,  #standard deviation
                                              "secondmoment_neg": dev**2 #variance                                              #"thirdmomend": , #skewness
                                              } 
"""