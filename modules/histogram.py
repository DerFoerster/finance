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
# Computes jumps between availiable data.
# rawdata: unedited data from csv of chart
# jumps:   all jumps on timegrid   

def getJumps( rawdata ):  # _ between the name of the stock/datafile and the data is needes in the plotfunction below!
    jumps = {}  #contains all kind of evaluable jumps.
    
    for index in rawdata: 
  
       
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
# Computes jumps between consecutive extremal points 
# jumps:    time-ordered daily jumps of charts
# maxjumps: monotonous differences/jumps

def maximalJumps( jumps ):
    maxjumps  = {}                                                             #contains all kind of evaluable jumps.
    jumparray = []
       
    for index in jumps:                                                       

        indexsize = np.size( jumps[ index ] )
        
        # initialize sign and value of first jump
        #______________________________________________________________________        
        oldsign   = np.sign( jumps[ index ][0] )
        oldjump   =          jumps[ index ][0]
        
        for i in range( 1, indexsize ):      
            
            # summation of all jumps with same sign
            #__________________________________________________________________
            if np.sign( jumps[ index ][ i ] ) == oldsign:                      # sum jumps up as long as sign doesnt change.  expects strictly monotonous changing series
                oldjump  += jumps[index][i]  
            # storing maximal jump and reinicialize summation if sign of daily jump changes
            #__________________________________________________________________
            else:
                jumparray.append( oldjump )                                    # if sign of jumps change: write actual sum into maxjumps[index]    
                oldjump   = jumps[ index ][ i ]                                 # initialize new
                oldsign   = np.sign( jumps[index][i] )                         # set new sign
        
        #  overgive maximal jumps as numpy array
        maxjumps[ index ] = np.array( jumparray )
        
    return maxjumps

        






# makeHistogram ( dictionary: jumps ) = dictionary: histogram, dictionary: histpos, dictionary: histneg
##############################################################################
# Precomputes histogram data for later use
# jumps:      data that shall be analyzed as histogram
# histogram:  contains all jumps
# histpos:    contains just positive jumps for evaluation
# histneg:    contains just negative jumps

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










# determineValues ( dictionary: charts ) = dictionary: singlekeyvalues
##############################################################################
# computes important real values for description of data
# charts:   
# singlekeyvalues:
    
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





# fitDistribution ( dictionary: data, real: minimum, real: maximum, real: binwidth, ax=None ) = list: bestdistributions
##############################################################################
# Model data by finding best fit distribution to data
# data
# minimum: is needed for generation of density
# maximum: is needed for generation of density
# binwidth
# ax
# bestdistributions: contains distributions together with error sorted such that distribution with minimal error comes first
 
def fitDistribution( data, minimum, maximum, binwidth=5, progres=False ):#, ax=None):
    if progres:
        print("\n\nStart fitting process:\n")
    
    # Get histogram of original data
    #__________________________________________________________________________
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
    #__________________________________________________________________________
    bestdistributions = []

    # Estimate distribution parameters from data
    #__________________________________________________________________________
    for ii, distribution in enumerate([d for d in _distn_names if not d in ['levy_stable', 'studentized_range']]):
        
        if progres:
            print( "   " + "{:>3} / {:<3}: {}".format( ii+1, len(_distn_names), distribution ))

        distribution = getattr(st, distribution)
        
        
        # Try to fit the distribution
        #______________________________________________________________________
        try:
            # Ignore warnings from data that can't be fit
            #__________________________________________________________________
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore')
 
                # fit dist to data
                #______________________________________________________________
                params = distribution.fit(data)

                # Separate parts of parameters
                #______________________________________________________________
                arg   = params[:-2]
                loc   = params[-2]
                scale = params[-1]
                
                # Calculate fitted PDF and error with fit in distribution
                #______________________________________________________________
                pdf   = distribution.pdf(x, loc=loc, scale=scale, *arg)
                sse   = np.sum(np.power(y - pdf, 2.0))
                
# for testing purposes                
                if ii >= 5:
                    return sorted(bestdistributions, key=lambda x:x[2])
                    break
#"""                

                # identify if this distribution is better
                #______________________________________________________________
                bestdistributions.append((distribution, params, sse))

        except Exception:
            pass

    return sorted( bestdistributions, key=lambda x:x[2] )#[0]                   #overgive just best fitting distribution [0]





# makeDensity ( dist, real: minimum, real: maximum, real: binwidth, ax=None ) = 
###############################################################################
# Generates density of overgiven distribution
# dist distribution
# minimum: lower bound from which on y-vector of density values will be generated
# maximum: upper bound
# binwidth
# ax

def makeDensity( dist, params, minimum, maximum, size=1000, quantiles=True ):

    # Separate parts of parameters
    arg   = params[:-2]
    loc   = params[-2]
    scale = params[-1]

    # Get sane start and end points of distribution
    start = minimum#max(dist.ppf(0, *arg, loc=loc, scale=scale) if arg else dist.ppf(0, loc=loc, scale=scale), minimum)
    end   = maximum#min(dist.ppf(1, *arg, loc=loc, scale=scale) if arg else dist.ppf(1, loc=loc, scale=scale), maximum)

    # Build PDF and turn into pandas Series
    x     = np.linspace(start, end, size)
    y     = dist.pdf(x, loc=loc, scale=scale, *arg)
    pdf   = pd.Series(y, x)
    
    if quantiles:
        # Get quantiles of distribution
        q99   = dist.ppf(0.99, *arg, loc=loc, scale=scale) if arg else dist.ppf(0.99, loc=loc, scale=scale)
        q90   = dist.ppf(0.90, *arg, loc=loc, scale=scale) if arg else dist.ppf(0.90, loc=loc, scale=scale)   
        q75   = dist.ppf(0.75, *arg, loc=loc, scale=scale) if arg else dist.ppf(0.75, loc=loc, scale=scale)
        q50   = dist.ppf(0.50, *arg, loc=loc, scale=scale) if arg else dist.ppf(0.50, loc=loc, scale=scale)
        q25   = dist.ppf(0.25, *arg, loc=loc, scale=scale) if arg else dist.ppf(0.25, loc=loc, scale=scale)
        q10   = dist.ppf(0.10, *arg, loc=loc, scale=scale) if arg else dist.ppf(0.10, loc=loc, scale=scale)
        
        return pdf, q99, q90, q75, q50, q25, q10
    


    return pdf

