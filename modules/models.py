#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  9 17:16:42 2023

@author: robin
"""


# general modules
import os
import numpy as np
import scipy as scp
import pandas as pd
import matplotlib.pyplot as plt


from modules.inout import *



# sdeBlackScholes( real: expectancy, real: volatility, real: u0 real: dt, integer: steps, real: tmin, real: tmax ) = vector: time, vector: u
###############################################################################
# expectancy: mu
# volatility: sigma
# u0: initial value 
# dt: time increment
# steps: count of tomesteps that will be performed
# tmin: lower interval bound
# tmax: upper interval bound

def sdeBlackScholes( expectancy, volatility, u0, dt, tmin, tmax ):        
    # initialize
    #__________________________________________________________________________ 
    time  = np.arange( tmin, tmax, dt) 
    
    steps = np.size( time )
    
    u     = np.zeros( steps )
    u[0]  = u0
    
    # generate wiener proces
    #__________________________________________________________________________
    dW   = np.random.normal( 
                             loc   = 0.0, 
                             scale = np.sqrt( dt ), 
                             size  = steps 
                             )
    # euler-maruyama-method
    #__________________________________________________________________________    
    for i in range( 0, steps-1 ):
        u[i+1] = u[i] + expectancy * dt + volatility * dW[i]
        
    
    return time, u



# sdeOrnsteinUhlenbeck( real: expectancy, real: volatility, real: u0 real: dt, integer: steps, real: tmin, real: tmax ) = vector: time, vector: u
###############################################################################
# expectancy: mu
# volatility: sigma
# u0: initial value 
# dt: time increment
# steps: count of tomesteps that will be performed
# tmin: lower interval bound
# tmax: upper interval bound
def sdeOrnsteinUhlenbeck( expectancy, volatility, u0, dt, tmin, tmax ):        
    # initialize
    #__________________________________________________________________________ 
    time  = np.arange( tmin, tmax, dt) 
    
    steps = np.size( time )
    
    u     = np.zeros( steps )
    u[0]  = u0
    
    # generate wiener proces
    #__________________________________________________________________________
    dW   = np.random.normal( 
                             loc   = 0.0, 
                             scale = np.sqrt( dt ), 
                             size  = steps 
                             )
    # euler-maruyama-method
    #__________________________________________________________________________    
    for i in range( 0, steps-1 ):
        u[i+1] = u[i] + ( expectancy - u[i] ) * dt + volatility * dW[i]
        
    
    return time, u



# sdeArch(  ) = vector: time, vector: u
###############################################################################
# weights: parameters
# volatility: sigma
# u0: initial values size must match sigma
# dt: time increment
# steps: count of tomesteps that will be performed
# tmin: lower interval bound
# tmax: upper interval bound
def sdeArch( volatility, u0, dt, tmin, tmax ):        
    # initialise
    #__________________________________________________________________________ 
    time   = np.arange( tmin, tmax, dt)     
    steps  = np.size( time )
    
    length = np.size(u0)
    u      = np.zeros( length + steps )
    u[0:length] = u0
   
    weight = np.ones( np.size(u0) )                                            # compute weights 
    w0     = volatility                                                        # overgive w0
    
    sigma  = np.sum ( weight * u0 * u0 ) + w0                                  # initialise rolling volatility
    sigma  = np.sqrt( sigma )
    
    # generate wiener proces
    #__________________________________________________________________________
    dW   = np.random.normal( 
                             loc   = 0.0, 
                             scale = 0.273 , 
                             size  = steps 
                             )
    # compute time series
    #__________________________________________________________________________    
    for i in range( length, steps-1 ):
        u[i] = sigma * dW[i-length] 
        
        ui     = u[ i-length : i ]
#        print(ui)
#        input()
        sigma  = w0
        sigma += np.sum ( weight[0:np.size(ui)] * ui * ui )                                   # update rolling volatility
#        sigma /= length
        sigma  = np.sqrt( sigma )
    
    return time, u[length:]



# sdeRarch(  ) = vector: time, vector: u
###############################################################################
# use distribution of last N days as starting distribution
# use volatility of last M days as starting volatility
# use w0 as constant weight
# use u0 of the last M as initial value 
#
# for future: overgive sde
# for future: volatility is modeled in a second equation/proces according to the initial values/history
#
#
#
# Algorithm:
#   compute initial parameters for sde / new time step ( sigma )
#   compute random number according to initial distribution
#   do
#     compute timestep
#     update distribution (every K steps)
#     update parameters
#     compute new random number
#   return vector u  
#
#
#
# problems: doesn't take into account the change of the distribution of the existent time-series before
# maybe internal distribution changes too fast (maybe that is not a problem for large enough N)
# weights have to be computed according to existent time-series before
# w0 also
# weights doesn't change over time ( leads to system of equations )
# at the moment: ues DS = sigma * Deps as evolution there could be more possible: DS = mu * Dt + sigma * Deps as in BS or other stuff
# all params have to be adjusted on existent data in seperate function
#
# need separate function for evaluating parameters via minimizing some errors or such stuff


#dgamma(a=0.45, loc=-0.00, scale=82.62)
#ksone(n=1.00, loc=-586.89, scale=16858.64)




def sdeRarch( volatility, initialvalues, weights, w0, dt, tmin, tmax, distribution=scp.stats.dgamma, arg=0.45, loc=0.00, scale=82.62 ):      
# kind of BS

    # initialise
    #__________________________________________________________________________ 
    time        = np.arange( tmin, tmax, dt)     
    steps       = np.size( time )

    length      = np.size( initialvalues )
    
#    print( "total count of steps is: {} \ mean length is: {}".format( steps, length ))
    
    u           = np.zeros( length + steps )
    u[0:length] = initialvalues
    
    sigma       = volatility      # initialise rolling mean
    sigma       = np.sqrt( sigma )
    
    # generate initial distribution
    #__________________________________________________________________________

    dW          = distribution.rvs(a=arg, loc=loc, scale=scale) #scp.stats.dgamma.rvs(a=0.45, loc=-0.00, scale=82.62) length = n is possible
    
    # compute time series
    #__________________________________________________________________________    
    for i in range( length, steps-1 ):
#        print(i)
#        print(dW)
#        print("sigma {}".format(sigma))
        # Varying of mu
        ui  = u[ i-length : i ]

        mu  = np.sum ( weights[0:np.size(ui)] * ui )                           #mean
        mu /= (length)
        
        # Timestep
        u[i]   =   mu + dW
#        print(u[i])
#        input()
        # new sigma
        sigma  = np.sum ( weights[0:np.size(ui)] * ui * ui )
        sigma += w0
        sigma  = np.sqrt( sigma ) 
        
        # storing old sigma
        w0    = sigma # maybe 
        
        # Update random number (maybe update distribution in sense of loc and scale also)
        dW     =  distribution.rvs( a=arg, loc=loc, scale=scale )#scp.stats.dgamma.rvs(a=0.45, loc=-0.00, scale=82.62)
        if i%100 == 0:
            
            jumps = np.zeros(i)
            for j in range(1,i):
                jumps[j] = u[j]-u[j-1]
            params = distribution.fit( jumps )#scp.stats.dgamma.fit( ui )
            arg    = params[:-2]
            loc    = params[ -2]
            scale  = params[ -1]
#            if i%1000 == 0:
#                plt.plot( range(0,10000),  distribution.pdf( range(0,10000), loc=loc, scale=scale, *arg), label=str(i) )
#            plt.plot( range(0,10000),  distribution.pdf( range(0,10000), loc=loc, scale=scale, *arg) )
#            plt.legend()
#            plt.show()
#            print( "arg = {} \n loc = {} \n scale = {} \n".format(arg, loc, scale))

#        dW   = np.random.normal( 
#                         loc   = 0.0, 
#                         scale = np.sqrt( dt )
#                         )

    return time[:steps-1], u[:steps-1]


"""
def sdeRarch_1( volatility, initialvalues, weights, w0, dt, tmin, tmax ):      
# volatility * normalised jumpdistribution ( const over time )

    # initialise
    #__________________________________________________________________________ 
    time        = np.arange( tmin, tmax, dt)     
    steps       = np.size( time )

    length      = np.size( initialvalues )
    
    u           = np.zeros( length + steps )
    u[0:length] = initialvalues
    
    sigma       = volatility      # initialise rolling mean
    sigma       = np.sqrt( sigma )
    
    # generate initial distribution
    #__________________________________________________________________________

    dW          = scp.stats.dgamma.rvs(a=0.45, loc=-0.00, scale=82.62) #length = n is possible
    
    # compute time series
    #__________________________________________________________________________    
    for i in range( length, steps-1 ):

        # Varying of mu
        ui  = u[ i-length : i ]
        mu  = np.sum ( weights[0:np.size(ui)] * ui )                   # * uiminimal change of
                                                         # old mean
        mu /= (length+1)
        
        # Timestep
        u[i] = sigma + dW
        
        # Storing old sigma
        w0     = sigma
        
        # Update random number (maybe update distribution in sense of loc and scale also)
        dW     =  scp.stats.dgamma.rvs(a=0.45, loc=-0.00, scale=82.62)
    
    return time, u[length:]
