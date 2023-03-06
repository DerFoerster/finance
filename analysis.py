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

# min-max-distribution
###############################################################################
###############################################################################

"""
directory    = "stocks/"  
  
data,        \
charts,      \
volumes      = readFile( directory )
jumps        = getJumps( data )
#print(jumps)
maxjumps     = maximalJumps( jumps )
#print(maxjumps)
histogram,   \
histpos,     \
histneg      = makeHistogram( maxjumps )
histkeyvalues= determineValues( histogram )
poskeyvalues = determineValues( histpos )
negkeyvalues = determineValues( histneg )
image       = givePlots( histneg, negkeyvalues,  5 ) #binweite anpassen
image       = givePlots( histogram, histkeyvalues,  5 )
"""

# log-log-histogram
###############################################################################
###############################################################################


directory    = "stocks/"  
  
data,        \
charts,      \
volumes      = readFile( directory )
jumps        = getJumps( data )

histogram,   \
histpos,     \
histneg      = makeHistogram( jumps )

loghistneg = { 'dax40': np.log(-histneg['dax40'][histneg['dax40']!=0]) }
loghistpos    = { 'dax40': np.log(histpos['dax40'][histpos['dax40']!=0]) }

histkeyvalues= determineValues( histogram )
poskeyvalues = determineValues( histpos )
negkeyvalues = determineValues( histneg )

lognegkeyvalues = determineValues( loghistneg )
logposkeyvalues = determineValues( loghistpos )


image       = givePlots( loghistneg, lognegkeyvalues,  35,  continuous=True, logarithm=True, name="negative " )
image       = givePlots( loghistpos, logposkeyvalues,  35,  continuous=True, logarithm=True, name="positive " )

image       = givePlots( histneg, negkeyvalues,  2,  continuous=True, logarithm=False, name="negative " ) 
image       = givePlots( histpos, poskeyvalues,  2,  continuous=True, logarithm=False, name="positive " )


# log-log-maxjump-histogram
###############################################################################
###############################################################################

"""
directory    = "stocks/"  
  
data,        \
charts,      \
volumes      = readFile( directory )
jumps        = getJumps( data )
#print(jumps)
maxjumps     = maximalJumps( jumps )
#print(maxjumps)
histogram,   \
histpos,     \
histneg      = makeHistogram( maxjumps )

loghistneg = { 'dax40': -np.log(-histneg['dax40'][histneg['dax40']<0]) }
loghist    = { 'dax40': -np.log(-histogram['dax40'][histogram['dax40']!=0]) }

histkeyvalues= determineValues( histogram )
poskeyvalues = determineValues( histpos )
negkeyvalues = determineValues( histneg )

lognegkeyvalues = determineValues( loghistneg )
logkeyvalues    = determineValues( loghistneg )


image       = givePlots( histneg, lognegkeyvalues,  5,  continuous=False, logarithm=True  ) #binweite anpassen
image       = givePlots( loghist, logkeyvalues,  5, logarithm=True, continuous=False )
"""

