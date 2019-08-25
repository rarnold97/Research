# -*- coding: utf-8 -*-
"""
Created on Sun Aug 25 13:41:09 2019

@author: ryanm
"""

#import pandas as pd 

class Polymer():
    
    def __init__(self,polymerName):
        self.name = polymerName
        
        #alternatively could use a list instead 
        self.IntensityAir = list()
        self.LambdaAir = list() #wavelength arrays in nm
        
        self.IntensityN2 = list()
        self.LambdaN2 = list() #wavelength arrays in nm
        
        self.IntensityO2 = list()
        self.LambdaO2 = list() #wavelength arrays in nm
        
        self.dyeWave = 0.0
        self.dyeInt = list()
        self.dyeInt0 = 0.0
        
        self.IN2 = 0.0
        self.IO2 = 0.0
        self.IAir = 0.0 
        
        self.IN2_Air = list()
        self.IN2_O2 = list()
    
        self.Time = list()
        
        self.Category = ""
        self.Dye = ""
        
        self.normN2AirAvg = list()
        self.normN2AirSTD = list()
        
        self.normN2O2Avg = list()
        self.normN2O2STD = list()
        
    def updateRatios(self):
        self.IN2_Air = self.IN2/self.IAir
        self.IN2_O2 = self.IN2/self.IO2        
        
        
    