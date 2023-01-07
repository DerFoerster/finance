#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created:
    on Fri Dec 30 18:11:45 2022

Contains:
    All functions smoothing data

Author:
    robin
"""


import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

#for faster fitting
from multiprocessing import Pool


# smoothChart ( vector: data, int: smoothnessrange, int: kindofsmoother, real: smootherbasist=0, real: expopower=1 )
##############################################################################
# :   
def smoothChart( data, smoothnessrange=200, kindofsmoother=2, smootherbasis=0, expopower=1 ):
    smoothdata={}
    nameofsmoother = "No smoother "
    
    print( "\n\nComputing rolling mean over " + str(smoothnessrange) + " days:" )
    
    if kindofsmoother == 0: # symmetric:    large-eddy-normed-rectangle-filter
        smoother = np.ones( smoothnessrange )  
        nameofsmoother = "Symmetric rectangle 1 smoother "
        
    if kindofsmoother == 1: #symmetric:    large-eddy-gaussian-filter-function 
        smoother = np.ones( smoothnessrange )
        smoother = -np.arange( -1, 1, 2/smoothnessrange )**2 # (1-x^2)
        smoother = np.exp( smoother )   # e^(-x^2)
        nameofsmoother = "Symmetric normed exponential smoother e^(-x^2) "

    if kindofsmoother == 2: #symmetric:    large-eddy-gaussian-filter-function #e(-1/(1-x²)) not implemented
        smoother = np.ones( smoothnessrange )
        smoother = smoother-np.linspace( -1+2/smoothnessrange, 1-2/smoothnessrange, num=smoothnessrange )**2 # (1-x^2)
        smoother = -1/smoother           # 1/(1-x^2)
        smoother = np.exp( smoother )   # e^(-1/(1-x^2))
        nameofsmoother = "Symmetric normed gaussian smoother e^(-1/(1-x^2)) "
        
    if kindofsmoother == 3: #symmetric:    large-eddy-sin-filter-function - cuttof-spectral transformation of rectangel filter
        smoother = np.arange( -1, 1, 2/smoothnessrange )
        smoother = np.sinc(smoother)           #sin(pi*x/n)/pi*x
        nameofsmoother = "Symmetric sinc-smoother smoother sinc(x) "
 
    if kindofsmoother == 4: #not symmetric:    exponential-normed
        smoother = np.linspace( 0, 1, num=smoothnessrange )
        smoother = expopower*smoother
        if smootherbasis == 0:
            smoother = np.exp( smoother )   # e^(-x) is needed for convolution caused by non-symmetricy
            nameofsmoother = "Notsymmetric negative smoother: e^(" + str(expopower)+ "x)  "
        else:
            for i in range(0, smoothnessrange):
                smoother[i] = smootherbasis ** smoother[i] # basis^(-x)
                nameofsmoother = "Notsymmetric exponential smoother (" + str(expopower) + str(smootherbasis)+"^x) "

    print(nameofsmoother + "is applied.")
    #print(smoother)
    
    for index in data:
#        try:
        if index != "Date":
            indexsize = np.size( data[ index ] )
            movingaverage = np.zeros(indexsize)
        
            for i in range(smoothnessrange, indexsize ): #evolving mean of the last smoothnessrange days is new value
                for j in range ( 0, smoothnessrange ):
#                    try:
                     movingaverage[i] += smoother[ j ] * data[index].iloc[ i-j ]  #weightet average / convolution with reflected smoother / adds the dotproduct of data[index][ i-smoothnessrange : i] and smoother
#                    except Exception:
#                        pass 
                movingaverage[i] /= np.sum(smoother)
            smoothdata[ index ]  = movingaverage
            
    return smoothdata
#        except Exception:
#            print( "Some error occured while smoothing. Maybe a tatatype was unusable. \n Computation goes on, no panic!" )
          


















# computeFouriertrafo ( dictionary: rawdata, cuttingcoefficient=0.75, cuttingvalue=3000 ) = dictionary: data
##############################################################################
# rawdata:              dictionary with raw stock data
# cuttingcoefficient:   real aout of [0,1] representing the percentage of top and bottom cutting in the spectrum
#                       should be larger than 0.99 for smoothing
# cuttingvalue:         real setting the value from which all frequencies of the spectrum with higher itensity will be cutted
#                       should be around , otherwise too many data will be removed
# 
# fourier:  dictionary containing all fouriertransformed data
# close_i /= open_i+1    
def computeFouriertrafo( charts, cuttingcoefficient=0.75, cuttingvalue=5000 ):
#    print(rawdata)
    fourier                 = {}  #contains dft of charts
    topreduced_fourier      = {}  #
    bottomreduced_fourier   = {}
    itensityreduced_fourier = {}
    
    print("compute the fourier-transformation of input data.")
    for index in charts: #iterates over index - an element of dictionary rawdata
       
       # compute fast fourier transformation/spectrum of chart
       #_______________________________________________________________________
       fourier[ index ] = np.fft.fft( charts[ index ] )

       # hardcopy to avoid pointer-handling
       #_______________________________________________________________________
       topreduced_fourier[ index ]      = fourier[ index ].copy()   
       bottomreduced_fourier[ index  ]   = fourier[ index ].copy()        
       itensityreduced_fourier[ index ]   = fourier[ index ].copy()    
       
       # eliminating frequencies with high itensity
       #_______________________________________________________________________       
       itensityreduced_fourier[ index ] = itensityreduced_fourier[ index ][  itensityreduced_fourier[ index ]  <= cuttingvalue  ]
       
       # save the sizes for top and bottom cutting
       #_______________________________________________________________________
       opensize  = np.size( fourier[ index ] )

       #print( type( fourier[ index + "top_reducedfourier"  ] ) )       
       #print( np.size( fourier[ index + "top_reducedfourier"  ] ) )
       #print( np.size( fourier[ index + "top_reducedfourier"  ][0] ) )
       #print( np.size( fourier[ index + "top_reducedfourier"  ][8819] ) )
       
       
       # eliminating top/high and bottom/low frequencies of fouriertransformed/the spectrum
       #_______________________________________________________________________
       for i in range( 0, int( cuttingcoefficient * opensize ) ):
           topreduced_fourier[ index ][ i ]      = 0   #-1 for indexing reasons
           bottomreduced_fourier[ index ][ opensize-i-1 ] = 0
       
       # computing the fast inverse fourier transformation   
       #_______________________________________________________________________
       topreduced_fourier[ index ]      = np.fft.ifft( topreduced_fourier[ index ] )
       bottomreduced_fourier[ index  ]  = np.fft.ifft( bottomreduced_fourier[ index  ] )
       itensityreduced_fourier[ index ] = np.fft.ifft( itensityreduced_fourier[ index ] )

    return fourier, topreduced_fourier, bottomreduced_fourier, itensityreduced_fourier




""" Old structure with open and close instead on working with the whole chart
 def computeFouriertrafo( rawdata, cuttingcoefficient=0.75, cuttingvalue=5000 ):
