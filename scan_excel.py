''' TO DO:
    Add another extraction layer to the intensity values, seemes to be one level to high
'''
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt  
import pickle
import polymer_class as plymr


def storeData(obj,str):
    file = open(str,'ab')
    pickle.dump(obj,file)
    file.close()
    
def loadData(fileName):
    file = open(fileName,'rb')
    obj = pickle.load(file)
    file.close()
    return obj 

#removes duplicates, namely for lists 
def Remove(duplicate): 
    final_list = [] 
    for num in duplicate: 
        if num not in final_list: 
            final_list.append(num) 
    return final_list

"""
def uniqueDict(dict,key,obj):
    if key not in dict.keys():
        dict[key] = obj
        return dict
    else:
        return dict
"""    

#fileName = 'Lifetime Spectrometer Data Aged and Unaged.xlsx'
#fileName = 'Photobleaching_test_refined.xlsx'
#fileName = 'Photobleaching_test_refined.xlsm'

def loadExcelData(fileName='Photobleaching_test_refined.xlsm', key='photobleaching', dye_choice='Pt'):
    """
    filename is the name of the spreadsheet, key is the value for the experiment type, dye_choice is the dye to be examined
    Function returns a list of polymer objects that contain all the experiment info and more depending on what methods are used 
    """
    
    xl = pd.ExcelFile(fileName)
    
    sheetNames = xl.sheet_names
    
    badNames = ['Analysis','Analysis 2']
    
    Dyes = {'Pd':673.93,'Pt':652.35,'Ru':604.49}
    
    analysisType  = {'photobleaching': 1, 'lifetime':2, 'temperature':3}
    
    allDataFrames = list()
    newShtNames = list()
    
    for sht in sheetNames:

        if sht not in badNames:
            
            newShtNames.append(sht)
            
            #df = pd.read_excel(xl,sheet_name = 'Aged',header=[1,2,3])
            df = pd.read_excel(xl,sheet_name = sht,header=[1,2,3])
            
            #df.reset_index(inplace = True,drop=True)
            df.reset_index(inplace=True,)
            
            colNames = df.columns.values.tolist()
            
            badLabel = list(colNames[0])
            
            tempLabel = list(colNames[1])
            
            tempLabel[-1] = 'λ(nm)'
            
            colNames[0] = tuple(tempLabel)
            
            df.columns = colNames
            
            polymerDesc = list()
            gas = list()
            var = list()
            for cols in colNames:
                polymerDesc.append(cols[0])
                gas.append(cols[1])
                var.append(cols[2])
                
            #remove all duplicate values 
            polymerDesc = Remove(polymerDesc)
            gas = Remove(gas)
            var = Remove(var)
                
            newCols = pd.MultiIndex.from_product([polymerDesc,gas,var])
            #alter the df so that it is properly multi indexed data frame 
            df = pd.DataFrame(df.values,columns = newCols)
            
            #fill in the missing nan values to be 0
            df.fillna(inplace=True,value = 0 )
            
            allDataFrames.append(df)
            
    
    allPolyNames = list()
    allGases = list()
    allVars = list()
    allTimes = list()
    basePoly = list()
    
    srchWave = Dyes[dye_choice]
    
    #create an empty dictionary for the lifetime portion of the experiment 
    expCollLifetime = {}
    
    Scaffolds_Photo = {}
    #buffer variable to evaulate wheter we are on the same polymer or not 
    #samePoly = False
    Air0 = {}
    N20 = {}
    O20 = {}
    
    for shtData, shtName in zip(allDataFrames,newShtNames):
        
        #Scaffolds_Lifetime = list()
        
        allColNames = shtData.columns.values.tolist()
        
        allPolyNames = list()
        allGases = list()
        allVars = list()
        allTimes = list()
        
        AirCurveData = {}
        O2CurveData = {}
        N2CurveData = {}
        
        for cols in allColNames:
            
            if (analysisType[key] == 1): #photobleaching
                allTimes.append(cols[0])
                #keep only unique times
                #THIS IS A NEW LINE CONSIDER DELETING
                allTimes = Remove(allTimes)
            elif(analysisType[key] == 2): #lifetime experiments 
                allPolyNames.append(cols[0])
                #take unique names only 
                allPolyNames = Remove(allPolyNames)            
                
            allGases.append(cols[1])
            allVars.append(cols[2])
            
            
        #gather all unique values of polymer descriptions, which vary depending on the experiment 
        
        if(analysisType[key] == 1): #this applies to the photobleaching experiment only 
            basePoly.append(shtName.split(' ')[0])
            
        allGases = Remove(allGases)
        allVars = Remove(allVars)
        
        if (analysisType[key] ==1 ): #photobleaching experiment
            
            curPoly = basePoly[-1]
            fullPolyName = shtName
            
            
            if curPoly in Scaffolds_Photo.keys():
                scaffold = Scaffolds_Photo.get(curPoly)
            else:
                scaffold = plymr.Polymer(curPoly)
                Scaffolds_Photo[curPoly] = scaffold
                
            """
            for polyType in Scaffolds_Photo:
                if curPoly in polyType.name:
                    scaffold = polyType
                    samePoly = True 
                    break
                else:
                    samePoly = False
            
            if not samePoly:
                scaffold = plymr.Polymer(basePoly[-1])
            """    
            
            scaffold.Aircurve.update({shtName:{}})
            scaffold.O2curve.update({shtName:{}})
            scaffold.N2curve.update({shtName:{}})
            scaffold.Category.append(fullPolyName)
            scaffold.IAir.update({shtName:list()})
            scaffold.IN2.update({shtName:list()})
            scaffold.IO2.update({shtName:list()})
            scaffold.IAir0.update({shtName:0})
            scaffold.IN20.update({shtName:0})
            scaffold.IO20.update({shtName:0})
            #sampleData.update({fullPolyname})
            
            for day in allTimes:
                
                #scaffold.Time.append(day)
                scaffold.Time.append(day.strip())
                scaffData = shtData[day]
                
                
                for gas in allGases:
                    
                    for var in allVars:
                        
                        if ('air' in gas or 'Air' in gas):
                            
                            AirCurveData.update({day : scaffData[gas]})
                        
                            if ('lambda' in var or 'λ(nm)' in var):
                                #scaffold.LambdaAir.append( scaffData[gas][var].values )
                                
                                Filter = scaffData[gas][var] >= srchWave
                                filterData = scaffData[gas].where(Filter)
                                filterData.dropna(inplace=True)
                                dataPair = filterData.values.tolist()[0]
                                
                                scaffold.IAir[shtName].append(dataPair[-1])
                                
                                if day == allTimes[0]:
                                    scaffold.IAir0[shtName] = dataPair[-1]
                                
                            #elif ('I' in var or 'Intensity' in var):
                                #scaffold.IntensityAir.append(scaffData[gas][var].values)
                            
                        elif ('N2' in gas or 'n2' in gas):
                            
                            N2CurveData.update({day:scaffData[gas]})
                            
                            if ('lambda' in var or 'λ(nm)' in var):
                                #scaffold.LambdaN2.append(scaffData[gas][var].values)
                                
                                Filter = scaffData[gas][var] >= srchWave
                                filterData = scaffData[gas].where(Filter)
                                filterData.dropna(inplace=True)
                                dataPair = filterData.values.tolist()[0]
                                
                                scaffold.IN2[shtName].append(dataPair[-1])
                                
                                if day == allTimes[0]:
                                    scaffold.IN20[shtName] = dataPair[-1]
                                
                            #elif ('I' in var or 'Intensity' in var):                    
                                #scaffold.IntensityN2.append(scaffData[gas][var].values)
                                
                        elif('O2'in gas or 'o2' in gas):
                            
                            O2CurveData.update({day:scaffData[gas]})
                            
                            if ('lambda' in var or 'λ(nm)' in var):
                                #scaffold.LambdaO2.append(scaffData[gas][var].values)
                                
                                Filter = scaffData[gas][var] >= srchWave
                                filterData = scaffData[gas].where(Filter)
                                filterData.dropna(inplace=True)
                                dataPair = filterData.values.tolist()[0]
                                
                                scaffold.IO2[shtName].append(dataPair[-1])
                                
                                if day == allTimes[0]:
                                    scaffold.IO20[shtName] = dataPair[-1]
                                
                            #elif ('I' in var or 'Intensity' in var):        
                                #scaffold.IntensityO2.append(scaffData[gas][var].values)
                                
        #scaffold.updateRatios()
        
        
            scaffold.Aircurve[fullPolyName] = AirCurveData
            scaffold.O2curve[fullPolyName] = O2CurveData
            scaffold.N2curve[fullPolyName] = N2CurveData
            
            #########################################################
            #consider removing this line of code  might cause issues#
            #########################################################
            scaffold.Time = Remove(scaffold.Time)
            scaffold.updateRatios()
            scaffold.updateSumStats()
            Scaffolds_Photo[curPoly] = scaffold
            
            
                
                
        elif (analysisType[key]==2): #lifetime experiment
            #scaff stands for scaffold.  Some polymers may differ by dye composition, so scaffold is the correct unique term 
            for scaffName in allPolyNames:
                
                baseName = scaffName.split(' ')[0] + '_' + shtName
                
                if baseName in expCollLifetime.keys():
                    scaffold = expCollLifetime.get(baseName)
                else:
                    scaffold = plymr.Polymer(baseName)
                    expCollLifetime[baseName] = scaffold
                
                #scaffold = plymr.Polymer(scaffName)
                scaffold.Aircurve.update({scaffName:{}})
                scaffold.O2curve.update({scaffName:{}})
                scaffold.N2curve.update({scaffName:{}})
                scaffold.Category.append(scaffName)
                scaffold.IAir.update({scaffName:list()})
                scaffold.IN2.update({scaffName:list()})
                scaffold.IO2.update({scaffName:list()})
                scaffold.IAir0.update({scaffName:0})
                scaffold.IN20.update({scaffName:0})
                scaffold.IO20.update({scaffName:0})
                
                scaffData = shtData[scaffName]
                
                for gas in allGases:
                    
                    for var in allVars:
                        
                        if ('air' in gas or 'Air' in gas):
                        
                            scaffold.Aircurve.update({scaffName:scaffData[gas]})
                            
                            if ('lambda' in var or 'λ(nm)' in var):
                                #scaffold.LambdaAir.append( scaffData[gas][var].values )
                                
                                Filter = scaffData[gas][var] >= srchWave
                                filterData = scaffData[gas].where(Filter)
                                filterData.dropna(inplace=True)
                                dataPair = filterData.values.tolist()[0]
    
                                scaffold.IAir[scaffName].append( dataPair[-1] )

                                if 'Unaged' in shtName or 'unaged' in shtName:
                                    Air0.update({scaffName:dataPair[-1]})
                                    scaffold.IAir0[scaffName] = dataPair[-1]
                                    
                            
                        elif ('N2' in gas or 'n2' in gas):
                            
                            scaffold.N2curve.update({scaffName:scaffData[gas]})
                            
                            if ('lambda' in var or 'λ(nm)' in var):
                                #scaffold.LambdaN2.append(scaffData[gas][var].values)
                                
                                Filter = scaffData[gas][var] >= srchWave
                                filterData = scaffData[gas].where(Filter)
                                filterData.dropna(inplace=True)
                                dataPair = filterData.values.tolist()[0]
    
                                scaffold.IN2[scaffName].append( dataPair[-1] )
    
                                if 'Unaged' in shtName or 'unaged' in shtName:
                                    N20.update({scaffName:dataPair[-1]})
                                    scaffold.IN20[scaffName] = dataPair[-1]
                                
                        elif('O2'in gas or 'o2' in gas):
                            
                            scaffold.O2curve.update({scaffName:scaffData[gas]})
                            
                            if ('lambda' in var or 'λ(nm)' in var):
                                #scaffold.LambdaO2.append(scaffData[gas][var].values)
                                
                                Filter = scaffData[gas][var] >= srchWave
                                filterData = scaffData[gas].where(Filter)
                                filterData.dropna(inplace=True)
                                dataPair = filterData.values.tolist()[0]
                                
                                scaffold.IO2[scaffName].append( dataPair[-1] )
                                
                                if 'Unaged'in shtName or 'unaged' in shtName:
                                    O20.update({scaffName:dataPair[-1]})
                                    scaffold.IO20[scaffName] = dataPair[-1]
                                
                                
                #scaffold.Aircurve[scaffName] = AirCurveData
                #scaffold.O2curve[scaffName] = O2CurveData
                #scaffold.N2curve[scaffName] = N2CurveData
                #scaffold.updateRatios()
                
                #Scaffolds_Lifetime.append(scaffold)
        
                
        if (analysisType[key] == 1):
            
            if(shtName == newShtNames[-1]):
                #for key in Scaffolds_Photo.keys():
                    #Scaffolds_Photo[key].updateRatios()
                    #Scaffolds_Photo[key].updateSumStats()
                return Scaffolds_Photo
            
            #Scaffolds.append(scaffold)       
    
        elif (analysisType[key] == 2):
            #collect the lifetime version of the data 
            #expCollLifetime[shtName] = Scaffolds_Lifetime
            
            if (shtName == newShtNames[-1]):
                for key in expCollLifetime.keys():
                    if 'unaged' not in key or 'Unaged' not in key:
                        polySample = expCollLifetime[key]
                        polySample.IAir0.update(Air0)
                        polySample.IN20.update(N20)
                        polySample.IO20.update(O20)
                        expCollLifetime[key] = polySample
                        
                    expCollLifetime[key].updateRatios()
                    expCollLifetime[key].updateSumStats()
                return expCollLifetime
        
        elif (analysisType[key] == 3):
            #do nothing for now
            print("no code yet home dawg")
    
    
    
    
    #df.rename(columns={badLabel[0]:tempLabel[0],badLabel[1]:tempLabel[1]}, inplace = True)
    #df4 = df3.rename(columns={badLabel[2]:tempLabel[2]})
    
    
    #for sht in sheetNames:
    #    if sht not in badNames:  
    #        df = pd.read_excel(xl,sheet_name = sht,header = 0)
    
    
if __name__=='__main__':
    dic = loadExcelData()    
