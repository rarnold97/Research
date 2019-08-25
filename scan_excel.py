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

fileName = 'Lifetime Spectrometer Data Aged and Unaged.xlsx'

xl = pd.ExcelFile(fileName)

sheetNames = xl.sheet_names

badNames = ['Analysis','Analysis 2']

Dye = 'Ru'

allDataFrames = list()
newShtNames = list()

for sht in sheetNames:
    
    if sht not in badNames:
        
        newShtNames.append(sht)
        
        #df = pd.read_excel(xl,sheet_name = 'Aged',header=[1,2,3])
        df = pd.read_excel(xl,sheet_name = sht,header=[1,2,3])
        
        df.reset_index(inplace = True,)
        
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

srchWave = 0

if ('Ru' in Dye):
    srchWave = 604.49
elif ('Pd' in Dye):
    srchWave = 673.93
elif ('Pt' in Dye):
    srchWave = 652.35

#create an empty dictionary 
expColl = {}

for shtData, shtName in zip(allDataFrames,newShtNames):
    
    Scaffolds = list()
    allColNames = shtData.columns.values.tolist()
    
    allPolyNames = list()
    allGases = list()
    allVars = list()
    
    for cols in allColNames:
        allPolyNames.append(cols[0])
        allGases.append(cols[1])
        allVars.append(cols[2])
        
    #gather all unique values of polymer descriptions, which vary depending on the experiment 
    allPolyNames = Remove(allPolyNames)
    allGases = Remove(allGases)
    allVars = Remove(allVars)
    
    #scaff stands for scaffold.  Some polymers may differ by dye composition, so scaffold is the correct unique term 
    for scaffName in allPolyNames:
        
        scaffold = plymr.Polymer(scaffName)
        
        scaffData = shtData[scaffName]
        
        for gas in allGases:
            
            for var in allVars:
                
                if ('air' in gas or 'Air' in gas):
                
                    if ('lambda' in var or 'λ(nm)' in var):
                        scaffold.LambdaAir.append( scaffData[gas][var].values )
                        
                        Filter = scaffData[gas][var] >= srchWave
                        filterData = scaffData[gas].where(Filter)
                        filterData.dropna(inplace=True)
                        dataPair = filterData.values.tolist()[0]
                        
                        scaffold.IAir = dataPair[-1]
                        
                    elif ('I' in var or 'Intensity' in var):
                        scaffold.IntensityAir.append(scaffData[gas][var].values)
                    
                elif ('N2' in gas or 'n2' in gas):
                    
                    if ('lambda' in var or 'λ(nm)' in var):
                        scaffold.LambdaN2.append(scaffData[gas][var].values)
                        
                        Filter = scaffData[gas][var] >= srchWave
                        filterData = scaffData[gas].where(Filter)
                        filterData.dropna(inplace=True)
                        dataPair = filterData.values.tolist()[0]
                        
                        scaffold.IN2 = dataPair[-1]
                        
                    elif ('I' in var or 'Intensity' in var):                    
                        scaffold.IntensityN2.append(scaffData[gas][var].values)
                        
                elif('O2'in gas or 'o2' in gas):
                    
                    if ('lambda' in var or 'λ(nm)' in var):
                        scaffold.LambdaO2.append(scaffData[gas][var].values)
                        
                        Filter = scaffData[gas][var] >= srchWave
                        filterData = scaffData[gas].where(Filter)
                        filterData.dropna(inplace=True)
                        dataPair = filterData.values.tolist()[0]
                        
                        scaffold.IO2 = dataPair[-1]
                        
                    elif ('I' in var or 'Intensity' in var):        
                        scaffold.IntensityO2.append(scaffData[gas][var].values)
                        
                        
        scaffold.updateRatios()
        
        Scaffolds.append(scaffold)
            
    expColl[shtName] = Scaffolds
    
        
        #Scaffolds.append(scaffold)
        
    


#df.rename(columns={badLabel[0]:tempLabel[0],badLabel[1]:tempLabel[1]}, inplace = True)
#df4 = df3.rename(columns={badLabel[2]:tempLabel[2]})


#for sht in sheetNames:
#    if sht not in badNames:  
#        df = pd.read_excel(xl,sheet_name = sht,header = 0)



