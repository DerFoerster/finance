#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created:
    on Fri Dec 30 18:11:45 2022

Contains:
    All functions for 
    variances and 
    covariances and
    correlations of all kind

Author:
    robin
"""


"""
kovarianzmatrix der charts
korrelationsmatrix
    beginn
    lang
    kurz
autokorrelation
Kreuzkorrelationen
"""

# general modules
import os
import numpy as np
import scipy as scp
import scipy.stats as st
import pandas as pd
import matplotlib.pyplot as plt


# autoCorrelation ( dictionary: rawdata, dictionary: fouriertransformed, dictionary: singlekeyvalues  ) = dictionary: autocorrelations
##############################################################################
# :   
def autoCorrelation( charts, fouriertransformed, singlekeyvalues ):
    autocorrelations = {}

    for index in charts: 

        # Get the power spectrum
        #______________________________________________________________________ 
        pwr = np.abs( fouriertransformed[ index ] ) ** 2
        
        # Calculate the autocorrelation from inverse FFT of the power spectrum
        #______________________________________________________________________ 
        autocorrelations[ index ]  = np.fft.ifft(pwr).real # maybe use np.abs 
        autocorrelations[ index ] /= singlekeyvalues[ index ][ "variance" ] 
        autocorrelations[ index ] /= len( charts[ index ] )

    return autocorrelations       
       
"""    
        # Compute the FFT
        #______________________________________________________________________ 
        #fft = numpy.fft.fft(ndata, size)
    
        # Get the power spectrum
        #______________________________________________________________________ 
        pwr = np.abs(fft) ** 2
        
        # Calculate the autocorrelation from inverse FFT of the power spectrum
        #______________________________________________________________________ 
        acorr = numpy.fft.ifft(pwr).real / var / len(data)
    """ 
       







# correlationMatrix ( dictionary: charts ) = ndarray: correlarions
##############################################################################
# :   
def correlationMatrix( charts ):
    numberofcharts = len(charts)
    
    accessmask     = np.chararray(( numberofcharts, numberofcharts, 2 ))       # alows to identify values of correlationmatrix with the two corresponding indices
    
    pearson        = np.zeros(( numberofcharts, numberofcharts ))   
    spearman       = np.zeros(( numberofcharts, numberofcharts ))   
    kendall        = np.zeros(( numberofcharts, numberofcharts ))   
    
    # compute the correlations dismiss p values
    #__________________________________________________________________________
    j = 0                                                                      # for storing the correlations into ndarray: j column index
    for index1 in charts:
        i = 0                                                                  # for storing the correlations into ndarray: i row index
        for index2 in charts:                                                  # maybe use a dictionars accessing the correlations between chart1 and chart2 as pearson[chart1][chart2]
        
            # correcting size-differences of charts
            #__________________________________________________________________          
            existence       = np.minimum( np.size( charts[index1] ), np.size( charts[index2] ) ) # length of shorter chart
            firstexistence  = np.size( charts[index1] ) - existence            # charts are sorted from old to new. 
            secondexistence = np.size( charts[index2] ) - existence            # selecting all values from the first day of recording of the younger chart           
            
            pearson  [i,j]  = st.pearsonr  ( 
                                            charts[index1].iloc[firstexistence:], 
                                            charts[index2].iloc[secondexistence:] 
                                            )[0]                               # charts are sorted from last to newest
            spearman [i,j]  = st.spearmanr( 
                                            charts[index1].iloc[firstexistence:], 
                                            charts[index2].iloc[secondexistence:] 
                                            )[0]
            kendall  [i,j]  = st.kendalltau( 
                                            charts[index1].iloc[firstexistence:], 
                                            charts[index2].iloc[secondexistence:] 
                                            )[0]    
            accessmask[i][j][1] = index1
            accessmask[i][j][1] = index2
        
            i +=1
        j +=1    
    return pearson, spearman, kendall        


    
# correlationSets ( dictionary: charts, chararray: accessmask, ndarray: correlations, real: minimalcorr ) = dictionary: poscorrset, negcorrset
##############################################################################
# Generation of highly correlated subset A and another highly correlated B with corr(A,B) is negative
"""
def correlationSets ( charts, accessmask, correlations, minimalcorr=0.8 ):
    poscorrset = {}
    negcorrset = {}
    
    workcorr   = correlations #create working copy
    
    workcorr[ workcorr < 0.8 ] = 0 # cutting all edges of corrgraph if correlation between charts is too small
    
    for i in range( 1, size( workcorr[0] ) ):
        for j in range( 1, size( workcorr[0] ) ):
            if workcorr[i][j] == 0:
                workcorr[j,:] = 0 #cutting all edges to vertices that have one edge less
                workcorr[:,j] = 0
    
    for index1 in charts:
"""        