"""
"""
def sdeRarch_2( volatility, initialvalues, weights, w0, dt, tmin, tmax ):      
# volatility * normalised jumpdistribution ( variable over time )
# therefore one has to compute dist-parameters new
# method one: fitting dist every L steps
# compute params continuously


    # initialise
    #__________________________________________________________________________ 
    time        = np.arange( tmin, tmax, dt)     
    steps       = np.size( time )

    length      = np.size( initialvalues )
    
    u           = np.zeros( length + steps )
    u[0:length] = initialvalues
    
    sigma       = volatility      # initialise rolling mean
    sigma       = np.sqrt( sigma )
    
    # generate initial distribution
    #__________________________________________________________________________

    dW          = scp.stats.dgamma.rvs(a=0.45, loc=-0.00, scale=82.62) #length = n is possible
    
    # compute time series
    #__________________________________________________________________________    
    for i in range( length, steps-1 ):

        # Varying of mu
        ui  = u[ i-length : i ]
        mu  = np.sum ( weights[0:np.size(ui)] * ui )                   # * uiminimal change of
                                                         # old mean
        mu /= (length+1)
        
        # Timestep
        u[i] = sigma + dW
        
        # Storing old sigma
        w0     = sigma
        
        # Update random number (maybe update distribution in sense of loc and scale also)
        dW     =  scp.stats.dgamma.rvs(a=0.45, loc=-0.00, scale=82.62)
    
    return time, u[length:]
