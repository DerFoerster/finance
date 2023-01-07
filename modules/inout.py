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
    
    for file in os.listdir(directory):                          # Extract filename filename
        folderobjectsname = os.path.join(directory, file)       # opening object in folder
        
        if os.path.isfile( folderobjectsname ):                 # checking if it is a file
            
            folderobject         = folderobjectsname.replace( directory, "")
            folderobject         = folderobject.replace( ending, "")
            
            rawdata[ folderobject ] = pd.read_csv(folderobjectsname)#, dtype=np.float64)#, parse_dates=['Date']) #folderobjectsname "stocks/dax40.csv"
            
            print( "   " + folderobject+" has been read.")
        
        for column in rawdata:
            #data[column]=data[column].dropna()  #dismiss NaN how='any' how='all'
            #rawdata[column]      = rawdata[column].fillna('', inplace=True) #fills empty strings
            rawdata[column]      = rawdata[column].ffill() #fills empty columns
            rawdata[column]      = rawdata[column].iloc[::-1]#revers sorting
        
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
        
        charts[folderobject]     = charts[folderobject].iloc[::-1]#revers sorting
        
    return rawdata, charts, volumes
    




# givePlots ( dictionary: histogram, dictionary: keyvalues, int: binwidth, real: epsilon ) = 0
##############################################################################
# :
# plt.hist(x, bins=None, range=None, density=False, weights=None, cumulative=False, bottom=None, histtype='bar', align='mid', orientation='vertical', rwidth=None, log=False, color=None, label=None, stacked=False, *, data=None, **kwargs)

def givePlots( histogram, keyvalues, binwidth=20, epsilon=0.05 ):
    
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
        plt.title( "Histogram of jumps of " + index + "." )
        
        # plot histogram
        #__________________________________________________________________ 
        amountofjumps, jumpheight, z \
        = plt.hist( histogram[ index ], 
                    bins=range(  
                                int( minimum ),  
                                int( maximum ),  
                                binwidth
                    ),   
                    histtype='bar', 
                    density=True, 
                    label="amount of jump heights",
                    color=list(plt.rcParams['axes.prop_cycle'])[0]['color']
                    ) # \ line continuing as optival sugar



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
        
        coarsedistance = round( (maximum-minimum)/6 , -roundingvalue ) #-2 means: go to next 100 -3 go to next 1000
        finedistance   = round( (maximum-minimum)/18 , -roundingvalue+1 ) #finer grind in center shall be allowed to use smaller steps
        
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
                  " standard deviation: "+str(int( keyvalues[ index ][ "deviation" ]))+"\n"+
                  " variance: "+str(int( keyvalues[ index][ "variance"]))
                  ) #todo x and y automatically

        # find best fitting distribution
        #__________________________________________________________________
        ordereddistibutions = fitDistribution( 
                                               histogram[ index ], 
                                               minimum,
                                               maximum, 
                                               binwidth
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
                         x        = quantile,
                         ymax     = 1,#0.25*np.max(amountofjumps),
                         linestyle='dotted'
                         )           
           

"""
           # plot quantiles
           #___________________________________________________________________
           for quantile in [-q10, -q99, -q90, -q75, -q50, -q25]:
               plt.axvline(
                            x        = quantile,
                            ymax     = 1,#0.25*np.max(amountofjumps),
                            linestyle='dotted'
                            )           
"""           
           

           








# printHeatmap ( ndarray: correlation )
##############################################################################
def printHeatmap( correlation ):
    
    # Generate a mask for the upper triangle
    mask = np.triu(np.ones_like(correlation, dtype=bool))
    
    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(11, 9))
    
    # Generate a custom diverging colormap
    cmap = sns.diverging_palette(
                                  h_neg=45,#359, 
                                  h_pos=250,#100,
                                  s=250, #saturation of both ends
                                  l=50, #lightness of both ends
                                  sep=1, #intermediate region
                                  center="dark", 
                                  as_cmap=True
                                  )
    
    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(
                 correlation, 
                 mask=mask, 
                 cmap=cmap,
                 vmax=.3, 
                 center=0,
                 square=True, 
                 linewidths=.5, 
                 annot=True, #values in heatmap
                 cbar_kws={"shrink": .5}
                 )    






