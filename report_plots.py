# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 16:58:04 2019

@author: ryanm
"""

import seaborn as sns
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.ticker as ticker
from textwrap import wrap
import pandas as pd

sns.set_context('poster')
# In[1]:

#plotting block for the temperature agglomeration experiments
dye = 'pt'

if dye =='pt':
    df = pd.read_excel('C:/Users/ryanm/Documents/Research/Pt_Agglomeration_Data_with_Day0.xlsx',sheet_name = 'refined_data')
elif dye =='pd':
    df = pd.read_excel('C:/Users/ryanm/Documents/Research/Pd_Agglomeration_Data_with_Day0.xlsx',sheet_name = 'refined_data')

data = {}

for index, row in df.iterrows():
    if row['Temperature ( C )'] in data:
        tempDict = data[row['Temperature ( C )']]
        
        if row['Dye Load'] in tempDict:
            loadDict = tempDict[row['Dye Load']]
            #############################################
            #if row['Day'] not in loadDict:
            if row['Day'] not in loadDict and row['Day']!=365.0 :
                values = (row['Mean Normalized Intensity'],row['95% CI error'])
                loadDict.update({row['Day']:values})            
        else:
            tempDict.update({row['Dye Load']:{}})
    else:
        data.update({row['Temperature ( C )']:{}})
        
fig = plt.figure()
ax = fig.add_subplot(111)

Colors = ()
Markers = ()

if dye == 'pt':
    Colors = ('red','blue','green')
    Markers = ('^','X')
elif dye == 'pd':
    Colors = ('red','blue','green','orange')
    Markers = ('^','X')

for tempKey,m in zip(data.keys(),Markers):
    
    for loadKey,c in zip(data[tempKey].keys(),Colors):
        
        intData = data[tempKey][loadKey]
        
        time = list(intData.keys())
        
        dataPair = list(intData.values())
        
        intensity,error = zip(*dataPair)
        
        loadString = '' 
        if 'Pd' in str(loadKey):
            loadString = str(loadKey).replace("_PdTFPP","")
        elif 'Pt' in str(loadKey):
            loadString = str(loadKey).replace("Pt","")
            
        labelStr = 'T = '+str(tempKey)+ ' C'+ ' ' + 'Dye Load = ' + loadString   
        
        
        ax.errorbar(time,intensity,yerr=error,linestyle='--',color = c, marker=m,label=labelStr, capsize=5,elinewidth=2,markeredgewidth=2)

#ax.legend(fontsize='xx-small')

box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize='x-small')

#ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),
#          ncol=3, fancybox=True, shadow=True)
ax.set_xlabel('Day')
ax.set_ylabel('Normalized Intensity $(I_{Air})/(I_{Air_0})$')
ax.set_title('Normalized Intensity Plot for Polymer with PdTFPP Dye')
#ax.set_xlim((0,50))

plt.show()

# In[2]:

#sheetName = 'refined_data_N2O2'
#sheetName = 'refined_data_N2Air'
#sheetName = 'refined_data_N2Air_nb'
#sheetName = 'refined_data_N2O2_nb'
#sheetName = 'refined_data_N2_fitted'
#sheetName = 'refined_data'
#sheetName = 'refined_data_normalized_fitted'
#sheetName = 'refined_data_normalized'
#sheetName = 'refined_data_N2O2_fitted'
#sheetName = 'refined_data_N2O2'
#sheetName = 'refined_data_N2Air'
#sheetName = 'refined_data_N2Air_fitted'

sheetName = 'refined_data_N2O2_normal'
#sheetName = 'refined_data_N2O2_normal_fitted'
#sheetName = 'refined_data_N2O2_fitted_normal'

#df = pd.read_excel('C:/Users/ryanm/Documents/Research/aging_test_full_fits.xlsx',sheet_name = sheetName)
#df = pd.read_excel('C:/Users/ryanm/Documents/Research/lifetime_spreadsheet.xlsx',sheet_name = sheetName)
df = pd.read_excel('C:/Users/ryanm/Documents/Research/BC006_spreadsheet_full_fit.xlsx' , sheet_name = sheetName)

#response = 'N2_O2'
#response = 'N2_Air'
#response = 'N2_O2_nb'
#response = 'N2_Air_nb'
#response = 'N2'
#response = 'N2_Lifetime'
#response = 'N2_Normal'
#response = 'N2_Normal_Lifetime'
#response = 'N2_Normal_BC'
#response = 'N2_O2_BC'
#response = 'N2_Air_BC'
response = 'N2_O2_nb_BC'
#response = 'N2_Air_nb_BC'

#response = 'N2_O2_normal'
#response = 'N2_O2_nb_BC'

data = {}

for index,row in df.iterrows():
    if row['Polymer'] in data:
        polyDict = data[row['Polymer']]
        if row['Day'] not in polyDict:
            polyDict.update({row['Day']:(row['Mean Prediction'],row['Yerr'])})
            data[row['Polymer']] = polyDict
    else:
        data.update({row['Polymer']:{}})
        
fig = plt.figure()
ax = fig.add_subplot(111)

if 'Lifetime' in response:
    Colors ={'Nylon-6':'blue','PES':'orange','PET':'green','PSU (High_Dye_Load)':'red','PSU (Low_Dye_Load)':'red'}
    Markers ={'Nylon-6':'o','PES':'s','PET':'X','PSU (High_Dye_Load)':'^','PSU (Low_Dye_Load)':'P'}
elif 'BC' in response:
    Colors = {'PSU with 0.06wt% Beta Carotene':'orange'}
    Markers = {'PSU with 0.06wt% Beta Carotene':'o'}
else:
    Colors = {'Nylon-6':'blue','PES':'orange','PET':'green','PSU':'red'}
    Markers = {'Nylon-6':'o','PES':'s','PET':'X','PSU':'^'}

for polyKey in data.keys():
    intData = data[polyKey]
    time = list(intData.keys())
    dataPair = list(intData.values())
    intensity,error = zip(*dataPair)
    labelStr = polyKey
    c = Colors[polyKey]
    m = Markers[polyKey]
    
    ax.errorbar(time,intensity,yerr=error,linestyle='--',color=c,marker=m, label=labelStr,capsize=5,elinewidth=2,markeredgewidth=2)
    
box = ax.get_position()
ax.set_position([box.x0,box.y0,box.width*0.8,box.height])
ax.legend(loc='center left',bbox_to_anchor=(1,0.5),fontsize='x-small')

ax.set_xlabel('Day')

if response == 'N2_O2' or response == 'N2_O2_BC':
    #ax.set_ylabel('Normalized Intensity $(I_{N2})/(I_{O2})$')
    #ax.set_title('Normalized Intensity Plots $(I_{N2})/(I_{O2})$ Blocked by Polymer with Blue Light Fit')
    ax.set_ylabel('Intensity $(I_{N2})/(I_{O2})$')
    ax.set_title('Intensity Plots $(I_{N2})/(I_{O2})$ Blocked by Polymer with Blue Light Fit')    
elif response =='N2_Air'or response == 'N2_Air_BC':
    ax.set_ylabel('Normalized Intensity $(I_{N2})/(I_{Air})$')
    ax.set_title('Normalized Intensity Plots $(I_{N2})/(I_{Air})$ Blocked by Polymer with Blue Light Fit')
elif response == 'N2_O2_nb'or response == 'N2_O2_nb_BC':
    #ax.set_ylabel('Normalized Intensity $(I_{N2})/(I_{O2})$')
    #ax.set_title('Normalized Intensity Plots $(I_{N2})/(I_{O2})$ Blocked by Polymer')   
    ax.set_ylabel('Normalized Intensity $(I_{N2})/(I_{O2})$')
    ax.set_title('Normalized Intensity Plots $(I_{N2})/(I_{O2})$ Blocked by Polymer')
elif response == 'N2_Air_nb'or response == 'N2_Air_nb_BC':
    ax.set_ylabel('Normalized Intensity $(I_{N2})/(I_{Air})$')
    ax.set_title('Normalized Intensity Plots $(I_{N2})/(I_{Air})$ Blocked by Polymer without Blue Light Fit')
elif response == 'N2':
    ax.set_ylabel('Intensity $(I_{N2})$')
    ax.set_title('Intensity Plots $(I_{N2})$ Blocked by Polymer with Blue Light Fit')
elif response == 'N2_Lifetime':
    ax.set_ylabel('Intensity $(I_{N2})$')
    ax.set_title('Intensity Plots $(I_{N2})$ Blocked by Polymer with Blue Light Fit for Lifetime Experiment')    
elif response == 'N2_Normal':
    ax.set_ylabel('Normalized Intensity $(I_{N2})/(I_{N20})$')
    ax.set_title('Normalized Intensity Plots $(I_{N2})/(I_{N20})$ Blocked by Polymer')   
elif response == 'N2_Normal_Lifetime':    
    ax.set_ylabel('Normalized Intensity $(I_{N2})/(I_{N20})$')
    ax.set_title('Normalized Intensity Plots $(I_{N2})/(I_{N20})$ Blocked by Polymer')   
elif response == 'N2_Normal_BC':    
    ax.set_ylabel('Normalized Intensity $(I_{N2})/(I_{N20})$')
    ax.set_title('Normalized Intensity Plots $(I_{N2})/(I_{N20})$ for Beta Carotene Experiment')  
elif response == 'N2_O2_normal':
    ax.set_ylabel('Normalized Intensity $(I_{N2})/(I_{O2})$')
    ax.set_title('Normalized Intensity Plots $(I_{N2})/(I_{O2})$ Blocked by Polymer')    
    
# In[3]:

#code to more properly plot the curves
fileName = 'C:/Users/ryanm/Documents/Research/006BC_curveData.xlsm'
#fileName = 'C:/Users/ryanm/Documents/Research/lifetime_curves.xlsm'
#fileName = 'C:/Users/ryanm/Documents/Research/aging_curve_data.xlsm'
#fileName = 'C:/Users/ryanm/Documents/Research/Pt_Temperature_Peak_Data.xlsm'
#fileName = 'C:/Users/ryanm/Documents/Research/Pd_T_curves.xlsx'

xl = pd.ExcelFile(fileName)

sheetNames = xl.sheet_names
    
badNames = ['Analysis','Analysis 2','Data Analysis ','Data Summaries ','Results ','Aged','Unaged','PSUBc','PSUBc60ms','PSU_Control',
            'PSU_Control_60ms','Stern_Volmer_Data']

plt.close('all')

for sht in sheetNames:
    
    df = pd.read_excel(xl,sheet_name = sht)
    
    y_vals = []
    
    for c in df.columns:
        if 'wavelength' in str(c):
            x_vals = df[c].values
        else:
            y_vals.append(df[c].values)



    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    ax.set_xlabel('Wavelength (nm)')
    ax.set_ylabel('$I_{N_{2}}$ Photon Counts')
    
    shtString = str(sht).replace("_"," ")
    
    if 'Bc' in shtString:
        shtString = shtString.replace("Bc","Beta Carotene")
        
    if 'Nylon6' in shtString:
        shtString = shtString.replace("Nylon6","Nylon-6")
    if 'Pt' in shtString:
        shtString = shtString.replace("Pt","PtTFPP")
    
    titleString = 'Decay of Intensity in Nitrogen: Subject = ' + shtString
    ax.set_title(titleString)
    
    lineTypes = ('-','--')
    
    colors = ('red','blue','green','cyan','magenta','gray','orange','purple')
    
    dayNames = list(df.columns)
    dayNames = dayNames[1:]
    
    for y, c, day in zip(y_vals,colors,dayNames):
        if day == dayNames[0]:
            lineType = lineTypes[0]
        else:
            lineType = lineTypes[-1]
        
        dayLabel = 'Day =  '+ str(day)    
        ax.plot(x_vals,y,linestyle=lineType,color = c, label = dayLabel)
    
    #ax.xlim((,))
    ax.set_xlim((630,730))
    #ax.set_xlim((630,680))
    #ax.set_xlim((550,700))
    box = ax.get_position()
    ax.set_position([box.x0,box.y0,box.width*0.8,box.height])
    ax.legend(loc='center left',bbox_to_anchor=(1,0.5),fontsize='x-small')

# In[4]:

fileName = 'C:/Users/ryanm/Documents/Research/stern_volmer_lifetime.xlsx'

xl = pd.ExcelFile(fileName)

sheetNames = xl.sheet_names
    
badNames = ['Analysis','Analysis 2','Data Analysis ','Data Summaries ','Results ','Aged','Unaged','PSUBc','PSUBc60ms','PSU_Control',
            'PSU_Control_60ms','Stern_Volmer_Data']

for sht in sheetNames:
    if sht not in badNames:
        df = pd.read_excel(xl,sheet_name = sht)
        
        polyDict = {}
        dayDict = {}
        valueDict = {'oxygen':[],'normal':[],'predicted':[],'error':[],'R^2':[]}
        
        allPolymers = df['Polymer'].tolist()
        Polymers = []
        [Polymers.append(x) for x in allPolymers if x not in Polymers]
        
        allDays = df['Day'].tolist()
        Days = []
        [Days.append(x) for x in allDays if x not in Days]
        
        for poly in Polymers:
            for day in Days:
                valueDict = {'oxygen':[],'normal':[],'predicted':[],'error':[],'R^2':[]}
                df2 = df.loc[df.Polymer == poly]
                df3 = df2.loc[df.Day==day]
                valueDict['oxygen'] = df3['Oxygen %'].tolist()
                valueDict['normal'] = df3['I0_I'].tolist()
                valueDict['predicted'] = df3['Predicted'].tolist()
                valueDict['error'] = df3['95% CI error'].tolist()
                valueDict['R^2'] = df3['R^2'].tolist()
                
                dayDict[day] = valueDict
            polyDict[poly] = dayDict
            dayDict = {}
                
                
            
            
            

plt.close('all')
colors = ['red','green']                
for poly in polyDict.keys():
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    ax.set_xlabel('Oxygen Concentration %')
    ax.set_ylabel('$I_{0}/I$')
    ax.set_title('Stern Volmer Plot for '+str(poly)+' Host')

    for day,c in zip(polyDict[poly].keys(),colors):
        values = polyDict[poly][day]
        x = values['oxygen']
        y = values['normal']
        y_fit = values['predicted']
        err = values['error']
        R = values['R^2'][0]
        
        #ax.errorbar(time,intensity,yerr=error,linestyle='--',color=c,marker=m, label=labelStr,capsize=5,elinewidth=2,markeredgewidth=2)
        if '0.0' in str(day):
            dayStr = '0'
        else:
            dayStr = str(day)
            
        ax.errorbar(x,y_fit,yerr=err,linestyle='-',color = c, marker='o',label =('Day: '+dayStr+' $; R^{2}: $'+str(R)), capsize=5,elinewidth=2,markeredgewidth=2)
    ax.legend()            
            