#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 16:10:56 2023

@author: robin
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Compute various interest & dynamics models
###############################################################################
###############################################################################

# parameters
###############################################################################
contractyears  = 20     # y  -  contract period in years
contractmonths = 12 * contractyears

interestrate   = 4      # %  -  yearly interest rate
monthlyrate    = 800    # €  -  invested sum per month

contractpercent= -5     # %  -  costs for conclude the contract initially
dynaquipercent = -0.25  # %  -  aquisition costs for new dynamics

dynamicpercent = 5      # %  -  periodicly added percentage on rates
dynamicperiod  = 12     # amount of months after whitch the rate is increased

#changingfunc   =       # model how costs change exp, linear, ...  
# fistst reduce linear  # rate(t) = 2*totalcosts/contractmonths - 2*totalcosts/contractmonths² * t





# all costs are setteled "once"
###############################################################################
costfirst      = np.zeros( contractmonths )         # fees are payed before investment ( first n months all money is for settle fees )
costlast       = np.zeros( contractmonths )         # fees are payed in the last months

# all costs are divided and payed monthly
###############################################################################
costcontinouos = np.zeros( contractmonths )         # fees are payed monthly, contract costs are divided and constant over time
costreduce     = np.zeros( contractmonths )         # fees are payed monthly, contract costs are divided and reducing over time
costincrease   = np.zeros( contractmonths )         # fees are payed monthly, contract costs are divided and increasing over time

# aquisition costs are payed first costs based on dynamics are payed monthly/reduce monthly investment rate
###############################################################################
contractfirstcostcontinuous = np.zeros( contractmonths )
contractfirstcostreduce     = np.zeros( contractmonths )
contractfirstconstincrease  = np.zeros( contractmonths )


totalvalue     = monthlyrate * contractmonths       # total value of investment at contract
aquisitioncosts= totalvalue  * contractpercent/100  # total costs for investment at contract        
dynamicscost   = 0

actualrate     = monthlyrate
oldrate        = monthlyrate

for i in range ( 1, contractmonths, dynamicperiod ):                           # compute percent of rised rates
    oldrate        = actualrate
    actualrate     = oldrate * ( 1 + dynamicpercent/100)
    dynamicscost  += (actualrate-oldrate) * dynamicperiod * dynaquipercent/100 # sum over difference times percentage
    
totalcosts     = aquisitioncosts + dynamicscost
totalsum       = 0

#print(aquisitioncosts)
#print(dynamicscost)
#print(totalcosts)





# initialisation
###############################################################################
costfirst[0]      = totalcosts
costlast [0]      = 0
costcontinouos[0] = 0
costreduce[0]     = 0
costincrease[0]   = 0
contractfirstcostcontinuous[0] = aquisitioncosts
contractfirstcostreduce[0]     = aquisitioncosts
contractfirstconstincrease[0]  = aquisitioncosts


# computation
###############################################################################
for i in range(0,contractmonths-1):
    totalsum += monthlyrate
    
    costfirst[i+1]                   = costfirst[i] + monthlyrate
    costlast [i+1]                   = costlast[i]  + monthlyrate
    costcontinouos[i+1]              = costcontinouos[i]              + monthlyrate+(totalcosts/contractmonths)
    costreduce[i+1]                  = costreduce[i]                  + monthlyrate+(2*totalcosts/contractmonths-2*totalcosts/contractmonths**2*i)  
    costincrease[i+1]                = costincrease[i]                + monthlyrate+(2*totalcosts/contractmonths**2*i)  
    contractfirstcostcontinuous[i+1] = contractfirstcostcontinuous[i] + monthlyrate+(dynamicscost/contractmonths)          
    contractfirstcostreduce[i+1]     = contractfirstcostreduce[i]     + monthlyrate+(2*dynamicscost/contractmonths-2*dynamicscost/contractmonths**2*i)  
    contractfirstconstincrease[i+1]  = contractfirstconstincrease[i]  + monthlyrate+(2*dynamicscost/contractmonths**2*i)       
    
    if( i%12 == 0 ): #interests        
        costfirst[i+1]                   = costfirst[i+1]                   * ( 1 + interestrate/100 )    
        costlast[i+1]                    = costlast[i+1]                    * ( 1 + interestrate/100 )
        costcontinouos[i+1]              = costcontinouos[i+1]              * ( 1 + interestrate/100 )   
        costreduce[i+1]                  = costreduce[i+1]                  * ( 1 + interestrate/100 )     
        costincrease[i+1]                = costincrease[i+1]                * ( 1 + interestrate/100 )   
        contractfirstcostcontinuous[i+1] = contractfirstcostcontinuous[i+1] * ( 1 + interestrate/100 ) 
        contractfirstcostreduce[i+1]     = contractfirstcostreduce[i+1]     * ( 1 + interestrate/100 )           
        contractfirstconstincrease[i+1]  = contractfirstconstincrease[i+1]  * ( 1 + interestrate/100 )     
    
    if( i%dynamicperiod == 0 ):#dynamics
        monthlyrate *= ( 1 + dynamicpercent/100)
         #print(monthlyrate)

