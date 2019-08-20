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

fileName = 'Polymers_Photobleaching_Master copy 2.xlsx'

xl = pd.ExcelFile(fileName)

sheetNames = xl.sheet_names

badNames = ['Analysis','Analysis 2']

for sht in sheetNames:
    if sht not in badNames:  
        df = pd.read_excel(xl,sheet_name = sht)



