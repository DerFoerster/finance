#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  9 06:00:45 2023

@author: robin
"""

# own modules
from modules.inout import *
from modules.histogram  import *
from modules.smoothers import *
from modules.dependencies import *
from modules.models import *

# general modules
import os
import numpy as np
import scipy as scp
import pandas as pd
import matplotlib.pyplot as plt
from multiprocessing import Pool
os.system("taskset -p 0xff %d" % os.getpid())

import time
#import multiprocessing


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
 


# Test for reading
###############################################################################    
###############################################################################
"""
directory    = "stocks/"    

data,        \
charts,      \
volumes      = readFile( directory )

x            = range( 0, np.size( charts["dax40"] ) )
plt.plot(x,charts["dax40"])

y            = range( 0, np.size( charts["sp500"] ) )
plt.plot(y,charts["sp500"])
"""

"""
maxchart     = 10*np.min( charts["dax40"] )
maxvolume    = np.max(          data["dax40"]["Volume"] )

y            = range( 0, np.size( volumes["dax40"] ) )

yimage       = volumes["dax40"]

yimage      *= maxchart/maxvolume
plt.plot(y,yimage)

plt.show()
"""    



# Test of Histograms 
###############################################################################    
###############################################################################
"""
directory    = "stocks/"  
  
data,        \
charts,      \
volumes      = readFile( directory )

jumps        = getJumps( data )

histogram,   \
histpos,     \
histneg      = makeHistogram( jumps )

histkeyvalues= determineValues( histogram )
poskeyvalues = determineValues( histpos )
negkeyvalues = determineValues( histneg )

image       = givePlots( histneg, negkeyvalues,  5 ) #binweite anpassen

image       = givePlots( histogram, histkeyvalues,  5 )
"""



# Test of maximal jumps
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



# Test of Fouriertransformation
###############################################################################    
###############################################################################
# one can see the influence of low frequencies in the chart
#  one can see the influence of high frequencies in the chart
# based on the shift of the itensity-reduced campared to the original chart one can see the influence of high itensity frequencies in the chart
# dies liegt daran, dass trotzdass wenig punkte im spektrum entfernt werden viel im rücktransformierten verloren geht.
"""
directory    = "stocks/"    
data, \
charts, \
volumes      = readFile( directory, ".csv" )

reductioncoef= 0.99
reductionval = 100

fourier,                \
topreduced_fourier,     \
bottomreduced_fourier,  \
itensityreduced_fourier = computeFouriertrafo( charts , reductioncoef, reductionval )

x            = range(0,np.size(charts["dax40"]))
plt.plot(x,charts["dax40"], label="original chart")

y            = range(0,np.size(topreduced_fourier["dax40"]))
#plt.plot(y,np.abs(topreduced_fourier["dax40"]), label="top reduced: >= "+str(reductioncoef)+"*maxfrequency")

z            = range(0,np.size(bottomreduced_fourier["dax40"]))
plt.plot(z, np.abs( bottomreduced_fourier["dax40"] ),   label="absolute of bottom reduced: <= "  +str(reductioncoef)+"*maxfrequency")
plt.plot(z,        bottomreduced_fourier["dax40"].real, label="real of bottom reduced: <= "      +str(reductioncoef)+"*maxfrequency")
plt.plot(z,        bottomreduced_fourier["dax40"].imag, label="imaginary of bottom reduced: <= " +str(reductioncoef)+"*maxfrequency")
 
a            = range(0,np.size(itensityreduced_fourier[ "dax40" ])) 
#plt.plot(a,np.abs(itensityreduced_fourier["dax40"]), label="itensity reduced: <="+str(reductionval) )

#plt.plot(x,np.abs(fourier["dax40"]))

plt.legend()
plt.show()
"""



# Test of Smoother
###############################################################################    
###############################################################################
"""
directory    = "stocks/"    
data, charts = readFile( directory )

x            = range(0,np.size(charts["dax40"]))

plt.plot(x,charts["dax40"])

smooth       = smoothChart( charts, kindofsmoother=1, expopower=-2 ) #rectangle
y            = range(0,np.size(smooth["dax40"]))
#z            = range(0,np.size(smooth["dax40_volume"]))

plt.plot(y,smooth["dax40"])


#plt.plot(z,smooth["dax40_volume"])
#plt.show()
#smooth       = smoothChart( charts, kindofsmoother=4, expopower=2 ) #gaussian
#z            = range(0,np.size(smooth["dax40"]))

#plt.plot(z,smooth["dax40"])

plt.show()
"""



# Test of Correlations
###############################################################################    
###############################################################################
"""
directory    = "stocks/"    

data,        \
charts,      \
volumes      = readFile( directory )

singlekeyvalues         = determineValues ( charts )

fourier,                \
topreduced_fourier,     \
bottomreduced_fourier,  \
itensityreduced_fourier = computeFouriertrafo( charts )