costlast[contractmonths-1] += totalcosts





# plot
###############################################################################
"""
plt.figure()

time = np.arange( contractmonths ) 
years= np.arange( contractyears ) 



plt.plot( time, costfirst, label="costfirst", color="b" )
#plt.plot( time, costlast, label="costlast", color="c" ) #optimum

plt.plot( time, costcontinouos, label="costcontinouos", color="g" )
plt.plot( time, costreduce, label="costreduce", color="y" ) 
plt.plot( time, costincrease, label="constincrease", color="c" )

plt.plot( time, contractfirstcostcontinuous, label="contractfirstcostcontinuous", color="r" )
plt.plot( time, contractfirstcostreduce, label="contractfirstcostreduce", color="m" )
plt.plot( time, contractfirstconstincrease, label="contractfirstconstincrease", color="k" )


plt.hlines( costfirst[contractmonths-1], 0, contractmonths, color="b" )
#plt.hlines( costlast[contractmonths-1], 0, contractmonths, color="c" )

plt.hlines( costcontinouos[contractmonths-1], 0, contractmonths, color="g" )
plt.hlines( costreduce[contractmonths-1], 0, contractmonths, color="y" )
plt.hlines( costincrease[contractmonths-1], 0, contractmonths, color="c" )

plt.hlines( contractfirstcostcontinuous[contractmonths-1], 0, contractmonths, color="r" )
plt.hlines( contractfirstcostreduce[contractmonths-1], 0, contractmonths, color="m" ) 
plt.hlines( contractfirstconstincrease[contractmonths-1], 0, contractmonths, color="k" )

plt.hlines( totalsum, 0, contractmonths, color="r", label="total sum" )

#ax = plt.axes()
#ax.xaxis.set_major_locator(ticker.MultipleLocator(2))

plt.legend()
plt.show()


print( costfirst[contractmonths-1])
print( costlast[contractmonths-1])

print( costcontinouos[contractmonths-1] )
print( costreduce[contractmonths-1] )
print( costincrease[contractmonths-1] )

print( contractfirstcostcontinuous[contractmonths-1] )
print( contractfirstcostreduce[contractmonths-1] ) 
print( contractfirstconstincrease[contractmonths-1] )
"""


# bausparvertrag
###############################################################################
zinssatz     = 1.5   # %
anlagezins   = 10     # %
tilgungsrate = 7     # %
abschlussgeb = 0     # %


bausparsumme = 20000
momentansumme= bausparsumme


gesamtkosten = abschlussgeb/100 * bausparsumme  # Kreditzins + Tilgung summiert + Abschlussgebühr
gesamtgewinn = bausparsumme                     # Anlagezins + Bausparsumme über die Laufzeit

print( "     Die Abschlusskosten für den Bausparvertrag sind {}".format( np.round( gesamtkosten ), 2 ) )

laufzeit     = 0


while momentansumme > 0:
    laufzeit      += 1
    gesamtkosten  += zinssatz/100 * momentansumme + np.minimum( tilgungsrate/100 * bausparsumme, momentansumme )
    gesamtgewinn  *= ( 1 + anlagezins/100 )
    momentansumme -= tilgungsrate/100 * bausparsumme


effektiverzinssatz = ( gesamtgewinn - gesamtkosten ) * 100 / ( gesamtkosten - bausparsumme )
effektiverjahrezins= np.power( ((gesamtgewinn - bausparsumme)/(gesamtkosten - bausparsumme) ) , 1/ laufzeit ) - 1 # G = K(1+x)^î nach x umgestellt. log_10(i) kürzt sich


#print(laufzeit)
#print( (1 + effektiverjahrezins)**laufzeit) # hier sollte nun 8.4 rauskommen, es kommt aber 9.4 raus bei anderen Zahlen ist das hier immer um 1 größer.


print( "     Die zu bezahlenden Zinskosten betragen gesamt: {}".format( np.round( gesamtkosten - bausparsumme, 2 ) ) )
print( "     Die gewonnenen Zinseinnahmen betragen gesamt:  {}".format( np.round( gesamtgewinn - bausparsumme, 2 ) ) )
print( "     Somit ergibt sich als Gesamtgewinn: {}".format( np.round( gesamtgewinn - gesamtkosten, 2 ) ) )
print( "     Als Gesamtzins entspricht dies {}%".format( np.round( effektiverzinssatz ), 2 ) )
print( "     Als Jahreszins entspricht dies {}%".format( np.round( effektiverjahrezins*100 ), 2 ) )
#print( gesamtkosten )
#print( gesamtgewinn - gesamtkosten )