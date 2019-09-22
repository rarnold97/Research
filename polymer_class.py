# -*- coding: utf-8 -*-
"""
Created on Sun Aug 25 13:41:09 2019

@author: ryanm
"""

#import pandas as pd 
import numpy as np 
import statsmodels.stats.api as sms
from scipy import stats

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
        
        self.N2BlueFit = {}
        self.O2BlueFit = {}
        self.AirBlueFit = {}
        
        self.RSquare = {}
        self.errorBarsAir = list()
        self.errorBarsN2 = list()
        self.errorBarsO2 = list()
        self.errorBarsN2Air = list()
        self.errorBarsN2O2 = list()
        
    def updateRatios(self):
        for key in self.IN2:    
            self.IN2_Air.update({key:list(np.array(self.IN2[key])/np.array(self.IAir[key]))}) 
            self.IN2_O2.update({key:list(np.array(self.IN2[key])/np.array(self.IO2[key]))})     
            
    def updateSumStats(self,expType = 'photobleaching'):
        #fix to reflect dictionaries 
        
        AirIntensities = np.array([])
        O2Intensities = np.array([])
        N2Intensities = np.array([])
        N2_AirIntensities = np.array([])
        N2_O2Intensities = np.array([])
            
        for key in self.IO2.keys():
            if AirIntensities.size==0:
                AirIntensities = np.array(self.IAir[key])
                O2Intensities = np.array(self.IO2[key])
                N2Intensities = np.array(self.IN2[key])
                N2_AirIntensities = np.array(self.IN2_Air[key])
                N2_O2Intensities = np.array(self.IN2_O2[key])
            else:
                AirIntensities = np.vstack([AirIntensities,self.IAir[key]])
                O2Intensities = np.vstack([O2Intensities,self.IO2[key]])
                N2Intensities = np.vstack([N2Intensities,self.IN2[key]])
                N2_AirIntensities = np.vstack([N2_AirIntensities,self.IN2_Air[key]])
                N2_O2Intensities = np.vstack([N2_O2Intensities,self.IN2_O2[key]])
            
        self.IN2Avg = np.mean(N2Intensities,axis=0)
        self.IAirAvg = np.mean(AirIntensities,axis=0)
        self.IO2Avg = np.mean(O2Intensities,axis=0)
        self.IN2_AirAvg = np.mean(N2_AirIntensities,axis=0)
        self.IN2_O2Avg = np.mean(N2_O2Intensities,axis=0)
        
        self.IN2Std = np.std(N2Intensities,axis=0)
        self.IAirStd = np.std(AirIntensities,axis=0)
        self.IO2Std = np.std(O2Intensities,axis=0)
        self.IN2_AirStd = np.std(N2_AirIntensities,axis=0)
        self.IN2_O2Std = np.std(N2_O2Intensities,axis=0)
        
    def subtractBlueLight(self,method=1,expType='photobleaching'):
        """ the method paramter is whether to subtract one value or to use unique values at each plot
        0:subtract initial only
        1: subtract unique values
        
        """
        if method ==1:
            if self.O2BlueFit : 
                if expType == 'photobleaching':
                    for sampKey in self.IN2.keys():
                        for dayKey in self.IN2[sampKey].keys():
                            self.IN2[sampKey][dayKey] = list(np.array(self.IN2[sampKey][dayKey]) - np.array(self.O2BlueFit[sampKey][dayKey]));
                            self.IO2[sampKey][dayKey] = list(np.array(self.IO2[sampKey][dayKey]) - np.array(self.O2BlueFit[sampKey][dayKey]));
                            self.IAir[sampKey][dayKey] = list(np.array(self.IAir[sampKey][dayKey]) - np.array(self.O2BlueFit[sampKey][dayKey]));
                elif expType == 'lifetime':
                    for sampKey in self.IN2.keys():
                        self.IN2[sampKey] = list(np.array(self.IN2) - np.array(self.O2BlueFit[sampKey]))
                        self.IO2[sampKey] = list(np.array(self.IO2) - np.array(self.O2BlueFit[sampKey]))
                        self.IAir[sampKey] = list(np.array(self.IAir) - np.array(self.O2BlueFit[sampKey]))
                
    def normalize(self,expType='photobleaching'):
        if expType == 'photobleaching':
            for sampKey in self.IN2.keys():
                self.IN2[sampKey] = list(np.array(self.IN2[sampKey]) / self.IN20[sampKey])
                self.IO2[sampKey] = list(np.array(self.IO2[sampKey]) / self.IO20[sampKey])
                self.IAir[sampKey] = list(np.array(self.IAir[sampKey]) / self.IAir0[sampKey])
                """
                for dayKey in self.IN2[sampKey].keys():
                    self.IN2[sampKey][dayKey] = list(np.array(self.IN2[sampKey][dayKey]) / self.IN20[sampKey][dayKey]);
                    self.IO2[sampKey][dayKey] = list(np.array(self.IO2[sampKey][dayKey]) / self.IO20[sampKey][dayKey]);
                    self.IAir[sampKey][dayKey] = list(np.array(self.IAir[sampKey][dayKey]) / self.IAir0[sampKey][dayKey]);
                """
                    
        elif expType == 'lifetime':
            for sampKey in self.IN2.keys():
                self.IN2[sampKey] = list(np.array(self.IN2[sampKey]) / self.IN20[sampKey])
                self.IO2[sampKey] = list(np.array(self.IO2[sampKey]) / self.IO20[sampKey])
                self.IAir[sampKey] = list(np.array(self.IAir[sampKey]) / self.IAir0[sampKey])
                
    def addErrorBars(self,errtype=1):
        """
        1: 95% CI
        0: standard deviations
        """
        
        """
        for i1,i2,i3,i4,i5 in zip(range(len(self.IAirAvg)),range(len(self.IO2Avg)),range(len(self.IN2Avg)),
                         range(len(self.IN2_AirAvg)),range(len(self.IN2_O2Avg))):
        """
            
        """
        sampMeanAir = self.IAirAvg[i1]
        sampMeanO2 = self.IO2Avg[i2]
        sampMeanN2 = self.IN2Avg[i3]
        sampMeanN2Air = self.IN2_AirAvg[i4]
        sampMeanN2O2 = self.IN2_O2Avg[i5]
        """
            
        sampStdAir = self.IAirStd
        sampStdO2 = self.IO2Std
        sampStdN2 = self.IN2Std
        sampStdN2Air = self.IN2_AirStd
        sampStdN2O2 = self.IN2_O2Std
        
        if errtype ==1: #confidence interval 95%
            n = len(self.Category)
            df = n-1
            alpha = 0.05
            tval = stats.t.ppf(1-alpha,df)                
            
            #leftAir = sampMeanAir - tval * sampStdAir/ np.sqrt(n)
            #rightAir = sampMeanAir + tval * sampStdAir/np.sqrt(n)
            #CIAir =(leftAir,rightAir)
            
            #self.errorBarsAir.append(CIAir)
            #self.errorBarsAir.append(tval*sampStdAir/np.sqrt(n))
            self.errorBarsAir = list(np.array(tval*sampStdAir/np.sqrt(n)))
            
            #leftO2 = sampMeanO2 - tval * sampStdO2/ np.sqrt(n)
            #rightO2 = sampMeanO2 + tval * sampStdO2/np.sqrt(n)
            #CIO2 =(leftO2,rightO2)
            
            #self.errorBarsO2.append(tval*sampStdO2/np.sqrt(n))
            self.errorBarsO2 = list(np.array(tval*sampStdO2/np.sqrt(n)))
            
            #leftN2 = sampMeanN2 - tval * sampStdN2/ np.sqrt(n)
            #rightN2 = sampMeanN2 + tval * sampStdN2/np.sqrt(n)
            #CIN2 =(leftN2,rightN2)
            
            #self.errorBarsN2.append(tval*sampStdN2/np.sqrt(n))
            self.errorBarsN2 = list(np.array(tval*sampStdN2/np.sqrt(n)))
            
            #leftN2Air = sampMeanN2Air - tval * sampStdN2Air/ np.sqrt(n)
            #rightN2Air = sampMeanN2Air + tval * sampStdN2Air/np.sqrt(n)
            #CIN2Air =(leftN2Air,rightN2Air)
            
            #self.errorBarsN2Air.append(CIN2Air)
            #self.errorBarsN2Air.append(tval*sampStdN2Air/np.sqrt(n))
            self.errorBarsN2Air = list(np.array(tval*sampStdN2Air/np.sqrt(n)))
            
            #leftN2O2 = sampMeanN2O2 - tval * sampStdN2O2/ np.sqrt(n)
            #rightN2O2 = sampMeanN2O2 + tval * sampStdN2O2/np.sqrt(n)
            #CIN2O2 =(leftN2O2,rightN2O2)
            
            #self.errorBarsN2O2.append(CIN2O2)
            #self.errorBarsN2O2.append(tval*sampStdN2O2/np.sqrt(n))
            self.errorBarsN2O2 = list(np.array(tval*sampStdN2O2/np.sqrt(n)))
            
            
        elif errtype ==0: #standard deviation
            
            #leftAir = sampMeanAir - sampStdAir
            #rightAir = sampMeanAir + sampStdAir
            #CIAir =(leftAir,rightAir)
            
            #self.errorBarsAir.append(CIAir)
            self.errorBarsAir.append(sampStdAir)
            
            #leftO2 = sampMeanO2 - sampStdO2
            #rightO2 = sampMeanO2 +sampStdO2
            #CIO2 =(leftO2,rightO2)
            
            #self.errorBarsO2.append(CIO2)
            self.errorBarsO2.append(sampStdO2)
            
            #leftN2 = sampMeanN2 -sampStdN2
            #rightN2 = sampMeanN2 + sampStdN2
            #CIN2 =(leftN2,rightN2)
            
            #self.errorBarsN2.append(CIN2)
            self.errorBarsN2.append(sampStdN2)
            
            #leftN2Air = sampMeanN2Air - sampStdN2Air
            #rightN2Air = sampMeanN2Air + sampStdN2Air
            #CIN2Air =(leftN2Air,rightN2Air)
            
            self.errorBarsN2Air.append(sampStdN2Air)
            
            #leftN2O2 = sampMeanN2O2 -  sampStdN2O2
            #rightN2O2 = sampMeanN2O2 +  sampStdN2O2
            #CIN2O2 =(leftN2O2,rightN2O2)
            
            #self.errorBarsN2O2.append(CIN2O2)
            self.errorBarsN2O2.append(sampStdN2O2)
            
    
        
            
            
        
        
    