autocorrelations       = autoCorrelation(charts, fourier, singlekeyvalues)

x            = range(0,np.size(autocorrelations["dax40"]))
plt.plot(x,autocorrelations["dax40"])

pearson,     \
spearman,    \
kendall      = correlationMatrix( charts )

#printHeatmap( pearson )
#printHeatmap( spearman )
#printHeatmap( kendall )

#print(pearson)
#print(kendall)
#print(spearman)
"""



"""
# Test of Black-Scholes
###############################################################################    
###############################################################################
plt.figure()
for i in range(1,1000):
    x, y = sdeBlackScholes( 
                            expectancy = 1, 
                            volatility  = 1, 
                            u0          = 10, 
                            dt          = 0.0001, 
                            tmin        = 0, 
                            tmax        = 1 
                            )    
    plt.plot( x, y )
plt.show()



# Test of Ornstein-Uhlenbeck
###############################################################################    
###############################################################################
plt.figure()
for i in range(1,1000):
    x, y = sdeOrnsteinUhlenbeck( 
                            expectancy = 1, 
                            volatility  = 1, 
                            u0          = 10, 
                            dt          = 0.0001, 
                            tmin        = 0, 
                            tmax        = 1 
                            )    
    plt.plot( x, y )
plt.show()
"""


# Test of Arch
###############################################################################    
###############################################################################
"""
directory = "stocks/"  
interval  = 100  

data,     \
charts,   \
volumes   = readFile( directory )

daxlength = np.size( charts["dax40"] )

daxclose  = charts["dax40"][ daxlength-100 :  ]

plt.figure()
for i in range(1,1000):
    print(i)
    x, y = sdeArch( 
                    volatility  = 1, 
                    u0          = daxclose, 
                    dt          = 0.001, 
                    tmin        = 0, 
                    tmax        = 1 
                    )    
    plt.plot( x, y )
plt.show()
"""


# Test of RArch
###############################################################################    
###############################################################################
# weights are not fitted
# how does dirst change if one varies interval ( [t,t+h] or [t_1. t_2] ) and are jumps stationary or independent?

# Parameters
directory = "stocks/"  
interval  = 1

# Reading file
data,     \
charts,   \
volumes   = readFile( directory )

# Get jumps
jumps        = getJumps( data )

# Compute histogram
histogram,   \
histpos,     \
histneg      = makeHistogram( jumps )

# get variance and stuff
histkeyvalues  = determineValues( histogram )
chartkeyvalues = determineValues( charts )

"""
# Fit distribution to histogram
ordereddistibutions = fitDistribution( 
                                        charts["dax40"],#histogram    ["dax40"], 
                                        chartkeyvalues["dax40"]["minimum"],#histkeyvalues["dax40"]["minimum"],
                                        chartkeyvalues["dax40"]["minimum"],#histkeyvalues["dax40"]["maximum"], 
                                        binwidth = 50,
                                        progres  = True
                                        )       
bestdist  = ordereddistibutions[0]

paramname = (bestdist[0].shapes + ', loc, scale').split(', ') if bestdist[0].shapes else ['loc', 'scale']
paramets  = ', '.join(['{}={:0.2f}'.format(k,v) for k,v in zip(paramname, bestdist[1])])

print( '{}({})'.format(bestdist[0].name, paramets) )
"""# Outcome of fitting:
# for jumps:  dgamma(a=0.45, loc=-0.00, scale=82.62)
# for charts: ksone(n=1.00, loc=-586.89, scale=16858.64)
# part of scipy.stats
# for jumps:  dgamma.rvs(a, loc=0, scale=1, size=1)
# for charts: ksone(n=1.00, loc=-586.89, scale=16858.64)


#x = range(-100, 100)
#print( x, scp.stats.dgamma.pdf(x, a=0.45, loc=-0.00, scale=82.62))

# Extract initial data
daxlength = np.size( charts["dax40"] )
daxclose  = charts["dax40"][ daxlength-interval :  ]

#plt.figure()
#plt.plot( range(0,1000), daxclose)
#plt.show()
#print(chartkeyvalues["dax40"]["mean"])

#compute 1000 testruns and print
     
plt.figure()  
for i in range(1,50):
    print(i)
    x, y = sdeRarch_5( 
                    volatility   = histkeyvalues["dax40"]["variance"], 
                    initialvalues= daxclose, 
                    weights      = np.ones(interval),
                    w0           = chartkeyvalues["dax40"]["mean"], # use initial/old volatility as w0 and add a minimal changed new one one could use deviation instead and then instead of adding first and tage sqrt: add after sqrt or make geometric mean
                    dt           = 0.001, 
                    tmin         = 0, 
                    tmax         = 10 
                    )    
    plt.plot( x, y )
plt.show()