#    print(rawdata)
    fourier = {}  #contains all kind of evaluable
    print("compute the fourier-transformation of input data.")
    for index in rawdata: #iterates over index - an element of dictionary rawdata
       nameofstock = index.replace("stock_", "")           
       
       # compute fast fourier transformation/spectrum of chart
       #_______________________________________________________________________
       fourier[ nameofstock+"_open_discretefourier"  ] = np.fft.fft( rawdata[ index ][ 'Open'  ] )
       fourier[ nameofstock+"_close_discretefourier" ] = np.fft.fft( rawdata[ index ][ 'Close' ] )

       # hardcopy to avoid pointer-handling
       #_______________________________________________________________________
       fourier[ nameofstock+"_open_top_reducedfourier" ]      = fourier[ nameofstock+"_open_discretefourier"   ].copy() 
       fourier[ nameofstock+"_close_top_reducedfourier" ]     = fourier[ nameofstock+"_close_discretefourier"  ].copy()      
       fourier[ nameofstock+"_open_bottom_reducedfourier" ]   = fourier[ nameofstock+"_open_discretefourier"   ].copy()
       fourier[ nameofstock+"_close_bottom_reducedfourier" ]  = fourier[ nameofstock+"_close_discretefourier"  ].copy()          
       fourier[ nameofstock+"_open_itensity_reducedfourier" ] = fourier[ nameofstock+"_open_discretefourier"   ].copy()    
       fourier[ nameofstock+"_close_itensity_reducedfourier" ]= fourier[ nameofstock+"_close_discretefourier"  ].copy()
       
       # eliminating frequencies with high itensity
       #_______________________________________________________________________       
       fourier[ nameofstock+"_open_itensity_reducedfourier" ] = fourier[ nameofstock+"_open_itensity_reducedfourier" ] [fourier[ nameofstock+"_open_itensity_reducedfourier" ]  <= cuttingvalue ]
       fourier[ nameofstock+"_close_itensity_reducedfourier" ]= fourier[ nameofstock+"_close_itensity_reducedfourier" ][fourier[ nameofstock+"_close_itensity_reducedfourier" ] <= cuttingvalue ]
       
       # save the sizes for top and bottom cutting
       #_______________________________________________________________________
       opensize  = np.size( fourier[ nameofstock+"_open_discretefourier"  ] )
       closesize = np.size( fourier[ nameofstock+"_close_discretefourier" ] )       

       #print( type( fourier[ nameofstock+"_open_top_reducedfourier" ] ) )       
       #print( np.size( fourier[ nameofstock+"_open_top_reducedfourier" ] ) )
       #print( np.size( fourier[ nameofstock+"_open_top_reducedfourier" ][0] ) )
       #print( np.size( fourier[ nameofstock+"_open_top_reducedfourier" ][8819] ) )
       
       
       # eliminating top/high and bottom/low frequencies of fouriertransformed/the spectrum
       #_______________________________________________________________________
       for i in range( 0, int( cuttingcoefficient * opensize ) ):
           fourier[ nameofstock+"_open_top_reducedfourier" ][ i ]  = 0   #-1 for indexing reasons
           fourier[ nameofstock+"_open_bottom_reducedfourier" ][ opensize-i-1 ] = 0

       for j in range( 0, int( cuttingcoefficient * closesize ) ):           
           fourier[ nameofstock+"_close_top_reducedfourier"][ j ] = 0   
           fourier[ nameofstock+"_close_bottom_reducedfourier"][ closesize-j-1 ] = 0
       
       # computing the fast inverse fourier transformation   
       #_______________________________________________________________________
       fourier[ nameofstock+"_open_itensity_reducedfourier" ] = np.fft.ifft( fourier[ nameofstock+"_open_itensity_reducedfourier" ] )
       fourier[ nameofstock+"_close_itensity_reducedfourier" ]= np.fft.ifft( fourier[ nameofstock+"_close_itensity_reducedfourier" ] )
       fourier[ nameofstock+"_open_top_reducedfourier" ]      = np.fft.ifft( fourier[ nameofstock+"_open_top_reducedfourier" ] )
       fourier[ nameofstock+"_close_top_reducedfourier" ]     = np.fft.ifft( fourier[ nameofstock+"_close_top_reducedfourier" ] )
       fourier[ nameofstock+"_open_bottom_reducedfourier" ]   = np.fft.ifft( fourier[ nameofstock+"_open_bottom_reducedfourier" ] )
       fourier[ nameofstock+"_close_bottom_reducedfourier" ]  = np.fft.ifft( fourier[ nameofstock+"_close_bottom_reducedfourier" ] )

    return fourier
"""