"""
# givePlots ( dictionary: histogram, dictionary: keyvalues, int: binwidth, real: epsilon ) = 0
##############################################################################
# :
# plt.hist(x, bins=None, range=None, density=False, weights=None, cumulative=False, bottom=None, histtype='bar', align='mid', orientation='vertical', rwidth=None, log=False, color=None, label=None, stacked=False, *, data=None, **kwargs)

def givePlots( histogram, keyvalues, binwidth=20, epsilon=0.05 ):
    
    for index in histogram: #iterates over index - an element of dictionary rawdata 
       nameofstock = data[:data.index("_")]

       if data.find('positive') != -1:
           # often used values
           #__________________________________________________________________  
           minimum = 0
           maximum = editeddata[ nameofstock+"_values" ]["maximum"]
           median  = editeddata[ nameofstock+"_values" ]["median_pos"]
           mean    = editeddata[ nameofstock+"_values" ]["mean_pos"]
           
           # general settings
           #__________________________________________________________________           
           plt.figure( figsize=(24,16) )                                                        #new plot, otherwise all will be in one plot
           plt.title( "Histogram of positive jumps" )
           
           # plot histogram
           #__________________________________________________________________ 
           amountofjumps, jumpheight, z \
           = plt.hist( editeddata[ data ], 
                       bins=range(  
                                   int( minimum ),  
                                   int( maximum ),  
                                   binwidth
                       ),   
                       histtype='bar', 
                       density=True, 
                       label="amount of jump heights",
                       color=list(plt.rcParams['axes.prop_cycle'])[0]['color']
                       ) # \ line continuing as optival sugar

           # limit & settings of axes
           #__________________________________________________________________  
           ymaximum = np.max(amountofjumps)
           
           plt.ylim([ 
                       0,  
                      (1+epsilon)*ymaximum
                      ])
           
           tickslimit = round(maximum,-2)
           
           centerticks= np.arange(
                                   start = 0, 
                                   stop  = 0.25* tickslimit, 
                                   step  = 50
                                   )
           upperticks = np.arange( 
                                   start = round(0.25*tickslimit,-2), 
                                   stop  = maximum, 
                                   step  = 100
                                   )
           
           splitticks = np.concatenate((
                                         centerticks,
                                         upperticks 
                                         ))
           plt.xticks(splitticks)

           
           plt.xlim([ 
                      (1+epsilon)*minimum,  
                      (1+epsilon)*maximum
                      ])
           
           
           # values as vlines
           #__________________________________________________________________
           plt.axvline( maximum, 
                        color='red', 
                        label='maximal positive jump: ' + str(round(maximum,2)) 
                        )                                          # max 
           plt.axvline( median, 
                        color='orange',
                        label='median: '+str(round(median,2))
                        )  # median
           plt.axvline( mean, 
                        color='pink',
                        label='mean: '+str(round(mean,2))
                        )     # mean=expectancy
           #plt.axvline() 
           
           # values as numbers
           #__________________________________________________________________
           plt.text( (1-epsilon)*minimum,   0.5*ymaximum, 
                     " standard deviation: "+str(int(editeddata[ nameofstock+"_values" ]["deviation_pos"]))+"\n"+
                     " variance: "+str(int(editeddata[ nameofstock+"_values" ]["secondmoment_pos"]))
                     ) #todo x and y automatically

           # find best fitting distribution
           #__________________________________________________________________
           ordereddistibutions = fitDistribution( 
                                                  editeddata[data], 
                                                  minimum,
                                                  maximum, 
                                                  binwidth
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
           for quantile in [q99, q90, q75,q50, q25, q10]:
               plt.axvline(
                            x        = quantile,
                            ymax     = 1,#0.25*np.max(amountofjumps),
                            linestyle='dotted'
                            )           
           
           
           
            
            
            
            
            
            
            
           
       if data.find('negative') != -1:
           # often used values
           #__________________________________________________________________  
           minimum = editeddata[ nameofstock+"_values" ]["minimum_neg"]
           maximum = 0
           median  = editeddata[ nameofstock+"_values" ]["median_neg"]
           mean    = editeddata[ nameofstock+"_values" ]["mean_neg"]
           
           # general settings
           #__________________________________________________________________           
           plt.figure( figsize=(24,16) )                                                        #new plot, otherwise all will be in one plot
           plt.title( "Histogram of all negative jumps" )
           
           # plot histogram
           #__________________________________________________________________ 
           amountofjumps, jumpheight, z \
           = plt.hist( editeddata[ data ], 
                       bins=range(  
                                   int( minimum ),  
                                   int( maximum ),  
                                   binwidth
                       ),   
                       histtype='bar', 
                       density=True, 
                       label="amount of jump heights",
                       color=list(plt.rcParams['axes.prop_cycle'])[0]['color']
                       ) # \ line continuing as optival sugar

           # limit & settings of axes
           #__________________________________________________________________  
           ymaximum = np.max(amountofjumps)
           
           plt.ylim([ 
                       0,  
                      (1+epsilon)*ymaximum
                      ])
           
           tickslimit = abs(round(minimum,-2))
           
           lowerticks = np.arange( 
                                   start = round(minimum,-2),
                                   stop  = round(0.25*-tickslimit,-2),
                                   step  = 100
                                   )
           centerticks= np.arange(
                                   start = 0.25*-tickslimit, 
                                   stop  = 0, 
                                   step  = 50
                                   )
           
           splitticks = np.concatenate((
                                         lowerticks,
                                         centerticks,
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
                        label='minimal negative jump: '+ str(round(editeddata[ nameofstock+"_values" ]["minimum_neg"],2)) 
                        )               # min                                       # max
           plt.axvline( median, 
                        color='orange',
                        label='median: '+str(round(median,2))
                        )  # median
           plt.axvline( mean, 
                        color='pink',
                        label='mean: '+str(round(mean,2))
                        )     # mean=expectancy
           #plt.axvline() 
           
           # values as numbers
           #__________________________________________________________________
           plt.text( (1-epsilon)*minimum,   0.5*ymaximum, 
                     " standard deviation: "+str(int(editeddata[ nameofstock+"_values" ]["deviation"]))+"\n"+
                     " variance: "+str(int(editeddata[ nameofstock+"_values" ]["secondmoment"]))
                     ) #todo x and y automatically

           # find best fitting distribution
           #__________________________________________________________________
           ordereddistibutions = fitDistribution( 
                                                  editeddata[data], 
                                                  minimum,
                                                  maximum, 
                                                  binwidth
                                                  )
           #print(ordereddistibutions)
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
           plt.legend(  bbox_to_anchor=( 1.5*epsilon, 0.7) )
           #print(bestdist[0].name)
           
           # plot quantiles
           #___________________________________________________________________
           for quantile in [-q10, -q99, -q90, -q75, -q50, -q25]:
               plt.axvline(
                            x        = quantile,
                            ymax     = 1,#0.25*np.max(amountofjumps),
                            linestyle='dotted'
                            )           
           
           
           
            
            
            
            
            
            
            
            
            
           
          
       if data.find('total') != -1: #todo: subplotfunction for all extra-stuff in plot #todo fitting function
           # often used values
           #__________________________________________________________________  
           minimum = editeddata[ nameofstock+"_values" ]["minimum"]
           maximum = editeddata[ nameofstock+"_values" ]["maximum"]
           median  = editeddata[ nameofstock+"_values" ]["median"]
           mean    = editeddata[ nameofstock+"_values" ]["mean"]
           
           # general settings
           #__________________________________________________________________           
           plt.figure( figsize=(24,16) )                                                        #new plot, otherwise all will be in one plot
           plt.title( "Histogram of all jumps" )
           
           # plot histogram
           #__________________________________________________________________ 
           amountofjumps, jumpheight, z \
           = plt.hist( editeddata[ data ], 
                       bins=range(  
                                   int( minimum ),  
                                   int( maximum ),  
                                   binwidth
                       ),   
                       histtype='bar', 
                       density=True, 
                       label="amount of jump heights",
                       color=list(plt.rcParams['axes.prop_cycle'])[0]['color']
                       ) # \ line continuing as optival sugar

           # limit & settings of axes
           #__________________________________________________________________  
           ymaximum = np.max(amountofjumps)
           
           plt.ylim([ 
                       0,  
                      (1+epsilon)*ymaximum
                      ])
           
           tickslimit = max(abs(round(minimum,-2)), abs(round(maximum,-2)))
           
           lowerticks = np.arange( 
                                   start = round(minimum,-2),
                                   stop  = round(0.3*-tickslimit,-2),
                                   step  = 200
                                   )
           centerticks= np.arange(
                                   start = 0.25*-tickslimit, 
                                   stop  = 0.25* tickslimit, 
                                   step  = 100
                                   )
           upperticks = np.arange( 
                                   start = round(0.3*tickslimit,-2), 
                                   stop  = maximum, 
                                   step  = 200
                                   )
           
           splitticks = np.concatenate((
                                         lowerticks,
                                         centerticks,
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
                        label='minimal jump: '+ str(round(minimum,2)) 
                        )               # min
           plt.axvline( maximum, 
                        color='red', 
                        label='maximal jump: ' + str(round(maximum,2)) 
                        )                                          # max
           plt.axvline( median, 
                        color='orange',
                        label='median: '+str(round(median,2))
                        )  # median
           plt.axvline( mean, 
                        color='pink',
                        label='mean: '+str(round(mean,2))
                        )     # mean=expectancy
           #plt.axvline() 
           
           # values as numbers
           #__________________________________________________________________
           plt.text( (1-epsilon)*minimum,   0.5*ymaximum, 
                     " standard deviation: "+str(int(editeddata[ nameofstock+"_values" ]["deviation"]))+"\n"+
                     " variance: "+str(int(editeddata[ nameofstock+"_values" ]["secondmoment"]))
                     ) #todo x and y automatically

           # find best fitting distribution
           #__________________________________________________________________
           ordereddistibutions = fitDistribution( 
                                                  editeddata[data], 
                                                  minimum,
                                                  maximum, 
                                                  binwidth
                                                  )
           #print(ordereddistibutions)
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
           for quantile in [q99, q90, q75,q50, q25, q10, -q10, -q99, -q90, -q75, -q50, -q25]:
               plt.axvline(
                            x        = quantile,
                            ymax     = 1,#0.25*np.max(amountofjumps),
                            linestyle='dotted'
                            )
#               plt.text( 
#                         quantile+0.1,
#                         0,
#                         "Quantile",
#                         rotation=90
#                         )

       #if data.find('') == 1:
       #if data.find('') == 1:
       #if data.find('') == 1:
       #if data.find('') == 1:
       #if data.find('') == 1:
"""












