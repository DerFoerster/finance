#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created:
    on Fri Dec 30 18:11:45 2022

Contains:
    All functions for plotting and reading files

Author:
    robin
"""


# general modules
import os
import numpy as np
import scipy as scp
import pandas as pd
import matplotlib.pyplot as plt

# for heatmap
import seaborn as sns

# for density

from modules.histogram  import *




# readFile (string: directory, string ending ) = dictionary: data
##############################################################################
# directory:    Name of folder containing all files to read
# ending:       Ending of ile: .csv
# rawdata:      Dictionary of red values
# charts:       Dictionary of charts in total
# folderobject: Contains columns   Date          Open          High           Low         Close

def readFile( directory, ending=".csv"  ):      
    rawdata    = {}
    charts     = {}
    volumes    = {}
    
    print("\n \nMake sure that you havent open your .csv-files anywhere! Otherwise the program may crash! \n\n")
    print("Start reading process:\n")
    
    for file in os.listdir(directory):                                         # Extract filename filename
        folderobjectsname = os.path.join(directory, file)                      # opening object in folder
        
        if os.path.isfile( folderobjectsname ):                                # checking if it is a file
            
            folderobject         = folderobjectsname.replace( directory, "")
            folderobject         = folderobject.replace( ending, "")
            
            rawdata[ folderobject ] = pd.read_csv(folderobjectsname)#, dtype=np.float64)#, parse_dates=['Date']) #folderobjectsname "stocks/dax40.csv"
            
            print( "   " + folderobject+" has been read.")
        
        for column in rawdata:
            #data[column]=data[column].dropna()                                # dismiss NaN how='any' how='all'
            #rawdata[column]      = rawdata[column].fillna('', inplace=True)   # fills empty strings
            rawdata[column]      = rawdata[column].ffill()                     # fills empty columns
            rawdata[column]      = rawdata[column].iloc[::-1]                  # revers sorting
        
       # extracting trading volumes. For printing reasons volumes are doubeled (same volume at open-time as on close-time)
       #_______________________________________________________________________        
        volumes[folderobject]    = pd.concat([
                                                         rawdata[ folderobject ]["Volume"], #"stock_{0}".format(folderobject)
                                                         rawdata[ folderobject ]["Volume"]
                                                         ]).sort_index()      
        
        volumes[folderobject]    = volumes[folderobject].iloc[::-1]
        
       # extracting charts.
       #_______________________________________________________________________           
        charts[folderobject]     = pd.concat([
                                               rawdata[ folderobject ]["Open"], 
                                               rawdata[ folderobject ]["Close"]
                                               ]).sort_index()
        
        charts[folderobject]     = charts[folderobject].iloc[::-1]             # revers sorting
        
    return rawdata, charts, volumes
    




# givePlots ( dictionary: histogram, dictionary: keyvalues, int: binwidth, real: epsilon ) = 0
##############################################################################
# :
# plt.hist(x, bins=None, range=None, density=False, weights=None, cumulative=False, bottom=None, histtype='bar', align='mid', orientation='vertical', rwidth=None, log=False, color=None, label=None, stacked=False, *, data=None, **kwargs)

def givePlots( histogram, keyvalues, binwidth=20, epsilon=0.05, continuous=True, logarithm=False, name="" ):
    
    for index in histogram: 
        
        # often used values
        #__________________________________________________________________  
        minimum = keyvalues[ index ][ "minimum" ]
        maximum = keyvalues[ index ][ "maximum" ]
        median  = keyvalues[ index ][ "median"  ]
        mean    = keyvalues[ index ][ "mean"    ]
        
        # general settings
        #__________________________________________________________________           
        plt.figure( figsize=(24,16) )                                                        #new plot, otherwise all will be in one plot
        plt.title( "Histogram of " + name + "jumps of " + index + "." )
        
        # create bins
        if( logarithm ):
            print( maximum )
            actualbins = np.arange(  
                                int( minimum ),  
                                int( maximum ),  
                                0.0005*binwidth,
                                dtype=np.float
                                ) 
        else:
            actualbins = range(  
                                int( minimum ),  
                                int( maximum ),  
                                binwidth
                                )
        
        # plot histogram
        #__________________________________________________________________ 
        amountofjumps, jumpheight, z \
        = plt.hist( histogram[ index ], 
                    bins     = actualbins,   
                    histtype = 'bar', 
                    density  = True, 
                    label    = "amount of jump heights",
                    color    = list( plt.rcParams['axes.prop_cycle'] )[0]['color'],
                    log      = logarithm,
                    ) 





                                                    
        # find best fitting distribution
        #__________________________________________________________________
        if( continuous ):
            ordereddistibutions = fitDistribution( 
                                                   histogram[ index ], 
                                                   minimum,
                                                   maximum, 
                                                   binwidth,
                                                   progres=True
                                                   )
    
            bestdist  = ordereddistibutions[0]
            paramname = (bestdist[0].shapes + ', loc, scale').split(', ') if bestdist[0].shapes else ['loc', 'scale']
            paramets  = ', '.join(['{}={:0.2f}'.format(k,v) for k,v in zip(paramname, bestdist[1])])
            distname  = '{}({})'.format(bestdist[0].name, paramets)
            
            # plot best fitting distribution
            #__________________________________________________________________           
            pdf, q99, q90, q75, q50, q25, q10 \
            = makeDensity( 
                           bestdist[0], 
                           bestdist[1],
                           minimum,
                           maximum
                           )
            
            #nameofdist = filter(lambda a: bestdist[0] in a, _distn_names)
            
            pdf.plot( 
                      linewidth       = 2, 
                      label           = distname, 
                      legend          = True, 
                      antialiased     = True,
                      color           = 'black'
                      )
            plt.legend(  bbox_to_anchor=( 0.8*epsilon, 0.7) )
            #print(bestdist[0].name)
            
            # plot quantiles
            #___________________________________________________________________
            for quantile in [q99, q90, q75, q50, q25, q10, -q10, -q25, -q50, -q75, -q90, -q99]:
                plt.axvline(
                             x        = np.log(quantile),
                             ymax     = 1,#0.25*np.max(amountofjumps),
                             linestyle='dotted'
                             )     
"""
        # limit & settings of axes
        #__________________________________________________________________  
        ymaximum = np.max(amountofjumps)
        plt.ylim([ 
                    0,  
                   (1+epsilon)*ymaximum
                   ])
        
        tickslimit = max(abs(round(minimum,-2)), abs(round(maximum,-2)))
        
        
        roundingvalue  = np.log10( np.maximum( np.abs(minimum), np.abs(maximum) )) #determines on what the rounding will be out of the maximal abolute value
        roundingvalue -= 1
        roundingvalue  = np.int( round( roundingvalue, 0 )) 
        
        coarsedistance = round( (maximum-minimum)/6 , -roundingvalue )         # -2 means: go to next 100 -3 go to next 1000
        finedistance   = round( (maximum-minimum)/18 , -roundingvalue+1 )      # finer grind in center shall be allowed to use smaller steps
        
        print(coarsedistance)
        print(finedistance)
        print(roundingvalue)
        
        lowerticks = np.arange( 
                                start = round(minimum,-2),
                                stop  = round(0.3*-tickslimit,-2),
                                step  = coarsedistance
                                )
        centerticks= np.arange(
                                start = 0.25*-tickslimit, 
                                stop  = 0, 
                                step  = finedistance
                                )
        upperticks = np.arange( 
                                start = round(0.3*tickslimit,-2), 
                                stop  = maximum, 
                                step  = coarsedistance
                                )
        
        splitticks = np.concatenate((
                                      lowerticks,
                                      centerticks,
                                      -centerticks,
                                      upperticks 
                                      ))
        plt.xticks(splitticks)

        
        plt.xlim([ 
                   (1+epsilon)*minimum,  
                   (1+epsilon)*maximum
                   ])
        
        
        # values as vlines
        #__________________________________________________________________
        plt.axvline( minimum, 
                     color='red', 
                     label='minimal jump: ' + str(round(minimum,2))
                     )  # min       
        plt.axvline( maximum, 
                     color='red', 
                     label='maximal jump: ' + str(round(maximum,2)) 
                     )  # max 
        plt.axvline( median, 
                     color='orange',
                     label='median: '       + str(round(median,2))
                     )  # median
        plt.axvline( mean, 
                     color='pink',
                     label='mean: '         + str(round(mean,2))
                     )  # mean
        #plt.axvline() 
        
        # values as numbers
        #__________________________________________________________________
        plt.text( (1-epsilon)*minimum,   0.5*ymaximum, 
                  " standard deviation: ".format( int( keyvalues[ index ][ "deviation" ]))
                  +"\n"+
                  " variance: {}".format( int( keyvalues[ index][ "variance" ]))
                  )    
                                                        # todo x and y automatically"""      

           

              





# printHeatmap ( ndarray: correlation )
##############################################################################
def printHeatmap( correlation ):
    
    # Generate a mask for the upper triangle
    #__________________________________________________________________________
    mask = np.triu(np.ones_like(correlation, dtype=bool))
    
    # Set up the matplotlib figure
    #__________________________________________________________________________
    f, ax = plt.subplots(figsize=(11, 9))
    
    # Generate a custom diverging colormap
    #__________________________________________________________________________
    cmap = sns.diverging_palette(
                                  h_neg   = 45,#359, 
                                  h_pos   = 250,#100,
                                  s       = 250, #saturation of both ends
                                  l       = 50, #lightness of both ends
                                  sep     = 1, #intermediate region
                                  center  = "dark", 
                                  as_cmap = True
                                  )
    
    # Draw the heatmap with the mask and correct aspect ratio
    #__________________________________________________________________________
    sns.heatmap(
                 correlation, 
                 mask       = mask, 
                 cmap       = cmap,
                 vmax       = .3, 
                 center     = 0,
                 square     = True, 
                 linewidths = .5, 
                 annot      = True, #values in heatmap
                 cbar_kws   = {"shrink": .5}
                 )    













