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
 


# Test for reading
###############################################################################    
###############################################################################
"""
directory    = "stocks/"    
data, charts = readFile( directory )

x            = range( 0, np.size( charts["dax40"] ) )
plt.plot(x,charts["dax40"])

y            = range( 0, np.size( charts["sp500"] ) )
plt.plot(y,charts["sp500"])
"""

"""
maxchart     = 10*np.min( charts["dax40"] )
maxvolume    = np.max(          data["stock_dax40"]["Volume"] )

y            = range( 0, np.size( charts["dax40_volume"] ) )

yimage       = charts["dax40_volume"]

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
#"""
directory    = "stocks/"  
  
data,        \
charts,      \
volumes      = readFile( directory )

jumps        = getJumps( data )
#print(jumps)

maxjumps     = maximalJumps( jumps )
#print(maxjumps)
#"""
histogram,   \
histpos,     \
histneg      = makeHistogram( maxjumps )

histkeyvalues= determineValues( histogram )
poskeyvalues = determineValues( histpos )
negkeyvalues = determineValues( histneg )

image       = givePlots( histneg, negkeyvalues,  5 ) #binweite anpassen

image       = givePlots( histogram, histkeyvalues,  5 )
#"""



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
data,   \
charts, \
volumes      = readFile( directory )

singlekeyvalues         = determineValues ( charts )

fourier,                \
topreduced_fourier,     \
bottomreduced_fourier,  \
itensityreduced_fourier = computeFouriertrafo( charts )

#autocorrelations        = autoCorrelation(charts, fourier, singlekeyvalues)

#x            = range(0,np.size(autocorrelations["dax40"]))
#plt.plot(x,autocorrelations["dax40"])

pearson,  \
spearman, \
kendall = correlationMatrix( charts )

printHeatmap( pearson )
printHeatmap( spearman )
printHeatmap( kendall )

#print(pearson)
#print(kendall)
#print(spearman)
"""






















"""Old structure with open and close instead on working with the whole chart
directory    = "stocks/"    
data, charts = readFile( directory, ".csv" )

reductioncoef= 0.99
reductionval = 100


fourier      = computeFouriertrafo( data , reductioncoef, reductionval )

x            = range(0,np.size(data["stock_dax40"]["Open"]))
plt.plot(x,data["stock_dax40"]["Open"], label="original chart")

y            = range(0,np.size(fourier["dax40_open_top_reducedfourier"]))
#plt.plot(y,np.abs(fourier["dax40_open_top_reducedfourier"]), label="top reduced: >= "+str(reductioncoef)+"*maxfrequency")

z            = range(0,np.size(fourier["dax40_open_bottom_reducedfourier"]))
plt.plot(z,np.abs(fourier["dax40_open_bottom_reducedfourier"]), label="absolute of bottom reduced: <= "+str(reductioncoef)+"*maxfrequency")
plt.plot(z,fourier["dax40_open_bottom_reducedfourier"].real, label="real of bottom reduced: <= "+str(reductioncoef)+"*maxfrequency")
plt.plot(z,fourier["dax40_open_bottom_reducedfourier"].imag, label="imaginary of bottom reduced: <= "+str(reductioncoef)+"*maxfrequency")

a            = range(0,np.size(fourier[ "dax40_open_itensity_reducedfourier" ])) 
#plt.plot(a,np.abs(fourier["dax40_open_itensity_reducedfourier"]), label="itensity reduced: <="+str(reductionval) )

#plt.plot(x,np.abs(fourier["dax40_open_discretefourier"]))

plt.legend()
plt.show()
"""



"""




# fitDistribution ( data, real: minimum, real: maximum, real: binwidth, ax=None )
##############################################################################
# :
 
def fitDistribution(data, minimum, maximum, binwidth=20):#, ax=None):
    "Model data by finding best fit distribution to data"
    # Get histogram of original data
    y, x = np.histogram(data,  bins=range( int(minimum),int(maximum),binwidth),  density=True)
    x = (x + np.roll(x, -1))[:-1] / 2.0

    # Best holders
    bestdistributions = []

    #open parallel computing
    with Pool() as pool:
        
        distributionlist = enumerate([d for d in _distn_names if not d in ['levy_stable', 'studentized_range']])
        
        for distribution in pool.map( fastFitting(data, distributionlist, x, y) ):
            
            sse, params = fastFitting( data, distribution, x, y )
            
            # identify if this distribution is better
            bestdistributions.append((distribution, params, sse))
    
    return sorted(bestdistributions, key=lambda x:x[2])
   
   








# fastFitting ( data, real: minimum, real: maximum, real: binwidth, ax=None )
##############################################################################
# :

def fastFitting( data, distribution, x, y ): 

        # Estimate distribution parameters from data
    
        print(distribution, " is tested.")
        print(type(distribution))
        #distribution = getattr(st, distribution)
        #print(type(data))
        #params = distribution.fit(data)
        # Try to fit the distribution
#        try:
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
                
                # if axis pass in add to plot
#                try:
#                    if ax:
#                        pd.Series(pdf, x).plot(ax=ax)
#                    end
#                except Exception:
#                    pass

#        except Exception:
            #print(Exception)
#            pass
            
        return sse, params
    









"""
