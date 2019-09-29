# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 13:10:02 2019

@author: ryanm
"""

"""
To DO:
    -add code that extrapolates the data to the peak value (add artificial wavelengths to the real data)
    -investigate the more advanced fits 
    -record fit value
    -update ratios and statistics
    -generate report plots 
    -investigate odd behavior with exponentials
"""
#custom imports
import scan_excel as SE
import fit_code as fit
##############################
import numpy as np 
import pandas as pd
import seaborn as sns
import importlib
import R_square as R2

from PyQt5.uic import loadUiType

from matplotlib.figure import Figure 

import matplotlib.pyplot as plt

from matplotlib.backends.backend_qt5agg import(FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar)

Ui_MainWindow, QMainWindow = loadUiType('blf.ui')

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QInputDialog
        

class Main(QMainWindow, Ui_MainWindow):
    #put signals and slots here 
    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)
        
        self.fig_dict = {}
        self.xlFileName = ""
        self.outputDir = ""
        self.dye = "Pt"
        self.expKey = "photobleaching"
        self.polymerObjects ={}
        self.fitType = "expSingle"
        self.xrange = [550,620] #default value 
        self.xrange2 = [720,800]
        self.currentFigKey = "" 
        self.peakWave = {'Pd':673.93,'Pt':652.35,'Ru':604.49}
        self.method = 0 #0 for extrapolation, 1 for interpolation
        self.blueFitMethod = 1 
        self.R2file = '' 
        
        #reporting variables
        
        self.reportOptions = {'plots':{'single':0,'all':1},'blueLight':{'use':0,'none':1},'normalized':{'normal':0,'none':1},
                              'errorBars':{'std':0,'CI':1},'blueMethod':{'one':1,'all':2}}
        #self.plotOption = 1 #all samples
        self.blueLight = 0 #apply the fits
        self.normalized = 0 #normalize the data
        self.errorBar = 1 # add ci error bars 
        
        self.reportSamples = {}
        #define polynomial degree widget
        self.QList = QListWidget()
        
        self.deg = "2"
        self.QList.setWindowTitle('Select Polynomial degree')
        self.QList.resize(350,120)
        self.QList.addItem("1")
        self.QList.addItem("2")
        self.QList.addItem("3")
        self.QList.addItem("4")
        self.QList.addItem("5")
        self.QList.addItem("6")
        self.QList.addItem("7")
        
        self.QList.itemClicked.connect(self.degListClicked)
        
        #initialize tree widget
        
        self.sample_treeWidget.setAlternatingRowColors(True)
        #self.sample_treeWidget.itemClicked.connect(self.changefig)
        self.sample_treeWidget.itemClicked.connect(self.setFigData)
        self.sample_treeWidget.setHeaderLabels(['Polymer','Sample','Time'])
        
        
        #initialize list dropdown
        
        self.exp_comboBox.addItem("Aging Experiment")
        self.exp_comboBox.addItem("Lifetime Experiment")
        self.exp_comboBox.addItem("Temperature Agglomeration Experiment")
        
        self.exp_comboBox.currentTextChanged.connect(self.setTreeCols)
        
        #define excel search button
        
        self.excelChoose_pushButton.clicked.connect(self.setxlFile)
        self.excel_lineEdit.textEdited.connect(self.setxlFile_lineEdit)
        
        #define where to save output data         
        self.fileChoose_pushButton.clicked.connect(self.setoutputDir)
        self.fileLoc_lineEdit.textEdited.connect(self.setoutputDir_lineEdit)
        
        #define dropbox for user to select dye 
        #assuming first item in list below is the default selected item.  hard coded for now due to lack of dev time
        
        self.dye_comboBox.addItem("Pt")
        self.dye_comboBox.addItem("Pd")
        self.dye_comboBox.addItem("Ru")
        
        self.dye_comboBox.currentTextChanged.connect(self.setDye)
        
        #connect toggle buttons with correct fitting method
        self.method1_radioButton.toggled.connect(self.method1Toggle)
        self.method1_radioButton.setChecked(True)
        self.method2_radioButton.toggled.connect(self.method2Toggle)
        
        #instruct code what to do when the user selects run 
        self.run_pushButton.clicked.connect(self.run)
        
        #assign what happens when the bounds are changed
        self.LB_lineEdit.textEdited.connect(self.lbEdit)
        self.RB_lineEdit.textEdited.connect(self.rbEdit)
        
        self.LB2_lineEdit.textEdited.connect(self.lb2Edit)
        self.RB2_lineEdit.textEdited.connect(self.rb2Edit)
        
        self.R2_lineEdit.textEdited.connect(self.setR2file)
        
        #clear the fitted curve from plot
        self.clearButton.clicked.connect(self.clearFit)
        #assign code to the curve fit push buttons 
        
        #polynomial
        self.polyButton.clicked.connect(self.fitPoly)
        #single Exponential
        self.singleExpButton.clicked.connect(self.fitSingleExp)
        #double exponential
        self.dblExpButton.clicked.connect(self.fitDblExp)
        #logarithmic
        self.logButton.clicked.connect(self.fitLog)
        #Huber Curve
        self.hubertButton.clicked.connect(self.fitHubert)
        #sigmoidal
        self.sigButton.clicked.connect(self.fitSigmoid)
        
        #reporting widgets
        self.samp_radioButton.toggled.connect(self.setOptions)
        self.allSamp_radioButton.toggled.connect(self.setOptions)
        self.BL_radioButton.toggled.connect(self.setOptions)
        self.noBL_radioButton.toggled.connect(self.setOptions)
        self.normal_radioButton.toggled.connect(self.setOptions)
        self.noNormal_radioButton.toggled.connect(self.setOptions)
        self.std_radioButton.toggled.connect(self.setOptions)
        self.CI_radioButton.toggled.connect(self.setOptions)
        
        self.allSamp_radioButton.setChecked(True)
        self.BL_radioButton.setChecked(True)
        self.normal_radioButton.setChecked(True)
        self.CI_radioButton.setChecked(True)
        
        self.reportSamples_listWidget.clicked.connect(self.updateReportSamples)
        
        self.reportButton.clicked.connect(self.generateReport)
        
        self.blueMethod1_radioButton.toggled.connect(self.setOptions)
        self.blueMethod2_radioButton.toggled.connect(self.setOptions)
        
        self.blueMethod1_radioButton.setChecked(True)
        
        self.excelOutput_pushButton.clicked.connect(self.excelOutput_clicked)
        
    def closeEvent(self,event):
        print("Exiting Program")
        #exit()
        sys.exit()
        
    def setFitRange(self):
        if self.expKey != 'temperature':
            xlabelN2 = self.N2Data.columns.tolist()[0]  
            self.N2FitRange = self.N2Data[(self.N2Data[xlabelN2]>=self.xrange[0])&(self.N2Data[xlabelN2]<=self.xrange[1])]            
            
            xlabelO2 = self.O2Data.columns.tolist()[0]
            self.O2FitRange =self.O2Data[(self.O2Data[xlabelO2]>=self.xrange[0])&(self.O2Data[xlabelO2]<=self.xrange[1])]
        
        xlabelAir = self.AirData.columns.tolist()[0]
        self.AirFitRange = self.AirData[(self.AirData[xlabelAir]>=self.xrange[0])&(self.AirData[xlabelAir]<=self.xrange[1])] 
        
    def setFitRange2(self):
        if self.expKey != 'temperature':
            xlabelN2 = self.N2Data.columns.tolist()[0]  
            self.N2FitRange2 = self.N2Data[(self.N2Data[xlabelN2]>=self.xrange2[0])&(self.N2Data[xlabelN2]<=self.xrange2[1])]            
            
            xlabelO2 = self.O2Data.columns.tolist()[0]
            self.O2FitRange2 =self.O2Data[(self.O2Data[xlabelO2]>=self.xrange2[0])&(self.O2Data[xlabelO2]<=self.xrange2[1])]
        
        xlabelAir = self.AirData.columns.tolist()[0]
        self.AirFitRange2 = self.AirData[(self.AirData[xlabelAir]>=self.xrange2[0])&(self.AirData[xlabelAir]<=self.xrange2[1])] 
        
    def setFigData(self,item):
        """ takes the currently selected polymer set, and stores the plot data variables
        """
        if (item.childCount() == 0) :
            if self.expKey == 'photobleaching':
                daySelected = item.text(0)
                parent1 = item.parent()
                sample = parent1.text(0)
                parent2 = parent1.parent()
                polyName = parent2.text(0)
                self.selectedPoly = self.polymerObjects[polyName]
                self.selectedSample = sample
                self.selectedDay = daySelected
                
                self.N2Data = self.selectedPoly.N2curve[sample][float(daySelected)]
                self.O2Data = self.selectedPoly.O2curve[sample][float(daySelected)]
                self.AirData = self.selectedPoly.Aircurve[sample][float(daySelected)]
            elif self.expKey == 'lifetime':
                sample = item.text(0)
                parent1 = item.parent()
                duration = parent1.text(0)
                parent2 = parent1.parent()
                polyName = parent2.text(0)
                self.selectedPoly = self.polymerObjects[polyName]
                self.selectedSample = sample
                self.selectedDuration = duration

                self.N2Data = self.selectedPoly.N2curve[duration][sample]
                self.O2Data = self.selectedPoly.O2curve[duration][sample]
                self.AirData = self.selectedPoly.Aircurve[duration][sample]
            elif self.expKey == 'temperature':
                daySelected = item.text(0)
                parent1 = item.parent()
                sample = parent1.text(0)
                parent2 = parent1.parent()
                polyName = parent2.text(0)
                self.selectedPoly = self.polymerObjects[polyName]
                self.selectedSample = sample
                self.selectedDay = daySelected
                
                self.AirData = self.selectedPoly.Aircurve[sample][float(daySelected)]
        
            self.setFitRange()
            
            if self.expKey != 'temperature':
                
                xlabelN2 = self.N2Data.columns.tolist()[0]  
                xlabelO2 = self.O2Data.columns.tolist()[0]
                ylabelN2 = self.N2Data.columns.tolist()[1]      
                ylabelO2 = self.O2Data.columns.tolist()[1]
            
            xlabelAir = self.AirData.columns.tolist()[0]
            
            ylabelAir = self.AirData.columns.tolist()[1]
            
            #plot the different gas spectrometer measurements
            fig = Figure()
            ax = fig.add_subplot(111)
            
            if self.expKey != 'temperature':
                ax.plot(self.N2Data[xlabelN2].values,self.N2Data[ylabelN2],color='red',label='N2 Intensity')
                ax.plot(self.O2Data[xlabelO2],self.O2Data[ylabelO2],color='blue',label='O2 Intensity')
                
            ax.plot(self.AirData[xlabelAir],self.AirData[ylabelAir],color='purple',label='Air Intensity')
            ax.set_xlabel('Wavelength (nm)')
            ax.set_ylabel('Photon Counts')
            ax.set_title('Spectrometer Intensity Readings')
            ax.legend(loc='upper right')
            
            if self.expKey == 'photobleaching':
                self.figKey = polyName + '&'+sample +'&'+ daySelected
                self.changefig(self.figKey,fig)                
            elif self.expKey == 'lifetime':
                self.figKey = polyName + '&' + duration+ '&' + sample
                self.changefig(self.figKey,fig)
            elif self.expKey == 'temperature':
                self.figKey = polyName + '&' + sample + '&' + daySelected
                self.changefig(self.figKey,fig)
                
            #self.figKey = polyName + ' '+sample +' '+ daySelected
            #self.changefig(self.figKey,fig)
            
            
            
    def FitData(self):
        if self.expKey != 'temperature':
            colHeadersN2 = self.N2FitRange.columns.tolist()
            colHeadersO2 = self.O2FitRange.columns.tolist()
        colHeadersAir = self.AirFitRange.columns.tolist()
        
        if self.method == 0 :
            x0 = self.xrange[1] + 0.001*self.xrange[1]
            x2 = self.peakWave[self.dye]
            extraData = pd.Series(np.linspace(x0,x2,100))
            
            if self.expKey != 'temperature':
                self.xfitN2Waves = self.N2FitRange[colHeadersN2[0]].append(extraData,ignore_index=True)
                self.xfitO2Waves = self.O2FitRange[colHeadersO2[0]].append(extraData,ignore_index=True)
            self.xfitAirWaves = self.AirFitRange[colHeadersAir[0]].append(extraData,ignore_index=True)
            
            if self.expKey != 'temperature':
                self.paramN2,self.param_covN2 = fit.fitCurve(xdata = self.N2FitRange[colHeadersN2[0]], 
                                                 ydata =self.N2FitRange[colHeadersN2[1]],fitType = self.fitType )
                self.paramO2,self.param_covO2 = fit.fitCurve(xdata = self.O2FitRange[colHeadersO2[0]],
                                                             ydata = self.O2FitRange[colHeadersO2[1]],fitType=self.fitType)
            self.paramAir,self.param_covAir = fit.fitCurve(xdata=self.AirFitRange[colHeadersAir[0]],
                                                           ydata=self.AirFitRange[colHeadersAir[1]],fitType=self.fitType)
            
            if self.expKey != 'temperature':
                yfitted = fit.applyFit(self.xfitO2Waves,self.paramO2,self.fitType)
                ydata = self.O2FitRange[colHeadersO2[1]]
            else:
                yfitted = fit.applyFit(self.xfitAirWaves,self.paramAir,self.fitType)
                ydata = self.AirFitRange[colHeadersAir[1]]                
            
            yi = ydata.values
            yf = yfitted.values
            yf = yf[:ydata.size]
            
            R = R2.coefficient_of_determination(yi,yf)
            
            if self.expKey == 'photobleaching':
                dayDict = {self.selectedDay:R}
                sampleDict = {self.selectedSample:dayDict}
                
                if self.selectedSample in self.selectedPoly.RSquare.keys():
                    self.selectedPoly.RSquare[self.selectedSample].update(dayDict)
                else:
                    self.selectedPoly.RSquare.update(sampleDict)
                    
            elif self.expKey == 'lifetime':
                if self.selectedDuration in self.selectedPoly.RSquare.keys():
                    self.selectedPoly.RSquare[self.selectedDuration].update({self.selectedSample:R})
                else:
                    self.selectedPoly.RSquare.update({self.selectedDuration:{self.selectedSample:R}})
            elif self.expKey == 'temperature':
                
                if self.selectedSample in self.selectedPoly.RSquare.keys():
                    self.selectedPoly.RSquare[self.selectedSample].update({self.selectedDay:R})
                else:
                    self.selectedPoly.RSquare.update({self.selectedSample:{self.selectedDay:R}})
                
            self.polymerObjects[self.selectedPoly.name] = self.selectedPoly
        
        elif self.method == 1:
            
            if self.expKey != 'temperature':
                self.xfitN2Waves = self.N2FitRange[colHeadersN2[0]].append(self.N2FitRange2[colHeadersN2[0]],ignore_index=True)
                self.xfitO2Waves = self.O2FitRange[colHeadersO2[0]].append(self.O2FitRange2[colHeadersO2[0]],ignore_index=True)

                self.yfitN2Waves = self.N2FitRange[colHeadersN2[1]].append(self.N2FitRange2[colHeadersN2[1]],ignore_index=True)
                self.yfitO2Waves = self.O2FitRange[colHeadersO2[1]].append(self.O2FitRange2[colHeadersO2[1]],ignore_index=True)
            
            self.xfitAirWaves = self.AirFitRange[colHeadersAir[0]].append(self.AirFitRange2[colHeadersAir[0]],ignore_index=True)
            
            self.yfitAirWaves = self.AirFitRange[colHeadersAir[1]].append(self.AirFitRange2[colHeadersAir[1]],ignore_index=True)
            
            if self.expKey != 'temperature':
                self.paramN2,self.param_covN2 = fit.fitCurve(xdata = self.xfitN2Waves, 
                                     ydata =self.yfitN2Waves,fitType = self.fitType )
                self.paramO2,self.param_covO2 = fit.fitCurve(xdata = self.xfitO2Waves,
                                     ydata = self.yfitO2Waves,fitType=self.fitType)
            self.paramAir,self.param_covAir = fit.fitCurve(xdata= self.xfitAirWaves,
                               ydata=self.yfitAirWaves,fitType=self.fitType)
            
            if self.expKey != 'temperature':
                yfitted = fit.applyFit(self.xfitO2Waves,self.paramO2,self.fitType)
                
                ydata = self.O2FitRange[colHeadersO2[1]].append(self.O2FitRange2[colHeadersO2[1]],ignore_index=True)
            else:
                yfitted = fit.applyFit(self.xfitAirWaves,self.paramAir,self.fitType)
                
                ydata = self.AirFitRange[colHeadersAir[1]].append(self.AirFitRange2[colHeadersAir[1]],ignore_index=True)                
            
            yi = ydata.values
            yf = yfitted.values
            
            R = R2.coefficient_of_determination(yi,yf)
            
            if self.expKey == 'photobleaching':
                dayDict = {self.selectedDay:R}
                sampleDict = {self.selectedSample:dayDict}
                if self.selectedSample in self.selectedPoly.RSquare.keys():
                    self.selectedPoly.RSquare[self.selectedSample].update(dayDict)
                else:
                    self.selectedPoly.RSquare.update(sampleDict)
            elif self.expKey == 'lifetime':
                if self.selectedDuration in self.selectedPoly.RSquare.keys():
                    self.selectedPoly.RSquare[self.selectedDuration].update({self.selectedSample:R})
                else:
                    self.selectedPoly.RSquare.update({self.selectedDuration:{self.selectedSample:R}})
            elif self.expKey == 'temperature':
                if self.selectedSample in self.selectedPoly.RSquare.keys():
                    self.selectedPoly.RSquare[self.selectedSample].update({self.selectedDay:R})
                else:
                    self.selectedPoly.RSquare.update({self.selectedSample:{self.selectedDay:R}})
            
        #start generating plot data here 
        #going to fit based on the air curve data
        #yfitted = fit.applyFit(self.O2FitRange[colHeadersO2[0]],self.paramO2,self.fitType)
        
        if hasattr(self,'figKey'):
            fig = self.fig_dict[self.figKey]
            ax = fig.gca()
            for line in ax.lines:
                if 'Extrapolated Blue Light Curve' == line.get_label():
                    ax.lines.remove(line)
                    break
            self.saveBlueOverlap()
            #ax.plot(self.O2FitRange[colHeadersO2[0]],yfitted,'--',color='green',label='Extrapolated Blue Light Curve')
            if self.expKey != 'temperature':
                ax.plot(self.xfitO2Waves,yfitted,'--',color='green',label='Extrapolated Blue Light Curve')
            else:
                ax.plot(self.xfitAirWaves,yfitted,'--',color='green',label='Extrapolated Blue Light Curve')
            
            ax.legend(loc='upper right')
            #self.fig_dict[self.figKey] = fig
            self.changefig(self.figKey,fig)
        
        
        
    def saveBlueOverlap(self):
        polyIDs = self.figKey.split('&')
        if self.expKey == 'photobleaching':
            name = polyIDs[0]
            sample = polyIDs[1]
            day = float(polyIDs[2])
            waveLength = self.peakWave[self.dye]
            blueFitVal = fit.applyFit(waveLength,self.paramO2,self.fitType)
            poly = self.polymerObjects[name]
            
            if sample in poly.O2BlueFit.keys():
                poly.O2BlueFit[sample].update({day:blueFitVal})
            else:
                poly.O2BlueFit.update({sample:{day:blueFitVal}})
                
            self.polymerObjects[name] = poly
        elif self.expKey == 'lifetime':
            name = polyIDs[0]
            duration = polyIDs[1]
            sample = polyIDs[2]
            waveLength = self.peakWave[self.dye]
            blueFitVal = fit.applyFit(waveLength,self.paramO2,self.fitType)
            poly = self.polymerObjects[name]
            if duration in poly.O2BlueFit.keys():
                poly.O2BlueFit[duration].update({sample:blueFitVal})
            else:    
                poly.O2BlueFit.update({duration:{sample:blueFitVal}})
            self.polymerObjects[name] = poly
            
        elif self.expKey == 'temperature':
            name = polyIDs[0]
            sample = polyIDs[1]
            day = float(polyIDs[2])
            waveLength = self.peakWave[self.dye]
            blueFitVal = fit.applyFit(waveLength,self.paramAir,self.fitType)
            poly = self.polymerObjects[name]
            
            if sample in poly.AirBlueFit.keys():
                poly.AirBlueFit[sample].update({day:blueFitVal})
            else:
                poly.AirBlueFit.update({sample:{day:blueFitVal}})
                
            self.polymerObjects[name] = poly
                    
    def addmpl(self, fig):
        self.canvas = FigureCanvas(fig)
        self.mplvl.addWidget(self.canvas)
        self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas, self.mplwindow,coordinates = True)
        self.mplvl.addWidget(self.toolbar)
        
    def rmpl(self,):
        self.mplvl.removeWidget(self.canvas)
        self.canvas.close()
        self.mplvl.removeWidget(self.toolbar)
        self.toolbar.close()
        
    def changefig(self, key,fig):
        if key not in self.fig_dict.keys():
            self.fig_dict[key] = fig
        if hasattr(self,'canvas'):
            self.rmpl()
        self.addmpl(self.fig_dict[key])
        
    """
    def addfig(self, name, fig):
        self.fig_dict[name] = fig
        listItem = QTreeWidgetItem(self.sample_treeWidget,[name])
        self.sample_treeWidget.addTopLevelItem(listItem)
    """
        
    def setTreeCols(self,expType):
        if "Aging Experiment" in expType:
            self.sample_treeWidget.clear()
            self.sample_treeWidget.setHeaderLabels(['Polymer','Sample','Time'])
            self.expKey = "photobleaching"
            
            if not (self.polymerObjects):
                return
            else:
                
                for key in self.polymerObjects.keys():
                    poly = self.polymerObjects[key]
                    li = QTreeWidgetItem(self.sample_treeWidget,[key])
                    for cat in poly.Category:
                        sampChild = QTreeWidgetItem(li,[cat])
                        li.addChild(sampChild)
                        for t in poly.Time:
                            timeChild = QTreeWidgetItem(sampChild,[str(t)])
                            
                            sampChild.addChild(timeChild)
                    
                    self.sample_treeWidget.addTopLevelItem(li)
                    
        elif "Lifetime Experiment" in expType:
            self.expKey = "lifetime"
            self.sample_treeWidget.clear()
            self.sample_treeWidget.setHeaderLabels(['Polymer','Aged/Unaged','Sample'])
            
            if not (self.polymerObjects):
                return
            else:
                
                for key in self.polymerObjects.keys():
                    poly = self.polymerObjects[key]
                    li = QTreeWidgetItem(self.sample_treeWidget,[key])
                    for dur in poly.IAir.keys():
                        durChild = QTreeWidgetItem(li,[dur])    
                        for cat in poly.Category:
                            sampChild = QTreeWidgetItem(durChild,[cat])
                    self.sample_treeWidget.addTopLevelItem(li)
                    
        elif "Temperature Agglomeration Experiment" in expType:
            self.expKey = 'temperature'
            self.sample_treeWidget.clear()
            self.sample_treeWidget.setHeaderLabels(['PSU Dye Load','Sample','Time'])
            
            if not (self.polymerObjects):
                return
            else:
                for key in self.polymerObjects.keys():
                    poly = self.polymerObjects[key]
                    li = QTreeWidgetItem(self.sample_treeWidget,[key])
                    for cat in poly.Category:
                        sampChild = QTreeWidgetItem(li,[cat])
                        li.addChild(sampChild)
                        for t in poly.Time:
                            timeChild = QTreeWidgetItem(sampChild,[str(t)])
                            
                            sampChild.addChild(timeChild)
                            
                    self.sample_treeWidget.addTopLevelItem(li)
            
    def setxlFile(self):
        fname = QFileDialog.getOpenFileName(self,'Open file', 
         'c:\\',"Excel files (*.xlsx *.xlsm)")
        self.xlFileName = fname[0]
        self.excel_lineEdit.setText(fname[0])
        
    def setoutputDir(self):
        dirname = QFileDialog.getExistingDirectory(self,"Select Directory for Analysis output")
        self.outputDir = dirname
        self.fileLoc_lineEdit.setText(dirname)
        
    def setxlFile_lineEdit(self, item):
        self.xlFileName = item 
        
    def setoutputDir_lineEdit(self,item):
        self.outputDir = item
        
        
    def setDye(self,item):
        self.dye = item
        
    def run(self):
        self.sample_treeWidget.clear()
        #self.polymerObjects.update( SE.loadExcelData(self.xlFileName,self.expKey,self.dye) ) 
        
        #*******************************************************************************
        self.polymerObjects =  SE.loadExcelData(self.xlFileName,self.expKey,self.dye)  
        #*******************************************************************************
        
        #print('Data Successfully Loaded')
        msg = QMessageBox()
        msg.setText("Data Successfully Loaded")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.exec_()
        self.setTreeCols(self.exp_comboBox.currentText())
        self.setReportSampleList()
        
    def setReportSampleList(self):
        self.reportSamples_listWidget.clear()
        self.reportSamples.clear()
        for key in self.polymerObjects.keys():
            self.reportSamples_listWidget.addItem(key)
    def updateReportSamples(self,item):
        #$self.reportSamples.update({item.text():self.polymerObjects[item.text()]})
        goodKeys = list()
        badKeys = list()
        for item in self.reportSamples_listWidget.selectedItems():
            self.reportSamples.update({item.text():self.polymerObjects[item.text()]})
            goodKeys.append(item.text())
        for key in self.reportSamples.keys():
            if key not in goodKeys:
                badKeys.append(key)
        for bdKey in badKeys:
            self.reportSamples.pop(bdKey)
        
    def fitPoly(self):
        self.QList.show()

    def fitSingleExp(self):
        self.fitType = "expSingle"
        if hasattr(self,'figKey'):
            self.FitData()
            
    def fitDblExp(self):
        self.fitType = "expDouble"
        if hasattr(self,'figKey'):
            self.FitData()
    def fitLog(self):
        self.fitType = "logarithmic"
        if hasattr(self,'figKey'):
            self.FitData()
            
    def fitSigmoid(self):
        self.fitType = "Sigmoidal"
        if hasattr(self,'figKey'):
            self.FitData()
            
    def fitHubert(self):
        self.fitType = "Hubert"
        if hasattr(self,'figKey'):
            self.FitData()
        
    def degListClicked(self,item):
        self.fitType = "poly" + item.text()
        QMessageBox.information(self,"ListWidget","You Clicked: "+item.text())
        self.QList.hide()
        if hasattr(self,'figKey'):
            self.FitData()
        
    def lbEdit(self,item):
        self.xrange[0] = float(item)
        
        self.setFitRange()
        
        
    def rbEdit(self,item):
        self.xrange[1] = float(item)
        
        self.setFitRange()
        
    def lb2Edit(self,item):
        self.xrange2[0] = float(item)
        
        self.setFitRange2()
    def rb2Edit(self,item):
        self.xrange2[1] = float(item)
        
        self.setFitRange2()
        
    def clearFit(self):
        if hasattr(self,'figKey'):
            fig = self.fig_dict[self.figKey]
            ax = fig.gca()
            for line in ax.lines:
                if 'Extrapolated Blue Light Curve' == line.get_label():
                    ax.lines.remove(line)
                    ax.legend(loc='upper right')
                    self.changefig(self.figKey,fig)
                    self.selectedPoly.O2BlueFit.clear()
                    self.polymerObjects[self.selectedPoly.name] = self.selectedPoly
                    break
    def method1Toggle(self):
        self.method = 0 
        self.LB2_lineEdit.setEnabled(False)
        self.RB2_lineEdit.setEnabled(False)
    def method2Toggle(self):
        self.method=1
        self.LB2_lineEdit.setEnabled(True)
        self.RB2_lineEdit.setEnabled(True)
        self.setFitRange2()
        
    def RSquared(self,ydata,yfit):
        SSReg = np.sum(np.power((yfit-np.average(yfit)),2))
        SSTotal = np.sum(np.power((ydata-np.average(ydata)),2))
        
        RSquare = 1 - (SSReg/SSTotal)
        
        return RSquare
    
    #report gui tab functions
    
    def setOptions(self):
        if self.samp_radioButton.isChecked():
            self.reportSamples_listWidget.setSelectionMode(QAbstractItemView.SingleSelection)
            
        elif self.allSamp_radioButton.isChecked():
            self.reportSamples_listWidget.setSelectionMode(QAbstractItemView.MultiSelection)
            
        if self.BL_radioButton.isChecked():
            self.blueLight = self.reportOptions['blueLight']['use']
            
        elif self.noBL_radioButton.isChecked():
            self.blueLight = self.reportOptions['blueLight']['none']
            
        if self.normal_radioButton.isChecked():
            self.normalized = self.reportOptions['normalized']['normal']
            
        elif self.noNormal_radioButton.isChecked():
            self.normalized = self.reportOptions['normalized']['none']
            
        if  self.std_radioButton.isChecked():
            self.errorBar = self.reportOptions['errorBars']['std']
            
        elif self.CI_radioButton.isChecked():
            self.errorBar = self.reportOptions['errorBars']['CI']
            
        if self.blueMethod2_radioButton.isChecked():
            self.blueFitMethod = self.reportOptions['blueMethod']['one']
            
        elif self.blueMethod1_radioButton.isChecked():
            self.blueFitMethod = self.reportOptions['blueMethod']['all']
    
    def formatPlot(self,fig,xlabel,ylabel,title,sensitivity):
         
        ax = plt.subplot(111)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        
        for key in self.reportSamples.keys():
                    
            Poly = self.polymerObjects[key]
            
            #apply blue light fit an error bars 
            if self.blueLight == 0: #apply the fit if zero
                if self.expKey != 'temperature':
                    IN2vals,IAirvals,IO2vals = Poly.subtractBlueLight(method=self.blueFitMethod,expType=self.expKey)
                    if self.normalized == 0:
                        IN2norm,IAirnorm,IO2norm = Poly.normalize(self.expKey,IN2vals,IAirvals,IO2vals)
                        IN2Airnorm,IN2O2norm = Poly.updateRatios(self.expKey,IN2norm,IAirnorm,IO2norm)    
                        Poly.updateSumStats(self.expKey,IN2norm,IAirnorm,IO2norm,IN2Airnorm,IN2O2norm)
                        
                    elif self.normalized == 1:
                        IN2_Airvals, IN2_O2vals = Poly.updateRatios(self.expKey,IN2vals,IAirvals,IO2vals)
                        Poly.updateSumStats(self.expKey,IN2vals,IAirvals,IO2vals,IN2_Airvals,IN2_O2vals)
                else:
                    IAirvals = Poly.subtractBlueLight(method=self.blueFitMethod,expType=self.expKey)
                    print('Intensities after subtraction')
                    print(IAirvals)
                    print('blue')
                    print(Poly.AirBlueFit)
                    
                    if self.normalized ==0:
                        IAirnorm = Poly.normalize(self.expKey,IAir=IAirvals)
                        Poly.updateSumStats(self.expKey,IAir=IAirnorm)
                    elif self.normalized ==1:
                        Poly.updateSumStats(self.expKey,IAir=IAirvals)
                        
            else:
                if self.expKey != 'temperature':
                    if self.normalized ==0:
                        IN2norm,IAirnorm,IO2norm = Poly.normalize(self.expKey,Poly.IN2,Poly.IAir,Poly.IO2)
                        IN2Airnorm,IN2O2norm = Poly.updateRatios(self.expKey,IN2norm,IAirnorm,IO2norm)
                        Poly.updateSumStats(self.expKey,IN2norm,IAirnorm,IO2norm,IN2Airnorm,IN2O2norm)
                    elif self.normalized ==1:
                        IN2_Airvals, IN2_O2vals = Poly.updateRatios(self.expKey,Poly.IN2,Poly.IAir,Poly.IO2)
                        Poly.updateSumStats(self.expKey,Poly.IN2,Poly.IAir,Poly.IO2,IN2_Airvals,IN2_O2vals)
                else:
                    if self.normalized ==0:
                        IAirnorm = Poly.normalize(self.expKey,IAir=Poly.IAir)
                        Poly.updateSumStats(self.expKey,IAir=IAirnorm)
                    elif self.normalized ==1:
                        Poly.updateSumStats(self.expKey,IAir = Poly.IAir)
            #********************************************************************
            """
            if self.normalized ==0:
                #Poly.normalize(self.expKey)
                if self.expKey != 'temperature':
                    (IN2norm,IAirnorm,IO2norm) = Poly.normalize(self.expKey)
                    (IN2Airnorm,IN2O2norm) = Poly.updateRatios(self.expKey,IN2norm,IAirnorm,IO2norm)
                    Poly.updateSumStats(self.expKey,IN2norm,IAirnorm,IO2norm,IN2Airnorm,IN2O2norm)
                else:
                    (IAirnorm) = Poly.normalize(self.expKey)
                    print(IAirnorm)
                    Poly.updateSumStats(self.expKey,IAir=IAirnorm)
                    
            """    
            Poly.addErrorBars(errtype=self.errorBar,expType = self.expKey)
                
            if self.expKey == 'photobleaching':
                #plt.plot(Poly.Time,Poly.IN2_AirAvg)
                if sensitivity == 0:
                    ax.errorbar(Poly.Time,Poly.IN2_AirAvg,yerr = Poly.errorBarsN2Air,capsize=6,marker='.',label = key)
                elif sensitivity == 1:
                    ax.errorbar(Poly.Time,Poly.IN2_O2Avg,yerr = Poly.errorBarsN2O2,capsize=6,marker='.',label = key)
                
            elif self.expKey == 'lifetime':
                #do stuff here 
                if sensitivity ==0:
                    ax.errorbar(['Unaged','Aged'],Poly.IN2_AirAvg,yerr = Poly.errorBarsN2Air,capsize=6,marker='.',label=key)
                elif sensitivity ==1:
                    ax.errorbar(['Unaged','Aged'],Poly.IN2_O2Avg,yerr = Poly.errorBarsN2O2,capsize=6,marker='.',label=key)
                    
            elif self.expKey == 'temperature':
                #do stuff here 
                ax.errorbar(Poly.Time,Poly.IAirAvg,yerr = Poly.errorBarsAir,capsize=6,marker='.',label=key)
              
        ax.legend(loc='upper right')
        
        
    def generateReport(self):
        sns.set_context('poster')
        if not self.outputDir:
            QMessageBox("Please Enter an output directory before generating report data.")
        else:
            if self.reportSamples: #check that user actually selected samples 
                
                if self.expKey != 'temperature':
                    fig1 = plt.figure(1)
                    #fig1.set_canvas(plt.gcf().canvas)
                    self.formatPlot(fig1,'Time (Days)','Intensity Ratio (Photon Counts)',
                                    'Sensitivity (IN2/Air)',sensitivity=0)
    
                    filename1 = self.outputDir +'/'+ 'N2_Air'+'_'+self.expKey+".pdf"
                    fig1.savefig(filename1,bbox_inches='tight')
                    
                    fig2 = plt.figure(2)
                    self.formatPlot(fig2,'Time (Days)','Intensity Ratio (Photon Counts)',
                                    'Sensitivity (IN2/IO2)',sensitivity=1)
                    #fig2.set_canvas(plt.gcf().canvas)
                    
                    filename2 = self.outputDir + '/'+'N2_O2'+'_'+self.expKey+".pdf"
                    fig2.savefig(filename2,bbox_inches='tight')
                else:
                    fig1 = plt.figure(1)
                    self.formatPlot(fig1,'Time (Days)','Intensity Ratio (Photon Counts)',
                                    'Normalized Air Intensities',sensitivity=0)
                    filename1 = self.outputDir +'/'+ 'Air_Normal'+'_'+self.expKey+".pdf"
                    fig1.savefig(filename1,bbox_inches='tight')                    
                
                self.saveR2()
            else:
                QMessageBox("Make Sure to load data before generating report data.")
                
        #importlib.reload(plt)
        
    def setR2file(self,item):
        self.R2file = self.outputDir +item+".xlsx"
    def saveR2(self):
        R2 = {}
        for key in self.reportSamples.keys():
            if self.expKey != 'temperature':
                R2.update({self.reportSamples[key].name:self.reportSamples[key].O2BlueFit})
            else:
                R2.update({self.reportSamples[key].name:self.reportSamples[key].AirBlueFit})
        R2df = pd.DataFrame.from_dict(R2)
        R2df.to_excel(self.R2file)
        
    def excelOutput_clicked(self):
        text,ok = QInputDialog.getText(self,'Text Input Dialog','Enter Spreadsheet name:')
        if ok:
            if self.polymerObjects:
                #self.storeBlueVals(text)
                self.printIntData(text)
            else:
                QMessageBox("Please Load Data before attempting to saving data.")
    def storeBlueVals(self,expTitle):
        fileName = expTitle + '_BlueLightVals.xlsx'
        writer = pd.ExcelWriter(fileName, engine='xlsxwriter')
        for polymerName in self.reportSamples.keys():
            if self.reportSamples[polymerName].O2BlueFit:
                lightDic = self.reportSamples[polymerName].O2BlueFit
                
                df = pd.DataFrame.from_dict(lightDic,orient='index')
                fileName = polymerName + 'Blu'
                df.to_excel(writer,sheet_name = polymerName)
            
    def printIntData(self,expTitle):
        fileName = expTitle + '.xlsx'
        #writer = pd.ExcelWriter(fileName,engine='xlsxwriter')
        frames = []
        for polymerName in self.reportSamples.keys():
            poly = self.reportSamples[polymerName]
            IAir = poly.IAir
            IN2 = poly.IN2
            IO2 = poly.IO2              

            for day,i in zip(poly.Time,range(len(poly.Time))):
                for sample in IAir.keys():
                    if self.expKey !='temperature':
                        if poly.O2BlueFit:
                            if self.blueFitMethod == 1:
                                Blue = poly.O2BlueFit[sample][list(poly.O2BlueFit[sample].keys())[0]]
                                R = poly.RSquare[sample][list(poly.RSquare[sample].keys())[0]]
                            else:
                                Blue = poly.O2BlueFit[sample][day]
                                R = poly.RSquare[sample][list(poly.RSquare[sample].keys())[i]]
                        else:
                            Blue = 0 
                            R = 0
                    else:
                        if poly.AirBlueFit:
                            if self.blueFitMethod == 1:
                                Blue = poly.AirBlueFit[sample][list(poly.AirBlueFit[sample].keys())[0]]
                                R = poly.RSquare[sample][list(poly.RSquare[sample].keys())[0]]
                            else:
                                Blue = poly.AirBlueFit[sample][day]
                                R = poly.RSquare[sample][list(poly.RSquare[sample].keys())[i]]
                        else:
                            Blue = 0 
                    data ={'Day':day,
                            'Polymer':polymerName,'Sample':sample,
                           'IN2 (Photon Counts)':IN2[sample][i],
                           'IAir (Photon Counts)':IAir[sample][i],
                           'IO2 (Photon Counts)':IO2[sample][i],
                           'blue light (Photon Counts)':Blue,
                           'R^2 for Blue fit':R}
                    S = pd.Series(data).to_frame()
                    df = S.swapaxes("index","columns")
                    frames.append(df)
            allDf = pd.concat(frames)
            allDf.set_index('Day')
            allDf.to_excel(fileName,sheet_name='Intensity Data')      
        
        if allDf.size >0:
            message = "Data Saved to: " + fileName
            msg = QMessageBox()
            msg.setText(message)
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msg.exec_()

if __name__ == "__main__":
    import sys
    #from PyQt5 import QtGui
    """
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtWidgets import QTreeWidgetItem
    from PyQt5.QtWidgets import QFileDialog
    from PyQt5.QtWidgets import QMessageBox
    from PyQt5.QtWidgets import QListWidget
    """
    
    #test the plot widget in the gui module
    """
    fig1 = Figure()
    ax1f1 = fig1.add_subplot(111)
    ax1f1.plot([1,2,3,4,5])
    
    fig2 = Figure()
    ax1f2 = fig2.add_subplot(111)
    ax1f2.plot([1,4,9,16,25])
    """
    
    app= QApplication(sys.argv)
    main = Main()
    #main.addfig('test plot 1',fig1)
    #main.addfig('test plot 2',fig2)
    #main.addmpl(fig1)
    main.show()
    app.exec_()

    sys.exit(app.exec_())
    

    
    