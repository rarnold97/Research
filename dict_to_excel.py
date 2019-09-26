# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 15:17:13 2019

@author: ryanm
"""

import pandas as pd 
"""
dic = {'sample1':{'day1':2.3,'day2':3,'day3':2.9},
        'sample2':{'day1':4,'day2':4.2,'day3':4.1}}
df = pd.DataFrame.from_dict({(i,j):dic[i][j] 
    for i in dic.keys() 
    for j in dic[i].keys()},orient = 'index')

samples = []
frames = [] 

for samp in dic.keys():
    samples.append(samp)
    frames.append(pd.DataFrame.from_dict(dic[samp]))
    
pd.concat(frames,keys=samples)
"""

def storeBlueVals(self,expTitle):
    fileName = expTitle + '_BlueLightVals.xlsx'
    writer = pd.ExcelWriter(fileName, engine='xlsxwriter')
    for polymerName in self.polymerObjects.keys():
        lightDic = self.polymerObjects[polymerName].O2BlueFit
        
        df = pd.DataFrame.from_dict(lightDic,orient='index')
        fileName = polymerName + 'Blu'
        df.to_excel(writer,sheet_name = polymerName)
        
def printIntData(self,expTitle):
    fileName = expTitle + 'Intensity_Summary.xlsx'
    writer = pd.ExcelWriter(fileName,engine='xlsxwriter')
    frames = []
    for polymerName in self.polymerObjects.keys():
        poly = self.polymerObjects[polymerName]
        IAir = poly.IAir
        IN2 = poly.IN2
        IO2 = poly.IO2
        for day,i in zip(poly.Time,range(poly.Time)):
            for sample in IAir.keys():
                data ={'Polymer':polymerName,'Sample':sample,
                       'IN2 (Photon Counts)':IN2[sample][i],
                       'IAir (Photon Counts)':IAir[sample][i],
                       'IO2 (Photon Counts)':IO2[sample][i]}
                df = pd.DataFrame(data)
                frames.append(df)
        df.to_excel(writer)