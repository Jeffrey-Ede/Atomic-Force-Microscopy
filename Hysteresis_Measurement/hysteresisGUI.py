# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 10:57:40 2017

@author: Jeffrey Ede
"""

# For communication with lock-in amplifier
from __future__ import print_function
import numpy as np
import zhinst.utils

# For graphical user interface
import tkinter as tk

# For plotting
#matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler

from matplotlib.figure import Figure

import tooltip

import webbrowser # To open link to help web page

import os # To delete files

import time # Data and time

class HystGUI(tk.Frame):

    # Initialise main window
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.hystGUI = parent
        self.deviceID = 'dev801'
        self.hystGUI.title("Hysteresis Measurement")
        self.backClr = "#a1dbcd"
        self.cfmClr = "#a1dbcd"
        self.btnClr = "#73c6b6"
        self.hystGUI.configure(background=self.backClr)
        
        self.scanPatterns = ("Min-Max", "Min-Max-Min", "0-Max-0-Min-0")
        self.auxOuts = ('1', '2', '3', '4')
        self.probeOut = ('1', '2')
        self.demods = ('1', '2', '3', '4', '5', '6')
        self.cfmIns = ('1', '2')
        self.scopeTimes = ('210 MS, 10 micro s', '105 MS, 20 micro s', '53 MS, 39 micro s', '26 MS, 78 micro s', '13 MS, 160 micro s',
                           '6.6 MS, 310 micro s', '3.3 MS, 620 micro s', '1.6 MS, 1.2 ms', '820 kS, 2.5 ms', '410 kS, 5 ms',
                           '205 kS, 10 ms','103 kS, 20 ms', '51 kS, 40 ms','26 kS, 80 ms','13 kS, 160 ms', '6.4 kS, 320 ms')
        self.scopeTimes_times = (10.0e-3, 20.0e-3, 39.0e-3, 78.0e-3, 160.0e-3,
                                 310.0e-3, 620.0e-3, 1.2, 2.5, 5.0,
                                 10.0, 20.0, 40.0, 80.0, 160.0, 320.0) # self.scopeTimes times in ms
        self.fourierSelection = ('None', 'Low Pass', 'High Pass')
        self.fourierOptions = ('Shot Set', 'Bias Set')
        self.shot_len = 2048
                                 
        # Read default entry values from file
        self.defaultFile = 'hysteresis_default_values.txt'
        hystDefaultVal = open(self.defaultFile, 'r')
        self.default = hystDefaultVal.read().splitlines()
        hystDefaultVal.close()

        self.plotSelection = ('TotalV', 'X', 'Y', 'R', 'Phase', 't', 'ProbeV', 'BotElectV', 'CFM_V')
        self.plotOptions = self.plotSelection
        self.units = ('V', 'V', 'V', 'V', 'Rad', 's', 'V', 'V', 'V')
                
        # Dictionary storing measurements
        self.measurements = {'TotalV': np.empty((0)), 'X': np.empty((0)), 'Y': np.empty((0)), 'R': np.empty((0)), 'Phase': np.empty((0)),
                             't': np.empty((0)), 'ProbeV': np.empty((0)), 'BotElectV': np.empty((0)), 'CFM_V': np.empty((0))} 

        self.helpPageURL = 'https://jeffrey-ede.shinyapps.io/voltage_trains/'


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
        self.plotxEntry = tk.ttk.Combobox(self.hystGUI, values=self.plotOptions)
        
        # Vertical axis
        self.plotyLabel = tk.Label(self.hystGUI, text="Vertical Axis", bg=self.backClr)
        self.plotyUnit = tk.Label(self.hystGUI, text="", bg=self.backClr)
        self.plotyEntry = tk.ttk.Combobox(self.hystGUI, values=self.plotOptions)
        
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
        
        # Help
        self.helpButton = tk.Button(self.hystGUI, text='Help', command=self.helpPage, bg=self.btnClr)
        
        
        # CFM
        self.cfmLabel = tk.Label(self.hystGUI, text="CFM", font=("bold", 10), bg=self.cfmClr)
        
        # Do CFM?
        self.doCFM = tk.IntVar()
        self.doCFMLabel = tk.Label(self.hystGUI, text="Do CFM", bg=self.cfmClr)
        self.doCFMEntry = tk.Checkbutton(self.hystGUI, text="", variable=self.doCFM, command=self.cfm_enabled,
                                         onvalue=1, offvalue=0, bg=self.cfmClr)
        
        # Bandwidth limit
        self.bwLim = tk.IntVar()
        self.bwLimLabel = tk.Label(self.hystGUI, text="Bandwith Limit", bg=self.cfmClr)
        self.bwLimEntry = tk.Checkbutton(self.hystGUI, text="", variable=self.bwLim, onvalue=1,
                                                offvalue=0, bg=self.cfmClr)
        
        # Voltage input channel
        self.cfmInLabel = tk.Label(self.hystGUI, text="Voltage In", bg=self.cfmClr)
        self.cfmInUnit = tk.Label(self.hystGUI, text="", bg=self.cfmClr)
        self.cfmInEntry = tk.ttk.Combobox(self.hystGUI, values=self.cfmClr)
        
        # Sampling rate
        self.scopeTimeLabel = tk.Label(self.hystGUI, text="Sampling Rate", bg=self.cfmClr)
        self.scopeTimeEntry = tk.ttk.Combobox(self.hystGUI, values=self.scopeTimes)
        
        # Save full CFM data?
        self.saveCFM = tk.IntVar()
        self.saveCFMLabel = tk.Label(self.hystGUI, text="Save Data", bg=self.cfmClr)
        self.saveCFMEntry = tk.Checkbutton(self.hystGUI, text="", variable=self.saveCFM, onvalue=1, 
                                                offvalue=0, bg=self.cfmClr)
        
        # Location to save CFM to
        self.saveCFMToLabel = tk.Label(self.hystGUI, text="Append To", bg=self.cfmClr)
        self.saveCFMToEntry = tk.Entry(self.hystGUI)
        
        # CFM save location
        self.saveCFMButton = tk.Button(self.hystGUI, text='Save CFM To', command=self.cfm_save_loc,
                                         bg=self.btnClr)
        
        # Clear CFM save location
        self.clearCFMButton = tk.Button(self.hystGUI, text='Clear CFM', command=self.clear_cfm_save_loc,
                                         bg=self.btnClr)
        
        # Save settings
        self.saveSettingsButton = tk.Button(self.hystGUI, text='Save Settings', command=self.save_settings,
                                         bg=self.btnClr)
        
        # Load settings
        self.loadSettingsButton = tk.Button(self.hystGUI, text='Load Settings', command=self.load_settings,
                                         bg=self.btnClr)
        
        # Choose whether to resynchronise settings during measurement
        self.unsync = tk.IntVar()
        self.unsyncLabel = tk.Label(self.hystGUI, text="Unsynchronised", bg=self.cfmClr)
        self.unsyncEntry = tk.Checkbutton(self.hystGUI, text="", variable=self.unsync,
                                         onvalue=1, offvalue=0, bg=self.cfmClr)
        
        # Fourier filter
        self.fourierSectLabel = tk.Label(self.hystGUI, text="Filter", font=("bold", 10), bg=self.cfmClr)
        
        # Fourier save location
        self.saveFourierButton = tk.Button(self.hystGUI, text='Save Fourier To', command=self.fourier_save_loc,
                                         bg=self.btnClr)
        
        # Clear Fourier save location
        self.clearFourierButton = tk.Button(self.hystGUI, text='Clear Fourier', command=self.clear_fourier_save_loc,
                                         bg=self.btnClr)
        
        # Fourier filter type
        self.filterTypeLabel = tk.Label(self.hystGUI, text="Filter Type", bg=self.cfmClr)
        self.filterTypeEntry = tk.ttk.Combobox(self.hystGUI, values=self.fourierSelection)
        
        
        # Automatic filtering
        self.fourier = tk.IntVar()
        self.fourierLabel = tk.Label(self.hystGUI, text="Auto Filter", bg=self.cfmClr)
        self.fourierEntry = tk.Checkbutton(self.hystGUI, text="", variable=self.fourier,
                                         onvalue=1, offvalue=0, bg=self.cfmClr)
        
        # Filter by shot set, voltage set\ or all data
        self.filterByLabel = tk.Label(self.hystGUI, text="Filter By", bg=self.cfmClr)
        self.filterByEntry = tk.ttk.Combobox(self.hystGUI, values=self.fourierOptions)
        
        # Fourier data
        self.fourierLocLabel = tk.Label(self.hystGUI, text="Save Fourier To", bg=self.cfmClr)
        self.fourierLocEntry = tk.Entry(self.hystGUI)
        
        # Fourier cutoff
        self.cutoffLabel = tk.Label(self.hystGUI, text="Filter Param", bg=self.cfmClr)
        self.cutoffUnit = tk.Label(self.hystGUI, text="Hz", bg=self.cfmClr)
        self.cutoffEntry = tk.Entry(self.hystGUI, validate="key")
        self.cutoffEntry['validatecommand'] = (self.cutoffEntry.register(self.testValPos),'%P','%i','%d')
        
        # Open text files
        self.openCFMButton = tk.Button(self.hystGUI, text='Open CFM', command=self.openCFM, bg=self.btnClr)
        self.openFourierButton = tk.Button(self.hystGUI, text='Open Fourier', command=self.openFourier, bg=self.btnClr)
        
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
        tooltip.createToolTip(self.patternEntry, "Bias offsetting pattern. Tip: switch the min and max biases\nfor the probe and bottom electrode to flip the pattern.")
        tooltip.createToolTip(self.probeAuxEntry, "Auxillary output supplying probe bias offset\nAdd it to the signal output to the probe.")
        tooltip.createToolTip(self.botElectAuxEntry, "Auxillary output supplying bottom electrode bias offset.")
        tooltip.createToolTip(self.executeButton, "Take hysteresis measurements.")
        tooltip.createToolTip(self.restoreDefaultButton, "Restore entry field values to their defaults.")
        tooltip.createToolTip(self.makeDefaultButton, "Make current entry field values default.")
        tooltip.createToolTip(self.plotxEntry, "Plot on horizontal axis of graph.")
        tooltip.createToolTip(self.plotyEntry, "Plot on vertical axis of graph.")
        tooltip.createToolTip(self.plotButton, "Plot graph.")
        tooltip.createToolTip(self.clearPlotButton, "Clear data.")
        tooltip.createToolTip(self.saveButton, "Opens save as dialogue.\nDefault: .txt\nAverages over repeats first if Avg Horiz or Avg Vert are\nticked. If both are ticked, only Horiz will be averaged over.")
        tooltip.createToolTip(self.probeOutEntry, "Probe signal output.")
        tooltip.createToolTip(self.avgRepeatedxEntry, "Average repeated horizontal values in plot.")
        tooltip.createToolTip(self.avgRepeatedyEntry, "Average repeated vertical values in plot.")
        tooltip.createToolTip(self.helpButton, "Opens voltage train simulation and\nparameter explanation in browser.")
        tooltip.createToolTip(self.doCFMEntry, "Enable CFM.\nNote: this constrains the lower bound of the bias 0V\ntimes to be at least 100ms+sampling time.")
        tooltip.createToolTip(self.bwLimEntry, "Bandwidth limitings helps avoid antialiasing\neffects caused by subsampling.")
        tooltip.createToolTip(self.cfmInEntry, "Voltage input used as current proxy.")
        tooltip.createToolTip(self.scopeTimeEntry, "Scope sampling rate.")
        tooltip.createToolTip(self.saveCFMEntry, "Save all CFM data after each poll.")
        tooltip.createToolTip(self.saveCFMToEntry, "Location to save CFM data to.")
        tooltip.createToolTip(self.saveCFMButton, "Opens save as dialogue.")
        tooltip.createToolTip(self.unsyncEntry, "Do not perform resynchronisations\nafter initial synchronisation.")
        tooltip.createToolTip(self.clearCFMButton, "Clear CFM save location(s).")
        tooltip.createToolTip(self.saveFourierButton, "Clear CFM save location(s).")
        tooltip.createToolTip(self.clearFourierButton, "Clear CFM save location(s).")
        tooltip.createToolTip(self.filterTypeEntry, "Clear CFM save location(s).")
        tooltip.createToolTip(self.fourierEntry, "Clear CFM save location(s).")
        tooltip.createToolTip(self.fourierLocEntry, "Clear CFM save location(s).")
        tooltip.createToolTip(self.filterByEntry, "Clear CFM save location(s).")

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
        p = 21
        self.plotLabel.grid(row=p, column=0, sticky=tk.W)
        
        # Horizontal axis
        self.plotxLabel.grid(row=p+1, column=0, sticky=tk.W)
        self.plotxUnit.grid(row=p+1, column=2, sticky=tk.W)
        self.plotxEntry.grid(row=p+1, column=1, sticky=tk.E+tk.W)
        
        # Vertical axis
        self.plotyLabel.grid(row=p+1, column=3, sticky=tk.W)
        self.plotyUnit.grid(row=p+1, column=5, sticky=tk.W)
        self.plotyEntry.grid(row=p+1, column=4, sticky=tk.E+tk.W)
        
        # Plot buttons
        self.plotButton.grid(row=p, column=7, sticky=tk.E+tk.W)
        self.clearPlotButton.grid(row=p+1, column=7, sticky=tk.E+tk.W)
        self.saveButton.grid(row=p+2, column=7, sticky=tk.E+tk.W)
        
        # Probe out
        self.probeOutLabel.grid(row=3, column=3, sticky=tk.W)
        self.probeOutUnit.grid(row=3, column=5, sticky=tk.W)
        self.probeOutEntry.grid(row=3, column=4, sticky=tk.E+tk.W)
        
        # Average repeated x values
        self.avgRepeatedxLabel.grid(row=p+2, column=0, sticky=tk.W)
        self.avgRepeatedxEntry.grid(row=p+2, column=1, sticky=tk.W)
        
        # Average repeated y values
        self.avgRepeatedyLabel.grid(row=p+2, column=3, sticky=tk.W)
        self.avgRepeatedyEntry.grid(row=p+2, column=4, sticky=tk.W)
        
        # Demodulator
        self.demodLabel.grid(row=9, column=0, sticky=tk.W)
        self.demodUnit.grid(row=9, column=2, sticky=tk.W)
        self.demodEntry.grid(row=9, column=1, sticky=tk.E+tk.W)
        
        # Save settings
        self.saveSettingsButton.grid(row=6, column=7, sticky=tk.E+tk.W)
        
        # Load settings
        self.loadSettingsButton.grid(row=7, column=7, sticky=tk.E+tk.W)
        
        # Help
        self.helpButton.grid(row=4, column=7, sticky=tk.E+tk.W)
        
        # CFM
        self.cfmLabel.grid(row=12, column=0, sticky=tk.W)
        
        # Do CFM?
        self.doCFMLabel.grid(row=13, column=0, sticky=tk.W)
        self.doCFMEntry.grid(row=13, column=1, sticky=tk.W)
        
        # Bandwidth limit
        self.bwLimLabel.grid(row=16, column=3, sticky=tk.W)
        self.bwLimEntry.grid(row=16, column=4, sticky=tk.W)
        
        # Voltage input channel
        self.cfmInLabel.grid(row=14, column=0, sticky=tk.W)
        self.cfmInUnit.grid(row=14, column=2, sticky=tk.W)
        self.cfmInEntry.grid(row=14, column=1, sticky=tk.E+tk.W)
        
        # Duration of full scope shot
        self.scopeTimeLabel.grid(row=15, column=0, sticky=tk.W)
        self.scopeTimeEntry.grid(row=15, column=1, sticky=tk.E+tk.W)
        
        # Save full CFM data?
        self.saveCFMLabel.grid(row=13, column=3, sticky=tk.W)
        self.saveCFMEntry.grid(row=13, column=4, sticky=tk.W)
        
        # Location to save CFM to
        self.saveCFMToLabel.grid(row=14, column=3, sticky=tk.W)
        self.saveCFMToEntry.grid(row=14, column=4, sticky=tk.E+tk.W)
        
        # CFM save location
        self.saveCFMButton.grid(row=14, column=7, sticky=tk.E+tk.W)
        
        # Clear CFM save location
        self.clearCFMButton.grid(row=15, column=7, sticky=tk.E+tk.W)
        
        # Fourier filter
        self.fourierSectLabel.grid(row=17, column=0, sticky=tk.W)
        
        # Fourier save location
        self.saveFourierButton.grid(row=18, column=7, sticky=tk.E+tk.W)

        # Clear Fourier save location
        self.clearFourierButton.grid(row=19, column=7, sticky=tk.E+tk.W)
        
        # Fourier filter type
        self.filterTypeLabel.grid(row=15, column=3, sticky=tk.W)
        self.filterTypeEntry.grid(row=15, column=4, sticky=tk.E+tk.W)
        
        # Automatic filtering
        self.fourierLabel.grid(row=18, column=3, sticky=tk.W)
        self.fourierEntry.grid(row=18, column=4, sticky=tk.W)
        
        # Filter by shot set, voltage set\ or all data
        self.filterByLabel.grid(row=18, column=0, sticky=tk.W)
        self.filterByEntry.grid(row=18, column=1, sticky=tk.E+tk.W)
        
        # Fourier data
        self.fourierLocLabel.grid(row=19, column=3, sticky=tk.W)
        self.fourierLocEntry.grid(row=19, column=4, sticky=tk.E+tk.W)
        
        # Fourier cutoff
        self.cutoffLabel.grid(row=19, column=0, sticky=tk.W)
        self.cutoffUnit.grid(row=19, column=2, sticky=tk.W)
        self.cutoffEntry.grid(row=19, column=1, sticky=tk.E+tk.W)
        
        # Disable resynchronisation
        self.unsyncLabel.grid(row=16, column=0, sticky=tk.W)
        self.unsyncEntry.grid(row=16, column=1, sticky=tk.W)
        
        self.openCFMButton.grid(row=13, column=7, sticky=tk.E+tk.W)
        self.openFourierButton.grid(row=17, column=7, sticky=tk.E+tk.W)
        
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
        self.doCFM.set(self.default[19])
        self.bwLim.set(self.default[20])
        self.cfmInEntry.insert(0, self.default[21])
        self.scopeTimeEntry.insert(0, self.default[22])
        self.saveCFM.set(self.default[23])
        self.saveCFMToEntry.insert(0, self.default[24])
        self.unsync.set(self.default[25])
        self.filterTypeEntry.insert(0, self.default[26])
        self.fourier.set(self.default[27])
        self.filterByEntry.insert(0, self.default[28])
        self.fourierLocEntry.insert(0, self.default[29])
        self.cutoffEntry.insert(0, self.default[30])
        
        # Only display available plot options: not CFM data if CFM mode is not enabled
        if self.default[19] == 1:
            self.plotOptions = [opt for opt in self.plotSelection if opt != 'CFM_V']
            
        
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
            errText.insert(tk.END, "Horizontal Axis is not in "+str(self.plotOptions)+"\n")
            
        if not self.plotyEntry.get() in self.plotSelection:
            errText.insert(tk.END, "Vertical Axis is not in "+str(self.plotOptions)+"\n")
            
        out_channel = self.probeOutEntry.get()
        if not out_channel in self.probeOut:
            errText.insert(tk.END, "Probe output is not in "+str(self.probeOut)+"\n")
            
        if not self.cfmInEntry.get() in self.cfmIns:
            errText.insert(tk.END, "CFM voltage input is not in "+str(self.cfmIns)+"\n")
            
        scopeTime = self.scopeTimeEntry.get()
        if not scopeTime in self.scopeTimes:
            errText.insert(tk.END, "CFM sampling rate is not in "+str(self.scopeTimes)+"\n")
            
#        if self.doCFM.get() == 1:
#            time = ''
#            for i, val in enumerate(self.scopeTimes):
#                if val == self.scopeTimeEntry.get():
#                    time = self.scopeTimes_times[i]
#                    
##            if biasTimeEntry < 100+time and biasTimeEntry !=0:
##                errText.insert(tk.END, "Bias time must be at leat 100ms+sampling\ntime, preferably higher, to poll the scope\n")
##                
##            if zeroVTimeEntry< 100+time and zeroVTimeEntry != 0:
##                errText.insert(tk.END, "0 V time must be at leat 100ms+sampling\ntime, preferably higher, to poll the scope\n")
            
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
        self.cfmInEntry.delete(0, tk.END)
        self.scopeTimeEntry.delete(0, tk.END)
        self.saveCFMToEntry.delete(0, tk.END)
        self.filterTypeEntry.delete(0, tk.END)
        self.filterByEntry.delete(0, tk.END)
        self.fourierLocEntry.delete(0, tk.END)
        self.cutoffEntry.delete(0, tk.END)
        
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
        self.doCFM.set(self.default[19])
        self.bwLim.set(self.default[20])
        self.cfmInEntry.insert(0, self.default[21])
        self.scopeTimeEntry.insert(0, self.default[22])
        self.saveCFM.set(self.default[23])
        self.saveCFMToEntry.insert(0, self.default[24])
        self.unsync.set(self.default[25])
        self.filterTypeEntry.insert(0, self.default[26])
        self.fourier.set(self.default[27])
        self.filterByEntry.insert(0, self.default[28])
        self.fourierLocEntry.insert(0, self.default[29])
        self.cutoffEntry.insert(0, self.default[30])
        
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
        self.default[19] = str(self.doCFM.get())
        self.default[20] = str(self.bwLim.get())
        self.default[21] = self.cfmInEntry.get()
        self.default[22] = self.scopeTimeEntry.get()
        self.default[23] = str(self.saveCFM.get())
        self.default[24] = self.saveCFMToEntry.get()
        self.default[25] = str(self.unsync.get())
        self.default[26] = self.filterTypeEntry.get()
        self.default[27] = str(self.fourier.get())
        self.default[28] = self.filterByEntry.get()
        self.default[29] = self.fourierLocEntry.get()
        self.default[30] = self.cutoffEntry.get()
        
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
        out_channel = hystParam[13]-1   # -1 so indices start at 0
        demod_index = hystParam[14]-1   # -1 so indices start at 0
    
        apilevel = 1  # The API level supported
        # Call a zhinst utility function that returns:
        # - an API session `daq` in order to communicate with devices via the data server.
        # - the device ID string that specifies the device branch in the server's node hierarchy.
        # - the device's discovery properties.
        err_msg = "This example only supports instruments with demodulators."
        (daq, device, props) = zhinst.utils.create_api_session(device_id, apilevel,
                                                               required_devtype='.*LI|.*IA|.*IS&HF2',
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
        
        scale = 0 # Scaling factor for 16-bit integers returned by CFM scope
        
        # Subscribe to scope if performing CFM 
        if self.doCFM.get() == 1 and biasTime+zeroVTime > 0:
            
            scope_time = 0
            for time_idx, rate in enumerate(self.scopeTimes):
                if self.scopeTimeEntry.get() == rate:
                    scope_time = time_idx
                
            scope_channel = int(self.cfmInEntry.get())-1 # -1 to get channel index rather than name
            bwLim = self.bwLim.get()
            
            scope_settings = [['/%s/scopes/0/channel'         % (device), scope_channel],
                              ['/%s/scopes/0/trigchannel'     % (device), -1],
                              #['/%s/scopes/0/triglevel'       % (device), 0.0],
                              #['/%s/scopes/0/trigholdoff'     % (device), 0.1],
                              # Enable bandwidth limiting: avoid antialiasing effects due to
                              # sub-sampling when the scope sample rate is less than the input
                              # channel's sample rate.
                              ['/%s/scopes/0/bwlimit'         % (device), bwLim],
                              # Set the sampling rate.
                              ['/%s/scopes/0/time'            % (device), scope_time],
                              # Enable the scope
                              ['/%s/scopes/0/enable' % device, 1]]
            
            daq.set(scope_settings)
            
            sigout_range = daq.getDouble('/%s/sigins/%d/range' % (device, scope_channel))
            scale = sigout_range/(2**15)  # The scope's wave are 16-bit integers
            
            # CWrite metadata to file
            fileName = self.saveCFMToEntry.get()
            save_cfm_to = open(fileName, "a")
            save_cfm_to.write(self.metadata())
            save_cfm_to.close()
            
            self.cfm_time0 = time.time()
    
        # Perform a global synchronisation between the device and the data server:
        # Ensure that 1. the settings have taken effect on the device before issuing
        # the poll() command and 2. clear the API's data buffers.
        daq.sync()
    
        # Set polling parameters
        poll_timeout = 500  # [ms]
        poll_flags=0
        poll_return_flat_dict=True
        
        # Prepare graph to dynamically display measurements as they are taken
        self.plot = tk.Tk()
        
        # Initialise figure
        
        f = Figure(figsize=(5, 4), dpi=100)
        self.a = f.add_subplot(111)
        
        # Add a tk.DrawingArea
        self.canvas = FigureCanvasTkAgg(f, master=self.plot)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        toolbar = NavigationToolbar2TkAgg(self.canvas, self.plot)
        toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        
        for i in range(numLoops):
            
            if pattern == 'Min-Max':
                
                # Calculate bias to apply
                probeVoltIncr = (probeMaxDC-probeMinDC)/(numSteps-1.0)
                botElectVoltIncr = (botElectMaxDC-botElectMinDC)/(numSteps-1.0)

                for j in range(numSteps):
                    
                    # Update progress
                    self.executeButton['text'] = "Progress: "+"{0:.2f}".format(((i+j/numSteps)/numLoops)*100)+"%"
                    self.hystGUI.update()
                    
                    # Calculate bias to apply cont.
                    probeOffset = probeMinDC+j*probeVoltIncr
                    botElectOffset = botElectMinDC+j*botElectVoltIncr
                    
                    # Record relevant measurements
                    sample = self.bias_zero_samp(daq, device, probeAux, botElectAux, probeOffset, botElectOffset, demod_index,
                       biasTime, zeroVTime, biasInter, zeroVInter, poll_timeout, poll_flags, poll_return_flat_dict, numLoops, scale)
                    self.record_meas(sample)
                    
    
            elif pattern == 'Min-Max-Min':
                
                # Calculate Min-Max bias to apply
                probeVoltIncr = (probeMaxDC-probeMinDC)/(int(numSteps/2)+numSteps%2-1.0)
                botElectVoltIncr = (botElectMaxDC-botElectMinDC)/(int(numSteps/2)+numSteps%2-1.0)
                
                for j in range(int(numSteps/2)+numSteps%2):
                    
                    # Update progress
                    self.executeButton['text'] = "Progress: "+"{0:.2f}".format(((i+j/numSteps)/numLoops)*100)+"%"
                    self.hystGUI.update()
                    
                    # Calculate bias to apply cont.
                    probeOffset = probeMinDC+j*probeVoltIncr
                    botElectOffset = botElectMinDC+j*botElectVoltIncr
                    
                    # Record relevant measurements
                    sample = self.bias_zero_samp(daq, device, probeAux, botElectAux, probeOffset, botElectOffset, demod_index,
                       biasTime, zeroVTime, biasInter, zeroVInter, poll_timeout, poll_flags, poll_return_flat_dict, numLoops, scale)
                    self.record_meas(sample)
                
                # Calculate Max-Min bias to apply
                probeVoltIncr = (probeMaxDC-probeMinDC)/(int(numSteps/2))
                botElectVoltIncr = (botElectMaxDC-botElectMinDC)/(int(numSteps/2))
                
                for j in range(1, int(numSteps/2)+1):
                    
                    # Update progress
                    temp = j-1+int(numSteps/2)+numSteps%2
                    self.executeButton['text'] = "Progress: "+"{0:.2f}".format(((i+temp/numSteps)/numLoops)*100)+"%"
                    self.hystGUI.update()
                    
                    # Calculate bias to apply cont.
                    probeOffset = probeMaxDC-j*probeVoltIncr
                    botElectOffset = botElectMaxDC-j*botElectVoltIncr
                    
                    # Record relevant measurements
                    sample = self.bias_zero_samp(daq, device, probeAux, botElectAux, probeOffset, botElectOffset, demod_index,
                       biasTime, zeroVTime, biasInter, zeroVInter, poll_timeout, poll_flags, poll_return_flat_dict, numLoops, scale)
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
                    self.executeButton['text'] = "Progress: "+"{0:.2f}".format(((i+j/numSteps)/numLoops)*100)+"%"
                    self.hystGUI.update()
                    
                    # Calculate bias to apply cont.
                    probeOffset = j*probeVoltIncr
                    botElectOffset = j*botElectVoltIncr
                    
                    # Record relevant measurements
                    sample = self.bias_zero_samp(daq, device, probeAux, botElectAux, probeOffset, botElectOffset, demod_index,
                       biasTime, zeroVTime, biasInter, zeroVInter, poll_timeout, poll_flags, poll_return_flat_dict, numLoops, scale)
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
                    self.executeButton['text'] = "Progress: "+"{0:.2f}".format(((i+(j+temp)/numSteps)/numLoops)*100)+"%"
                    self.hystGUI.update()
                    
                    # Calculate bias to apply cont.
                    probeOffset = probeMaxDC-j*probeVoltIncr
                    botElectOffset = botElectMaxDC-j*botElectVoltIncr
                    
                    # Record relevant measurements
                    sample = self.bias_zero_samp(daq, device, probeAux, botElectAux, probeOffset, botElectOffset, demod_index,
                       biasTime, zeroVTime, biasInter, zeroVInter, poll_timeout, poll_flags, poll_return_flat_dict, numLoops, scale)
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
                    self.executeButton['text'] = "Progress: "+"{0:.2f}".format(((i+(j+temp)/numSteps)/numLoops)*100)+"%"
                    self.hystGUI.update()
                    
                    # Calculate bias to apply cont.
                    probeOffset = probeMinDC+j*probeVoltIncr
                    botElectOffset = botElectMinDC+j*botElectVoltIncr
                    
                    # Record relevant measurements
                    sample = self.bias_zero_samp(daq, device, probeAux, botElectAux, probeOffset, botElectOffset, demod_index,
                       biasTime, zeroVTime, biasInter, zeroVInter, poll_timeout, poll_flags, poll_return_flat_dict, numLoops, scale)
                    self.record_meas(sample)
                
                
        # Disable the scope.
        if self.doCFM.get() == 1:
            daq.setInt('/%s/scopes/0/enable' % device, 0)
                
        # Update progress
        self.executeButton['text'] = "Execute"
        self.hystGUI.update()
        
        # Fourier filter CFM data
        if self.doCFM.get() == 1:
            self.fourier_filter()
                    
                
    def bias_zero_samp(self, daq, device, probeAux, botElectAux, probeOffset, botElectOffset, demod_index,
                       biasTime, zeroVTime, biasInter, zeroVInter, poll_timeout, poll_flags,
                       poll_return_flat_dict, numLoops, scale):
        
        # Apply Bias
        daq.set([['/%s/auxouts/%d/offset' % (device, probeAux), probeOffset],
                 ['/%s/auxouts/%d/offset' % (device, botElectAux), botElectOffset]])
        
        # Allow bias intermissionary settling time
        if biasInter != 0.0:
            time.sleep(biasInter)
        
        if not self.unsync.get() == 1:
            daq.sync()
                    
        # Record data while bias is being applied
        # Unsubscribe from all paths.
        daq.unsubscribe('*')
        
        path = '/%s/demods/%d/sample' % (device, demod_index) # Demodulator path
        path2 = '/%s/scopes/0/wave' % (device) # CFM scope path
        save_cfm_to = ""
        
        # Open file to append data if performing CFM
        if self.doCFM.get() == 1 and biasTime+zeroVTime > 0:
            
            # Complete cfm dataset will be save to hard disk
            fileName = self.saveCFMToEntry.get()
            save_cfm_to = open(fileName, "a")
            
            
        if biasTime != 0:
            
            daq.subscribe(path)
            
            if self.doCFM.get() == 1:
                daq.subscribe(path2)
            
            data = daq.poll(biasTime, poll_timeout, poll_flags, poll_return_flat_dict)   # *1000 for s -> ms
            # Unsubscribe from all paths
            daq.unsubscribe('*')
                        
            # Check that the dictionary returned is non-empty
            assert data, "poll() returned an empty data dictionary, did you subscribe to any paths?"
                    
            # The data returned is a dictionary of dictionaries that reflects the node's path.
            # Note, the data could be empty if no data had arrived, e.g., if the demods
            # were disabled or had demodulator rate 0.
            assert path in data, "The data dictionary returned by poll has no key `%s`." % path
            
            # Initialise samples to avoid unbound local variable errors
            sample = data[path]
            if self.doCFM.get() == 1:
                scope_sample = data[path2]
            
            tries = 1
            limit = 10
            while tries < limit and len(sample['timestamp'])<=1:
                tries += 1
                
                if self.doCFM.get() == 1:
                    daq.subscribe(path2)
                    
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
                if self.doCFM.get() == 1:
                    scope_sample = data[path2]
                    
    
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
            
            
        if zeroVTime+zeroVInter > 0:
            # Apply 0 V bias between steps
            daq.set([['/%s/auxouts/%d/offset' % (device, probeAux), 0],
                     ['/%s/auxouts/%d/offset' % (device, botElectAux), 0]])
                    
                    
        # Allow 0 V intermissionary settling time
        if zeroVInter != 0.0:
            time.sleep(zeroVInter)
        
        
        if not self.unsync.get() == 1:
            daq.sync()
        
        if zeroVTime != 0.0:
            
            # Resubscribe and poll.                
            daq.subscribe(path)
            if self.doCFM.get() == 1:
                daq.subscribe(path2)
            data = daq.poll(zeroVTime, poll_timeout, poll_flags, poll_return_flat_dict)   # *1000 for s -> ms
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
            if self.doCFM.get() == 1:
                scope_sample2 = data[path2]
            
            # Make sure daq was successfully polled
            # Sometimes it stalls after reading 1 element, otherwise it normally works
            tries = 1
            limit = 10
            while tries < limit and len(sample2['timestamp'])<=1:
                tries += 1
                
                # Resubscribe and poll.                
                daq.subscribe(path)
                data = daq.poll(zeroVTime, poll_timeout, poll_flags, poll_return_flat_dict)   # *1000 for s -> ms
                
                if self.doCFM.get() == 1:
                    daq.subscribe(path2)
                            
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
                if self.doCFM.get() == 1:
                    scope_sample2 = data[path2]
                    
    
            # Check how many seconds of demodulator data were returned by poll.
            # First, get the sampling rate of the device's ADCs, the device clockbase...
            clockbase = float(daq.getInt('/%s/clockbase' % device))
                        
            # Convert timestamps from ticks to seconds via clockbase.
            sample2['t'] = (sample2['timestamp'] - sample2['timestamp'][0])/clockbase
            sample2['t'] += sample2['t'][1]
    
            # Voltages
            sample2['ProbeV'] = np.empty(len(sample2['t']))
            sample2['ProbeV'].fill(0)
            sample2['BotElectV'] = np.empty(len(sample2['t']))
            sample2['BotElectV'].fill(0)
            sample2['TotalV'] = sample2['ProbeV']-sample2['BotElectV']
                        
            # Calculate the demodulator's magnitude and phase and add them to the dict.
            sample2['R'] = np.abs(sample2['x'] + 1j*sample2['y'])
            sample2['Phase'] = np.angle(sample2['x'] + 1j*sample2['y'])
            
        
        # Amalgamate any CFM data and iterpolate times
        if self.doCFM.get() == 1:
            
            if biasTime != 0.0:
                
                # Combine shot trains, saving the scaled scope trains if requested
                shot_sets = np.empty((0))
                if self.saveCFM.get() == 1:
                    # Provide bias metadata
                    save_cfm_to.write("\nProbe Offset\n")
                    save_cfm_to.write(str(probeOffset)+"\n")
                    save_cfm_to.write("Bottom Electrode Offset\n")
                    save_cfm_to.write(str(botElectOffset)+"\n")
                    save_cfm_to.write("Time\n")
                    save_cfm_to.write(str(time.time()-self.cfm_time0)+"\n")
                    
                    for shot_set in scope_sample:
                        for key in shot_set:
                            if key != 'wave':
                                
                                save_cfm_to.write(str(key)+"\n")
                                save_cfm_to.write(str(shot_set[key])+"\n")
                                    
                            else:
                                
                                save_cfm_to.write("wave\n")
                                
                                # Extract and scale the voltages
                                scaled_shots = scale*shot_set['wave']
                                for scaled_shot in scaled_shots:
                                    save_cfm_to.write(str(scaled_shot)+"\n")                                        
                                    
                                shot_sets = np.append(shot_sets, scaled_shots)
                                
                else:
                    
                    for shot_set in scope_sample:
                        scaled_shots = scale*shot_set['wave']
                        shot_sets = np.append(shot_sets, scaled_shots)
            
                # Compress shot train array to same size as other arrays
                sample['CFM_V'] = self.mean_chunks(shot_sets, len(shot_sets), len(sample['t']))
            
            
            if zeroVTime != 0.0:
            
                # Combine shot trains
                shot_sets2 = np.empty((0))
                if self.saveCFM.get() == 1:
                    # Provide bias metadata
                    save_cfm_to.write("\nProbe Offset\n")
                    save_cfm_to.write("0\n")
                    save_cfm_to.write("Bottom Electrode Offset\n")
                    save_cfm_to.write("0\n")
                    save_cfm_to.write("Time\n")
                    save_cfm_to.write(str(time.time()-self.cfm_time0)+"\n")
                    
                    for shot_set in scope_sample2:
                        for key in shot_set:
                            if key != 'wave':
                                
                                save_cfm_to.write(str(key)+"\n")
                                save_cfm_to.write(str(shot_set[key])+"\n")
                                
                            else:
                                
                                save_cfm_to.write("wave\n")
                                
                                # Extract and scale the voltages
                                scaled_shots = scale*shot_set['wave']
                                for scaled_shot in scaled_shots:
                                    save_cfm_to.write(str(scaled_shot)+"\n")
                                    
                                shot_sets2 = np.append(shot_sets2, scaled_shots)
                        
                else:
                    
                    for shot_set in scope_sample2:
                        scaled_shots = scale*shot_set['wave']
                        shot_sets2 = np.append(shot_sets2, scaled_shots)
                
                
                # Compress shot train array to same size as other arrays
                sample2['CFM_V'] = self.mean_chunks(shot_sets2, len(shot_sets2), len(sample2['t']))
                        
                sample['CFM_V'] = np.append(sample['CFM_V'], sample2['CFM_V'])
                
                
            save_cfm_to.close()
                
        if biasTime != 0 and zeroVTime != 0.0:
            
            sample['x'] = np.append(sample['x'], sample2['x'])
            sample['y'] = np.append(sample['y'], sample2['y'])
            sample['R'] = np.append(sample['R'], sample2['R'])
            sample['Phase'] = np.append(sample['Phase'], sample2['Phase'])
            sample['t'] = np.append(sample['t'], sample2['t']+sample['t'][-1])
            sample['ProbeV'] = np.append(sample['ProbeV'], sample2['ProbeV'])
            sample['BotElectV'] = np.append(sample['BotElectV'], sample2['BotElectV'])
            sample['TotalV'] = np.append(sample['TotalV'], sample2['TotalV'])
            
        if biasTime != 0:
            return sample
        if zeroVTime != 0:
            return sample2
        
    # Record all relevant measurements in dictionary
    def record_meas(self, sample):
        
        # Append sampled data to sample train
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
        
        if self.doCFM.get() == 1:
            self.measurements['CFM_V'] =  np.append(self.measurements['CFM_V'], sample['CFM_V'])
        
        # Update graph
        self.update_graph()
        
    # Live display of measurements as they are taken
    def update_graph(self):
        x1 = self.plotxEntry.get()
        y1 = self.plotyEntry.get()
        
        self.plot.title(x1+"-"+y1+" Plot")
        
        self.a.clear()
        
        x, y = self.measurements[x1], self.measurements[y1]
        # Average over repeated values, if specified
        if self.avgRepeatedx.get() == 1:
            y, x = self.avg_xrepeats(self.measurements[y1], self.measurements[x1])
        if self.avgRepeatedy.get() == 1:
            x, y = self.avg_xrepeats(self.measurements[x1], self.measurements[y1])
        
        # Update graph
        self.a.plot(x, y)
        
        # Update canvas
        self.canvas.draw()

        self.plot.update()
        
        
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

        return avgedx, avgedy
        
    
    # Output data
    def output_data(self):        
        
        text = ""
        
        if self.doCFM.get() == 0:
            
            index = -1
            for i in range(len(self.plotSelection)):
                if self.plotSelection[i] == 'CFM_V':
                    index = i
                    break
            
            for i in range(len(self.plotSelection)):
                if not i == index:
                    text += " "+self.plotSelection[i]
            text += "\n"
            
            for i in range(len(self.units)):
                if not i == index:
                    text += " "+self.units[i]
            text += "\n"
            
        else:
            
            for heading in self.plotSelection:
                    text += " "+heading
            text += "\n"
            
            for unit in self.units:
                    text += " "+unit
            text += "\n"

        # Average over repeating values and print to file
        x_get = self.avgRepeatedx.get()
        if x_get == 1 or self.avgRepeatedy.get() == 1:
            
            # Average over x if both x and y averaging are ticked. 
            if x_get == 1:
                x_axis = self.plotxEntry.get()
            else:
                x_axis = self.plotyEntry.get()
            
            total = [0 for meas in self.measurements] # Sums of values to average over initially 0            
            start, end = 0, 1   # Average between y[start] and y[end] so x and y have same lengths
            prevx = self.measurements[x_axis][0]
    
            # If the next value of x is not the same as the previous, add data to the array
            for i in range(1, len(self.measurements[x_axis])):
                # If x is same as previous
                if self.measurements[x_axis][i] == prevx:
                    end += 1
                        
                    # Check if this is the last element of the array
                    if i == len(self.measurements[x_axis])-1:
                        # Add averages to output
                        for k, key in enumerate(self.measurements):
                            if key == 'CFM_V' and self.doCFM.get() == 0:
                                continue
                            if key == x_axis:
                                text += str(prevx) + "    "
                            else:
                                for j in range(start, end):                              
                                    total[k] += self.measurements[key][i]
                                text += str(total[k]/(end-start)) + "    "
                        text += "\n"
                            
                        
                # If x is not the same as previous
                else:
                    for k, key in enumerate(self.measurements):
                        if key == 'CFM_V' and self.doCFM.get() == 0:
                            continue
                        if key == x_axis:
                            text += str(prevx) + "    "
                            prevx = self.measurements[x_axis][i]
                        else:
                            for j in range(start, end):                              
                                total[k] += self.measurements[key][j]
                            text += str(total[k]/(end-start)) + "    "
                    text += "\n"
                        
                    for l in range(len(total)):
                        total[l] = 0
                    start, end = i, i+1
                        
                    # Check if this is the last element of the array
                    if i == len(self.measurements[x_axis])-1:
                        for key in self.measurements:
                            if key == 'CFM_V' and self.doCFM.get() == 0:
                                continue
                            text += str(self.measurements[key][i]) + "    "
                        text += "\n"
        
        else:
            # Print data to file without averaging repeats
            for i in range(len(self.measurements['X'])):
                for key in self.measurements:
                    if key == 'CFM_V' and self.doCFM.get() == 0:
                        continue
                    text += str(self.measurements[key][i])+"    "
                text += "\n"
            
        # Get save location
        f = tk.filedialog.asksaveasfile(mode='w', defaultextension=".txt")
        if f is None: # asksaveasfile returns `None` if dialog closed with 'cancel'.
            return
    
        # Get metadata
        f.write(self.metadata())
        
        f.write(text)
        f.close()
        
        
    # Location to save CFM data to
    def cfm_save_loc(self):
        
        f = tk.filedialog.asksaveasfilename()
        f.replace("\\", "/")
        self.saveCFMToEntry.delete(0, tk.END)
        self.saveCFMToEntry.insert(0, f)
        
        
    # Clear CFM save location
    def clear_cfm_save_loc(self):
        
        fileName = self.saveCFMToEntry.get()
        f = open(fileName, "w")
        f.close()
        
        
    # Interactive simulation to help user understand voltage train times
    def helpPage(self):
        webbrowser.open(self.helpPageURL, new=2)
            
    
    # If CFM is enabled show CFM data plot option, else remove it
    def cfm_enabled(self):
        if self.doCFM.get() == 1:
            self.plotOptions = self.plotSelection
        else:
            self.plotOptions = [opt for opt in self.plotSelection if opt != 'CFM_V']
            
            if self.plotxEntry.get() == 'CFM_V':
                # Change value to first on list
                self.plotxEntry.delete(0, tk.END)
                self.plotxEntry.insert(0, self.plotOptions[0])
                
            if self.plotyEntry.get() == 'CFM_V':
                # Change value to first on list
                self.plotyEntry.delete(0, tk.END)
                self.plotyEntry.insert(0, self.plotOptions[0])
                
        self.plotxEntry.configure(values=self.plotOptions)
        self.plotyEntry.configure(values=self.plotOptions)
        
        
    # Save current settings to file
    def save_settings(self):
        
        f = tk.filedialog.asksaveasfile(mode='w', defaultextension=".txt")
        
        # Write entry field values to file 
        f.write(self.probeMaxDCEntry.get())
        f.write(self.probeMinDCEntry.get())
        f.write(self.botElectMaxDCEntry.get())
        f.write(self.botElectMinDCEntry.get())
        f.write(self.biasTimeEntry.get())
        f.write(self.biasInterEntry.get())
        f.write(self.zeroVTimeEntry.get())
        f.write(self.zeroVInterEntry.get())
        f.write(self.numStepsEntry.get())
        f.write(self.numLoopsEntry.get())
        f.write(self.probeAuxEntry.get())
        f.write(self.botElectAuxEntry.get())
        f.write(self.patternEntry.get())
        f.write(self.plotxEntry.get())
        f.write(self.plotyEntry.get())
        f.write(self.probeOutEntry.get())
        f.write(str(self.avgRepeatedx.get()))
        f.write(str(self.avgRepeatedy.get()))
        f.write(self.demodEntry.get())
        f.write(str(self.doCFM.get()))
        f.write(str(self.bwLim.get()))
        f.write(self.cfmInEntry.get())
        f.write(self.scopeTimeEntry.get())
        f.write(str(self.saveCFM.get()))
        f.write(self.saveCFMToEntry.get())
        f.write(str(self.unsync.get()))
        f.write(self.filterTypeEntry.get())
        f.write(str(self.fourier.get()))
        f.write(self.filterByEntry.get())
        f.write(self.fourierLocEntry.get())
        f.write(self.cutoffEntry.get())
        
        f.close()
        
        
    # Load current settings to file
    def load_settings(self):
        
        # Get new settings
        fileName = tk.filedialog.askopenfilename()
        
        f = open(fileName, "r")
        new_setting = f.read().splitlines()
        f.close()
        
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
        self.cfmInEntry.delete(0, tk.END)
        self.scopeTimeEntry.delete(0, tk.END)
        self.saveCFMToEntry.delete(0, tk.END)
        self.filterTypeEntry.delete(0, tk.END)
        self.filterByEntry.insert(0, tk.END)
        self.fourierLocEntry.insert(0, tk.END)
        self.cutoffEntry.insert(0, tk.END)
        
        # Insert new values into now-cleared entry fields
        self.probeMaxDCEntry.insert(0, new_setting[0])
        self.probeMinDCEntry.insert(0, new_setting[1])
        self.botElectMaxDCEntry.insert(0, new_setting[2])
        self.botElectMinDCEntry.insert(0, new_setting[3])
        self.biasTimeEntry.insert(0, new_setting[4])
        self.biasInterEntry.insert(0, new_setting[5])
        self.zeroVTimeEntry.insert(0, new_setting[6])
        self.zeroVInterEntry.insert(0, new_setting[7])
        self.numStepsEntry.insert(0, new_setting[8])
        self.numLoopsEntry.insert(0, new_setting[9])
        self.probeAuxEntry.insert(0, new_setting[10])
        self.botElectAuxEntry.insert(0, new_setting[11])
        self.patternEntry.insert(0, new_setting[12])
        self.plotxEntry.insert(0, new_setting[13])
        self.plotyEntry.insert(0, new_setting[14])
        self.probeOutEntry.insert(0, new_setting[15])
        self.avgRepeatedx.set(new_setting[16])
        self.avgRepeatedy.set(new_setting[17])
        self.demodEntry.insert(0, new_setting[18])
        self.doCFM.set(new_setting[19])
        self.bwLim.set(new_setting[20])
        self.cfmInEntry.insert(0, new_setting[21])
        self.scopeTimeEntry.insert(0, new_setting[22])
        self.saveCFM.set(new_setting[23])
        self.saveCFMToEntry.insert(0, new_setting[24])
        self.unsync.set(new_setting[25])
        self.filterTypeEntry.insert(0, new_setting[26])
        self.fourier.set(new_setting[27])
        self.filterByEntry.insert(0, new_setting[28])
        self.fourierLocEntry.insert(0, new_setting[29])
        self.cutoffEntry.insert(0, new_setting[30])
        
        
    # Change arr1 of sizelen1 to smaller size len2 by taking means of chinks
    def mean_chunks(self, arr1, len1, len2):
        
        result = np.zeros(len2)
        
        # Larger array length is perfect multiple of smaller array size
        box_size = int(len1/len2)
        if len1%len2 == 0:
            for i in range(len2):
                result[i] = np.mean(arr1[(i*box_size):((i+1)*box_size)])
         
        # Larger array length is not a perfect multiple of smaller array size
        else:
            
            over = int(len1%len2)
            tot_over = 0
            start, end = 0, box_size
            for i in range(len2):
                tot_over += over
                
                if tot_over >= len2:
                    end += 1
                    tot_over -= len2
                    
                result[i] = np.mean(arr1[start:end])
                
                start = end
                end = end+box_size
            
        return result
    
        
    # Prepare metadata
    def metadata(self):
        
        metadata = "Current date & time: " + time.strftime("%c")+"\n\n"
        
        # Entry field values
        metadata += "Probe Max DC: "+self.probeMaxDCEntry.get()+" V\n"
        metadata += "Probe Min DC: "+self.probeMinDCEntry.get()+" V\n"
        metadata += "Bottom Electrode Max DC: "+self.botElectMaxDCEntry.get()+" V\n"
        metadata += "Bottom Electrode Min DC: "+self.botElectMinDCEntry.get()+" V\n"
        metadata += "Bias Time: "+self.biasTimeEntry.get()+" ms\n"
        metadata += "Bias Wait: "+self.biasInterEntry.get()+" ms\n"
        metadata += "0 V Time: "+self.zeroVTimeEntry.get()+" ms\n"
        metadata += "0 V Wait: "+self.zeroVInterEntry.get()+" ms\n"
        metadata += "Number of Steps: "+self.numStepsEntry.get()+"\n"
        metadata += "Number of Loops: "+self.numLoopsEntry.get()+"\n"
        metadata += "Probe Auxiliary Output: "+self.probeAuxEntry.get()+"\n"
        metadata += "Bottom Electrode Auxiliary Output: "+self.botElectAuxEntry.get()+"\n"
        metadata += "Pattern: "+self.patternEntry.get()+"\n"
        metadata += "Probe Output: "+self.probeOutEntry.get()+"\n"
        metadata += "Average Repeated x: "+str(self.avgRepeatedx.get())+"\n"
        metadata += "Average Repeated y: "+str(self.avgRepeatedy.get())+"\n"
        metadata += "Demodulator: "+self.demodEntry.get()+"\n"
        metadata += "Do CFM: "+str(self.doCFM.get())+"\n"
        metadata += "Bandwidth Limit: "+str(self.bwLim.get())+"\n"
        metadata += "CFM Input: "+self.cfmInEntry.get()+"\n"
        metadata += "Scope Sampling Rate: "+self.scopeTimeEntry.get()+"\n"
        metadata += "Save CFM: "+str(self.saveCFM.get())+"\n"
        metadata += "CFM Location: "+self.saveCFMToEntry.get()+"\n"
        metadata += "Unsynchronised: "+str(self.unsync.get())+"\n"
        metadata += "Filter Type: "+self.filterTypeEntry.get()+"\n"
        metadata += "Auto Fourier: "+str(self.fourier.get())+"\n"
        metadata += "Filter By: "+self.filterByEntry.get()+"\n"
        metadata += "Fourier Location: "+self.fourierLocEntry.get()+"\n"
        metadata += "Cutoff: "+self.cutoffEntry.get()+"Hz\n\n"
        
        return metadata
        
      
    # Location to save Fourier data to
    def fourier_save_loc(self):
        
        f = tk.filedialog.asksaveasfilename()
        f.replace("\\", "/")
        self.fourierLocEntry.delete(0, tk.END)
        self.fourierLocEntry.insert(0, f)
        
       
    # Clear data from Fourier data save location
    def clear_fourier_save_loc(self):
        
        fileName = self.fourierLocEntry.get()
        f = open(fileName, "w")
        f.close()
        
        
    # FFT data, apply filter(s), then IFFT back
    def fourier_filter(self):
        
        # Check that user wants their data filtered
        if self.filterTypeEntry.get() != "":
            
            # Get filters to apply
            filters = [filt.strip() for filt in self.filterTypeEntry.get().split(';') if filt != '']
            
            # Get filtering modes
            modes = [mode.strip() for mode in self.filterByEntry.get().split(';') if mode != '']
            
            filt_param = [param.strip() for param in self.cutoffEntry.get().split(';') if param != '']
            
            # Unfiltered fourier transform
            if 'None' in filters:
                
                # Open Fourier data file for appending
                with open(self.fourierLocEntry.get(), "a") as f:
                    
                    f.write(self.metadata())
                    f.write("time\tSignal\tfrequency\tfft\tfiltered_signal\n")
                    f.write("s\t-\tHz\t-\t-\n")
                
                    # FFT shots
                    if 'Shot Set' in self.filterByEntry.get():
                        
                        with open(self.saveCFMToEntry.get(), "r") as data:
                            
                            append = False
                            get_time = False
                            get_start_time = False
                            shot = np.zeros(self.shot_len)                                            
                            i = 0
                            start_time = 0
                            shot_start = 0
                            for line in data:
                                    
                                if line == 'bwlimit\n':                                        
                                    append = False
                                    
                                elif append:
                                    shot[i] = float(line)
                                    i += 1
                                    
                                elif line == 'wave\n':
                                    append = True
                                    i = 0
                                    
                                elif get_time == True:
                                    # Fourier transform shot
                                    dt = float(line)
                                    fft = np.fft.fft(shot)
                                    freq = np.fft.fftfreq(self.shot_len, dt)
                                    
                                    
                                    # Append results to fourier file
                                    for i in range(self.shot_len):
                                        
                                        f.write(str(i*dt+shot_start+start_time)+"\t")
                                        f.write(str(shot[i])+"\t")
                                        f.write(str(freq[i])+"\t")
                                        f.write(str(fft[i].real)+"\t")
                                        f.write(str(fft[i].imag)+"\t")
                                        f.write("-\n")
                                        
                                    # Increment start time for next shot
                                    shot_start += self.shot_len*dt
                                    
                                    get_time = False
                                    
                                elif line == 'dt\n':
                                    get_time = True
                                    
                                elif get_start_time == True:
                                    start_time = float(line)                                                    
                                    get_start_time = False
                                    
                                elif line == 'Time\n':
                                    get_start_time = True
                                        
                    # FFT bias sets
                    if 'Bias Set' in self.filterByEntry.get():
                            
                        with open(self.saveCFMToEntry.get(), "r") as data:
                        
                            append = False
                            get_time = False
                            first_scope = True
                            shot = np.zeros(self.shot_len)
                            shot_train = np.empty((0)) # Shots will be appended to the shot train
                            i = 0
                            dt = 0
                            start_time = 0
                            size = os.path.getsize(self.saveCFMToEntry.get()) # Use file size to detect if EOF has been reached
                            for line in data:
                                
                                size -= len(line) # When size 0, EOF has been reached
                                
                                if line == 'bwlimit\n':    
                                    # Append each shot to the shot train
                                    shot_train = np.append(shot_train, shot)
                                    append = False
                                    
                                elif append:
                                    shot[i] = float(line)
                                    i += 1
                                    
                                elif line == 'wave\n':
                                    append = True
                                    i = 0
                                    
                                elif get_time == True:
                                    dt = float(line)                                                    
                                    get_time = False
                                    
                                elif line == 'dt\n':
                                    get_time = True
                                    
                                elif get_start_time == True:
                                    start_time = float(line)                                                    
                                    get_start_time = False
                                    
                                elif line == 'Time\n':
                                    get_start_time = True
                                    
                                elif first_scope and line == "Probe Offset\n":
                                    first_scope = False
                                    
                                elif line == "Probe Offset\n" or not size:
                                    
                                    fft = np.fft.fft(shot_train)
                                    freq = np.fft.fftfreq(len(shot_train), dt)
                                    
                                    # Append results to fourier file
                                    for i in range(len(shot_train)):
                                        
                                        f.write(str(i*dt+start_time)+"\t")
                                        f.write(str(shot_train[i])+"\t")
                                        f.write(str(freq[i])+"\t")
                                        f.write(str(fft[i].real)+"\t")
                                        f.write(str(fft[i].imag)+"\t")
                                        f.write("-\n")
                                    
                                    # Clear the shot train for the next shots
                                    if size:
                                        shot_train = np.empty((0))
                    
                                                    
            # Open Fourier data file for appending
            if self.fourierLocEntry.get() != "":
                
                with open(self.fourierLocEntry.get(), "a") as f:
                    
                    f.write(self.metadata())
                    f.write("time\tSignal\tfrequency\tfft\tfiltered_signal\n")
                    f.write("s\t-\tHz\t-\t-\n")
                    
                    # Check if user also wants automatic Fourier filtering
                    if self.fourier.get() == 1:
                        
                        # Filter each shot set
                        if 'Shot Set' in modes:
                            
                            # Apply filters
                            for param_idx, filt in enumerate(filters):
                                
                                # Update meta
                                f.write("Meta: Shot Set, "+filt)
                                
                                temp2 = "temp2.txt"
                                temp = "temp.txt"
                                with open(self.saveCFMToEntry.get(), "r") as data:
                                
                                    # Copy original data, replacing values with filtered values,
                                    # then replace original data file with it
                                    with open(temp2, "w") as auto_filt:
                                        # Create temp file to put calculations in
                                        with open(temp, "w") as calcs:
                                            
                                            append = False
                                            get_time = False
                                            get_start_time = False
                                            shot = np.zeros(self.shot_len)                                            
                                            i = 0
                                            start_time = 0
                                            shot_start = 0
                                            for line in data:
                                                    
                                                if line == 'bwlimit\n':                                        
                                                    append = False
                                                    
                                                elif append:
                                                    shot[i] = float(line)
                                                    i += 1
                                                    
                                                elif line == 'wave\n':
                                                    append = True
                                                    i = 0
                                                    
                                                elif get_time == True:
                                                    # Fourier transform shot
                                                    dt = float(line)
                                                    fft = np.fft.fft(shot)
                                                    freq = np.fft.fftfreq(self.shot_len, dt)
                                                    
                                                    # Apply filter
                                                    filt_sig = self.apply_filter(filt, filt_param[param_idx], fft, freq, self.shot_len, np.mean(shot)<0)
                                                    
                                                    # Append results to fourier file
                                                    for i in range(self.shot_len):
                                                        
                                                        f.write(str(i*dt+shot_start+start_time)+"\t")
                                                        f.write(str(shot[i])+"\t")
                                                        f.write(str(freq[i])+"\t")
                                                        f.write(str(fft[i].real)+"\t")
                                                        f.write(str(fft[i].imag)+"\t")
                                                        f.write(str(filt_sig[i])+"\t")
                                                        
                                                        # Add absolute filtered values to temp file as well
                                                        calcs.write(str(filt_sig[i])+"\n")
                                                        
                                                    # Increment start time for next shot
                                                    shot_start += self.shot_len*dt
                                                        
                                                    # Add blank line between each filtering instance
                                                    f.write("\n")
                                                    
                                                    get_time = False
                                                    
                                                elif line == 'dt\n':
                                                    get_time = True
                                                    
                                                elif get_start_time == True:
                                                    start_time = float(line)                                                    
                                                    get_start_time = False
                                                    
                                                elif line == 'Time\n':
                                                    get_start_time = True
                                                    
                                                    
                                        # Read calculations from file
                                        with open(temp, "r") as calcs:
                                            
                                            # Copy metadata and replace non-metadata with filtered data
                                            nonmeta = False
                                            i = 0
                                            data.seek(0) # Go back to start of data file
                                            for line in data:
                                                
                                                if nonmeta:
                                                    
                                                    if i < self.shot_len:
                                                        auto_filt.write(calcs.readline())
                                                        i += 1
                                                        
                                                    else:
                                                        i = 0
                                                        nonmeta = False
                                                        auto_filt.write(line)
                                                        
                                                # Following lines will be non-meta
                                                elif line == 'wave':
                                                    auto_filt.write(line)
                                                    nonmeta = True
                                                   
                                                # Meta
                                                else:
                                                    auto_filt.write(line)
                                                    
                                        os.remove(temp)
                                
                                with open(self.saveCFMToEntry.get(), "w") as data:
                                    with open(temp2, "r") as auto_filt:
                                        for line in auto_filt:
                                            data.write(line)
                                    
                                os.remove(temp2)
                                
                                
                        # Filter each bias set
                        if 'Bias Set' in modes:
                            
                            # Apply filters
                            for param_idx, filt in enumerate(filters):
                                
                                # Update meta
                                f.write("Meta: Bias Set, "+filt)
                                
                                temp2 = "temp2.txt"
                                temp = "temp.txt"
                                with open(self.saveCFMToEntry.get(), "r") as data:
                                
                                    # Copy original data, replacing values with filtered values,
                                    # then replace original data file with it
                                    with open(temp2, "w") as auto_filt:
                                        # Create temp file to put calculations in
                                        with open(temp, "w") as calcs:
                                            
                                            append = False
                                            get_time = False
                                            get_start_time = False
                                            first_scope = True
                                            shot = np.zeros(self.shot_len)
                                            shot_train = np.empty((0)) # Shots will be appended to the shot train
                                            i = 0
                                            dt = 0
                                            start_time = 0
                                            size = os.path.getsize(self.saveCFMToEntry.get()) # Use file size to detect if EOF has been reached
                                            for line in data:
                                                
                                                size -= len(line) # When size 0, EOF has been reached
                                                
                                                if line == 'bwlimit\n':
                                                    # Append each shot to the shot train
                                                    shot_train = np.append(shot_train, shot)
                                                    append = False
                                                    
                                                elif append:
                                                    shot[i] = float(line)
                                                    i += 1
                                                    
                                                elif line == 'wave\n':
                                                    append = True
                                                    i = 0
                                                    
                                                elif get_time == True:
                                                    dt = float(line)                                                    
                                                    get_time = False
                                                    
                                                elif line == 'dt\n':
                                                    get_time = True
                                                    
                                                elif get_start_time == True:
                                                    start_time = float(line)                                                    
                                                    get_start_time = False
                                                    
                                                elif line == 'Time\n':
                                                    get_start_time = True
                                                    
                                                elif first_scope and line == "Probe Offset\n":
                                                    first_scope = False
                                                    
                                                elif line == "Probe Offset\n" or not size:
                                                    
                                                    fft = np.fft.fft(shot_train)
                                                    freq = np.fft.fftfreq(len(shot_train), dt)
                                                    
                                                    # Apply filter
                                                    filt_sig = self.apply_filter(filt, filt_param[param_idx], fft, freq, len(shot_train), np.mean(shot_train)<0)
                                                    
                                                    # Append results to fourier file
                                                    for i in range(self.shot_len):
                                                        
                                                        f.write(str(i*dt+start_time)+"\t")
                                                        f.write(str(shot_train[i])+"\t")
                                                        f.write(str(freq[i])+"\t")
                                                        f.write(str(fft[i].real)+"\t")
                                                        f.write(str(fft[i].imag)+"\t")
                                                        f.write(str(filt_sig[i])+"\t")
                                                        
                                                        # Add absolute filtered values to temp file as well
                                                        calcs.write(str(filt_sig[i])+"\n")
                                                    
                                                    # Add blank line between each filtering instance
                                                    f.write("\n")
                                                    
                                                    # Clear the shot train for the next shots
                                                    if size:
                                                        shot_train = np.empty((0))
                                                    
                                        # Read calculations from file
                                        with open(temp, "r") as calcs:
                                            
                                            # Copy metadata and replace non-metadata with filtered data
                                            nonmeta = False
                                            i = 0
                                            data.seek(0) # Go back to start of data file
                                            for line in data:
                                                
                                                if nonmeta:
                                                    
                                                    if i < self.shot_len:
                                                        auto_filt.write(calcs.readline())
                                                        i += 1
                                                        
                                                    else:
                                                        i = 0
                                                        nonmeta = False
                                                        auto_filt.write(line)
                                                        
                                                # Following lines will be non-meta
                                                elif line == 'wave':
                                                    auto_filt.write(line)
                                                    nonmeta = True
                                                   
                                                # Meta
                                                else:
                                                    auto_filt.write(line)
                                                    
                                        os.remove(temp)
                                
                                with open(self.saveCFMToEntry.get(), "w") as data:
                                    with open(temp2, "r") as auto_filt:
                                        for line in auto_filt:
                                            data.write(line)
                                    
                                os.remove(temp2)
                       
                    # User does not want automatic Fourier analysis
                    else:
                        
                        # Filter each shot set
                        if 'Shot Set' in modes:
                            
                            # Apply filters
                            for param_idx, filt in enumerate(filters):
                                
                                # Update meta
                                f.write("Meta: Shot Set, "+filt)
                                
                                with open(self.saveCFMToEntry.get(), "r") as data:
                                    
                                    append = False
                                    get_time = False
                                    shot = np.zeros(self.shot_len)                                            
                                    i = 0
                                    start_time = 0
                                    shot_start = 0
                                    for line in data:
                                            
                                        if line == 'bwlimit\n':                                        
                                            append = False
                                            
                                        elif append:
                                            shot[i] = float(line)
                                            i += 1
                                            
                                        elif line == 'wave\n':
                                            append = True
                                            i = 0
                                            
                                        elif get_time == True:
                                            # Fourier transform shot
                                            dt = float(line)
                                            fft = np.fft.fft(shot)
                                            freq = np.fft.fftfreq(self.shot_len, dt)
                                            
                                            # Apply filter
                                            filt_sig = self.apply_filter(filt, filt_param[param_idx], fft, freq, len(shot_train), np.mean(shot)<0)
                                            
                                            # Append results to fourier file
                                            for i in range(self.shot_len):
                                                
                                                f.write(str(i*dt+shot_start+start_time)+"\t")
                                                f.write(str(shot[i])+"\t")
                                                f.write(str(freq[i])+"\t")
                                                f.write(str(fft[i].real)+"\t")
                                                f.write(str(fft[i].imag)+"\t")
                                                f.write(str(filt_sig[i].real)+"\t")
                                                f.write(str(filt_sig[i].imag)+"\n")
                                                
                                            # Increment start time for next shot
                                            shot_start += self.shot_len*dt
                                                
                                            # Add blank line between each filtering instance
                                            f.write("\n")
                                            
                                            get_time = False
                                            
                                        elif line == 'dt\n':
                                            get_time = True
                                            
                                        elif get_start_time == True:
                                            start_time = float(line)                                                    
                                            get_start_time = False
                                            
                                        elif line == 'Time\n':
                                            get_start_time = True
                                                
                        
                        # Filter each shot train
                        if 'Bias Set' in modes:
                            
                            # Apply filters
                            for param_idx, filt in enumerate(filters):
                                
                                # Update meta
                                f.write("Meta: Bias Set, "+filt)
                                
                                with open(self.saveCFMToEntry.get(), "r") as data:
                                    
                                    append = False
                                    get_time = False
                                    first_scope = True
                                    shot = np.zeros(self.shot_len)
                                    shot_train = np.empty((0)) # Shots will be appended to the shot train
                                    i = 0
                                    dt = 0
                                    start_time = 0
                                    size = os.path.getsize(self.saveCFMToEntry.get()) # Use file size to detect if EOF has been reached
                                    for line in data:
                                        
                                        size -= len(line) # When size 0, EOF has been reached
                                        
                                        if line == 'bwlimit\n':     
                                            # Append each shot to the shot train
                                            shot_train = np.append(shot_train, shot)
                                            append = False
                                            
                                        elif append:
                                            shot[i] = float(line)
                                            i += 1
                                            
                                        elif line == 'wave\n':
                                            append = True
                                            i = 0
                                            
                                        elif get_time == True:
                                            dt = float(line)                                                    
                                            get_time = False
                                            
                                        elif line == 'dt\n':
                                            get_time = True
                                            
                                        elif get_start_time == True:
                                            start_time = float(line)                                                    
                                            get_start_time = False
                                            
                                        elif line == 'Time\n':
                                            get_start_time = True
                                            
                                        elif first_scope and line == "Probe Offset\n":
                                            first_scope = False
                                            
                                        elif line == "Probe Offset\n" or not size:
                                            
                                            fft = np.fft.fft(shot_train)
                                            freq = np.fft.fftfreq(len(shot_train), dt)
                                            
                                            # Apply filter
                                            filt_sig = self.apply_filter(filt, filt_param[param_idx], fft, freq, len(shot_train), np.mean(shot_train)<0)
                                            
                                            # Append results to fourier file
                                            for i in range(self.shot_len):
                                                
                                                f.write(str(i*dt+start_time)+"\t")
                                                f.write(str(shot_train[i])+"\t")
                                                f.write(str(freq[i])+"\t")
                                                f.write(str(fft[i].real)+"\t")
                                                f.write(str(fft[i].imag)+"\t")
                                                f.write(str(filt_sig[i].real)+"\t")
                                                f.write(str(filt_sig[i].imag)+"\n")
                                            
                                            # Add blank line between each filtering instance
                                            f.write("\n")
                                            
                                            # Clear the shot train for the next shots
                                            if size:
                                                shot_train = np.empty((0))
                                                        
                   
            # Check if user wants automatic Fourier filtering with no seperate output
            elif self.fourier.get() == 1:
                
                # Filter each shot
                if 'Shot Set' in modes:
                    
                    # Apply filters
                    for param_idx, filt in enumerate(filters):
                        
                        # Update meta
                        f.write("Meta: Shot Set, "+filt)
                        
                        temp2 = "temp2.txt"
                        temp = "temp.txt"
                        with open(self.saveCFMToEntry.get(), "r") as data:
                        
                            # Copy original data, replacing values with filtered values,
                            # then replace original data file with it
                            with open(temp2, "w") as auto_filt:
                                # Create temp file to put calculations in
                                with open(temp, "w") as calcs:
                                    
                                    append = False
                                    get_time = False
                                    shot = np.zeros(self.shot_len)                                            
                                    i = 0
                                    for line in data:
                                            
                                        if line == 'bwlimit\n':                                        
                                            append = False
                                            
                                        elif append:
                                            shot[i] = float(line)
                                            i += 1
                                            
                                        elif line == 'wave\n':
                                            append = True
                                            i = 0
                                            
                                        elif get_time == True:
                                            # Fourier transform shot
                                            dt = float(line)
                                            fft = np.fft.fft(shot)
                                            freq = np.fft.fftfreq(self.shot_len, dt)
                                            
                                            # Apply filter
                                            filt_sig = self.apply_filter(filt, filt_param[param_idx], fft, freq, len(shot), np.mean(shot)<0)
                                            
                                            # Append results to fourier file
                                            for i in range(self.shot_len):                                                        
                                                # Add absolute filtered values to temp file as well
                                                calcs.write(str(filt_sig[i])+"\n")
                                            
                                            get_time = False
                                            
                                        elif line == 'dt\n':
                                            get_time = True
                                            
                                            
                                # Read calculations from file
                                with open(temp, "r") as calcs:
                                    
                                    # Copy metadata and replace non-metadata with filtered data
                                    nonmeta = False
                                    i = 0
                                    data.seek(0) # Go back to start of data file
                                    for line in data:
                                        
                                        if nonmeta:
                                            
                                            if i < self.shot_len:
                                                auto_filt.write(calcs.readline())
                                                i += 1
                                                
                                            else:
                                                i = 0
                                                nonmeta = False
                                                auto_filt.write(line)
                                                
                                        # Following lines will be non-meta
                                        elif line == 'wave':
                                            auto_filt.write(line)
                                            nonmeta = True
                                           
                                        # Meta
                                        else:
                                            auto_filt.write(line)
                                            
                                os.remove(temp)
                        
                        with open(self.saveCFMToEntry.get(), "w") as data:
                            with open(temp2, "r") as auto_filt:
                                for line in auto_filt:
                                    data.write(line)
                            
                        os.remove(temp2)
                        
                # Filter each bias set
                if 'Bias Set' in modes:
                    
                    # Apply filters
                    for param_idx, filt in enumerate(filters):
                        
                        # Update meta
                        f.write("Meta: Shot Set, "+filt)
                        
                        temp2 = "temp2.txt"
                        temp = "temp.txt"
                        with open(self.saveCFMToEntry.get(), "r") as data:
                        
                            # Copy original data, replacing values with filtered values,
                            # then replace original data file with it
                            with open(temp2, "w") as auto_filt:
                                # Create temp file to put calculations in
                                with open(temp, "w") as calcs:
                                    
                                    append = False
                                    get_time = False
                                    first_scope = True
                                    shot = np.zeros(self.shot_len)
                                    shot_train = np.empty((0)) # Shots will be appended to the shot train
                                    i = 0
                                    dt = 0
                                    size = os.path.getsize(self.saveCFMToEntry.get()) # Use file size to detect if EOF has been reached
                                    for line in data:
                                        
                                        size -= len(line) # When size is 0, EOF has been reached
                                        
                                        if line == 'bwlimit\n':
                                            # Append each shot to the shot train
                                            shot_train = np.append(shot_train, shot)
                                            append = False
                                            
                                        elif append:
                                            shot[i] = float(line)
                                            i += 1
                                            
                                        elif line == 'wave\n':
                                            append = True
                                            i = 0
                                            
                                        elif get_time == True:
                                            dt = float(line)                                                    
                                            get_time = False
                                            
                                        elif line == 'dt\n':
                                            get_time = True
                                            
                                        elif first_scope and line == "Probe Offset\n":
                                            first_scope = False
                                            
                                        elif line == "Probe Offset\n" or not size:
                                            
                                            fft = np.fft.fft(shot_train)
                                            freq = np.fft.fftfreq(len(shot_train), dt)
                                            
                                            # Apply filter
                                            filt_sig = self.apply_filter(filt, filt_param[param_idx], fft, freq, len(shot_train), np.mean(shot_train)<0)
                                            
                                            # Append results to fourier file
                                            for i in range(self.shot_len):                                                        
                                                # Add absolute filtered values to temp file as well
                                                calcs.write(str(filt_sig[i])+"\n")
                                            
                                            # Clear the shot train for the next shots
                                            if size:
                                                shot_train = np.empty((0))
                                            
                                # Read calculations from file
                                with open(temp, "r") as calcs:
                                    
                                    # Copy metadata and replace non-metadata with filtered data
                                    nonmeta = False
                                    i = 0
                                    data.seek(0) # Go back to start of data file
                                    for line in data:
                                        
                                        if nonmeta:
                                            
                                            if i < self.shot_len:
                                                auto_filt.write(calcs.readline())
                                                i += 1
                                                
                                            else:
                                                i = 0
                                                nonmeta = False
                                                auto_filt.write(line)
                                                
                                        # Following lines will be non-meta
                                        elif line == 'wave\n':
                                            auto_filt.write(line)
                                            nonmeta = True
                                           
                                        # Meta
                                        else:
                                            auto_filt.write(line)
                                            
                                os.remove(temp)
                        
                        with open(self.saveCFMToEntry.get(), "w") as data:
                            with open(temp2, "r") as auto_filt:
                                for line in auto_filt:
                                    data.write(line)
                            
                        os.remove(temp2)
    
    
    # View CFM data in text editor
    def openCFM(self):
        os.startfile(self.saveCFMToEntry.get())
    
    
    # View filter data in text editor
    def openFourier(self):
        os.startfile(self.fourierLocEntry.get())
        
        
    # Convolute signal with filter in frequency domain
    @staticmethod
    def apply_filter(filt, filt_param, fft_orig, freq, size, neg = False):
        
        # Copy fft so we can convolute filters with it without affecting the original fft
        fft = np.copy(fft_orig)
        
        # Get subfilters
        sub_filts = [sub_filt.strip() for sub_filt in filt.split(':') if sub_filt != '' and sub_filt != 'None']
        
        # Get subfilter parameters
        sub_filt_params = [sub_filt_param.strip() for sub_filt_param in filt_param.split(':') if sub_filt_param != '']
        
        # Convolute subfilters with signal. The lowest index filter is applied first
        for param_idx, sub_filt in enumerate(sub_filts):
            
            if sub_filt == 'Low Pass':
                
                cutoff = float(sub_filt_params[param_idx])
                for i in range(size):
                    if freq[i] > cutoff:
                        fft[i] = 0+0j
                        
            if sub_filt == 'High Pass':
                
                cutoff = float(sub_filt_params[param_idx])
                for i in range(size):
                    if freq[i] < cutoff:
                        fft[i] = 0+0j
                
        # Transform filtered signal back to time domain and take absolute values
        # negating them if specified
        if neg:
            return -np.absolute(np.fft.ifft(fft))
        else:
            return np.absolute(np.fft.ifft(fft))
    

if __name__ == "__main__":
    hystGUI = tk.Tk()
    HystGUI(hystGUI)
    hystGUI.mainloop()
