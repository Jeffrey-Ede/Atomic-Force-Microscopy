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

# Dual frequency resonance tracking
class DFRT_GUI(tk.Frame):

    # Initialise main window
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.dfrtGUI = parent
        self.deviceID = 'dev801'
        self.dfrtGUI.title("Dual Frequency Resonance Tracking")
        self.backClr = "#a1dbcd"
        self.btnClr = "#73c6b6"
        self.dfrtGUI.configure(background=self.backClr)
        
        # Device parameters
        self.demodDiffPair = ('1,2', '2,3', '3,4', '4,5', '5,6')
        self.demods = ('1', '2', '3', '4', '5', '6')
        self.filterInput = ('1', '2')
        self.filterdBOct = ('6', '12', '18', '24', '30', '36', '42', '48')
        self.outVoltPeak = ('10 mV', '100 mV', '1 V', '10 V')
        self.setpoint = ('Fixed', 'Toggle', 'Aux Input 1', 'Aux Input 2', 'PID 4 Output')
        self.pidOutMode = ('Sig Out 1: Amplitude', 'Sig Out 2: Amplitude', 'Oscillator: Frequency',
                           'Aux Output: Offset', 'DIO (Int16)')
        self.auxs = ('1', '2', '3', '4')
        self.outVoltRange = ('10 mV', '100 mV', '1 V', '10 V')
        self.inputs = ('1', '2')
        self.outputs = ('1', '2')
        self.filterInputs = ('1', '2')
        self.auxOuts = ('Manual', 'Demod: X', 'Demod: Y', 'Demod: R', 'Demod: Phase', 'PID 1: Output',
                        'PID 2: Output', 'PID 3: Output', 'PID 4: Output')
        
        
        # Read default entry values from file
        self.defaultFile = 'dfrt_default_values.txt'
        dfrtDefaultVal = open(self.defaultFile, 'r')
        self.default = dfrtDefaultVal.read().splitlines()


        """
        1. Initialise all data entry terminals, labels, etc.
        2. Arrange them on a grid
        3. Confgure the grid
        4. Configure their inputs
        """
        # Instantiate widgets
        # Modulation
        self.modLabel = tk.Label(self.dfrtGUI, text="Modulation", font=("bold", 10), bg=self.backClr)
                
        # Resonant frequency
        self.resFreqLabel = tk.Label(self.dfrtGUI, text="Resonant Freq", bg=self.backClr)
        self.resFreqUnit = tk.Label(self.dfrtGUI, text="kHz", bg=self.backClr)
        self.resFreqEntry = tk.Entry(self.dfrtGUI, validate="key")
        self.resFreqEntry['validatecommand'] = (self.resFreqEntry.register(self.testValPos),'%P','%i','%d')
        
        # Sideband frequency difference
        self.sidebandDiffLabel = tk.Label(self.dfrtGUI, text="Sideband Freq", bg=self.backClr)
        self.sidebandDiffUnit = tk.Label(self.dfrtGUI, text="kHz", bg=self.backClr)
        self.sidebandDiffEntry = tk.Entry(self.dfrtGUI, validate="key")
        self.sidebandDiffEntry['validatecommand'] = (self.sidebandDiffEntry.register(self.testValPos),'%P','%i','%d')
        
        # Modulation output voltage
        self.modOutLabel = tk.Label(self.dfrtGUI, text="Modulation Volt", bg=self.backClr)
        self.modOutUnit = tk.Label(self.dfrtGUI, text="V", bg=self.backClr)
        self.modOutEntry = tk.Entry(self.dfrtGUI, validate="key")
        self.modOutEntry['validatecommand'] = (self.modOutEntry.register(self.testValPos),'%P','%i','%d')
        
        # PID
        self.pidLabel = tk.Label(self.dfrtGUI, text="PID", font=("bold", 10), bg=self.backClr)
        
        # Demodulator difference pair
        self.demodDiffPairLabel = tk.Label(self.dfrtGUI, text="Demod Diff Pair", bg=self.backClr)
        self.demodDiffPairUnit = tk.Label(self.dfrtGUI, text="", bg=self.backClr)
        self.demodDiffPairEntry = tk.ttk.Combobox(self.dfrtGUI, values=self.demodDiffPair)
        
        # Setpoint mode
        self.setpointLabel = tk.Label(self.dfrtGUI, text="Setpoint Mode", bg=self.backClr)
        self.setpointUnit = tk.Label(self.dfrtGUI, text="", bg=self.backClr)
        self.setpointEntry = tk.ttk.Combobox(self.dfrtGUI, values=self.setpoint)
        
        # Setpoint
        self.setLabel = tk.Label(self.dfrtGUI, text="Setpoint", bg=self.backClr)
        self.setUnit = tk.Label(self.dfrtGUI, text="V", bg=self.backClr)
        self.setEntry = tk.Entry(self.dfrtGUI, validate="key")
        self.setEntry['validatecommand'] = (self.setEntry.register(self.testValPos),'%P','%i','%d')
        
        # Output mode
        self.outModeLabel = tk.Label(self.dfrtGUI, text="Output Mode", bg=self.backClr)
        self.outModeUnit = tk.Label(self.dfrtGUI, text="", bg=self.backClr)
        self.outModeEntry = tk.ttk.Combobox(self.dfrtGUI, values=self.pidOutMode)
        
        # Output demodulator
        self.outDemodLabel = tk.Label(self.dfrtGUI, text="Output Demod", bg=self.backClr)
        self.outDemodUnit = tk.Label(self.dfrtGUI, text="", bg=self.backClr)
        self.outDemodEntry = tk.ttk.Combobox(self.dfrtGUI, values=self.demods)
        
        # Center
        self.centerLabel = tk.Label(self.dfrtGUI, text="Center", bg=self.backClr)
        self.centerUnit = tk.Label(self.dfrtGUI, text= "kHz", bg=self.backClr)
        self.centerEntry = tk.Entry(self.dfrtGUI, validate="key")
        self.centerEntry['validatecommand'] = (self.setEntry.register(self.testValPos),'%P','%i','%d')
        
        # Range
        self.rangeLabel = tk.Label(self.dfrtGUI, text="Range", bg=self.backClr)
        self.rangeUnit = tk.Label(self.dfrtGUI, text= "kHz", bg=self.backClr)
        self.rangeEntry = tk.Entry(self.dfrtGUI, validate="key")
        self.rangeEntry['validatecommand'] = (self.setEntry.register(self.testValPos),'%P','%i','%d')
        
        # P
        self.pLabel = tk.Label(self.dfrtGUI, text="Proportional", bg=self.backClr)
        self.pUnit = tk.Label(self.dfrtGUI, text= "Hz/V", bg=self.backClr)
        self.pEntry = tk.Entry(self.dfrtGUI, validate="key")
        self.pEntry['validatecommand'] = (self.setEntry.register(self.testVal),'%P','%i','%d')
        
        # I
        self.iLabel = tk.Label(self.dfrtGUI, text="Integral", bg=self.backClr)
        self.iUnit = tk.Label(self.dfrtGUI, text= "Hz/V/s", bg=self.backClr)
        self.iEntry = tk.Entry(self.dfrtGUI, validate="key")
        self.iEntry['validatecommand'] = (self.setEntry.register(self.testVal),'%P','%i','%d')
        
        # D
        self.dLabel = tk.Label(self.dfrtGUI, text="Differential", bg=self.backClr)
        self.dUnit = tk.Label(self.dfrtGUI, text= "Hz/V*s", bg=self.backClr)
        self.dEntry = tk.Entry(self.dfrtGUI, validate="key")
        self.dEntry['validatecommand'] = (self.setEntry.register(self.testVal),'%P','%i','%d')
        
        # TC mode
        self.tcMode = tk.IntVar()
        self.tcModeLabel = tk.Label(self.dfrtGUI, text="TC Mode", bg=self.backClr)
        self.tcModeEntry = tk.Checkbutton(self.dfrtGUI, text="", variable=self.tcMode, onvalue=1,
                                            offvalue=0, bg=self.backClr)
        
        # Auxillary I/O
        self.auxIOLabel = tk.Label(self.dfrtGUI, text="Aux I/O", font=("bold", 10), bg=self.backClr)
        
        # Auxillary X
        self.auxXLabel = tk.Label(self.dfrtGUI, text="Auxillary", bg=self.backClr)
        self.auxXUnit = tk.Label(self.dfrtGUI, text="", bg=self.backClr)
        self.auxXEntry = tk.ttk.Combobox(self.dfrtGUI, values=self.auxs)
        
        # Auxillary Y
        self.auxYLabel = tk.Label(self.dfrtGUI, text="Auxillary", bg=self.backClr)
        self.auxYUnit = tk.Label(self.dfrtGUI, text="", bg=self.backClr)
        self.auxYEntry = tk.ttk.Combobox(self.dfrtGUI, values=self.auxs)
        
        # Demodulation X
        self.demodXLabel = tk.Label(self.dfrtGUI, text="Demodulation", bg=self.backClr)
        self.demodXEntry = tk.ttk.Combobox(self.dfrtGUI, values=self.demods)
        
        # Demodulation Y
        self.demodYLabel = tk.Label(self.dfrtGUI, text="Demodulation", bg=self.backClr)
        self.demodYEntry = tk.ttk.Combobox(self.dfrtGUI, values=self.demods)
        
        # Auxillary output X
        self.auxOutXLabel = tk.Label(self.dfrtGUI, text="Output", bg=self.backClr)
        self.auxOutXUnit = tk.Label(self.dfrtGUI, text="", bg=self.backClr)
        self.auxOutXEntry = tk.ttk.Combobox(self.dfrtGUI, values=self.auxOuts)
        
        # Auxillary output Y
        self.auxOutYLabel = tk.Label(self.dfrtGUI, text="Output", bg=self.backClr)
        self.auxOutYUnit = tk.Label(self.dfrtGUI, text="", bg=self.backClr)
        self.auxOutYEntry = tk.ttk.Combobox(self.dfrtGUI, values=self.auxOuts)
        
        # Auxillary output X scale
        self.auxXScaleLabel = tk.Label(self.dfrtGUI, text="Scale", bg=self.backClr)
        self.auxXScaleUnit = tk.Label(self.dfrtGUI, text="", bg=self.backClr)
        self.auxXScaleEntry = tk.Entry(self.dfrtGUI, validate="key")
        self.auxXScaleEntry['validatecommand'] = (self.auxXScaleEntry.register(self.testValPos),'%P','%i','%d')
        
        # Auxillary Output Y scale
        self.auxYScaleLabel = tk.Label(self.dfrtGUI, text="Scale", bg=self.backClr)
        self.auxYScaleUnit = tk.Label(self.dfrtGUI, text="", bg=self.backClr)
        self.auxYScaleEntry = tk.Entry(self.dfrtGUI, validate="key")
        self.auxYScaleEntry['validatecommand'] = (self.auxYScaleEntry.register(self.testValPos),'%P','%i','%d')
        
        
        # Lock-in MF
        self.lockinMFLabel = tk.Label(self.dfrtGUI, text="Lock-In MF", font=("bold", 10), bg=self.backClr)
        
        # Input voltage range
        self.inVoltRangeLabel = tk.Label(self.dfrtGUI, text="Input Range", bg=self.backClr)
        self.inVoltRangeUnit = tk.Label(self.dfrtGUI, text="", bg=self.backClr)
        self.inVoltRangeEntry = tk.Entry(self.dfrtGUI, validate="key")
        self.inVoltRangeEntry['validatecommand'] = (self.inVoltRangeEntry.register(self.testValPos),'%P','%i','%d')
        
        # Output voltage range
        self.outVoltRangeLabel = tk.Label(self.dfrtGUI, text="Output Range", bg=self.backClr)
        self.outVoltRangeUnit = tk.Label(self.dfrtGUI, text="", bg=self.backClr)
        self.outVoltRangeEntry = tk.ttk.Combobox(self.dfrtGUI, values=self.outVoltRange)
        
        # Signal Input
        self.inputLabel = tk.Label(self.dfrtGUI, text="Input", bg=self.backClr)
        self.inputUnit = tk.Label(self.dfrtGUI, text="", bg=self.backClr)
        self.inputEntry = tk.ttk.Combobox(self.dfrtGUI, values=self.inputs)
        
        # Signal Output
        self.outputLabel = tk.Label(self.dfrtGUI, text="Output", bg=self.backClr)
        self.outputUnit = tk.Label(self.dfrtGUI, text="", bg=self.backClr)
        self.outputEntry = tk.ttk.Combobox(self.dfrtGUI, values=self.outputs)
        
        # Demodulator
        self.demodLabel = tk.Label(self.dfrtGUI, text="Demodulator", bg=self.backClr)
        self.demodUnit = tk.Label(self.dfrtGUI, text="", bg=self.backClr)
        self.demodEntry = tk.ttk.Combobox(self.dfrtGUI, values=self.demods)
        
        # Demodulator frequency
        self.demodFreqLabel = tk.Label(self.dfrtGUI, text="Demod Freq", bg=self.backClr)
        self.demodFreqUnit = tk.Label(self.dfrtGUI, text="kHz", bg=self.backClr)
        self.demodFreqEntry = tk.Entry(self.dfrtGUI, validate="key")
        self.demodFreqEntry['validatecommand'] = (self.demodFreqEntry.register(self.testValPos),'%P','%i','%d')
        
        # Filter input
        self.filterInputLabel = tk.Label(self.dfrtGUI, text="Filter Input", bg=self.backClr)
        self.filterInputUnit = tk.Label(self.dfrtGUI, text="", bg=self.backClr)
        self.filterInputEntry = tk.ttk.Combobox(self.dfrtGUI, values=self.filterInputs)
        
        # Filter dB/Oct
        self.filterdBOctLabel = tk.Label(self.dfrtGUI, text="Filter dB/Oct", bg=self.backClr)
        self.filterdBOctUnit = tk.Label(self.dfrtGUI, text="dB/Oct", bg=self.backClr)
        self.filterdBOctEntry = tk.ttk.Combobox(self.dfrtGUI, values=self.filterdBOct)
        
        # Filter time constant
        self.filterTCLabel = tk.Label(self.dfrtGUI, text="Filter TC", bg=self.backClr)
        self.filterTCUnit = tk.Label(self.dfrtGUI, text="s", bg=self.backClr)
        self.filterTCEntry = tk.Entry(self.dfrtGUI, validate="key")
        self.filterTCEntry['validatecommand'] = (self.filterTCEntry.register(self.testValPos),'%P','%i','%d')
        
        
        # Execution buttons
        self.configButton = tk.Button(self.dfrtGUI, text='Configure', command=self.config, bg=self.btnClr)
        self.restoreDefaultButton = tk.Button(self.dfrtGUI, text='Restore Default Values',
                                              command=self.restoreDefault, bg=self.btnClr)
        self.makeDefaultButton = tk.Button(self.dfrtGUI, text='Make Values Default',
                                           command=self.makeDefault, bg=self.btnClr)
        

        ###################################################
        # Grid positions of labels, entry boxes, etc.                
        # Modulation
        self.modLabel.grid(row=0, column=0, sticky=tk.W)
        
        # Resonant frequency
        self.resFreqLabel.grid(row=1, column=0, sticky=tk.W)
        self.resFreqUnit.grid(row=1, column=2, sticky=tk.W)
        self.resFreqEntry.grid(row=1, column=1, sticky=tk.E+tk.W)
        
        # Sideband frequency difference
        self.sidebandDiffLabel.grid(row=1, column=3, sticky=tk.W)
        self.sidebandDiffUnit.grid(row=1, column=5, sticky=tk.W)
        self.sidebandDiffEntry.grid(row=1, column=4, sticky=tk.E+tk.W)
        
        # Modulation output voltage
        self.modOutLabel.grid(row=2, column=0, sticky=tk.W)
        self.modOutUnit.grid(row=2, column=2, sticky=tk.W)
        self.modOutEntry.grid(row=2, column=1, sticky=tk.E+tk.W)
        
        
        # PID
        self.pidLabel.grid(row=3, column=0, sticky=tk.W)
        
        # Demodulator difference pair
        self.demodDiffPairLabel.grid(row=4, column=0, sticky=tk.W)
        self.demodDiffPairUnit.grid(row=4, column=2, sticky=tk.W)
        self.demodDiffPairEntry.grid(row=4, column=1, sticky=tk.E+tk.W)
        
        # Setpoint mode
        self.setpointLabel.grid(row=5, column=0, sticky=tk.W)
        self.setpointUnit.grid(row=5, column=2, sticky=tk.W)
        self.setpointEntry.grid(row=5, column=1, sticky=tk.E+tk.W)
        
        # Setpoint
        self.setLabel.grid(row=5, column=3, sticky=tk.W)
        self.setUnit.grid(row=5, column=5, sticky=tk.W)
        self.setEntry.grid(row=5, column=4, sticky=tk.E+tk.W)
        
        # Output mode
        self.outModeLabel.grid(row=6, column=0, sticky=tk.W)
        self.outModeUnit.grid(row=6, column=2, sticky=tk.W)
        self.outModeEntry.grid(row=6, column=1, sticky=tk.E+tk.W)
        
        # Output demodulator
        self.outDemodLabel.grid(row=6, column=3, sticky=tk.W)
        self.outDemodUnit.grid(row=6, column=5, sticky=tk.W)
        self.outDemodEntry.grid(row=6, column=4, sticky=tk.E+tk.W)
        
        # Center
        self.centerLabel.grid(row=7, column=0, sticky=tk.W)
        self.centerUnit.grid(row=7, column=2, sticky=tk.W)
        self.centerEntry.grid(row=7, column=1, sticky=tk.E+tk.W)
        
        # Range
        self.rangeLabel.grid(row=7, column=3, sticky=tk.W)
        self.rangeUnit.grid(row=7, column=5, sticky=tk.W)
        self.rangeEntry.grid(row=7, column=4, sticky=tk.E+tk.W)
        
        # P
        self.pLabel.grid(row=8, column=0, sticky=tk.W)
        self.pUnit.grid(row=8, column=2, sticky=tk.W)
        self.pEntry.grid(row=8, column=1, sticky=tk.E+tk.W)
        
        # I
        self.iLabel.grid(row=8, column=3, sticky=tk.W)
        self.iUnit.grid(row=8, column=5, sticky=tk.W)
        self.iEntry.grid(row=8, column=4, sticky=tk.E+tk.W)
        
        # D
        self.dLabel.grid(row=8, column=6, sticky=tk.W)
        self.dUnit.grid(row=8, column=8, sticky=tk.W)
        self.dEntry.grid(row=8, column=7, sticky=tk.E+tk.W)
        
        # TC Mode
        self.tcModeLabel.grid(row=7, column=6, sticky=tk.W)
        self.tcModeEntry.grid(row=7, column=7, sticky=tk.W)
        
        
        # Auxillary I/O
        self.auxIOLabel.grid(row=9, column=0, sticky=tk.W)
        
        # Auxillary output X
        self.auxXLabel.grid(row=10, column=0, sticky=tk.W)
        self.auxXUnit.grid(row=10, column=2, sticky=tk.W)
        self.auxXEntry.grid(row=10, column=1, sticky=tk.E+tk.W)
        
        # Auxillary output Y
        self.auxYLabel.grid(row=10, column=3, sticky=tk.W)
        self.auxYUnit.grid(row=10, column=5, sticky=tk.W)
        self.auxYEntry.grid(row=10, column=4, sticky=tk.E+tk.W)
        
        # Demodulation X
        self.demodXLabel.grid(row=13, column=0, sticky=tk.W)
        self.demodXEntry.grid(row=13, column=1, sticky=tk.E+tk.W)
        
        # Demodulation Y
        self.demodYLabel.grid(row=13, column=3, sticky=tk.W)
        self.demodYEntry.grid(row=13, column=4, sticky=tk.E+tk.W)
        
        # Auxillary output X
        self.auxOutXLabel.grid(row=11, column=0, sticky=tk.W)
        self.auxOutXUnit.grid(row=11, column=2, sticky=tk.W)
        self.auxOutXEntry.grid(row=11, column=1, sticky=tk.E+tk.W)
        
        # Auxillary output Y
        self.auxOutYLabel.grid(row=11, column=3, sticky=tk.W)
        self.auxOutYUnit.grid(row=11, column=5, sticky=tk.W)
        self.auxOutYEntry.grid(row=11, column=4, sticky=tk.E+tk.W)
        
        # Auxillary output X scale
        self.auxXScaleLabel.grid(row=12, column=0, sticky=tk.W)
        self.auxXScaleEntry.grid(row=12, column=1, sticky=tk.E+tk.W)
        
        # Auxillary output Y scale
        self.auxYScaleLabel.grid(row=12, column=3, sticky=tk.W)
        self.auxYScaleEntry.grid(row=12, column=4, sticky=tk.E+tk.W)
        
        
        # Lock-in MF label
        self.lockinMFLabel.grid(row=14, column=0, sticky=tk.W)
        
        # Input
        self.inputLabel.grid(row=15, column=0, sticky=tk.W)
        self.inputUnit.grid(row=15, column=2, sticky=tk.W)
        self.inputEntry.grid(row=15, column=1, sticky=tk.E+tk.W)
        
        # Input voltage range
        self.inVoltRangeLabel.grid(row=15, column=3, sticky=tk.W)
        self.inVoltRangeUnit.grid(row=15, column=5, sticky=tk.W)
        self.inVoltRangeEntry.grid(row=15, column=4, sticky=tk.E+tk.W)
        
        # Output
        self.outputLabel.grid(row=16, column=0, sticky=tk.W)
        self.outputUnit.grid(row=16, column=2, sticky=tk.W)
        self.outputEntry.grid(row=16, column=1, sticky=tk.E+tk.W)
        
        # Output voltage range
        self.outVoltRangeLabel.grid(row=16, column=3, sticky=tk.W)
        self.outVoltRangeUnit.grid(row=16, column=5, sticky=tk.W)
        self.outVoltRangeEntry.grid(row=16, column=4, sticky=tk.E+tk.W)
        
        # Demodulator
        self.demodLabel.grid(row=17, column=0, sticky=tk.W)
        self.demodUnit.grid(row=17, column=2, sticky=tk.W)
        self.demodEntry.grid(row=17, column=1, sticky=tk.E+tk.W)
        
        # Demodulator frequency
        self.demodFreqLabel.grid(row=17, column=3, sticky=tk.W)
        self.demodFreqUnit.grid(row=17, column=5, sticky=tk.W)
        self.demodFreqEntry.grid(row=17, column=4, sticky=tk.E+tk.W)
        
        # Filter input
        self.filterInputLabel.grid(row=18, column=0, sticky=tk.W)
        self.filterInputUnit.grid(row=18, column=2, sticky=tk.W)
        self.filterInputEntry.grid(row=18, column=1, sticky=tk.E+tk.W)
        
        # Filter dB/Oct
        self.filterdBOctLabel.grid(row=18, column=3, sticky=tk.W)
        self.filterdBOctUnit.grid(row=18, column=5, sticky=tk.W)
        self.filterdBOctEntry.grid(row=18, column=4, sticky=tk.E+tk.W)
        
        # Filter time constant
        self.filterTCLabel.grid(row=19, column=0, sticky=tk.W)
        self.filterTCUnit.grid(row=19, column=2, sticky=tk.W)
        self.filterTCEntry.grid(row=19, column=1, sticky=tk.E+tk.W)
        
        
        # Execution buttons
        self.configButton.grid(row=0, column=7, sticky=tk.E+tk.W)
        self.restoreDefaultButton.grid(row=1, column=7, sticky=tk.E+tk.W)
        self.makeDefaultButton.grid(row=2, column=7, sticky=tk.E+tk.W)
        
        
        # Configure grid spacing
        for row_num in range(self.dfrtGUI.grid_size()[1]):
            self.dfrtGUI.rowconfigure(row_num, pad=4)
            
        for col_num in range(self.dfrtGUI.grid_size()[0]):
            self.dfrtGUI.columnconfigure(col_num, pad=5)
        
            
        # Insert defaults into now-cleared entry fields
        self.resFreqEntry.insert(0, self.default[0])
        self.sidebandDiffEntry.insert(0, self.default[1])
        self.modOutEntry.insert(0, self.default[2])
        self.demodDiffPairEntry.insert(0, self.default[3])
        self.setpointEntry.insert(0, self.default[4])
        self.setEntry.insert(0, self.default[5])
        self.outModeEntry.insert(0, self.default[6])
        self.outDemodEntry.insert(0, self.default[7])
        self.centerEntry.insert(0, self.default[8])
        self.rangeEntry.insert(0, self.default[9])
        self.pEntry.insert(0, self.default[10])
        self.iEntry.insert(0, self.default[11])
        self.dEntry.insert(0, self.default[12])
        self.tcMode.set(self.default[13])
        self.demodXEntry.insert(0, self.default[14])
        self.demodYEntry.insert(0, self.default[15])
        self.auxOutXEntry.insert(0, self.default[16])
        self.auxOutYEntry.insert(0, self.default[17])
        self.auxXScaleEntry.insert(0, self.default[18])
        self.auxYScaleEntry.insert(0, self.default[19])
        self.inputEntry.insert(0, self.default[20])
        self.inVoltRangeEntry.insert(0, self.default[21])
        self.outputEntry.insert(0, self.default[22])
        self.outVoltRangeEntry.insert(0, self.default[23])
        self.demodEntry.insert(0, self.default[24])
        self.demodFreqEntry.insert(0, self.default[25])
        self.filterInputEntry.insert(0, self.default[26])
        self.filterdBOctEntry.insert(0, self.default[27])
        self.filterTCEntry.insert(0, self.default[28])
        self.auxXEntry.insert(0, self.default[29])
        self.auxYEntry.insert(0, self.default[30])

            
        # Configure apparatus
    def config(self):
        self.dfrtGUI.destroy()
    
                  
    # Restore default entry values
    def restoreDefault(self):
        
        # Clear the entry fields
        self.resFreqEntry.delete(0, tk.END)
        self.sidebandDiffEntry.delete(0, tk.END)
        self.modOutEntry.delete(0, tk.END)
        self.demodDiffPairEntry.delete(0, tk.END)
        self.setpointEntry.delete(0, tk.END)
        self.setEntry.delete(0, tk.END)
        self.outModeEntry.delete(0, tk.END)
        self.outDemodEntry.delete(0, tk.END)
        self.centerEntry.delete(0, tk.END)
        self.rangeEntry.delete(0, tk.END)
        self.pEntry.delete(0, tk.END)
        self.iEntry.delete(0, tk.END)
        self.dEntry.delete(0, tk.END)
        self.demodXEntry.delete(0, tk.END)
        self.demodYEntry.delete(0, tk.END)
        self.auxOutXEntry.delete(0, tk.END)
        self.auxOutYEntry.delete(0, tk.END)
        self.auxXScaleEntry.delete(0, tk.END)
        self.auxYScaleEntry.delete(0, tk.END)
        self.inputEntry.delete(0, tk.END)
        self.inVoltRangeEntry.delete(0, tk.END)
        self.outputEntry.delete(0, tk.END)
        self.outVoltRangeEntry.delete(0, tk.END)
        self.demodEntry.delete(0, tk.END)
        self.demodFreqEntry.delete(0, tk.END)
        self.filterInputEntry.delete(0, tk.END)
        self.filterdBOctEntry.delete(0, tk.END)
        self.filterTCEntry.delete(0, tk.END)
        self.auxXEntry.delete(0, tk.END)
        self.auxYEntry.delete(0, tk.END)
        
        # Insert defaults into now-cleared entry fields
        self.resFreqEntry.insert(0, self.default[0])
        self.sidebandDiffEntry.insert(0, self.default[1])
        self.modOutEntry.insert(0, self.default[2])
        self.demodDiffPairEntry.insert(0, self.default[3])
        self.setpointEntry.insert(0, self.default[4])
        self.setEntry.insert(0, self.default[5])
        self.outModeEntry.insert(0, self.default[6])
        self.outDemodEntry.insert(0, self.default[7])
        self.centerEntry.insert(0, self.default[8])
        self.rangeEntry.insert(0, self.default[9])
        self.pEntry.insert(0, self.default[10])
        self.iEntry.insert(0, self.default[11])
        self.dEntry.insert(0, self.default[12])
        self.tcMode.set(self.default[13])
        self.demodXEntry.insert(0, self.default[14])
        self.demodYEntry.insert(0, self.default[15])
        self.auxOutXEntry.insert(0, self.default[16])
        self.auxOutYEntry.insert(0, self.default[17])
        self.auxXScaleEntry.insert(0, self.default[18])
        self.auxYScaleEntry.insert(0, self.default[19])
        self.inputEntry.insert(0, self.default[20])
        self.inVoltRangeEntry.insert(0, self.default[21])
        self.outputEntry.insert(0, self.default[22])
        self.outVoltRangeEntry.insert(0, self.default[23])
        self.demodEntry.insert(0, self.default[24])
        self.demodFreqEntry.insert(0, self.default[25])
        self.filterInputEntry.insert(0, self.default[26])
        self.filterdBOctEntry.insert(0, self.default[27])
        self.filterTCEntry.insert(0, self.default[28])
        self.auxXEntry.insert(0, self.default[29])
        self.auxYEntry.insert(0, self.default[30])
    
        
    # Make current values default
    def makeDefault(self):
        self.default[0] = self.resFreqEntry.get()
        self.default[1] = self.sidebandDiffEntry.get()
        self.default[2] = self.modOutEntry.get()
        self.default[3] = self.demodDiffPairEntry.get()
        self.default[4] = self.setpointEntry.get()
        self.default[5] = self.setEntry.get()
        self.default[6] = self.outModeEntry.get()
        self.default[7] = self.outDemodEntry.get()
        self.default[8] = self.centerEntry.get()
        self.default[9] = self.rangeEntry.get()
        self.default[10] = self.pEntry.get()
        self.default[11] = self.iEntry.get()
        self.default[12] = self.dEntry.get()
        self.default[13] = str(self.tcMode.get())
        self.default[14] = self.demodXEntry.get()
        self.default[15] = self.demodYEntry.get()
        self.default[16] = self.auxOutXEntry.get()
        self.default[17] = self.auxOutYEntry.get()
        self.default[18] = self.auxXScaleEntry.get()
        self.default[19] = self.auxYScaleEntry.get()
        self.default[20] = self.inputEntry.get()
        self.default[21] = self.inVoltRangeEntry.get()
        self.default[22] = self.outputEntry.get()
        self.default[23] = self.outVoltRangeEntry.get()
        self.default[24] = self.demodEntry.get()
        self.default[25] = self.demodFreqEntry.get()
        self.default[26] = self.filterInputEntry.get()
        self.default[27] = self.filterdBOctEntry.get()
        self.default[28] = self.filterTCEntry.get()
        self.default[29] = self.auxXEntry.get()
        self.default[30] = self.auxYEntry.get()
        
        defaults = open(self.defaultFile, 'w')
        for default in self.default:
            defaults.write(default+'\n')

            
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

if __name__ == "__main__":
    dfrtGUI = tk.Tk()
    DFRT_GUI(dfrtGUI)
    dfrtGUI.mainloop()