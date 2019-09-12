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
    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)
        
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
        
if __name__ == "__main__":
    import sys
    #from PyQt5 import QtGui
    from PyQt5.QtWidgets import QApplication
    
    #test the plot widget in the gui module
    fig1 = Figure()
    ax1f1 = fig1.add_subplot(111)
    ax1f1.plot([1,2,3,4,5])
    
    app= QApplication(sys.argv)
    main = Main()
    main.addmpl(fig1)
    main.show()
    app.exec_()

    sys.exit(app.exec_())
    

    
    