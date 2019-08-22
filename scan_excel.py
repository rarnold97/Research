import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt  
import pickle

def storeData(obj,str):
    file = open(str,'ab')
    pickle.dump(obj,file)
    file.close()
    
def loadData(fileName):
    file = open(fileName,'rb')
    obj = pickle.load(file)
    file.close()
    return obj 

fileName = 'Lifetime Spectrometer Data Aged and Unaged.xlsx'

xl = pd.ExcelFile(fileName)

sheetNames = xl.sheet_names

badNames = ['Analysis','Analysis 2']

df = pd.read_excel(xl,sheet_name = 'Aged',header=[1,2,3])

df.reset_index(inplace = True,)

colNames = df.columns.values.tolist()

badLabel = list(colNames[0])

tempLabel = list(colNames[1])

tempLabel[-1] = 'λ(nm)'

#colNames[0] = tuple(tempLabel)

df3 = df.rename(columns={badLabel[0]:tempLabel[0],badLabel[1]:tempLabel[1]})
df4 = df3.rename(columns={badLabel[2]:tempLabel[2]})


#for sht in sheetNames:
#    if sht not in badNames:  
#        df = pd.read_excel(xl,sheet_name = sht,header = 0)



