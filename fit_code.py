# -*- coding: utf-8 -*-
"""
Created on Sun Sep 15 12:52:32 2019

@author: ryanm
"""

from scipy.optimize import curve_fit
import numpy as np 
import matplotlib.pyplot as plt

#define the fit function templates
def expSingle(x,a,b):
    return a * np.exp(b*x)

def expDecay(x,a,b):
    return a* np.exp(-b*x) 

def expDouble(x,a,b,d,e):
    return a*np.exp(b*x) + d*np.exp(e*x)  

def expDoubleDecay(x,a,b,d,e):
    return a*np.exp(-b*x) + d*np.exp(-e*x)  

def logarithmic(x,a,b):
    return a + b*np.log(x)

def Hubert(x,k):
    return k*np.exp(-k*(x-x[0]))/np.power((1+np.exp(-k*(x-x[0]))),2)

def Sigmoidal(x,a,b):
    return 1.0 / (1.0 + np.exp(-a*(x-b)))

def poly1(x,a,b):
    return a*x + b

def poly2(x,a,b,c):
    return a*x + b*np.power(x,2) + c

def poly3(x,a,b,c,d):
    return a*x + b*np.power(x,2) + c * np.power(x,3) + d

def poly4(x,a,b,c,d,e):
    return a*x + b*np.power(x,2) + c * np.power(x,3) + d*np.power(x,4) + e

def poly5(x,a,b,c,d,e,f):
    return a*x + b*np.power(x,2) + c * np.power(x,3) + d*np.power(x,4) + e*np.power(x,5) + f

def poly6(x,a,b,c,d,e,f,g):
    return a*x + b*np.power(x,2) + c * np.power(x,3) + d*np.power(x,4) + e*np.power(x,5) + f*np.power(x,6) + g

def poly7(x,a,b,c,d,e,f,g,h):
    return a*x + b*np.power(x,2) + c * np.power(x,3) + d*np.power(x,4) + e*np.power(x,5) + f*np.power(x,6) + g*np.power(x,7) + h

def fitCurve(xdata,ydata,fitType):
    #xdata = np.linspace(xRange[0],xRange[1],1000)
    
    if "expSingle" in fitType:
        param, param_cov = curve_fit(expSingle,xdata,ydata)
        
    elif "expDouble" in fitType:
        param, param_cov = curve_fit(expDouble,xdata,ydata)
        
    elif "logarithmic" in fitType:
        param, param_cov = curve_fit(logarithmic,xdata,ydata)
        
    elif "poly1" in fitType:
        param, param_cov = curve_fit(poly1,xdata,ydata)
        
    elif "poly2" in fitType:
        param, param_cov = curve_fit(poly2,xdata,ydata)
    
    elif "poly3" in fitType:
        param, param_cov = curve_fit(poly3,xdata,ydata)
        
    elif "poly4" in fitType:
        param, param_cov = curve_fit(poly4,xdata,ydata)
        
    elif "poly5" in fitType:
        param, param_cov = curve_fit(poly5,xdata,ydata)
        
    elif "poly6" in fitType:
        param, param_cov = curve_fit(poly6,xdata,ydata)
        
    elif "poly7" in fitType:
        param, param_cov = curve_fit(poly7,xdata,ydata)
    
    elif "Sigmoidal" in fitType:
        param, param_cov = curve_fit(Sigmoidal,xdata,ydata)
    
    elif "Hubert" in fitType:
        param, param_cov = curve_fit(Hubert,xdata,ydata)
        
    return (param,param_cov)

def applyFit(xdata,param,fitType):
    
    if "expSingle" in fitType:
        yfitted = expSingle(xdata,*param)
        
    elif "expDouble" in fitType:
        yfitted = expDouble(xdata,*param)
        
    elif "logarithmic" in fitType:
        yfitted = logarithmic(xdata,*param)
        
    elif "poly1" in fitType:
        yfitted = poly1(xdata,*param)
        
    elif "poly2" in fitType:
        yfitted = poly2(xdata,*param)
    
    elif "poly3" in fitType:
        yfitted = poly3(xdata,*param)
        
    elif "poly4" in fitType:
        yfitted = poly4(xdata,*param)
        
    elif "poly5" in fitType:
        yfitted = poly5(xdata,*param)
        
    elif "poly6" in fitType:
        yfitted = poly6(xdata,*param)
        
    elif "poly7" in fitType:
        yfitted = poly7(xdata,*param)
    
    elif "Sigmoidal" in fitType:
        yfitted = Sigmoidal(xdata,*param)
    
    elif "Hubert" in fitType:
        yfitted = Hubert(xdata,*param)
        
    return yfitted