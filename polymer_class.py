# -*- coding: utf-8 -*-
"""
Created on Sun Aug 25 13:41:09 2019

@author: ryanm
"""

#import pandas as pd 
import numpy as np 

class Polymer():
    
    def __init__(self,polymerName):
        self.name = polymerName
        
        #alternatively could use a list instead 
        #self.IntensityAir = list()
        #self.LambdaAir = list() #wavelength arrays in nm
        
        #self.IntensityN2 = list()
        #self.LambdaN2 = list() #wavelength arrays in nm
        
        #self.IntensityO2 = list()
        #self.LambdaO2 = list() #wavelength arrays in nm
        
        self.O2curve = {}
        self.N2curve = {}
        self.Aircurve = {}
        
        self.dyeWave = 0.0
        self.dyeInt = list()
        self.dyeInt0 = 0.0
        
        self.IN2 = {}
        self.IO2 = {}
        self.IAir = {}
        
        self.IN20 = {}
        self.IO20 = {}
        self.IAir0 = {}
        
        self.IN2_Air = {}
        self.IN2_O2 = {}
    
        self.Time = list()
        
        self.Category = list()
        self.Dye = ""
        
        self.normN2AirAvg = list()
        self.normN2AirSTD = list()
        
        self.normN2O2Avg = list()
        self.normN2O2STD = list()
        
        self.IN2Avg = list()
        self.IAirAvg = list()
        self.IO2Avg = list()
        self.IN2_AirAvg = list()
        self.IN2_O2Avg = list()
        
        self.IN2Std = list()
        self.IAirStd = list()
        self.IO2AStd = list()
        self.IN2_AirStd = list()
        self.IN2_O2Std = list()
        
    def updateRatios(self):
        for key in self.IN2:    
            self.IN2_Air.update({key:list(np.array(self.IN2[key])/np.array(self.IAir[key]))}) 
            self.IN2_O2.update({key:list(np.array(self.IN2[key])/np.array(self.IO2[key]))})     
            
    def updateSumStats(self):
        
        AirIntensities = list(self.IAir.values())
        O2Intensities = list(self.IO2.values())
        N2Intensities = list(self.IN2.values())
        N2_AirIntensities = list(self.IN2_Air.values())
        N2_O2Intensities = list(self.IN2_O2.values())
        
        self.IN2Avg = np.mean(N2Intensities,axis=0)
        self.IAirAvg = np.mean(AirIntensities,axis=0)
        self.IO2Avg = np.mean(O2Intensities,axis=0)
        self.IN2_AirAvg = np.mean(N2_AirIntensities,axis=0)
        self.IN2_O2Avg = np.mean(N2_O2Intensities,axis=0)
        
        self.IN2Std = np.std(N2Intensities,axis=0)
        self.IAirStd = np.std(AirIntensities,axis=0)
        self.IO2AStd = np.std(O2Intensities,axis=0)
        self.IN2_AirStd = np.std(N2_AirIntensities,axis=0)
        self.IN2_O2Std = np.std(N2_O2Intensities,axis=0)
        
            
            
        
        
    