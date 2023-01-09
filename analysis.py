#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created:
    on Fri Dec 30 18:11:45 2022

Contains:
    Main program
    testcases

Author:
    robin
"""


# own modules
from modules.inout import *
from modules.histogram  import *
from modules.smoothers import *
from modules.dependencies import *

# general modules
import os
import numpy as np
import scipy as scp
import pandas as pd
import matplotlib.pyplot as plt



""" 
fehlerhandling
differenzenchart der Sprünge: Abwärts - aufwärts, 
Vergleichender Chart: Sprünge aufwärts-sprünge abwärts
Exponentiell abfallende tails?
beschleunigen, indem beim plotten nicht jeder scheiß 5x ausgelesen wird.

smoother: mehrere optionen:
x   1. integer, der einem erlaubt die Art der glättung auszuwählen
    2. rechne alle glättungsarten aus
x   a. übergabe der glättungsfunktion je nach integer
    b. rechne alles direkt in der funktion aus

verlustrisiko des prozesses

fourier
 - rücktrafo ohne hohe frequenzen
 - fourier-glätten
 
parallelisieren:
 - smoother
 - fitting

abtrag über daten

längenprobleme bei plot der charts, korrelation

ändere die ausgabe der werte in hist in ein zweites dictionary:singlekeyvalues
ändere die aufrufstruktur in ein allgemeinere: aktuell wird alles auf open und close gerechnet, 
mehr dictionarys mit jeweils nur einem inhaltstyp, sprich eins mit open-kursen, eines mit den histogrammen, 
eines mit den charts, einesm it den volume-dingsis

aber außer das sprunghistogram sollte eigentlich alles auf dem chart gerechnet werden.

heatmap
correlationsmatrix
ausgabe mit datum
"""

#
###############################################################################
###############################################################################

# parameters
#______________________________________________________________________________
directory    = "stocks/"  
interval     = 1000

# reading and extracting jumps
#______________________________________________________________________________  
data,        \
charts,      \
volumes      = readFile( directory )

jumps        = getJumps( data )


for index in jumps:
    # variables for storing
    #__________________________________________________________________________    
    variancevector = []
    posvarvector   = []
    negvarvector   = []
    
    densityvector  = []
    posdensvector  = []
    negdensvector  = []  
  
    jumpsize = np.size( jumps[index] )

    for i in range( 0, jumpsize, interval ):
       # progres
       #_______________________________________________________________________
       print( "   {} % of {}-index".format( np.round( 100*i/jumpsize, 2 ), index ) )
       
            
       # computing histogram of interval
       #_______________________________________________________________________
       histogram,   \
       histpos,     \
       histneg      = makeHistogram( { index : jumps[index][i:(i+1)*interval ] } )         
       #makeHistogram accepts only dictionaries. Therefore overgive dictionary built of last N jumps


       # computing keyvalues of interval
       #_______________________________________________________________________      
       histkeyvalues = determineValues( histogram )                            # keyvalues of last N jumps#
       poskeyvalues  = determineValues( histpos )
       negkeyvalues  = determineValues( histneg )
       
       
       # storing variances of interval
       #_______________________________________________________________________
       variancevector.append( histkeyvalues[index]["variance"] )               # variance of last N jumps#
       posvarvector.append(   poskeyvalues [index]["variance"] )
       negvarvector.append(   negkeyvalues [index]["variance"] )    

        
       # computing distribution of interval
       #_______________________________________________________________________
       ordereddistibutions = fitDistribution( 
                                               histogram[ index ], 
                                               histkeyvalues[index]["minimum"],
                                               histkeyvalues[index]["maximum"], 
                                               binwidth = 50,
                                               progres=False
                                               )       
       bestdist  = ordereddistibutions[0]    
       
       ordereddistibutions = fitDistribution( 
                                               histpos[ index ], 
                                               poskeyvalues [index]["minimum"],
                                               poskeyvalues [index]["maximum"], 
                                               binwidth = 50,
                                               progres=False
                                               )       
       posdist  = ordereddistibutions[0]
       
       ordereddistibutions = fitDistribution( 
                                               histneg[ index ], 
                                               negkeyvalues [index]["minimum"],
                                               negkeyvalues [index]["maximum"], 
                                               binwidth = 50,
                                               progres=False
                                               )       
       negdist  = ordereddistibutions[0]      
       
       
       # computing density of distribution
       #_______________________________________________________________________
       pdf = makeDensity( 
                          bestdist[0], 
                          bestdist[1],
                          histkeyvalues[index]["minimum"],
                          histkeyvalues[index]["maximum"],
                          quantiles=False
                          )
       posdf = makeDensity( 
                          posdist[0], 
                          posdist[1],
                          poskeyvalues[index]["minimum"],
                          poskeyvalues[index]["maximum"],
                          quantiles=False
                          )
       
       negdf = makeDensity( 
                          negdist[0], 
                          negdist[1],
                          negkeyvalues[index]["minimum"],
                          negkeyvalues[index]["maximum"],
                          quantiles=False
                          )


       # storing density
       #_______________________________________________________________________
       densityvector.append( pdf   )
       posdensvector.append( posdf )
       negdensvector.append( negdf )
       


       

    # plotting variances
    #__________________________________________________________________________   
    variancevector = np.array( variancevector )
    posvarvector   = np.array( posvarvector )
    negvarvector   = np.array( negvarvector )    
    
    x = np.arange( 0, jumpsize, interval )
    
    y = range( 0, np.size( volumes["dax40"] ) )

    plt.figure()
    plt.plot( x, variancevector )
    plt.plot( x, posvarvector )
    plt.plot( x, negvarvector )
    
    plt.plot( y, charts["dax40"] )
    
    plt.title( "variances of {} in intervals of size {}".format( index, interval ) )
    plt.show()
    
 
    # plotting densities
    #__________________________________________________________________________   
    plt.figure()
    for pdf in densityvector:

        pdf.plot( 
                  linewidth       = 2, 
                  #label           = distname, 
                  #legend          = True, 
                  antialiased     = True,
                  color           = 'black'
                  )
    plt.show()
    
    plt.figure()
    for pdf in posdensvector:
        pdf.plot( 
                  linewidth       = 2, 
                  #label           = distname, 
                  #legend          = True, 
                  antialiased     = True,
                  color           = 'black'
                  )
    plt.show() 

    plt.figure()
    for pdf in negdensvector:
        pdf.plot( 
                  linewidth       = 2, 
                  #label           = distname, 
                  #legend          = True, 
                  antialiased     = True,
                  color           = 'black'
                  )
    plt.show()

