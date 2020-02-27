# -*- coding: utf-8 -*-
"""
Created on Wed Nov  7 11:42:30 2018

@author: ryanm
"""

#define model function
from scipy.optimize import curve_fit
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import xlwt 
import xlrd
from xlwt import Workbook 
from xlutils.copy import copy

#set up report quality formatting for plots
import seaborn as sns
sns.set_context('poster')
#generate linearly spaced vector to eventually apply fit on to generate fitted curve
x = np.linspace(0,40000,1000)

#define template exponential function with respective coefficients 
def LifetimeExpFit(filename=None,outName = None):
    def fn(x,a,b,c):
        return a * np.exp(-b * x) + c
    #check if file exists or not 
    if filename is None or outName is None:
        raise ValueError('Please Enter a name for the input and output files: \n')
    #setup data variable with pandas dataframe
    data = pd.read_csv(filename, skiprows=8)
    #defne columns
    data.columns = ['time (ns)','photon counts','blank']
    #initialize lists
    time = []
    counts = []
    #define time from list read in by pandas dataframe functions
    time = data['time (ns)'].tolist()
    counts = data['photon counts'].tolist()
    #create indexing variable
    index = 0 
    #loop through all time values and cutoff after 40000 us 
    for i in range(0,len(time)):
        if time[i] >= 40000:
            index = i 
            break
    #delete cutoff data
    del(time[index:])
    del(counts[index:])
    
    #apply fit to raw data and
    fit_params, pcov = curve_fit(fn, time,counts,p0=(0,0,0))
    x = np.linspace(0,40000,1000)
    #compute fitted values
    values = fn(x,fit_params[0],fit_params[1],fit_params[2])
    #extract lifetime from fitted coefficient
    lifetime = 1 / fit_params[1]
    #plot results for given sample
    fig = plt.figure()
    ax = plt.axes()
    ax.scatter(time,counts,color='blue',label = 'Raw Data')
    ax.plot(x, values, 'r-',linewidth=2.0,label = 'Exponential Fit')
    ax.set_xlabel('Time (ns)')
    ax.set_ylabel('Photon Counts')
    ax.set_title(outName)
    textString = 'Lifetime: '+str(round(lifetime/1000,2)) +' (us)'
    ax.text(20000,300,textString)
    ax.legend()
    
    fig.savefig(outName+".png")
    

    
    return lifetime, fit_params


def MainFn():

    plt.close()
    check = False
    counter = 0
    file = []
    fileIn =[]
    name = []
    acceptedInput = ['y','Y','n','N','a','A']
    parameters = np.array([])
    
    spreadsheet = input('Enter a name for the output spreadsheet to be saved in cwd: ')
    
    spreadsheet = spreadsheet + '.xls'
    
    while not check:
        try:
            fileIn = input('Enter a file name for text file '+str(counter+1) + ' : ')
            nameSamp = input('Enter a file output name for sample ' +str(counter+1) + ' :')
            userCheck = input('Enter more values? Enter Y/N Append to existing File? Enter a/A: ')
            
            if userCheck not in acceptedInput:
                raise ValueError('Please Enter Y/N: ')
                
            if userCheck == 'n' or userCheck == 'N' or userCheck =='A' or userCheck =='a':
                check = True
            if userCheck =='y' or 'Y' or len(file) == 0:
                file.append(fileIn)
                name.append(nameSamp)
                counter +=1
                
        except:
            continue
    
    
    
    if userCheck == 'a' or userCheck == 'A':
        
        book = xlrd.open_workbook(spreadsheet)
        first_sheet = book.sheet_by_index(0)
        col = first_sheet.col(0)
        rowCt = len(col) 
        
        wb = copy(book)
        work_sheet = wb.get_sheet(0)
        
        if len(file) == 1:
                lifetime_result,parameters = LifetimeExpFit(file[0],name[0])
                work_sheet.write(rowCt,0, name[0])
                work_sheet.write(rowCt,1, lifetime_result/1000)
                work_sheet.write(rowCt,2, parameters[0])
                work_sheet.write(rowCt,3, parameters[1])
                work_sheet.write(rowCt,4, parameters[2])
            
        else:
            
            for sampNum in range(0,len(file)):
                lifetime_result,parameters = LifetimeExpFit(file[sampNum],name[sampNum])
                work_sheet.write(sampNum+rowCt,0, name[sampNum])
                work_sheet.write(sampNum+rowCt,1, lifetime_result/1000)
                work_sheet.write(sampNum+rowCt,2, parameters[0])
                work_sheet.write(sampNum+rowCt,3, parameters[1])
                work_sheet.write(sampNum+rowCt,4, parameters[2])
            
        wb.save(spreadsheet)
        
    else:
        
        wb = Workbook()    
        sheet1 = wb.add_sheet('Lifetime Data')
        
        sheet1.write(0,0, 'Sample Description')
        sheet1.write(0,1, 'Lifetime (us)')
        sheet1.write(0,2, 'a')
        sheet1.write(0,3, 'b')
        sheet1.write(0,4, 'c')
        sheet1.write(0,6,'Time (ns)')
        
        for i in range(0,len(x)):
            sheet1.write(i+1,6,x[i])
        
        P = np.zeros((len(file),3))
        y = np.zeros(len(x))
        
        for sampNum in range(0,len(file)):
            lifetime_result,parameters = LifetimeExpFit(file[sampNum],name[sampNum])
            sheet1.write(sampNum+1,0, name[sampNum])
            sheet1.write(sampNum+1,1, lifetime_result/1000)
            sheet1.write(sampNum+1,2, parameters[0])
            sheet1.write(sampNum+1,3, parameters[1])
            sheet1.write(sampNum+1,4, parameters[2])
            
            sheet1.write(0,sampNum + 7,name[sampNum])
            
            P[sampNum][0] = parameters[0]
            P[sampNum][1] = parameters[1]
            P[sampNum][2] = parameters[2]
            
        
        for sample in range(0,len(file)):
            y = P[sample][0] * np.exp(-P[sample][1]*x) + P[sample][2]
            
            for i in range(0,len(x)):
                sheet1.write(i+1,sample+7,y[i])
                
        
            """if sampNum == 0:
                parametersTot = parameters
            else:
                parametersTot = np.vstack((parametersTot,parameters))"""
            
        wb.save(spreadsheet) 
            
            
    
    
            
    #LifetimeExpFit(file[0],name[0])



if __name__=='__main__':
    MainFn()



