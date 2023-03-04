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
 

# Change in histogram over moving intervals
###############################################################################    
###############################################################################
samples      = 1000
directory    = "stocks/"  
  
data,        \
charts,      \
volumes      = readFile( directory )

jumps        = getJumps( data )



for i in range(2*samples, np.size(jumps["dax40"]), samples ):
    print(i)
    histogram,   \
    histpos,     \
    histneg      = makeHistogram( {"dax40": jumps["dax40"][ i : i+samples ] } )
        
    params = scp.stats.dgamma.fit( histogram["dax40"] ) 
#    arg    = params[:-2]
#    loc    = params[ -2]
#    scale  = params[ -1]
  
    histkeyvalues = determineValues( histogram )
#    poskeyvalues = determineValues( histpos )
#    negkeyvalues = determineValues( histneg )
  
    pdf, q99, q90, q75, q50, q25, q10 \
           = makeDensity( 
                          scp.stats.dgamma, 
                          params,
                          -100,#histkeyvalues["dax40"]["minimum"],
                          100#histkeyvalues["dax40"]["maximum"]
                          )    
           
    #plt.figure()
    paramname = (scp.stats.dgamma.shapes + ', loc, scale').split(', ') if scp.stats.dgamma.shapes else ['loc', 'scale']
    paramets  = ', '.join(['{}={:0.2f}'.format(k,v) for k,v in zip(paramname, params)])
    distname  = '{}{}({})'.format(scp.stats.dgamma.name, paramets, i)

    plt.hist(jumps["dax40"][ i : i+samples ], bins=200, label=str(i) )   
    plt.legend()   
    plt.show()
    #counts, bins = np.histogram(jumps["dax40"][ i : i+samples ])
    #plt.hist(bins[:-1], bins, weights=counts)
"""    pdf.plot( 
              linewidth       = 2, 
              label           = distname, 
              legend          = True, 
              antialiased     = True,
#              color           = 'black',
              )"""

#    image       = givePlots( histneg, negkeyvalues ) #binweite anpassen   
#    image       = givePlots( histogram, histkeyvalues )


