# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 13:10:02 2019

@author: ryanm
"""
import numpy as np 

from PyQt5.uic import loadUiType

from matplotlib.figure import Figure 

from matplotlib.backends.backend_qt5agg import(FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar)

Ui_MainWindow, QMainWindow = loadUiType('blf.ui')


class Main(QMainWindow, Ui_MainWindow):
    #put signals and slots here 
    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)
        
        self.fig_dict = {}
        
        #initialize tree widget
        self.sample_treeWidget.setAlternatingRowColors(True)
        self.sample_treeWidget.itemClicked.connect(self.changefig)
        
        
        #initialize list dropdown
        self.exp_comboBox.addItem("Aging Experiment")
        self.exp_comboBox.addItem("Temperature Agglomeration Experiment")
        self.exp_comboBox.addItem("Lifetime Experiment")
        
        self.exp_comboBox.currentTextChanged.connect(self.setTreeCols)
        
    def closeEvent(self,event):
        print("Exiting Program")
        #exit()
        sys.exit()
        
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
        
    def changefig(self, item):
        text = item.text(0)
        self.rmpl()
        self.addmpl(self.fig_dict[text])
        
    def addfig(self, name, fig):
        self.fig_dict[name] = fig
        listItem = QTreeWidgetItem(self.sample_treeWidget,[name])
        self.sample_treeWidget.addTopLevelItem(listItem)
        
    def setTreeCols(self,expType):
        if "Aging Experiment" in expType:
            self.sample_treeWidget.setHeaderLabels(['Polymer','Sample','Time'])
        elif "Temperature Agglomeration Experiment" in expType:
            print("shit")
        elif "Lifetime Experiment" in expType:
            print('fuck')
        
        
if __name__ == "__main__":
    import sys
    #from PyQt5 import QtGui
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtWidgets import QTreeWidgetItem
    
    #test the plot widget in the gui module
    fig1 = Figure()
    ax1f1 = fig1.add_subplot(111)
    ax1f1.plot([1,2,3,4,5])
    
    fig2 = Figure()
    ax1f2 = fig2.add_subplot(111)
    ax1f2.plot([1,4,9,16,25])
    
    app= QApplication(sys.argv)
    main = Main()
    main.addfig('test plot 1',fig1)
    main.addfig('test plot 2',fig2)
    main.addmpl(fig1)
    main.show()
    app.exec_()

    sys.exit(app.exec_())
    

    
    