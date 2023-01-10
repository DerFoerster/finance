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



def sdeRarch( distribution, volatility, initialvalues, weights, w0,  tmin, tmax ):        
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
    
    # generate actual used distribution
    #__________________________________________________________________________
    dW   = distribution( size  = steps )
    
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