"""

"""
def sdeRarch_3( volatility, initialvalues, weights, w0, dt, tmin, tmax ):      
# mean + jumpdistribution ( variable over time )
# therefore one has to compute dist-parameters new
# method one: fitting dist every L steps
# compute params continuously


    # initialise
    #__________________________________________________________________________ 
    time        = np.arange( tmin, tmax, dt)     
    steps       = np.size( time )

    length      = np.size( initialvalues )
    
    u           = np.zeros( length + steps )
    u[0:length] = initialvalues
    
    sigma       = volatility      # initialise rolling mean
    sigma       = np.sqrt( sigma )
    
    # generate initial distribution
    #__________________________________________________________________________

    dW          = scp.stats.dgamma.rvs(a=0.45, loc=-0.00, scale=82.62) #length = n is possible
    
    # compute time series
    #__________________________________________________________________________    
    for i in range( length, steps-1 ):

        # Varying of mu
        ui  = u[ i-length : i ]
        mu  = np.sum ( weights[0:np.size(ui)] * ui )                   # * uiminimal change of
                                                         # old mean
        mu /= (length+1)
        
        # Timestep
        u[i] = sigma + dW
        
        # Storing old sigma
        w0     = sigma
        
        # Update random number (maybe update distribution in sense of loc and scale also)
        dW     =  scp.stats.dgamma.rvs(a=0.45, loc=-0.00, scale=82.62)
    
    return time, u[length:]
"""


"""
def sdeRarch_4( volatility, initialvalues, weights, w0, dt, tmin, tmax ):      
# mean + jumpdistribution ( const over time )


    # initialise
    #__________________________________________________________________________ 
    time        = np.arange( tmin, tmax, dt)     
    steps       = np.size( time )

    length      = np.size( initialvalues )
    
    u           = np.zeros( length + steps )
    u[0:length] = initialvalues
    
    mu       = w0       # initialise rolling mean
#    sigma       = np.sqrt( sigma )
    
    # generate initial distribution
    #__________________________________________________________________________

    dW         = scp.stats.dgamma.rvs(a=0.45, loc=-0.00, scale=82.62) #length = n is possible
    
    # compute time series
    #__________________________________________________________________________    
    for i in range( length, steps-1 ):

        # Varying of mu
        ui     = u[ i-length : i ]
        mu  = np.sum ( weights[0:np.size(ui)] * ui )                   # * uiminimal change of
                                                         # old mean
        mu /= (length+1)
        
        # Timestep
        u[i] = sigma + dW
        
        # Storing old sigma
        w0     = sigma
        
        # Update random number (maybe update distribution in sense of loc and scale also)
        dW     =  scp.stats.dgamma.rvs(a=0.45, loc=-0.00, scale=82.62)
    
    return time, u[length:]
"""


""" General trial



    # initialise
    #__________________________________________________________________________ 
    time        = np.arange( tmin, tmax, dt)     
    steps       = np.size( time )

    length      = np.size( initialvalues )
    
    u           = np.zeros( length + steps )
    u[0:length] = initialvalues
    
    sigma       = volatility       # initialise rolling volatility
    sigma       = np.sqrt( sigma )
    
    # generate initial distribution
    #__________________________________________________________________________
    arg        = distribution[1][:-2]
    loc        = distribution[1][-2]
    scale      = distribution[1][-1]
    dW         = np.random.distribution[0]( 
                                  loc=loc, 
                                  scale=scale, 
                                  )
    
    # compute time series
    #__________________________________________________________________________    
    for i in range( length, steps-1 ):
        # Timestep
        u[i] = sigma * dW
        
        # Varying of sigma
        ui     = u[ i-length : i ]

        sigma  = np.sum ( weights[0:np.size(ui)] * ui * ui )                    
        sigma /= length                                                        # minimal change of
        sigma  = w0                                                            # old sigma
        sigma  = np.sqrt( sigma )
        
        # Storing old sigma
        w0     = sigma
        
        # Update random number (maybe update distribution in sense of loc and scale also)
        dW     = distribution[0]( 
                                  loc=loc, 
                                  scale=scale, 
                                  )
    
    return time, u[length:]"""