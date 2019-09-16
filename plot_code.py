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
"""
#custom imports
import scan_excel as SE
import fit_code as fit
##############################
import numpy as np 

from PyQt5.uic import loadUiType

from matplotlib.figure import Figure 

from matplotlib.backends.backend_qt5agg import(FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar)

Ui_MainWindow, QMainWindow = loadUiType('blf.ui')

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QListWidget
        

class Main(QMainWindow, Ui_MainWindow):
    #put signals and slots here 
    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)
        
        self.fig_dict = {}
        self.xlFileName = ""
        self.outputdir = ""
        self.dye = "Pd"
        self.expKey = "photobleaching"
        self.polymerObjects ={}
        self.fitType = "expSingle"
        self.xrange = [550,620] #default value 
        self.currentFigKey = "" 
    
        
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
        self.exp_comboBox.addItem("Temperature Agglomeration Experiment")
        self.exp_comboBox.addItem("Lifetime Experiment")
        
        self.exp_comboBox.currentTextChanged.connect(self.setTreeCols)
        
        #define excel search button
        
        self.excelChoose_pushButton.clicked.connect(self.setxlFile)
        self.excel_lineEdit.textEdited.connect(self.setxlFile_lineEdit)
        
        #define save file location
        
        self.fileChoose_pushButton.clicked.connect(self.setoutputdir)
        self.fileLoc_lineEdit.textEdited.connect(self.setoutputdir_lineEdit)
        
        #define dropbox for user to select dye 
        #assuming first item in list below is the default selected item.  hard coded for now due to lack of dev time
        self.dye_comboBox.addItem("Pd")
        self.dye_comboBox.addItem("Pt")
        self.dye_comboBox.addItem("Ru")
        
        self.dye_comboBox.currentTextChanged.connect(self.setDye)
        
        #instruct code what to do when the user selects run 
        self.run_pushButton.clicked.connect(self.run)
        
        #assign what happens when the bounds are changed
        self.LB_lineEdit.textEdited.connect(self.lbEdit)
        self.RB_lineEdit.textEdited.connect(self.rbEdit)
        #clear the fitted curve from plot
        self.clearButton.clicked.connect(self.clearFit)
        #assign code to the curve fit push buttons 
        
        #polynomial
        self.polyButton.clicked.connect(self.fitPoly)
        #single Exponential
        self.singleExpButton.clicked.connect(self.fitSingleExp)
        
        
        
    def closeEvent(self,event):
        print("Exiting Program")
        #exit()
        sys.exit()
        
    def setFigData(self,item):
        """ takes the currently selected polymer set, and stores the plot data variables
        """
        if (item.childCount() == 0) :
            daySelected = item.text(0)
            parent1 = item.parent()
            sample = parent1.text(0)
            parent2 = parent1.parent()
            polyName = parent2.text(0)
            self.selectedPoly = self.polymerObjects[polyName]
            
            self.N2Data = self.selectedPoly.N2curve[sample][daySelected]
            self.O2Data = self.selectedPoly.O2curve[sample][daySelected]
            self.AirData = self.selectedPoly.Aircurve[sample][daySelected]
            
            
            xlabelN2 = self.N2Data.columns.tolist()[0]  
            ylabelN2 = self.N2Data.columns.tolist()[1] 
            self.N2FitRange = self.N2Data[(self.N2Data[xlabelN2]>=self.xrange[0])&(self.N2Data[xlabelN2]<=self.xrange[1])]            
            
            xlabelO2 = self.O2Data.columns.tolist()[0]
            ylabelO2 = self.O2Data.columns.tolist()[1]
            self.O2FitRange =self.O2Data[(self.O2Data[xlabelO2]>=self.xrange[0])&(self.O2Data[xlabelO2]<=self.xrange[1])]
            
            xlabelAir = self.AirData.columns.tolist()[0]
            ylabelAir = self.AirData.columns.tolist()[1]
            self.AirFitRange = self.AirData[(self.AirData[xlabelAir]>=self.xrange[0])&(self.AirData[xlabelAir]<=self.xrange[1])]
            
            #plot the different gas spectrometer measurements
            fig = Figure()
            ax = fig.add_subplot(111)
            ax.plot(self.N2Data[xlabelN2].values,self.N2Data[ylabelN2],color='red',label='N2 Intensity')
            ax.plot(self.O2Data[xlabelO2],self.O2Data[ylabelO2],color='blue',label='O2 Intensity')
            ax.plot(self.AirData[xlabelAir],self.AirData[ylabelAir],color='purple',label='Air Intensity')
            ax.set_xlabel('Wavelength (nm)')
            ax.set_ylabel('Photon Counts')
            ax.set_title('Spectrometer Intensity Readings')
            ax.legend(loc='upper right')
            
            self.figKey = polyName + sample + daySelected
            self.changefig(self.figKey,fig)
            
            
            
    def FitData(self):
        colHeadersN2 = self.N2FitRange.columns.tolist()
        colHeadersO2 = self.O2FitRange.columns.tolist()
        colHeadersAir = self.AirFitRange.columns.tolist()
        
        self.paramN2,self.param_covN2 = fit.fitCurve(xdata = self.N2FitRange[colHeadersN2[0]], 
                                                     ydata =self.N2FitRange[colHeadersN2[1]],fitType = self.fitType )
        self.paramO2,self.param_covO2 = fit.fitCurve(xdata = self.O2FitRange[colHeadersO2[0]],
                                                     ydata = self.O2FitRange[colHeadersO2[1]],fitType=self.fitType)
        self.paramAir,self.param_covAir = fit.fitCurve(xdata=self.AirFitRange[colHeadersAir[0]],
                                                       ydata=self.AirFitRange[colHeadersAir[1]],fitType=self.fitType)
        #start generating plot data here 
        #going to fit based on the air curve data
        yfitted = fit.applyFit(self.O2FitRange[colHeadersO2[0]],self.paramO2,self.fitType)
        
        if hasattr(self,'figKey'):
            fig = self.fig_dict[self.figKey]
            ax = fig.gca()
            for line in ax.lines:
                if 'Extrapolated Blue Light Curve' == line.get_label():
                    ax.lines.remove(line)
                    break
            ax.plot(self.O2FitRange[colHeadersO2[0]],yfitted,'--',color='green',label='Extrapolated Blue Light Curve')
            ax.legend(loc='upper right')
            #self.fig_dict[self.figKey] = fig
            self.changefig(self.figKey,fig)
        
        
        
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
            self.sample_treeWidget.setHeaderLabels(['Polymer','Sample','Time'])
            self.key = "photobleaching"
            
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
                            timeChild = QTreeWidgetItem(sampChild,[t])
                            
                            sampChild.addChild(timeChild)
                    
                    self.sample_treeWidget.addTopLevelItem(li)
                    
                
        elif "Temperature Agglomeration Experiment" in expType:
            self.key = "temperature"
        elif "Lifetime Experiment" in expType:
            self.key = "lifetime"
            
    def setxlFile(self):
        fname = QFileDialog.getOpenFileName(self,'Open file', 
         'c:\\',"Excel files (*.xlsx *.xlsm)")
        self.xlFileName = fname[0]
        self.excel_lineEdit.setText(fname[0])
        
    def setoutputdir(self):
        dirname = QFileDialog.getExistingDirectory(self,"Select Directory for Analysis output")
        self.outputdir = dirname[0]
        self.fileLoc_lineEdit.setText(dirname[0])
        
    def setxlFile_lineEdit(self, item):
        self.xlFileName = item 
        
    def setoutputdir_lineEdit(self,item):
        self.outputdir = item
        
    def setDye(self,item):
        self.dye = item
        
    def run(self):
        self.polymerObjects.update( SE.loadExcelData(self.xlFileName,self.expKey,self.dye) ) 
        #print('Data Successfully Loaded')
        msg = QMessageBox()
        msg.setText("Data Successfully Loaded")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.exec_()
        self.setTreeCols(self.exp_comboBox.currentText())
        
    def fitPoly(self):
        self.QList.show()

    def fitSingleExp(self):
        self.fitType = "expSingle"
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
        
        xlabelN2 = self.N2Data.columns.tolist()[0]  
        self.N2FitRange = self.N2Data[(self.N2Data[xlabelN2]>=self.xrange[0])&(self.N2Data[xlabelN2]<=self.xrange[1])]            
        
        xlabelO2 = self.O2Data.columns.tolist()[0]
        self.O2FitRange =self.O2Data[(self.O2Data[xlabelO2]>=self.xrange[0])&(self.O2Data[xlabelO2]<=self.xrange[1])]
        
        xlabelAir = self.AirData.columns.tolist()[0]
        self.AirFitRange = self.AirData[(self.AirData[xlabelAir]>=self.xrange[0])&(self.AirData[xlabelAir]<=self.xrange[1])]
        
        
    def rbEdit(self,item):
        self.xrange[1] = float(item)
        
        xlabelN2 = self.N2Data.columns.tolist()[0]  
        self.N2FitRange = self.N2Data[(self.N2Data[xlabelN2]>=self.xrange[0])&(self.N2Data[xlabelN2]<=self.xrange[1])]            
        
        xlabelO2 = self.O2Data.columns.tolist()[0]
        self.O2FitRange =self.O2Data[(self.O2Data[xlabelO2]>=self.xrange[0])&(self.O2Data[xlabelO2]<=self.xrange[1])]
        
        xlabelAir = self.AirData.columns.tolist()[0]
        self.AirFitRange = self.AirData[(self.AirData[xlabelAir]>=self.xrange[0])&(self.AirData[xlabelAir]<=self.xrange[1])]
        
    def clearFit(self):
        if hasattr(self,'figKey'):
            fig = self.fig_dict[self.figKey]
            ax = fig.gca()
            for line in ax.lines:
                if 'Extrapolated Blue Light Curve' == line.get_label():
                    ax.lines.remove(line)
                    ax.legend(loc='upper right')
                    self.changefig(self.figKey,fig)
                    break
            
        
        
        
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
    

    
    