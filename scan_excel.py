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

#code that imports data in spreadsheet format
def loadExcelData(fileName='Photobleaching_test_refined.xlsm', key='photobleaching', dye_choice='Pd',customWave=0):
    """
    filename is the name of the spreadsheet, key is the value for the experiment type, dye_choice is the dye to be examined
    Function returns a list of polymer objects that contain all the experiment info and more depending on what methods are used 
    """
    #fileName = 'Temperature_Agglomeration_Pd_Analysis.xlsm'
    #dye_choice = 'Pd'
    #key = 'temperature'
    
    xl = pd.ExcelFile(fileName)
    
    sheetNames = xl.sheet_names
    
    badNames = ['Analysis','Analysis 2','Data Analysis ','Data Summaries ','Results ','Aged','Unaged']
    
    Dyes = {'Pd':673.93,'Pt':652.35,'Ru':604.49}
    
    if dye_choice not in Dyes.keys():
        Dyes.update({dye_choice:customWave})
    
    analysisType  = {'photobleaching': 1, 'lifetime':2, 'temperature':3}
    
    allDataFrames = list()
    newShtNames = list()
    
    for sht in sheetNames:
    
        if sht not in badNames:
            
            newShtNames.append(sht)
            
            df = pd.read_excel(xl,sheet_name = sht,header=[1,2,3])
            
            df.reset_index(inplace=True,)
            
            colNames = df.columns.values.tolist()
            
            tempLabel = list(colNames[1])
            
            correctLabel = list(colNames[2])[-1]
            
            tempLabel[-1] = correctLabel
            
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
    
    Scaffolds_Temp = {}
    #buffer variable to evaulate wheter we are on the same polymer or not 
    Air0 = {}
    N20 = {}
    O20 = {}
    
    for shtData, shtName in zip(allDataFrames,newShtNames):
        
        
        allColNames = shtData.columns.values.tolist()
        
        allPolyNames = list()
        allGases = list()
        allVars = list()
        allTimes = list()
        
        AirCurveData = {}
        O2CurveData = {}
        N2CurveData = {}
        
        for cols in allColNames:
            
            if (analysisType[key] == 1 or analysisType[key]==3): #photobleaching
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
        
        if(analysisType[key] == 1 or analysisType[key] ==3 ): #this applies to the photobleaching experiment and temperature only 
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
            
            for day in allTimes:
                
                scaffold.Time.append(day)
                scaffData = shtData[day]
                
                
                for gas in allGases:
                    
                    for var in allVars:
                        
                        if ('air' in gas or 'Air' in gas):
                            
                            AirCurveData.update({day : scaffData[gas]})
                        
                            if ('lambda' in var or 'λ(nm)' in var):
                                
                                Filter = scaffData[gas][var] >= srchWave
                                filterData = scaffData[gas].where(Filter)
                                filterData.dropna(inplace=True)
                                dataPair = filterData.values.tolist()[0]
                                
                                scaffold.IAir[shtName].append(dataPair[-1])
                                
                                if day == allTimes[0]:
                                    scaffold.IAir0[shtName] = dataPair[-1]
                                
                            
                        elif ('N2' in gas or 'n2' in gas):
                            
                            N2CurveData.update({day:scaffData[gas]})
                            
                            if ('lambda' in var or 'λ(nm)' in var):
                                
                                Filter = scaffData[gas][var] >= srchWave
                                filterData = scaffData[gas].where(Filter)
                                filterData.dropna(inplace=True)
                                dataPair = filterData.values.tolist()[0]
                                
                                scaffold.IN2[shtName].append(dataPair[-1])
                                
                                if day == allTimes[0]:
                                    scaffold.IN20[shtName] = dataPair[-1]
                                
                        elif('O2'in gas or 'o2' in gas):
                            
                            O2CurveData.update({day:scaffData[gas]})
                            
                            if ('lambda' in var or 'λ(nm)' in var):
                                
                                Filter = scaffData[gas][var] >= srchWave
                                filterData = scaffData[gas].where(Filter)
                                filterData.dropna(inplace=True)
                                dataPair = filterData.values.tolist()[0]
                                
                                scaffold.IO2[shtName].append(dataPair[-1])
                                
                                if day == allTimes[0]:
                                    scaffold.IO20[shtName] = dataPair[-1]
        
            scaffold.Aircurve[fullPolyName] = AirCurveData
            scaffold.O2curve[fullPolyName] = O2CurveData
            scaffold.N2curve[fullPolyName] = N2CurveData
            
            scaffold.Time = Remove(scaffold.Time)
            Scaffolds_Photo[curPoly] = scaffold
            
            
                
                
        elif (analysisType[key]==2): #lifetime experiment
            
            for scaffName in allPolyNames:
                
                baseName = scaffName.split(' ')[0] 
                
                if baseName in expCollLifetime.keys():
                    scaffold = expCollLifetime.get(baseName)
                else:
                    scaffold = plymr.Polymer(baseName)
                    expCollLifetime[baseName] = scaffold
                    
                    for each_sht in newShtNames:
                        scaffold.Aircurve.update({each_sht:{}})
                        scaffold.O2curve.update({each_sht:{}})
                        scaffold.N2curve.update({each_sht:{}})
                        
                        scaffold.IAir.update({each_sht:{}})
                        scaffold.IN2.update({each_sht:{}})
                        scaffold.IO2.update({each_sht:{}})
    
                scaffold.Aircurve[shtName].update({scaffName.strip():{}})
                scaffold.O2curve[shtName].update({scaffName.strip():{}})
                scaffold.N2curve[shtName].update({scaffName.strip():{}})
                scaffold.Category.append(scaffName.strip())
                scaffold.IAir[shtName].update({scaffName.strip():list()})
                scaffold.IN2[shtName].update({scaffName.strip():list()})
                scaffold.IO2[shtName].update({scaffName.strip():list()})
                scaffold.IAir0.update({scaffName.strip():0})
                scaffold.IN20.update({scaffName.strip():0})
                scaffold.IO20.update({scaffName.strip():0})
                
                scaffData = shtData[scaffName]
                
                for gas in allGases:
                    
                    for var in allVars:
                        
                        if ('air' in gas or 'Air' in gas):
                        
                            scaffold.Aircurve[shtName.strip()].update({scaffName.strip():scaffData[gas]})
                            
                            if ('lambda' in var or 'λ(nm)' in var):
                                
                                Filter = scaffData[gas][var] >= srchWave
                                filterData = scaffData[gas].where(Filter)
                                filterData.dropna(inplace=True)
                                dataPair = filterData.values.tolist()[0]
    
                                scaffold.IAir[shtName][scaffName.strip()].append( dataPair[-1] )
    
                                if 'Unaged' in shtName or 'unaged' in shtName:
                                    Air0.update({scaffName:dataPair[-1]})
                                    scaffold.IAir0[scaffName.strip()] = dataPair[-1]
                            
                        elif ('N2' in gas or 'n2' in gas):
                            
                            scaffold.N2curve[shtName.strip()].update({scaffName.strip():scaffData[gas]})
                            
                            if ('lambda' in var or 'λ(nm)' in var):
                                
                                Filter = scaffData[gas][var] >= srchWave
                                filterData = scaffData[gas].where(Filter)
                                filterData.dropna(inplace=True)
                                dataPair = filterData.values.tolist()[0]
    
                                scaffold.IN2[shtName][scaffName.strip()].append( dataPair[-1] )
    
                                if 'Unaged' in shtName or 'unaged' in shtName:
                                    N20.update({scaffName:dataPair[-1]})
                                    scaffold.IN20[scaffName.strip()] = dataPair[-1]
                                
                        elif('O2'in gas or 'o2' in gas):
                            
                            scaffold.O2curve[shtName].update({scaffName.strip():scaffData[gas]})
                            
                            if ('lambda' in var or 'λ(nm)' in var):
                                
                                Filter = scaffData[gas][var] >= srchWave
                                filterData = scaffData[gas].where(Filter)
                                filterData.dropna(inplace=True)
                                dataPair = filterData.values.tolist()[0]
                                
                                scaffold.IO2[shtName][scaffName.strip()].append( dataPair[-1] )
                                
                                if 'Unaged'in shtName or 'unaged' in shtName:
                                    O20.update({scaffName:dataPair[-1]})
                                    scaffold.IO20[scaffName.strip()] = dataPair[-1]
                                
        
        elif (analysisType[key]==3): #aggregation data
            curPoly = basePoly[-1]
            fullPolyName = shtName
            
            if curPoly in Scaffolds_Temp.keys():
                scaffold = Scaffolds_Temp.get(curPoly)
            else:
                scaffold = plymr.Polymer(curPoly)
                Scaffolds_Temp[curPoly] = scaffold
            
            scaffold.Aircurve.update({shtName:{}})
            scaffold.Category.append(fullPolyName)
            scaffold.IAir.update({shtName:list()})
            scaffold.IAir0.update({shtName:0})
            
            for day in allTimes:
                
                scaffold.Time.append(day)
                scaffData = shtData[day]
                
                
                for gas in allGases:
                    
                    for var in allVars:
                        
                        if ('air' in gas or 'Air' in gas):
                            
                            AirCurveData.update({day : scaffData[gas]})
                        
                            if ('lambda' in var or 'λ(nm)'in var or 'λ'in var):
                                
                                Filter = scaffData[gas][var] >= srchWave
                                filterData = scaffData[gas].where(Filter)
                                filterData.dropna(inplace=True)
                                dataPair = filterData.values.tolist()[0]
                                
                                scaffold.IAir[shtName].append(dataPair[-1])
                                
                                if day == allTimes[0]:
                                    scaffold.IAir0[shtName] = dataPair[-1]
                                
            
            scaffold.Aircurve[fullPolyName] = AirCurveData
            
            scaffold.Time = Remove(scaffold.Time)
    
            Scaffolds_Temp[curPoly] = scaffold     
            
        if (analysisType[key] == 1):
            
            if(shtName == newShtNames[-1]):
                return Scaffolds_Photo  
    
        elif (analysisType[key] == 2):
            #collect the lifetime version of the data 
            if (shtName == newShtNames[-1]):
                for sampKey in expCollLifetime.keys():
                    polySample = expCollLifetime[sampKey]
                    polySample.Category = Remove(polySample.Category)
                    expCollLifetime[sampKey] = polySample
                return expCollLifetime
        
        elif (analysisType[key] == 3):
            #do nothing for now
            if(shtName == newShtNames[-1]):
                return Scaffolds_Temp
                print('hello')
        
if __name__=='__main__':
    dic = loadExcelData()    
