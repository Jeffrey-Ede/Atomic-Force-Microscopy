# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 10:57:40 2017

@author: Jeffrey Ede
"""

# For communication with lock-in amplifier
from __future__ import print_function
import time
import numpy as np
import zhinst.utils

# For graphical user interface
import tkinter as tk
from tkinter import ttk

# For plotting
import matplotlib
#matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler

from matplotlib.figure import Figure

import tooltip

class HystGUI(tk.Frame):

    # Initialise main window
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.hystGUI = parent
        self.deviceID = 'dev801'
        self.hystGUI.title("Hysteresis Measurement")
        self.backClr = "#a1dbcd"
        self.btnClr = "#73c6b6"
        self.hystGUI.configure(background=self.backClr)
        
        self.scanPatterns = ("Min-Max", "Min-Max-Min", "0-Max-0-Min-0")
        self.auxOuts = ('1', '2', '3', '4')
        self.probeOut = ('1', '2')
        self.demods = ('1', '2', '3', '4', '5', '6')
        
        # Read default entry values from file
        self.defaultFile = 'hysteresis_default_values.txt'
        hystDefaultVal = open(self.defaultFile, 'r')
        self.default = hystDefaultVal.read().splitlines()
        hystDefaultVal.close()

        self.plotSelection = ('X', 'Y', 'R', 'Phase', 't', 'ProbeV', 'BotElectV', 'TotalV')
        self.units = ('V', 'V', 'V', 'Rad', 's', 'V', 'V', 'V')
                
        # Dictionary storing measurements
        self.measurements = {'X': np.empty((0)), 'Y': np.empty((0)), 'R': np.empty((0)), 'Phase': np.empty((0)),
                             't': np.empty((0)), 'ProbeV': np.empty((0)), 'BotElectV': np.empty((0)), 'TotalV': np.empty((0))} 


        """
        1. Initialise all data entry terminals, labels, etc.
        2. Arrange them on a grid
        3. Confgure the grid
        4. Configure their inputs
        """
        # Instantiate widgets
        # Voltages
        self.probeLabel = tk.Label(self.hystGUI, text="Probe", font=("bold", 10), bg=self.backClr)
        
        # Probe max DC Offset
        self.probeMaxDCLabel = tk.Label(self.hystGUI, text="DC Max", bg=self.backClr)
        self.probeMaxDCUnit = tk.Label(self.hystGUI, text="V", bg=self.backClr)
        self.probeMaxDCEntry = tk.Entry(self.hystGUI, validate="key")
        self.probeMaxDCEntry['validatecommand'] = (self.probeMaxDCEntry.register(self.testVal),'%P','%i','%d')
        
        # Probe min DC Offset
        self.probeMinDCLabel = tk.Label(self.hystGUI, text="DC Min", bg=self.backClr)
        self.probeMinDCUnit = tk.Label(self.hystGUI, text="V", bg=self.backClr)
        self.probeMinDCEntry = tk.Entry(self.hystGUI, validate="key")
        self.probeMinDCEntry['validatecommand'] = (self.probeMinDCEntry.register(self.testVal),'%P','%i','%d')
        
        
        self.botElectLabel = tk.Label(self.hystGUI, text="Bottom Electrode", font=("bold", 10), bg=self.backClr)
        
        # Bottom Electrode max DC Offset
        self.botElectMaxDCLabel = tk.Label(self.hystGUI, text="DC Max", bg=self.backClr)
        self.botElectMaxDCUnit = tk.Label(self.hystGUI, text="V", bg=self.backClr)
        self.botElectMaxDCEntry = tk.Entry(self.hystGUI, validate="key")
        self.botElectMaxDCEntry['validatecommand'] = (self.botElectMaxDCEntry.register(self.testVal),'%P','%i','%d')
        
        # Bottom Electrode min DC Offset
        self.botElectMinDCLabel = tk.Label(self.hystGUI, text="DC Min", bg=self.backClr)
        self.botElectMinDCUnit = tk.Label(self.hystGUI, text="V", bg=self.backClr)
        self.botElectMinDCEntry = tk.Entry(self.hystGUI, validate="key")
        self.botElectMinDCEntry['validatecommand'] = (self.botElectMinDCEntry.register(self.testVal),'%P','%i','%d')
        
        
        self.configLabel = tk.Label(self.hystGUI, text="Configure Scan", font=("bold", 10), bg=self.backClr)
        
        # Times
        # Bias time
        self.biasTimeLabel = tk.Label(self.hystGUI, text="Bias Time", bg=self.backClr)
        self.biasTimeUnit = tk.Label(self.hystGUI, text="ms", bg=self.backClr)
        self.biasTimeEntry = tk.Entry(self.hystGUI, validate="key")
        self.biasTimeEntry['validatecommand'] = (self.biasTimeEntry.register(self.testValPos),'%P','%i','%d')
        
        # Bias intermission time; to allow system to settle before data aquisition
        self.biasInterLabel = tk.Label(self.hystGUI, text="Bias Wait", bg=self.backClr)
        self.biasInterUnit = tk.Label(self.hystGUI, text="ms", bg=self.backClr)
        self.biasInterEntry = tk.Entry(self.hystGUI, validate="key")
        self.biasInterEntry['validatecommand'] = (self.biasInterEntry.register(self.testValPos),'%P','%i','%d')
        
        # 0 V time
        self.zeroVTimeLabel = tk.Label(self.hystGUI, text="0 V Time", bg=self.backClr)
        self.zeroVTimeUnit = tk.Label(self.hystGUI, text="ms", bg=self.backClr)
        self.zeroVTimeEntry = tk.Entry(self.hystGUI, validate="key")
        self.zeroVTimeEntry['validatecommand'] = (self.zeroVTimeEntry.register(self.testValPos),'%P','%i','%d')
        
        # 0 V intermission time; to allow system to settle before data aquisition
        self.zeroVInterLabel = tk.Label(self.hystGUI, text="0 V Wait", bg=self.backClr)
        self.zeroVInterUnit = tk.Label(self.hystGUI, text="ms", bg=self.backClr)
        self.zeroVInterEntry = tk.Entry(self.hystGUI, validate="key")
        self.zeroVInterEntry['validatecommand'] = (self.zeroVInterEntry.register(self.testValPos),'%P','%i','%d')
        
        
        # Hysteresis Setup
        # Number of voltage increments, from 0th, per loop
        self.numStepsLabel = tk.Label(self.hystGUI, text="Steps", bg=self.backClr)
        self.numStepsEntry = tk.Entry(self.hystGUI, validate="key")
        self.numStepsEntry['validatecommand'] = (self.numStepsEntry.register(self.testValPosInteg),'%P','%i','%d')
        
        # Number of loops
        self.numLoopsLabel = tk.Label(self.hystGUI, text="Loop", bg=self.backClr)
        self.numLoopsUnit = tk.Label(self.hystGUI, text="times", bg=self.backClr)
        self.numLoopsEntry = tk.Entry(self.hystGUI, validate="key")
        self.numLoopsEntry['validatecommand'] = (self.numLoopsEntry.register(self.testValPosInteg),'%P','%i','%d')
        
        # Pattern
        self.patternLabel = tk.Label(self.hystGUI, text="Pattern", bg=self.backClr)
        self.patternUnit = tk.Label(self.hystGUI, text="", bg=self.backClr)
        self.patternEntry = tk.ttk.Combobox(self.hystGUI, values=self.scanPatterns)
        
        
        # Probe offset source
        self.probeAuxLabel = tk.Label(self.hystGUI, text="Aux Out", bg=self.backClr)
        self.probeAuxUnit = tk.Label(self.hystGUI, text="", bg=self.backClr)
        self.probeAuxEntry = tk.ttk.Combobox(self.hystGUI, values=self.auxOuts)
        
        # Bottom Electrode offset source
        self.botElectAuxLabel = tk.Label(self.hystGUI, text="Aux Out", bg=self.backClr)
        self.botElectAuxUnit = tk.Label(self.hystGUI, text="", bg=self.backClr)
        self.botElectAuxEntry = tk.ttk.Combobox(self.hystGUI, values=self.auxOuts)
        
        
        # Execution buttons
        self.executeButton = tk.Button(self.hystGUI, text='Execute', command=self.execute, bg=self.btnClr)
        self.restoreDefaultButton = tk.Button(self.hystGUI, text='Restore Default Values',
                                              command=self.restoreDefault, bg=self.btnClr)
        self.makeDefaultButton = tk.Button(self.hystGUI, text='Make Values Default',
                                           command=self.makeDefault, bg=self.btnClr)

        
        # Plot
        self.plotLabel = tk.Label(self.hystGUI, text="Plot", font=("bold", 10), bg=self.backClr)
        
        # Horizontal axis
        self.plotxLabel = tk.Label(self.hystGUI, text="Horizontal Axis", bg=self.backClr)
        self.plotxUnit = tk.Label(self.hystGUI, text="", bg=self.backClr)
        self.plotxEntry = tk.ttk.Combobox(self.hystGUI, values=self.plotSelection)
        
        # Vertical axis
        self.plotyLabel = tk.Label(self.hystGUI, text="Vertical Axis", bg=self.backClr)
        self.plotyUnit = tk.Label(self.hystGUI, text="", bg=self.backClr)
        self.plotyEntry = tk.ttk.Combobox(self.hystGUI, values=self.plotSelection)
        
        # Plot button
        self.plotButton = tk.Button(self.hystGUI, text='New Plot', command=self.plot, bg=self.btnClr)
        self.clearPlotButton = tk.Button(self.hystGUI, text='Clear', command=self.clear_meas,
                                         bg=self.btnClr)
        self.saveButton = tk.Button(self.hystGUI, text='Save', command=self.output_data,
                                         bg=self.btnClr)
        
        # Probe out
        self.probeOutLabel = tk.Label(self.hystGUI, text="Probe Out", bg=self.backClr)
        self.probeOutUnit = tk.Label(self.hystGUI, text="", bg=self.backClr)
        self.probeOutEntry = tk.ttk.Combobox(self.hystGUI, values=self.probeOut)
        
        # Average over repeated x values
        self.avgRepeatedx = tk.IntVar()
        self.avgRepeatedxLabel = tk.Label(self.hystGUI, text="Avg Horiz Repeats", bg=self.backClr)
        self.avgRepeatedxEntry = tk.Checkbutton(self.hystGUI, text="", variable=self.avgRepeatedx, onvalue=1, 
                                                offvalue=0, bg=self.backClr)
        
        # Average over repeated y values
        self.avgRepeatedy = tk.IntVar()
        self.avgRepeatedyLabel = tk.Label(self.hystGUI, text="Avg Vert Repeats", bg=self.backClr)
        self.avgRepeatedyEntry = tk.Checkbutton(self.hystGUI, text="", variable=self.avgRepeatedy, onvalue=1,
                                                offvalue=0, bg=self.backClr)
        
        # Demodulator
        self.demodLabel = tk.Label(self.hystGUI, text="Demod", bg=self.backClr)
        self.demodUnit = tk.Label(self.hystGUI, text="", bg=self.backClr)
        self.demodEntry = tk.ttk.Combobox(self.hystGUI, values=self.demods)
        
        # Tooltips
        # Probe max DC Offset
        tooltip.createToolTip(self.probeMaxDCEntry, "Probe max bias offset.\nLimits: ±10V")
        tooltip.createToolTip(self.probeMinDCEntry, "Probe min bias offset.\nLimits: ±10V")
        tooltip.createToolTip(self.botElectMaxDCEntry, "Bottom electrode max bias offset.\nLimits: ±10V")
        tooltip.createToolTip(self.botElectMinDCEntry, "Bottom electrode min bias offset.\nLimits: ±10V")
        tooltip.createToolTip(self.biasTimeEntry, "Time at each bias, not including intermission time.")
        tooltip.createToolTip(self.biasInterEntry, "Settling time before measurement at each bias.")
        tooltip.createToolTip(self.zeroVTimeEntry, "Time at 0V, not including intermission time.")
        tooltip.createToolTip(self.zeroVInterEntry, "Settling time before measurement at 0V.")
        tooltip.createToolTip(self.numStepsEntry, "Number of bias steps, not including the 0th.")
        tooltip.createToolTip(self.numLoopsEntry, "Number of times to repeat.")
        tooltip.createToolTip(self.patternEntry, "Bias offseting pattern. Tip: switch the min and max biases\nfor the probe and bottom electrode to flip the pattern.")
        tooltip.createToolTip(self.probeAuxEntry, "Auxillary output supplying probe bias offset\nAdd it to the signal output to the probe.")
        tooltip.createToolTip(self.botElectAuxEntry, "Auxillary output supplying bottom electrode bias offset.")
        tooltip.createToolTip(self.executeButton, "Take hysteresis measurements.")
        tooltip.createToolTip(self.restoreDefaultButton, "Restore entry field values to their defaults.")
        tooltip.createToolTip(self.makeDefaultButton, "Make current entry field values default.")
        tooltip.createToolTip(self.plotxEntry, "Plot on horizontal axis of graph.")
        tooltip.createToolTip(self.plotyEntry, "Plot on vertical axis of graph.")
        tooltip.createToolTip(self.plotButton, "Plot graph.")
        tooltip.createToolTip(self.clearPlotButton, "Clear data.")
        tooltip.createToolTip(self.saveButton, "Opens save as dialogue.\nDefault: .txt")
        tooltip.createToolTip(self.probeOutEntry, "Probe signal output.")
        tooltip.createToolTip(self.avgRepeatedxEntry, "Average repeated horizontal values in plot.")
        tooltip.createToolTip(self.avgRepeatedyEntry, "Average repeated vertical values in plot.")
        

        ###################################################
        # Grid positions of labels, entry boxes, etc.
        self.probeLabel.grid(row=1, column=0, sticky=tk.W)
        
        self.probeMaxDCLabel.grid(row=2, column=0, sticky=tk.W)
        self.probeMaxDCUnit.grid(row=2, column=2, sticky=tk.W)
        self.probeMaxDCEntry.grid(row=2, column=1, sticky=tk.E+tk.W)
        
        self.probeMinDCLabel.grid(row=2, column=3, sticky=tk.W)
        self.probeMinDCUnit.grid(row=2, column=5, sticky=tk.W)
        self.probeMinDCEntry.grid(row=2, column=4, sticky=tk.E+tk.W)
        
        
        self.botElectLabel.grid(row=4, column=0, sticky=tk.W)
        
        self.botElectMaxDCLabel.grid(row=5, column=0, sticky=tk.W)
        self.botElectMaxDCUnit.grid(row=5, column=2, sticky=tk.W)
        self.botElectMaxDCEntry.grid(row=5, column=1, sticky=tk.E+tk.W)
        
        self.botElectMinDCLabel.grid(row=5, column=3, sticky=tk.W)
        self.botElectMinDCUnit.grid(row=5, column=5, sticky=tk.W)
        self.botElectMinDCEntry.grid(row=5, column=4, sticky=tk.E+tk.W)
        
        
        self.configLabel.grid(row=7, column=0, sticky=tk.W)
        
        self.biasTimeLabel.grid(row=10, column=0, sticky=tk.W)
        self.biasTimeUnit.grid(row=10, column=2, sticky=tk.W)
        self.biasTimeEntry.grid(row=10, column=1, sticky=tk.E+tk.W)
        
        self.biasInterLabel.grid(row=10, column=3, sticky=tk.W)
        self.biasInterUnit.grid(row=10, column=5, sticky=tk.W)
        self.biasInterEntry.grid(row=10, column=4, sticky=tk.E+tk.W)
        
        self.zeroVTimeLabel.grid(row=11, column=0, sticky=tk.W)
        self.zeroVTimeUnit.grid(row=11, column=2, sticky=tk.W)
        self.zeroVTimeEntry.grid(row=11, column=1, sticky=tk.E+tk.W)
        
        self.zeroVInterLabel.grid(row=11, column=3, sticky=tk.W)
        self.zeroVInterUnit.grid(row=11, column=5, sticky=tk.W)
        self.zeroVInterEntry.grid(row=11, column=4, sticky=tk.E+tk.W)
        
        self.numStepsLabel.grid(row=9, column=3, sticky=tk.W)
        self.numStepsEntry.grid(row=9, column=4, sticky=tk.E+tk.W)
        
        self.numLoopsLabel.grid(row=8, column=3, sticky=tk.W)
        self.numLoopsUnit.grid(row=8, column=5, sticky=tk.W)
        self.numLoopsEntry.grid(row=8, column=4, sticky=tk.E+tk.W)
        
        self.patternLabel.grid(row=8, column=0, sticky=tk.W)
        self.patternUnit.grid(row=8, column=2, sticky=tk.W)
        self.patternEntry.grid(row=8, column=1, sticky=tk.E+tk.W)
        
        self.probeAuxLabel.grid(row=3, column=0, sticky=tk.W)
        self.probeAuxUnit.grid(row=3, column=2, sticky=tk.W)
        self.probeAuxEntry.grid(row=3, column=1, sticky=tk.E+tk.W)
        
        # Bottom Electrode
        self.botElectAuxLabel.grid(row=6, column=0, sticky=tk.W)
        self.botElectAuxUnit.grid(row=6, column=2, sticky=tk.W)
        self.botElectAuxEntry.grid(row=6, column=1, sticky=tk.E+tk.W)
        
        # Execution buttons
        self.executeButton.grid(row=1, column=7, sticky=tk.E+tk.W)
        self.restoreDefaultButton.grid(row=2, column=7, sticky=tk.E+tk.W)
        self.makeDefaultButton.grid(row=3, column=7, sticky=tk.E+tk.W)
        
        # Plot
        self.plotLabel.grid(row=11, column=0, sticky=tk.W)
        
        # Horizontal axis
        self.plotxLabel.grid(row=13, column=0, sticky=tk.W)
        self.plotxUnit.grid(row=13, column=2, sticky=tk.W)
        self.plotxEntry.grid(row=13, column=1, sticky=tk.E+tk.W)
        
        # Vertical axis
        self.plotyLabel.grid(row=13, column=3, sticky=tk.W)
        self.plotyUnit.grid(row=13, column=5, sticky=tk.W)
        self.plotyEntry.grid(row=13, column=4, sticky=tk.E+tk.W)
        
        # Plot buttons
        self.plotButton.grid(row=12, column=7, sticky=tk.E+tk.W)
        self.clearPlotButton.grid(row=13, column=7, sticky=tk.E+tk.W)
        self.saveButton.grid(row=14, column=7, sticky=tk.E+tk.W)
        
        # Probe out
        self.probeOutLabel.grid(row=3, column=3, sticky=tk.W)
        self.probeOutUnit.grid(row=3, column=5, sticky=tk.W)
        self.probeOutEntry.grid(row=3, column=4, sticky=tk.E+tk.W)
        
        # Average repeated x values
        self.avgRepeatedxLabel.grid(row=14, column=0, sticky=tk.W)
        self.avgRepeatedxEntry.grid(row=14, column=1, sticky=tk.W)
        
        # Average repeated y values
        self.avgRepeatedyLabel.grid(row=14, column=3, sticky=tk.W)
        self.avgRepeatedyEntry.grid(row=14, column=4, sticky=tk.W)
        
        # Demodulator
        self.demodLabel.grid(row=9, column=0, sticky=tk.W)
        self.demodUnit.grid(row=9, column=2, sticky=tk.W)
        self.demodEntry.grid(row=9, column=1, sticky=tk.E+tk.W)
        
        # Configure grid spacing
        for row_num in range(self.hystGUI.grid_size()[1]):
            self.hystGUI.rowconfigure(row_num, pad=4)
            
        for col_num in range(self.hystGUI.grid_size()[0]):
            self.hystGUI.columnconfigure(col_num, pad=5)
        
        # Set default values
        self.probeMaxDCEntry.insert(0, self.default[0])
        self.probeMinDCEntry.insert(0, self.default[1])
        self.botElectMaxDCEntry.insert(0, self.default[2])
        self.botElectMinDCEntry.insert(0, self.default[3])
        self.biasTimeEntry.insert(0, self.default[4])
        self.biasInterEntry.insert(0, self.default[5])
        self.zeroVTimeEntry.insert(0, self.default[6])
        self.zeroVInterEntry.insert(0, self.default[7])
        self.numStepsEntry.insert(0, self.default[8])
        self.numLoopsEntry.insert(0, self.default[9])
        self.probeAuxEntry.delete(0, tk.END)
        self.probeAuxEntry.insert(0, self.default[10])
        self.botElectAuxEntry.delete(0, tk.END)
        self.botElectAuxEntry.insert(0, self.default[11])
        self.patternEntry.delete(0, tk.END)
        self.patternEntry.insert(0, self.default[12])
        self.plotxEntry.delete(0, tk.END)
        self.plotxEntry.insert(0, self.default[13])
        self.plotyEntry.delete(0, tk.END)
        self.plotyEntry.insert(0, self.default[14])
        self.probeOutEntry.insert(0, self.default[15])
        self.avgRepeatedx.set(self.default[16])
        self.avgRepeatedy.set(self.default[17])
        self.demodEntry.insert(0, self.default[18])
        
        
    # Tests if entry input is a number
    def testVal(self, inStr, i, acttyp):
        ind=int(i)
        if acttyp == '1': #insert
            if (not inStr[ind] in '0123456789+-.eE'):
                return False
        return True
    
    # Tests if entry input is a positive number
    def testValPos(self, inStr, i, acttyp):
        ind=int(i)
        if acttyp == '1': #insert
            if (not inStr[ind] in '0123456789+-.eE'):
                return False
            if inStr[0] in '-':
                return False
        return True
        
    # Tests if entry input is a positive integer
    def testValPosInteg(self, inStr, i, acttyp):
        ind=int(i)
        if acttyp == '1': #insert
            if (not inStr[ind] in '0123456789+eE'):
                return False
        return True
    
    # Execute hysteresis measurement procedures
    def execute(self):     
        
        # Error dialogue box
        errDialogueBox = tk.Tk()
        errDialogueBox.title("Error Dialogue")
        scrollbar = tk.Scrollbar(errDialogueBox)
        errText = tk.Text(errDialogueBox, height=20, width=45)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        errText.pack(side=tk.LEFT, fill=tk.Y)
        scrollbar.config(command=errText.yview)
        errText.config(yscrollcommand=scrollbar.set)        
        
        
        # Check that entries are correctly formatted and within physical bounds
        try:
            probeMaxDCEntry = float(self.probeMaxDCEntry.get())
            if not -10 <= probeMaxDCEntry <= 10:
                errText.insert(tk.END, "Probe DC Max bounds are ±10 V\n")
        except ValueError:
            errText.insert(tk.END, "Probe DC Max is not a float\n")
            
        try:
            probeMinDCEntry = float(self.probeMinDCEntry.get())
            if not -10 <= probeMinDCEntry <= 10:
                errText.insert(tk.END, "Probe DC Min bounds are ±10 V\n")
        except ValueError:
            errText.insert(tk.END, "Probe DC Min is not a float\n")
            
            
        try:
            botElectMaxDCEntry = float(self.botElectMaxDCEntry.get())
            if not -10 <= botElectMaxDCEntry <= 10:
                errText.insert(tk.END, "Bottom Electrode DC Max bounds are ±10 V\n")
        except ValueError:
            errText.insert(tk.END, "Bottom Electrode DC Max is not a float\n")
            
        try:
            botElectMinDCEntry = float(self.botElectMinDCEntry.get())
            if not -10 <= botElectMinDCEntry <= 10:
                errText.insert(tk.END, "Bottom Electrode DC Min bounds are ±10 V\n")
        except ValueError:
            errText.insert(tk.END, "Bottom Electrode DC Min is not a float\n")
            
        try:
            biasTimeEntry = float(self.biasTimeEntry.get())
            if not 0 <= biasTimeEntry:
                errText.insert(tk.END, "Configure Scan Bias Time must be at least 0 ms\n")
        except ValueError:
            errText.insert(tk.END, "Configure Scan Bias Time is not a float\n")
            
        try:
            biasInterEntry = float(self.biasInterEntry.get())
            if not 0 <= biasInterEntry:
                errText.insert(tk.END, "Configure Scan Bias Intermission must be at least 0 ms\n")
        except ValueError:
            errText.insert(tk.END, "Configure Scan Bias Intermission is not a float\n")
            
        try:
            zeroVTimeEntry = float(self.zeroVTimeEntry.get())
            if not 0 <= zeroVTimeEntry:
                errText.insert(tk.END, "Configure Scan 0 V Time must be at least 0 ms\n")
        except ValueError:
            errText.insert(tk.END, "Configure Scan 0 V Time is not a float\n")
            
        try:
            zeroVInterEntry = float(self.zeroVInterEntry.get())
            if not 0 <= zeroVInterEntry:
                errText.insert(tk.END, "Configure Scan 0 V Intermission must be at least 0 ms\n")
        except ValueError:
            errText.insert(tk.END, "Configure Scan 0 V Intermission is not a float\n")
            
        try:
            numStepsEntry = float(self.numStepsEntry.get())
            if not 1 <= numStepsEntry:
                errText.insert(tk.END, "Configure Scan Steps must be at least 1\n")
        except ValueError:
            errText.insert(tk.END, "Configure Scan Steps is not a float\n")
            
        try:
            numLoopsEntry = float(self.numLoopsEntry.get())
            if not 1 <= numLoopsEntry:
                errText.insert(tk.END, "Configure Scan Loop number must be at least 1\n")
        except ValueError:
            errText.insert(tk.END, "Configure Scan Loop number is not a float\n")
            
        if not self.probeAuxEntry.get() in self.auxOuts:
            errText.insert(tk.END, "Probe Aux Out is not in "+str(self.auxOuts)+"\n")
            
        if not self.botElectAuxEntry.get() in self.auxOuts:
            errText.insert(tk.END, "Bottom Electrode Aux Out is not in "+str(self.auxOuts)+"\n")
            
        if self.probeAuxEntry.get() == self.botElectAuxEntry.get():
            errText.insert(tk.END, "Probe and Bottom Electrode Aux Outs cannot be same\n")
        
        if not self.patternEntry.get() in self.scanPatterns:
            errText.insert(tk.END, "Pattern is not in "+str(self.scanPatterns)+"\n")
            
        if not self.plotxEntry.get() in self.plotSelection:
            errText.insert(tk.END, "Horizontal Axis is not in "+str(self.plotSelection)+"\n")
            
        if not self.plotyEntry.get() in self.plotSelection:
            errText.insert(tk.END, "Vertical Axis is not in "+str(self.plotSelection)+"\n")
            
        out_channel = self.probeOutEntry.get()
        if not out_channel in self.probeOut:
            errText.insert(tk.END, "Probe output is not in "+str(self.probeOut)+"\n")
            
        demod_index = self.demodEntry.get()
        if not demod_index in self.demods:
            errText.insert(tk.END, "Demodulator is not in "+str(self.demods)+"\n")
            
        # Do not open error message window if all entries are valid
        if len(errText.get("1.0", "end-1c")) == 0:
            errDialogueBox.destroy()
            
            # Prepare measurement parameter array to be passed to hyst_meas
            hystParam = [None]*15
            hystParam[0] = probeMaxDCEntry
            hystParam[1] = probeMinDCEntry
            hystParam[2] = botElectMaxDCEntry
            hystParam[3] = botElectMinDCEntry
            hystParam[4] = biasTimeEntry/1000.0   # Convert from ms to s
            hystParam[5] = biasInterEntry/1000.0   # Convert from ms to s
            hystParam[6] = zeroVTimeEntry/1000.0   # Convert from ms to s
            hystParam[7] = zeroVInterEntry/1000.0   # Convert from ms to s
            hystParam[8] = numStepsEntry
            hystParam[9] = numLoopsEntry
            hystParam[10] = self.probeAuxEntry.get()
            hystParam[11] = self.botElectAuxEntry.get()
            hystParam[12] = self.patternEntry.get()
            hystParam[13] = int(out_channel)
            hystParam[14] = int(demod_index)
            
            self.hyst_meas(self.deviceID, hystParam)
            
            
    # Restore default entry values
    def restoreDefault(self):
        
        # Clear the entry fields
        self.probeMaxDCEntry.delete(0, tk.END)
        self.probeMinDCEntry.delete(0, tk.END)
        self.botElectMaxDCEntry.delete(0, tk.END)
        self.botElectMinDCEntry.delete(0, tk.END)
        self.biasTimeEntry.delete(0, tk.END)
        self.biasInterEntry.delete(0, tk.END)
        self.zeroVTimeEntry.delete(0, tk.END)
        self.zeroVInterEntry.delete(0, tk.END)
        self.numStepsEntry.delete(0, tk.END)
        self.numLoopsEntry.delete(0, tk.END)
        self.patternEntry.delete(0, tk.END)
        self.probeAuxEntry.delete(0, tk.END)
        self.botElectAuxEntry.delete(0, tk.END)
        self.patternEntry.delete(0, tk.END)
        self.plotxEntry.delete(0, tk.END)
        self.plotyEntry.delete(0, tk.END)
        self.probeOutEntry.delete(0, tk.END)
        self.demodEntry.delete(0, tk.END)
        
        # Insert defaults into now-cleared entry fields
        self.probeMaxDCEntry.insert(0, self.default[0])
        self.probeMinDCEntry.insert(0, self.default[1])
        self.botElectMaxDCEntry.insert(0, self.default[2])
        self.botElectMinDCEntry.insert(0, self.default[3])
        self.biasTimeEntry.insert(0, self.default[4])
        self.biasInterEntry.insert(0, self.default[5])
        self.zeroVTimeEntry.insert(0, self.default[6])
        self.zeroVInterEntry.insert(0, self.default[7])
        self.numStepsEntry.insert(0, self.default[8])
        self.numLoopsEntry.insert(0, self.default[9])
        self.probeAuxEntry.insert(0, self.default[10])
        self.botElectAuxEntry.insert(0, self.default[11])
        self.patternEntry.insert(0, self.default[12])
        self.plotxEntry.insert(0, self.default[13])
        self.plotyEntry.insert(0, self.default[14])
        self.probeOutEntry.insert(0, self.default[15])
        self.avgRepeatedx.set(self.default[16])
        self.avgRepeatedy.set(self.default[17])
        self.demodEntry.insert(0, self.default[18])
        
    # Make current values default
    def makeDefault(self):
        self.default[0] = self.probeMaxDCEntry.get()
        self.default[1] = self.probeMinDCEntry.get()
        self.default[2] = self.botElectMaxDCEntry.get()
        self.default[3] = self.botElectMinDCEntry.get()
        self.default[4] = self.biasTimeEntry.get()
        self.default[5] = self.biasInterEntry.get()
        self.default[6] = self.zeroVTimeEntry.get()
        self.default[7] = self.zeroVInterEntry.get()
        self.default[8] = self.numStepsEntry.get()
        self.default[9] = self.numLoopsEntry.get()
        self.default[10] = self.probeAuxEntry.get()
        self.default[11] = self.botElectAuxEntry.get()
        self.default[12] = self.patternEntry.get()
        self.default[13] = self.plotxEntry.get()
        self.default[14] = self.plotyEntry.get()
        self.default[15] = self.probeOutEntry.get()
        self.default[16] = str(self.avgRepeatedx.get())
        self.default[17] = str(self.avgRepeatedy.get())
        self.default[18] = self.demodEntry.get()
        
        defaults = open(self.defaultFile, 'w')
        for default in self.default:
            defaults.write(default+'\n')
        defaults.close()
            
    
    def hyst_meas(self, device_id, hystParam):
        
        # Measurement parameters
        probeMaxDC = hystParam[0]
        probeMinDC = hystParam[1]
        botElectMaxDC = -hystParam[2]   # Apply in opposite direction to probe offset
        botElectMinDC = -hystParam[3]   # Apply in opposite direction to probe offset
        biasTime = hystParam[4]
        biasInter = hystParam[5]
        zeroVTime = hystParam[6]
        zeroVInter = hystParam[7]
        numSteps = int(hystParam[8])+1   # +1 to add 0th step
        numLoops = int(hystParam[9])
        probeAux = int(hystParam[10])-1   # -1 so indices start at 0
        botElectAux = int(hystParam[11])-1   # -1 so indices start at 0
        pattern = hystParam[12]
        out_channel = hystParam[13]-1
        demod_index = hystParam[14]-1
    
        apilevel_example = 5  # The API level supported by this example.
        # Call a zhinst utility function that returns:
        # - an API session `daq` in order to communicate with devices via the data server.
        # - the device ID string that specifies the device branch in the server's node hierarchy.
        # - the device's discovery properties.
        err_msg = "This example only supports instruments with demodulators."
        (daq, device, props) = zhinst.utils.create_api_session(device_id, apilevel_example,
                                                               required_devtype='.*LI|.*IA|.*IS',
                                                               required_err_msg=err_msg)
    
        # Create a base instrument configuration: disable all outputs, demods and scopes.
        general_setting = [['/%s/demods/*/enable' % device, 0],
                           ['/%s/demods/*/trigger' % device, 0],
                           ['/%s/sigouts/*/enables/*' % device, 0],
                           ['/%s/scopes/*/enable' % device, 0]]
        if 'IA' in props['options']:
            general_setting.append(['/%s/imps/*/enable' % device, 0])
        daq.set(general_setting)
        # Perform a global synchronisation between the device and the data server:
        # Ensure that the settings have taken effect on the device before setting
        # the next configuration.
        daq.sync()
    
        # Now configure the instrument for this experiment. The following channels
        # and indices work on all device configurations. The values below may be
        # changed if the instrument has multiple input/output channels and/or either
        # the Multifrequency or Multidemodulator options installed.
        exp_setting = [['/%s/demods/%d/enable'         % (device, demod_index), 1],
                       ['/%s/sigouts/%d/on'            % (device, out_channel), 1],
                       ['/%s/auxouts/%d/outputselect' % (device, probeAux), -1],   # Manual output
                       ['/%s/auxouts/%d/outputselect' % (device, botElectAux), -1]]   # Manual output
        # Some other device-type dependent configuration may be required. For
        # example, disable the signal inputs `diff` and the signal outputs `add` for
        # HF2 instruments.
        if props['devicetype'].startswith('HF2'):
            exp_setting.append(['/%s/sigouts/%d/add'      % (device, out_channel), 1])
        daq.set(exp_setting)
    
        # Wait for the demodulator filter to settle.
        time_constant = 1e-6
        time.sleep(10*time_constant)
    
        # Perform a global synchronisation between the device and the data server:
        # Ensure that the settings have taken effect on the device before issuing
        # the getSample() command. Note: the sync() must be issued after waiting for
        # the demodulator filter to settle above.
        daq.sync()
    
        # Obtain one demodulator sample via ziDAQServer's low-level getSample()
        # method - for extended data acquisition it's preferable to use
        # ziDAQServer's poll() method or the ziDAQRecorder class.
        sample = daq.getSample('/%s/demods/%d/sample' % (device, demod_index))
        # Calculate the demodulator's magnitude and phase and add them to the sample
        # dict.
        sample['R'] = np.abs(sample['x'] + 1j*sample['y'])
        sample['phi'] = np.angle(sample['x'] + 1j*sample['y'])
        
        poll_timeout = 500  # [ms]
        poll_flags=0
        poll_return_flat_dict=True
        
        for i in range(numLoops):
            
            if pattern == 'Min-Max':
                
                # Calculate bias to apply
                probeVoltIncr = (probeMaxDC-probeMinDC)/(numSteps-1.0)
                botElectVoltIncr = (botElectMaxDC-botElectMinDC)/(numSteps-1.0)

                for j in range(numSteps):
                    
                    # Update progress
                    self.executeButton['text'] = "Progress: "+"{0:.2f}".format((i/numLoops+j/numSteps)*100)+"%"
                    self.hystGUI.update()
                    
                    # Calculate bias to apply cont.
                    probeOffset = probeMinDC+j*probeVoltIncr
                    botElectOffset = botElectMinDC+j*botElectVoltIncr
                    
                    # Record relevant measurements
                    sample = self.bias_zero_samp(daq, device, probeAux, botElectAux, probeOffset, botElectOffset, demod_index,
                       biasTime, zeroVTime, biasInter, zeroVInter, poll_timeout, poll_flags, poll_return_flat_dict)
                    self.record_meas(sample)
                    
    
            elif pattern == 'Min-Max-Min':
                
                # Calculate Min-Max bias to apply
                probeVoltIncr = (probeMaxDC-probeMinDC)/(int(numSteps/2)+numSteps%2-1.0)
                botElectVoltIncr = (botElectMaxDC-botElectMinDC)/(int(numSteps/2)+numSteps%2-1.0)
                
                for j in range(int(numSteps/2)+numSteps%2):
                    
                    # Update progress
                    self.executeButton['text'] = "Progress: "+"{0:.2f}".format((i/numLoops+j/numSteps)*100)+"%"
                    self.hystGUI.update()
                    
                    # Calculate bias to apply cont.
                    probeOffset = probeMinDC+j*probeVoltIncr
                    botElectOffset = botElectMinDC+j*botElectVoltIncr
                    
                    # Record relevant measurements
                    sample = self.bias_zero_samp(daq, device, probeAux, botElectAux, probeOffset, botElectOffset, demod_index,
                       biasTime, zeroVTime, biasInter, zeroVInter, poll_timeout, poll_flags, poll_return_flat_dict)
                    self.record_meas(sample)
                
                # Calculate Max-Min bias to apply
                probeVoltIncr = (probeMaxDC-probeMinDC)/(int(numSteps/2))
                botElectVoltIncr = (botElectMaxDC-botElectMinDC)/(int(numSteps/2))
                
                for j in range(1, int(numSteps/2)+1):
                    
                    # Update progress
                    temp = j-1+int(numSteps/2)+numSteps%2
                    self.executeButton['text'] = "Progress: "+"{0:.2f}".format((i/numLoops+temp/numSteps)*100)+"%"
                    self.hystGUI.update()
                    
                    # Calculate bias to apply cont.
                    probeOffset = probeMaxDC-j*probeVoltIncr
                    botElectOffset = botElectMaxDC-j*botElectVoltIncr
                    
                    # Record relevant measurements
                    sample = self.bias_zero_samp(daq, device, probeAux, botElectAux, probeOffset, botElectOffset, demod_index,
                       biasTime, zeroVTime, biasInter, zeroVInter, poll_timeout, poll_flags, poll_return_flat_dict)
                    self.record_meas(sample)
                    
                    
            elif pattern == '0-Max-0-Min-0':
                
                # Calculate 0-Max bias to apply
                addStep = 0
                if numSteps%4 > 0:
                    addStep = 1
                probeVoltIncr = probeMaxDC/(int(numSteps/4)+addStep-1.0)
                botElectVoltIncr = botElectMaxDC/(int(numSteps/4)+addStep-1.0)
                
                temp = 0
                
                for j in range(int(numSteps/4)+addStep):
                    
                    # Update progress
                    self.executeButton['text'] = "Progress: "+"{0:.2f}".format((i/numLoops+j/numSteps)*100)+"%"
                    self.hystGUI.update()
                    
                    # Calculate bias to apply cont.
                    probeOffset = j*probeVoltIncr
                    botElectOffset = j*botElectVoltIncr
                    
                    # Record relevant measurements
                    sample = self.bias_zero_samp(daq, device, probeAux, botElectAux, probeOffset, botElectOffset, demod_index,
                       biasTime, zeroVTime, biasInter, zeroVInter, poll_timeout, poll_flags, poll_return_flat_dict)
                    self.record_meas(sample)
                    
                temp += int(numSteps/4)+addStep-1
                
                # Calculate Max-Min bias to apply
                if numSteps%4 > 1:
                    addStep = 1
                else:
                    addStep = 0
                probeVoltIncr = (probeMaxDC-probeMinDC)/(int(numSteps/2)+addStep)
                botElectVoltIncr = (botElectMaxDC-botElectMinDC)/(int(numSteps/2)+addStep)
                
                for j in range(1, int(numSteps/2)+addStep+1):
                    
                    # Update progress
                    self.executeButton['text'] = "Progress: "+"{0:.2f}".format((i/numLoops+(j+temp)/numSteps)*100)+"%"
                    self.hystGUI.update()
                    
                    # Calculate bias to apply cont.
                    probeOffset = probeMaxDC-j*probeVoltIncr
                    botElectOffset = botElectMaxDC-j*botElectVoltIncr
                    
                    # Record relevant measurements
                    sample = self.bias_zero_samp(daq, device, probeAux, botElectAux, probeOffset, botElectOffset, demod_index,
                       biasTime, zeroVTime, biasInter, zeroVInter, poll_timeout, poll_flags, poll_return_flat_dict)
                    self.record_meas(sample)
                    
                temp += int(numSteps/2)+addStep
                
                # Calculate 0-Min bias to apply
                if numSteps%4 > 2:
                    addStep = 1
                else:
                    addStep = 0
                probeVoltIncr = -probeMinDC/(int(numSteps/4)+addStep)
                botElectVoltIncr = -botElectMinDC/(int(numSteps/4)+addStep)
                
                for j in range(1, int(numSteps/4)+addStep+1):
                    
                    # Update progress
                    self.executeButton['text'] = "Progress: "+"{0:.2f}".format((i/numLoops+(j+temp)/numSteps)*100)+"%"
                    self.hystGUI.update()
                    
                    # Calculate bias to apply cont.
                    probeOffset = probeMinDC+j*probeVoltIncr
                    botElectOffset = botElectMinDC+j*botElectVoltIncr
                    
                    # Record relevant measurements
                    sample = self.bias_zero_samp(daq, device, probeAux, botElectAux, probeOffset, botElectOffset, demod_index,
                       biasTime, zeroVTime, biasInter, zeroVInter, poll_timeout, poll_flags, poll_return_flat_dict)
                    self.record_meas(sample)
                    
        # Update progress
        self.executeButton['text'] = "Execute"
        self.hystGUI.update()
                    
                
    def bias_zero_samp(self, daq, device, probeAux, botElectAux, probeOffset, botElectOffset, demod_index,
                       biasTime, zeroVTime, biasInter, zeroVInter, poll_timeout, poll_flags,
                       poll_return_flat_dict):
        
        # Apply Bias
        daq.set([['/%s/auxouts/%d/offset' % (device, probeAux), probeOffset],
                 ['/%s/auxouts/%d/offset' % (device, botElectAux), botElectOffset]])
        
        # Allow bias intermissionary settling time
        time.sleep(biasInter)
        daq.sync()
                    
                    
        # Record data while bias is being applied
        # Unsubscribe from all paths.
        daq.unsubscribe('*')
                
        path = '/%s/demods/%d/sample' % (device, demod_index)
        daq.subscribe(path)
                    
        data = daq.poll(biasTime, poll_timeout, poll_flags, poll_return_flat_dict)   # *1000 for s -> ms

        # Unsubscribe from all paths
        daq.unsubscribe('*')
                    
        # Check that the dictionary returned is non-empty
        assert data, "poll() returned an empty data dictionary, did you subscribe to any paths?"
                
        # The data returned is a dictionary of dictionaries that reflects the node's path.
        # Note, the data could be empty if no data had arrived, e.g., if the demods
        # were disabled or had demodulator rate 0.
        assert path in data, "The data dictionary returned by poll has no key `%s`." % path
                
        # Access the demodulator sample using the node's path
        sample = data[path]

        # Check how many seconds of demodulator data were returned by poll.
        # First, get the sampling rate of the device's ADCs, the device clockbase...
        clockbase = float(daq.getInt('/%s/clockbase' % device))
                    
        # Convert timestamps from ticks to seconds via clockbase.
        sample['t'] = (sample['timestamp'] - sample['timestamp'][0])/clockbase
        sample['t'] += sample['t'][1]

        # Voltages
        sample['ProbeV'] = np.empty(len(sample['t']))
        sample['ProbeV'].fill(probeOffset)
        sample['BotElectV'] = np.empty(len(sample['t']))
        sample['BotElectV'].fill(botElectOffset)
        sample['TotalV'] = sample['ProbeV']-sample['BotElectV']
                    
                    
        # Calculate the demodulator's magnitude and phase and add them to the dict.
        sample['R'] = np.abs(sample['x'] + 1j*sample['y'])
        sample['Phase'] = np.angle(sample['x'] + 1j*sample['y'])
                    
                    
        # Apply 0 V bias between steps
        daq.set([['/%s/auxouts/%d/offset' % (device, probeAux), 0],
                 ['/%s/auxouts/%d/offset' % (device, botElectAux), 0]])
                    
                    
        # Allow 0 V intermissionary settling time
        time.sleep(zeroVInter)
        daq.sync()
                    
                    
        # Resubscribe and poll.                
        daq.subscribe(path)
        data = daq.poll(biasTime, poll_timeout, poll_flags, poll_return_flat_dict)   # *1000 for s -> ms
                    
        # Unsubscribe from all paths
        daq.unsubscribe('*')
                    
        # Check that the dictionary returned is non-empty
        assert data, "poll() returned an empty data dictionary, did you subscribe to any paths?"
                
        # The data returned is a dictionary of dictionaries that reflects the node's path.
        # Note, the data could be empty if no data had arrived, e.g., if the demods
        # were disabled or had demodulator rate 0.
        assert path in data, "The data dictionary returned by poll has no key `%s`." % path
                
        # Access the demodulator sample using the node's path
        sample2 = data[path]

        # Check how many seconds of demodulator data were returned by poll.
        # First, get the sampling rate of the device's ADCs, the device clockbase...
        clockbase = float(daq.getInt('/%s/clockbase' % device))
                    
        # Convert timestamps from ticks to seconds via clockbase.
        sample2['t'] = (sample2['timestamp'] - sample2['timestamp'][0])/clockbase
        sample2['t'] += sample2['t'][1]

        # Voltages
        sample2['ProbeV'] = np.empty(len(sample2['t']))
        sample2['ProbeV'].fill(probeOffset)
        sample2['BotElectV'] = np.empty(len(sample2['t']))
        sample2['BotElectV'].fill(botElectOffset)
        sample2['TotalV'] = sample2['ProbeV']-sample2['BotElectV']
                    
        # Calculate the demodulator's magnitude and phase and add them to the dict.
        sample2['R'] = np.abs(sample2['x'] + 1j*sample2['y'])
        sample2['Phase'] = np.angle(sample2['x'] + 1j*sample2['y'])
                    
        sample['x'] = np.append(sample['x'], sample2['x'])
        sample['y'] = np.append(sample['y'], sample2['y'])
        sample['R'] = np.append(sample['R'], sample2['R'])
        sample['Phase'] = np.append(sample['Phase'], sample2['Phase'])
        sample['t'] = np.append(sample['t'], sample2['t']+sample['t'][-1])
        sample['ProbeV'] = np.append(sample['ProbeV'], sample2['ProbeV'])
        sample['BotElectV'] = np.append(sample['BotElectV'], sample2['BotElectV'])
        sample['TotalV'] = np.append(sample['TotalV'], sample2['TotalV'])
        
        return sample
                
        
    # Record all relevant measurements in dictionary
    def record_meas(self, sample):
        self.measurements['X'] = np.append(self.measurements['X'], sample['x'])
        self.measurements['Y'] = np.append(self.measurements['Y'], sample['y'])
        self.measurements['R'] = np.append(self.measurements['R'], sample['R'])
        self.measurements['Phase'] = np.append(self.measurements['Phase'], sample['Phase'])
        try:
            self.measurements['t'] = np.append(self.measurements['t'], sample['t']+self.measurements['t'][-1])
        except IndexError:
            self.measurements['t'] = np.append(self.measurements['t'], sample['t'])
        self.measurements['ProbeV'] = np.append(self.measurements['ProbeV'], sample['ProbeV'])
        self.measurements['BotElectV'] = np.append(self.measurements['BotElectV'], sample['BotElectV'])
        self.measurements['TotalV'] = np.append(self.measurements['TotalV'], sample['ProbeV']-sample['BotElectV'])
        
        
    # Clear measurements dictionary
    def clear_meas(self):
        for key in self.measurements:
            self.measurements[key] = np.empty((0))
        
        
    # Plot results of hysteresis measurement
    def plot(self):
        plot = tk.Tk()
        x1 = self.plotxEntry.get()
        y1 = self.plotyEntry.get()
        
        plot.title(x1+"-"+y1+" Plot")
        
        f = Figure(figsize=(5, 4), dpi=100)
        a = f.add_subplot(111)
        
        x, y = self.measurements[x1], self.measurements[y1]
        # Average over repeated values, if specified
        if self.avgRepeatedx.get() == 1:
            y, x = self.avg_xrepeats(self.measurements[y1], self.measurements[x1])
        if self.avgRepeatedy.get() == 1:
            x, y = self.avg_xrepeats(self.measurements[x1], self.measurements[y1])
            

        # Prepare graph
        a.plot(x, y)
        
        # Add a tk.DrawingArea
        canvas = FigureCanvasTkAgg(f, master=plot)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        toolbar = NavigationToolbar2TkAgg(canvas, plot)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        
    # Average over repeated x values. Can average over y by passing x and y the other way around
    def avg_xrepeats(self, x, y):
        
        avgedx, avgedy = np.empty((0)), np.empty((0))
        
        total = 0
        start, end = 0, 1   # Average between y[start] and y[end] so x and y have same lengths
        prevx = x[0]

        # If the next value of x is not the same as the previous, add it to the array
        for i in range(1, len(x)):
            # If x is same as previous
            if x[i] == prevx:
                end += 1
                    
                # Check if this is the last element of the array
                if i == len(x)-1:
                    avgedx = np.append(avgedx, prevx)
                    
                    for j in range(start, end):
                        total += y[i]
                    avgedy = np.append(avgedy, total/(end-start))
                        
                    
            # If x is not the same as previous
            else:
                avgedx = np.append(avgedx, prevx)
                prevx = x[i]
                    
                for j in range(start, end):
                    total += y[j]
                avgedy = np.append(avgedy, total/(end-start))
                    
                total = 0
                start, end = i, i+1
                    
                # Check if this is the last element of the array
                if i == len(x)-1:
                    avgedx = np.append(avgedx, x[i])
                    avgedy = np.append(avgedy, y[i])
                    
        print(len(x), len(y), len(avgedx), len(avgedy))
        return avgedx, avgedy
        
    
    # Output data
    def output_data(self):
        
        text = "#"
        for heading in self.plotSelection:
            text += " "+heading
        text += "\n#"
        for unit in self.units:
            text += " "+unit
        text += "\n"
        
        
        for i in range(len(self.measurements['X'])):
            for key in self.measurements:
                text += str(self.measurements[key][i])+"    "
            text += "\n"
        
        f = tk.filedialog.asksaveasfile(mode='w', defaultextension=".txt")
        if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
            return
        f.write(text)
        f.close()     
            

if __name__ == "__main__":
    hystGUI = tk.Tk()
    HystGUI(hystGUI)
    hystGUI.mainloop()
