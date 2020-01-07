# -*- coding: utf-8 -*-
"""
Created on Sun Aug 25 13:41:09 2019

@author: ryanm
"""

#import pandas as pd 
import numpy as np 
import statsmodels.stats.api as sms
from scipy import stats

#class definition for polymer object
class Polymer():
    #initialize properties of polymer object
    def __init__(self,polymerName):
        #type of polymer 
        self.name = polymerName
        #the curve data under different oxygen environment levels
        self.O2curve = {}
        self.N2curve = {}
        self.Aircurve = {}
        #search wavelength and corresponding intensity depending on dye 
        self.dyeWave = 0.0
        self.dyeInt = list()
        self.dyeInt0 = 0.0
        self.normalized = False
        #intensities at specified emission wavelength
        self.IN2 = {}
        self.IO2 = {}
        self.IAir = {}
        #initial values of intensities
        self.IN20 = {}
        self.IO20 = {}
        self.IAir0 = {}
        #sensitivity ratios
        self.IN2_Air = {}
        self.IN2_O2 = {}
        #array for time
        self.Time = list()
        
        self.Category = list()
        self.Dye = ""
        #normalized values
        self.normN2AirAvg = list()
        self.normN2AirSTD = list()
        
        self.normN2O2Avg = list()
        self.normN2O2STD = list()
        #average values
        self.IN2Avg = list()
        self.IAirAvg = list()
        self.IO2Avg = list()
        self.IN2_AirAvg = list()
        self.IN2_O2Avg = list()
        #standard deviations
        self.IN2Std = list()
        self.IAirStd = list()
        self.IO2Std = list()
        self.IN2_AirStd = list()
        self.IN2_O2Std = list()
        #blue light overlap fit values
        self.N2BlueFit = {}
        self.O2BlueFit = {}
        self.AirBlueFit = {}
        # R Squared values and error bars 
        self.RSquare = {}
        self.errorBarsAir = list()
        self.errorBarsN2 = list()
        self.errorBarsO2 = list()
        self.errorBarsN2Air = list()
        self.errorBarsN2O2 = list()
        self.errorBarsN2Airnorm = list()
        self.errorBarsN2O2norm = list()
   #set function to reset intensities 
    def setIntensities(self,IAir,IN2,IO2):
        self.IAir = IAir
        self.IN2 = IN2
        self.IO2 = IO2
    #retrieve intensities
    def getIntensities(self,expType):
        if expType != 'temperature':
            return (self.IN2,self.IAir,self.IO2)
        else:
            return (self.IAir)
    #update ratios 
    def updateRatios(self,expType,IN2,IAir,IO2):
        """
        returns (IN2_Air, IN2_O2)
        """
        IN2_Air = {}
        IN2_O2 = {}
        #compute the requred sensitivity ratios based on recorded intensities.  
        #If statement checks the type of experiment
        if expType == 'photobleaching':
            for key in IN2:    
                IN2_Air.update({key:list(np.array(IN2[key])/np.array(IAir[key]))}) 
                IN2_O2.update({key:list(np.array(IN2[key])/np.array(IO2[key]))})     
        elif expType == 'lifetime':
            for key in IN2:
                IN2_Air.update({key:{}})
                IN2_O2.update({key:{}})
                for key2 in IN2[key]:
                    #IN2_Air[key].update( {key2:(IN2[key][key2][0] / IAir[key][key2][0])})
                    #IN2_O2[key].update( {key2:(IN2[key][key2][0] / IO2[key][key2][0])})
                    IN2_Air[key].update( {key2:(IN2[key][key2] / IAir[key][key2])})
                    IN2_O2[key].update( {key2:(IN2[key][key2] / IO2[key][key2])})
        return (IN2_Air,IN2_O2)
    #function to compute summary statstics
    def updateSumStats(self,expType,IN2={},IAir={},IO2={},IN2_Air={},IN2_O2={}):
        
        #initialize arrays
        AirIntensities = np.array([])
        O2Intensities = np.array([])
        N2Intensities = np.array([])
        N2_AirIntensities = np.array([])
        N2_O2Intensities = np.array([])
        #guide code based on experiment
        if expType == 'photobleaching':
            for key in IO2.keys():
                #reinitialize at initial value
                if AirIntensities.size==0:
                    AirIntensities = np.array(IAir[key])
                    O2Intensities = np.array(IO2[key])
                    N2Intensities = np.array(IN2[key])
                    N2_AirIntensities = np.array(IN2_Air[key])
                    N2_O2Intensities = np.array(IN2_O2[key])
                else:
                    AirIntensities = np.vstack([AirIntensities,IAir[key]])
                    O2Intensities = np.vstack([O2Intensities,IO2[key]])
                    N2Intensities = np.vstack([N2Intensities,IN2[key]])
                    N2_AirIntensities = np.vstack([N2_AirIntensities,IN2_Air[key]])
                    N2_O2Intensities = np.vstack([N2_O2Intensities,IN2_O2[key]])
            #update average and standard deviation on each pass
            self.IN2Avg = list(np.mean(N2Intensities,axis=0))
            self.IAirAvg = list(np.mean(AirIntensities,axis=0))
            self.IO2Avg = list(np.mean(O2Intensities,axis=0))
            self.IN2_AirAvg = list(np.mean(N2_AirIntensities,axis=0))
            self.IN2_O2Avg = list(np.mean(N2_O2Intensities,axis=0))
            
            self.IN2Std = list(np.std(N2Intensities,axis=0))
            self.IAirStd = list(np.std(AirIntensities,axis=0))
            self.IO2Std = list(np.std(O2Intensities,axis=0))
            self.IN2_AirStd = list(np.std(N2_AirIntensities,axis=0))
            self.IN2_O2Std = list(np.std(N2_O2Intensities,axis=0))
            
        elif expType == 'lifetime':
            #slightly different alteration of previous code for lifetime experiment
            
            #initialize averages
            IN2Avg = np.zeros(2)
            IO2Avg = np.zeros(2)
            IAirAvg = np.zeros(2)
            IN2_AirAvg = np.zeros(2)
            IN2_O2Avg = np.zeros(2)
            
            IN2Std = np.zeros(2)
            IO2Std = np.zeros(2)
            IAirStd = np.zeros(2)
            IN2_AirStd = np.zeros(2)
            IN2_O2Std = np.zeros(2) 
            #loop through all time points
            for dur in IO2.keys():
                AirList = list()
                N2List = list()
                O2List = list()
                N2AirList = list()
                N2O2List = list()
                #add values to lists
                for samp in IO2[dur].keys():
                    AirList.append(IAir[dur][samp])
                    N2List.append(IN2[dur][samp])
                    O2List.append(IO2[dur][samp])
                    N2AirList.append(IN2_Air[dur][samp])
                    N2O2List.append(IN2_O2[dur][samp])
                #remove unwanted delimeters from strings then compute means and standard deviations of replicates
                if 'aged' == dur.strip() or 'Aged' == dur.strip():
                    IN2Avg[1] = np.mean(np.array(N2List))
                    IO2Avg[1] = np.mean(np.array(O2List))
                    IAirAvg[1] = np.mean(np.array(AirList))
                    IN2_AirAvg[1] = np.mean(np.array(N2AirList))
                    IN2_O2Avg[1] = np.mean(np.array(N2O2List))
                    
                    IN2Std[1] = np.std(np.array(N2List))
                    IO2Std[1] = np.std(np.array(O2List))
                    IAirStd[1] = np.std(np.array(AirList))
                    IN2_AirStd[1] = np.std(np.array(N2AirList))
                    IN2_O2Std[1] = np.std(np.array(N2O2List))
                elif 'unaged' == dur.strip() or 'Unaged' == dur.strip():
                    IN2Avg[0] = (np.mean(np.array(N2List)))
                    IO2Avg[0] = (np.mean(np.array(O2List)))
                    IAirAvg[0] = (np.mean(np.array(AirList)))
                    IN2_AirAvg[0] = (np.mean(np.array(N2AirList)))
                    IN2_O2Avg[0] = (np.mean(np.array(N2O2List)))
                    
                    IN2Std[0] = (np.std(np.array(N2List)))
                    IO2Std[0] = (np.std(np.array(O2List)))
                    IAirStd[0] = (np.std(np.array(AirList)))
                    IN2_AirStd[0] = (np.std(np.array(N2AirList)))
                    IN2_O2Std[0] = (np.std(np.array(N2O2List)))     
            #convert from numpy arrays back to lists        
            self.IN2Avg = list(IN2Avg)
            self.IO2Avg = list(IO2Avg)
            self.IAirAvg = list(IAirAvg)
            self.IN2_AirAvg = list(IN2_AirAvg)
            self.IN2_O2Avg = list(IN2_O2Avg)
            
            self.IN2Std = list(IN2Std)
            self.IO2Std = list(IO2Std)
            self.IAirStd = list(IAirStd)
            self.IN2_AirStd = list(IN2_AirStd)
            self.IN2_O2Std = list(IN2_O2Std)
        elif expType == 'temperature': #used in aggregation experiment data 
            for key in IAir.keys():
                if AirIntensities.size==0:
                    AirIntensities = np.array(IAir[key])
                else:
                    AirIntensities = np.vstack([AirIntensities,IAir[key]])
            
            self.IAirAvg = list(np.mean(AirIntensities,axis=0))
            
            self.IAirStd = list(np.std(AirIntensities,axis=0))
            

        
    def subtractBlueLight(self,method=1,expType='photobleaching'):
        """ the method paramter is whether to subtract one value or to use unique values at each plot
        0:subtract initial only
        1: subtract unique values
        
        returns a tuple of (IN2,IAir,IO2)
        
        """
        if method ==2:
            if self.O2BlueFit or self.AirBlueFit: 
                IN2_dict = {}
                IO2_dict = {}
                IAir_dict = {}
                #subtracts fit values from measured intensities
                if expType == 'photobleaching':
                    lightArray = list()
                    for sampKey in self.IN2.keys():
                        for day in self.O2BlueFit[sampKey].keys():
                            lightArray.append(self.O2BlueFit[sampKey][day])

                        IN2new = np.array(self.IN2[sampKey]) - np.array(lightArray)
                        IO2new = np.array(self.IO2[sampKey]) - np.array(lightArray)
                        IAirnew = np.array(self.IAir[sampKey]) - np.array(lightArray)    
                        #if negative value occurs, which is physically impossible, replace with a near-zero value
                        #if 0 is used, divide by zero errors will persist
                        IN2new[IN2new<=0] = 0.1
                        IO2new[IO2new<=0] = 0.1
                        IAirnew[IAirnew<=0] = 0.1
                        #store values
                        IN2_dict.update({sampKey:list(IN2new)})
                        IO2_dict.update({sampKey:list(IO2new)})
                        IAir_dict.update({sampKey:list(IAirnew)})
                        
                        lightArray.clear()
                        
                    return(IN2_dict,IAir_dict,IO2_dict)
                            
                elif expType == 'lifetime': #lifetime experiment spectrometer data subtraction
                    for durKey in self.IN2.keys():
                        for sampKey in self.IN2[durKey].keys():
                            #similar logic as before with slightly different indexing
                            IN2new = self.IN2[durKey][sampKey] - self.O2BlueFit[durKey][sampKey]
                            IO2new = self.IO2[durKey][sampKey] - self.O2BlueFit[durKey][sampKey]
                            IAirnew = self.IAir[durKey][sampKey] - self.O2BlueFit[durKey][sampKey]
                            
                            if IN2new <= 0 :
                                IN2new = 0.1
                            if IO2new <= 0 :
                                IO2new = 0.1
                            if IAirnew <=0:
                                IAirnew = 0.1
                                
                            IN2_dict.update({durKey:{sampKey:IN2new}})
                            IO2_dict.update({durKey:{sampKey:IO2new}})
                            IAir_dict.update({durKey:{sampKey:IAirnew}})
                            
                    return(IN2_dict,IAir_dict,IO2_dict)
                            
                elif expType == 'temperature': #subtracts value from air environment only
                    lightArray = list()
                    for sampKey in self.IAir.keys():
                        for day in self.AirBlueFit[sampKey].keys():
                            lightArray.append(self.AirBlueFit[sampKey][day])
                        #subtract the array of fit values
                        IAirnew = np.array(self.IAir[sampKey]) - np.array(lightArray)    
                        #replace negative values with near zero quantity
                        IAirnew[IAirnew<=0] = 0.1
                        
                        IAir_dict.update({sampKey:list(IAirnew)})
                        
                        lightArray.clear()                    
                        
                    return (IAir_dict)
            
        elif method == 1 : #subtracts day 0 fit values only 
            
            if self.O2BlueFit or self.AirBlueFit:
                
                IN2_dict = {}
                IO2_dict = {}
                IAir_dict = {}
                
                if expType == 'photobleaching':
                    
                    for sampKey in self.IN2.keys():
                        
                        lightArray = self.O2BlueFit[sampKey][list(self.O2BlueFit[sampKey].keys())[0]]
                        
                        IN2new = np.array(self.IN2[sampKey]) - np.array(lightArray)
                        IO2new = np.array(self.IO2[sampKey]) - np.array(lightArray)
                        IAirnew = np.array(self.IAir[sampKey]) - np.array(lightArray)    
                        
                        IN2new[IN2new<=0] = 0.1
                        IO2new[IO2new<=0] = 0.1
                        IAirnew[IAirnew<=0] = 0.1
                        
                        IN2_dict.update({sampKey:list(IN2new)})
                        IO2_dict.update({sampKey:list(IO2new)})
                        IAir_dict.update({sampKey:list(IAirnew)})
                            
                    return(IN2_dict,IAir_dict,IO2_dict)
                                
                elif expType == 'lifetime':
                    for durKey in self.IN2.keys():
                        for sampKey in self.IN2[durKey].keys():
                            
                            IN2new = self.IN2[durKey][sampKey] - self.O2BlueFit[durKey][list(self.O2BlueFit[durKey].keys())[0]]
                            IO2new = self.IO2[durKey][sampKey] - self.O2BlueFit[durKey][list(self.O2BlueFit[durKey].keys())[0]]
                            IAirnew = self.IAir[durKey][sampKey] - self.O2BlueFit[durKey][list(self.O2BlueFit[durKey].keys())[0]]
                            
                            if IN2new <= 0 :
                                IN2new = 0.1
                            if IO2new <= 0 :
                                IO2new = 0.1
                            if IAirnew <=0:
                                IAirnew = 0.1
                                
                            IN2_dict.update({durKey:{sampKey:IN2new}})
                            IO2_dict.update({durKey:{sampKey:IO2new}})
                            IAir_dict.update({durKey:{sampKey:IAirnew}})
                            
                    return(IN2_dict,IAir_dict,IO2_dict)
                if expType == 'temperature':
                    
                    for sampKey in self.IAir.keys():
                        
                        lightArray = self.AirBlueFit[sampKey][list(self.AirBlueFit[sampKey].keys())[0]]

                        IAirnew = np.array(self.IAir[sampKey]) - np.array(lightArray)    

                        IAirnew[IAirnew<=0] = 0.1
                        
                        IAir_dict.update({sampKey:list(IAirnew)})
               
                    return (IAir_dict)
        
    def normalize(self,expType='photobleaching',IN2={},IAir={},IO2={}): #code to normalize intensities by initial values  
        self.normalized = True

        if expType == 'photobleaching':
            for sampKey in IN2.keys():
                
                IN2[sampKey] = list(np.array(IN2[sampKey]) / IN2[sampKey][0])
                IO2[sampKey] = list(np.array(IO2[sampKey]) / IO2[sampKey][0])
                IAir[sampKey] = list(np.array(IAir[sampKey]) / IAir[sampKey][0])
                
            return (IN2,IAir,IO2)
                
                    
        elif expType == 'lifetime':  #fix this 
            
            for sampKey in IN2.keys():
                
                IN2[sampKey] =  list(np.array(self.IN2[sampKey]) / IN2[sampKey][0])
                IO2[sampKey] = list(np.array(self.IO2[sampKey]) / IO2[sampKey][0])
                IAir[sampKey] = list(np.array(self.IAir[sampKey]) / IAir[sampKey][0])
                
            return(IN2,IAir,IO2)
                
        elif expType == 'temperature':  #fix this 
            
            for sampKey in IAir.keys():

                IAir[sampKey] = list(np.array(IAir[sampKey]) / IAir[sampKey][0])
                
            return(IAir)
                #self.IAirAvg = self.IAirAvg/self.IAirAvg[0]
                
    def addErrorBars(self,errtype=1,expType='photobleaching'): #computes various types of error bars 
        """
        1: 95% CI
        0: standard deviations
        """
            
        if expType != 'temperature':
            sampStdAir = np.array(self.IAirStd)
            sampStdO2 = np.array(self.IO2Std)
            sampStdN2 = np.array(self.IN2Std)
            sampStdN2Air = np.array(self.IN2_AirStd)
            sampStdN2O2 = np.array(self.IN2_O2Std)
            
            
            if errtype ==1: #confidence interval 95%
                n = len(self.Category)
                df = n-1
                alpha = 0.025
                tval = stats.t.ppf(1-alpha,df)                

                self.errorBarsAir = list(np.array(tval*sampStdAir/np.sqrt(n)))

                self.errorBarsO2 = list(np.array(tval*sampStdO2/np.sqrt(n)))

                self.errorBarsN2 = list(np.array(tval*sampStdN2/np.sqrt(n)))
                
                self.errorBarsN2Air = list(np.array(tval*sampStdN2Air/np.sqrt(n)))
                
                self.errorBarsN2O2 = list(np.array(tval*sampStdN2O2/np.sqrt(n)))
                
                
            elif errtype ==0: #standard deviation
                
                self.errorBarsAir = list(sampStdAir)
                
                self.errorBarsO2 = list(sampStdO2)
                
                self.errorBarsN2 =list(sampStdN2)
                
                self.errorBarsN2Air = list(sampStdN2Air)
                
                self.errorBarsN2O2 = list(sampStdN2O2)
                
        else:
            sampStdAir = np.array(self.IAirStd)
            
            if errtype ==1:
                n = len(self.Category)
                df = n-1
                #set alpha for statistics
                alpha = 0.05
                #use a studentized t-test to compute 95% CI
                tval = stats.t.ppf(1-alpha,df)
                
                self.errorBarsAir = list(np.array(tval*sampStdAir/np.sqrt(n)))
                
            elif errtype ==0:
                
                self.errorBarsAir = list(sampStdAir)
                
            print('error')
            print(self.errorBarsAir)
                
            
            
    
        
            
            
        
        
    