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
class Normal_PFM_GUI(tk.Frame):

    # Initialise main window
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.pfmGUI = parent
        self.deviceID = 'dev801'
        self.pfmGUI.title("Normal PFM Setup")
        self.backClr = "#a1dbcd"
        self.btnClr = "#73c6b6"
        self.pfmGUI.configure(background=self.backClr)
        
        # Device parameters
        self.demods = ('1', '2', '3', '4', '5', '6')
        self.outVoltRange = ('10 mV', '100 mV', '1 V', '10 V')
        self.outVoltRangeToVolt = {'10 mV': 0.01, '100 mV': 0.1, '1 V': 1.0, '10 V': 10.0}
        self.filterdBOct = ('6', '12', '18', '24', '30', '36', '42', '48')
        self.demodDiffPair = ('1,2', '2,3', '3,4', '4,5', '5,6')
        self.inputs = ('1', '2')
        self.outputs = ('1', '2')
        self.filterInputs = ('1', '2')
        self.auxs = ('1', '2', '3', '4')
        self.auxOuts = ('Manual', 'Demod: X', 'Demod: Y', 'Demod: R', 'Demod: Phase', 'PID 1: Output',
                        'PID 2: Output', 'PID 3: Output', 'PID 4: Output')
        
        # Read default entry values from file
        self.defaultFile = 'normal_PFM_default_values.txt'
        pfmDefaultVal = open(self.defaultFile, 'r')
        self.default = pfmDefaultVal.read().splitlines()


        """
        1. Initialise all data entry terminals, labels, etc.
        2. Arrange them on a grid
        3. Confgure the grid
        4. Configure their inputs
        """
        
        # Instantiate widgets          
        # Lock In MF
        self.lockinMFLabel = tk.Label(self.pfmGUI, text="Lock-In MF", font=("bold", 10), bg=self.backClr)
        
        # Input voltage range
        self.inVoltRangeLabel = tk.Label(self.pfmGUI, text="Input Range", bg=self.backClr)
        self.inVoltRangeUnit = tk.Label(self.pfmGUI, text="", bg=self.backClr)
        self.inVoltRangeEntry = tk.Entry(self.pfmGUI, validate="key")
        self.inVoltRangeEntry['validatecommand'] = (self.inVoltRangeEntry.register(self.testValPos),'%P','%i','%d')
        
        # Output voltage range
        self.outVoltRangeLabel = tk.Label(self.pfmGUI, text="Output Range", bg=self.backClr)
        self.outVoltRangeUnit = tk.Label(self.pfmGUI, text="", bg=self.backClr)
        self.outVoltRangeEntry = tk.ttk.Combobox(self.pfmGUI, values=self.outVoltRange)
        
        # Signal Input
        self.inputLabel = tk.Label(self.pfmGUI, text="Input", bg=self.backClr)
        self.inputUnit = tk.Label(self.pfmGUI, text="", bg=self.backClr)
        self.inputEntry = tk.ttk.Combobox(self.pfmGUI, values=self.inputs)
        
        # Signal Output
        self.outputLabel = tk.Label(self.pfmGUI, text="Output", bg=self.backClr)
        self.outputUnit = tk.Label(self.pfmGUI, text="", bg=self.backClr)
        self.outputEntry = tk.ttk.Combobox(self.pfmGUI, values=self.outputs)
        
        # Demodulator
        self.demodLabel = tk.Label(self.pfmGUI, text="Demodulator", bg=self.backClr)
        self.demodUnit = tk.Label(self.pfmGUI, text="", bg=self.backClr)
        self.demodEntry = tk.ttk.Combobox(self.pfmGUI, values=self.demods)
        
        # Demodulator frequency
        self.demodFreqLabel = tk.Label(self.pfmGUI, text="Demod Freq", bg=self.backClr)
        self.demodFreqUnit = tk.Label(self.pfmGUI, text="kHz", bg=self.backClr)
        self.demodFreqEntry = tk.Entry(self.pfmGUI, validate="key")
        self.demodFreqEntry['validatecommand'] = (self.demodFreqEntry.register(self.testValPos),'%P','%i','%d')
        
        # Filter input
        self.filterInputLabel = tk.Label(self.pfmGUI, text="Filter Input", bg=self.backClr)
        self.filterInputUnit = tk.Label(self.pfmGUI, text="", bg=self.backClr)
        self.filterInputEntry = tk.ttk.Combobox(self.pfmGUI, values=self.filterInputs)
        
        # Filter dB/Oct
        self.filterdBOctLabel = tk.Label(self.pfmGUI, text="Filter dB/Oct", bg=self.backClr)
        self.filterdBOctUnit = tk.Label(self.pfmGUI, text="dB/Oct", bg=self.backClr)
        self.filterdBOctEntry = tk.ttk.Combobox(self.pfmGUI, values=self.filterdBOct)
        
        # Filter time constant
        self.filterTCLabel = tk.Label(self.pfmGUI, text="Filter TC", bg=self.backClr)
        self.filterTCUnit = tk.Label(self.pfmGUI, text="s", bg=self.backClr)
        self.filterTCEntry = tk.Entry(self.pfmGUI, validate="key")
        self.filterTCEntry['validatecommand'] = (self.filterTCEntry.register(self.testValPos),'%P','%i','%d')
        
        
        # Aux I/O
        self.auxIOLabel = tk.Label(self.pfmGUI, text="Aux I/O", font=("bold", 10), bg=self.backClr)
        
        # Auxillary X
        self.auxXLabel = tk.Label(self.pfmGUI, text="Auxillary", bg=self.backClr)
        self.auxXUnit = tk.Label(self.pfmGUI, text="", bg=self.backClr)
        self.auxXEntry = tk.ttk.Combobox(self.pfmGUI, values=self.auxs)
        
        # Auxillary Y
        self.auxYLabel = tk.Label(self.pfmGUI, text="Auxillary", bg=self.backClr)
        self.auxYUnit = tk.Label(self.pfmGUI, text="", bg=self.backClr)
        self.auxYEntry = tk.ttk.Combobox(self.pfmGUI, values=self.auxs)
    
        # Demodulation X
        self.demodXLabel = tk.Label(self.pfmGUI, text="Demodulation", bg=self.backClr)
        self.demodXEntry = tk.ttk.Combobox(self.pfmGUI, values=self.demods)
        
        # Demodulation Y
        self.demodYLabel = tk.Label(self.pfmGUI, text="Demodulation", bg=self.backClr)
        self.demodYEntry = tk.ttk.Combobox(self.pfmGUI, values=self.demods)
        
        # Auxillary output X
        self.auxOutXLabel = tk.Label(self.pfmGUI, text="Output", bg=self.backClr)
        self.auxOutXUnit = tk.Label(self.pfmGUI, text="", bg=self.backClr)
        self.auxOutXEntry = tk.ttk.Combobox(self.pfmGUI, values=self.auxOuts)
        
        # Auxillary output Y
        self.auxOutYLabel = tk.Label(self.pfmGUI, text="Output", bg=self.backClr)
        self.auxOutYUnit = tk.Label(self.pfmGUI, text="", bg=self.backClr)
        self.auxOutYEntry = tk.ttk.Combobox(self.pfmGUI, values=self.auxOuts)
        
        # Auxillary output X scale
        self.auxXScaleLabel = tk.Label(self.pfmGUI, text="Scale", bg=self.backClr)
        self.auxXScaleUnit = tk.Label(self.pfmGUI, text="", bg=self.backClr)
        self.auxXScaleEntry = tk.Entry(self.pfmGUI, validate="key")
        self.auxXScaleEntry['validatecommand'] = (self.auxXScaleEntry.register(self.testValPos),'%P','%i','%d')
        
        # Auxillary Output Y scale
        self.auxYScaleLabel = tk.Label(self.pfmGUI, text="Scale", bg=self.backClr)
        self.auxYScaleUnit = tk.Label(self.pfmGUI, text="", bg=self.backClr)
        self.auxYScaleEntry = tk.Entry(self.pfmGUI, validate="key")
        self.auxYScaleEntry['validatecommand'] = (self.auxYScaleEntry.register(self.testValPos),'%P','%i','%d')
        
        
        # Execution buttons
        self.configButton = tk.Button(self.pfmGUI, text='Configure', command=self.execute, bg=self.btnClr)
        self.restoreDefaultButton = tk.Button(self.pfmGUI, text='Restore Default Values',
                                              command=self.restoreDefault, bg=self.btnClr)
        self.makeDefaultButton = tk.Button(self.pfmGUI, text='Make Values Default',
                                           command=self.makeDefault, bg=self.btnClr)
                        

        ###################################################
        # Grid positions of labels, entry boxes, etc.                
        # Lock-in MF
        self.lockinMFLabel.grid(row=0, column=0, sticky=tk.W)
        
        # Input
        self.inputLabel.grid(row=1, column=0, sticky=tk.W)
        self.inputUnit.grid(row=1, column=2, sticky=tk.W)
        self.inputEntry.grid(row=1, column=1, sticky=tk.E+tk.W)
        
        # Input voltage range
        self.inVoltRangeLabel.grid(row=1, column=3, sticky=tk.W)
        self.inVoltRangeUnit.grid(row=1, column=5, sticky=tk.W)
        self.inVoltRangeEntry.grid(row=1, column=4, sticky=tk.E+tk.W)
        
        # Output
        self.outputLabel.grid(row=2, column=0, sticky=tk.W)
        self.outputUnit.grid(row=2, column=2, sticky=tk.W)
        self.outputEntry.grid(row=2, column=1, sticky=tk.E+tk.W)
        
        # Output voltage range
        self.outVoltRangeLabel.grid(row=2, column=3, sticky=tk.W)
        self.outVoltRangeUnit.grid(row=2, column=5, sticky=tk.W)
        self.outVoltRangeEntry.grid(row=2, column=4, sticky=tk.E+tk.W)
        
        # Demodulator
        self.demodLabel.grid(row=3, column=0, sticky=tk.W)
        self.demodUnit.grid(row=3, column=2, sticky=tk.W)
        self.demodEntry.grid(row=3, column=1, sticky=tk.E+tk.W)
        
        # Demodulator frequency
        self.demodFreqLabel.grid(row=3, column=3, sticky=tk.W)
        self.demodFreqUnit.grid(row=3, column=5, sticky=tk.W)
        self.demodFreqEntry.grid(row=3, column=4, sticky=tk.E+tk.W)
        
        # Filter input
        self.filterInputLabel.grid(row=4, column=0, sticky=tk.W)
        self.filterInputUnit.grid(row=4, column=2, sticky=tk.W)
        self.filterInputEntry.grid(row=4, column=1, sticky=tk.E+tk.W)
        
        # Filter dB/Oct
        self.filterdBOctLabel.grid(row=4, column=3, sticky=tk.W)
        self.filterdBOctUnit.grid(row=4, column=5, sticky=tk.W)
        self.filterdBOctEntry.grid(row=4, column=4, sticky=tk.E+tk.W)
        
        # Filter time constant
        self.filterTCLabel.grid(row=5, column=0, sticky=tk.W)
        self.filterTCUnit.grid(row=5, column=2, sticky=tk.W)
        self.filterTCEntry.grid(row=5, column=1, sticky=tk.E+tk.W)
        
        
        # Auxillary I/O
        self.auxIOLabel.grid(row=6, column=0, sticky=tk.W)
        
        # Auxillary output X
        self.auxXLabel.grid(row=7, column=0, sticky=tk.W)
        self.auxXUnit.grid(row=7, column=2, sticky=tk.W)
        self.auxXEntry.grid(row=7, column=1, sticky=tk.E+tk.W)
        
        # Auxillary output Y
        self.auxYLabel.grid(row=7, column=3, sticky=tk.W)
        self.auxYUnit.grid(row=7, column=5, sticky=tk.W)
        self.auxYEntry.grid(row=7, column=4, sticky=tk.E+tk.W)
        
        # Demodulation X
        self.demodXLabel.grid(row=10, column=0, sticky=tk.W)
        self.demodXEntry.grid(row=10, column=1, sticky=tk.E+tk.W)
        
        # Demodulation Y
        self.demodYLabel.grid(row=10, column=3, sticky=tk.W)
        self.demodYEntry.grid(row=10, column=4, sticky=tk.E+tk.W)
        
        # Auxillary output X
        self.auxOutXLabel.grid(row=8, column=0, sticky=tk.W)
        self.auxOutXUnit.grid(row=8, column=2, sticky=tk.W)
        self.auxOutXEntry.grid(row=8, column=1, sticky=tk.E+tk.W)
        
        # Auxillary output Y
        self.auxOutYLabel.grid(row=8, column=3, sticky=tk.W)
        self.auxOutYUnit.grid(row=8, column=5, sticky=tk.W)
        self.auxOutYEntry.grid(row=8, column=4, sticky=tk.E+tk.W)
        
        # Auxillary output X scale
        self.auxXScaleLabel.grid(row=9, column=0, sticky=tk.W)
        self.auxXScaleEntry.grid(row=9, column=1, sticky=tk.E+tk.W)
        
        # Auxillary output Y scale
        self.auxYScaleLabel.grid(row=9, column=3, sticky=tk.W)
        self.auxYScaleEntry.grid(row=9, column=4, sticky=tk.E+tk.W)
        
        
        # Execution buttons
        self.configButton.grid(row=0, column=7, sticky=tk.E+tk.W)
        self.restoreDefaultButton.grid(row=1, column=7, sticky=tk.E+tk.W)
        self.makeDefaultButton.grid(row=2, column=7, sticky=tk.E+tk.W)
        
        
        # Configure grid spacing
        for row_num in range(self.pfmGUI.grid_size()[1]):
            self.pfmGUI.rowconfigure(row_num, pad=4)
            
        for col_num in range(self.pfmGUI.grid_size()[0]):
            self.pfmGUI.columnconfigure(col_num, pad=5)
        
            
        # Insert defaults into now-cleared entry fields
        self.inputEntry.insert(0, self.default[0])
        self.inVoltRangeEntry.insert(0, self.default[1])
        self.outputEntry.insert(0, self.default[2])
        self.outVoltRangeEntry.insert(0, self.default[3])
        self.demodEntry.insert(0, self.default[4])
        self.demodFreqEntry.insert(0, self.default[5])
        self.filterInputEntry.insert(0, self.default[6])
        self.filterdBOctEntry.insert(0, self.default[7])
        self.filterTCEntry.insert(0, self.default[8])
        self.demodXEntry.insert(0, self.default[9])
        self.demodYEntry.insert(0, self.default[10])
        self.auxOutXEntry.insert(0, self.default[11])
        self.auxOutYEntry.insert(0, self.default[12])
        self.auxXScaleEntry.insert(0, self.default[13])
        self.auxYScaleEntry.insert(0, self.default[14])
        self.auxXEntry.insert(0, self.default[15])
        self.auxYEntry.insert(0, self.default[16])
        
    
    # Configure apparatus
    def execute(self):     
        
        pfmParam = [None]*17
        
        pfmParam[0] = self.inputEntry.get()
        pfmParam[1] = self.inVoltRangeEntry.get()
        pfmParam[2] = self.outputEntry.get()
        pfmParam[3] = self.outVoltRangeEntry.get()
        pfmParam[4] = self.demodEntry.get()
        pfmParam[5] = self.demodFreqEntry.get()
        pfmParam[6] = self.filterInputEntry.get()
        pfmParam[7] = self.filterdBOctEntry.get()
        pfmParam[8] = self.filterTCEntry.get()
        pfmParam[9] = self.demodXEntry.get()
        pfmParam[10] = self.demodYEntry.get()
        pfmParam[11] = self.auxOutXEntry.get()
        pfmParam[12] = self.auxOutYEntry.get()
        pfmParam[13] = self.auxXScaleEntry.get()
        pfmParam[14] = self.auxYScaleEntry.get()
        pfmParam[15] = self.auxXEntry.get()
        pfmParam[16] = self.auxYEntry.get()
        
        self.config(self.deviceID, pfmParam)
        
        
    # Configure apparatus
    def config(self, device, pfmParam):
        
        # Measurement parameters
        inputChan = int(pfmParam[0])-1
        inVoltRange = float(pfmParam[1])
        outputChan = int(pfmParam[2])-1
        outVoltRange = self.outVoltRangeToVolt[pfmParam[3]]
        demod = int(pfmParam[4])
        demodFreq = float(pfmParam[5])*1000
        filterInput = pfmParam[6]
        filterdBOct = int(int(pfmParam[7])/6)
        filterTC = float(pfmParam[8])
        demodX = pfmParam[9]
        demodY = pfmParam[10]
        auxOutX = pfmParam[11]
        auxOutY = pfmParam[12]
        auxXScale = pfmParam[13]
        auxYScale = pfmParam[14]
        auxX = pfmParam[15]
        auxY = pfmParam[16]
    
        apilevel_example = 5  # The API level supported by this example.
        # Call a zhinst utility function that returns:
        # - an API session `daq` in order to communicate with devices via the data server.
        # - the device ID string that specifies the device branch in the server's node hierarchy.
        # - the device's discovery properties.
        err_msg = "This example only supports instruments with demodulators."
        (daq, device, props) = zhinst.utils.create_api_session(device, apilevel_example,
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
        out_channel = 0
        out_mixer_channel = zhinst.utils.default_output_mixer_channel(props)
        in_channel = 0
        demod_index = 0
        osc_index = 0
        demod_rate = 10e3
        time_constant = 1e-6
        exp_setting = [['/%s/sigins/%d/range'          % (device, inputChan), inVoltRange],
                       ['/%s/sigouts/%d/on'            % (device, outputChan), 1],
                       ['/%s/sigouts/%d/range'         % (device, outputChan), outVoltRange],
                       ['/%s/sigins/%d/diff'           % (device, inputChan), 0],
                       ['/%s/demods/%d/enable'         % (device, demod), 1]]
                       
                       
                       #['/%s/sigins/%d/ac'             % (device, in_channel), 0]]
                       #['/%s/demods/%d/rate'           % (device, demod_index), demod_rate],
                       #['/%s/demods/%d/adcselect'      % (device, demod_index), in_channel],
                       #['/%s/demods/%d/harmonic'       % (device, demod_index), 1],
                       #['/%s/sigouts/%d/enables/%d'    % (device, out_channel, out_mixer_channel), 1]]
                       
                       #['/%s/pids/%d/demod/adcselect'  % (device, demod), 0],
                       #['/%s/pids/%d/demod/order'      % (device, demod), filterdBOct],
                       #['/%s/pidss/%d/demod/timeconstant'   % (device, demod), filterTC],
                       #['/%s/demods/%d/freq'           % (device, demod), demodFreq],
                        
        daq.set(exp_setting)
    
        # Wait for the demodulator filter to settle.
        time.sleep(10*time_constant)
    
        # Perform a global synchronisation between the device and the data server:
        # Ensure that the settings have taken effect on the device before issuing
        # the getSample() command. Note: the sync() must be issued after waiting for
        # the demodulator filter to settle above.
        daq.sync()
        
        print("Hello")
    
                  
    # Restore default entry values
    def restoreDefault(self):
        
        # Clear the entry fields
        self.inputEntry.delete(0, tk.END)
        self.inVoltRangeEntry.delete(0, tk.END)
        self.outputEntry.delete(0, tk.END)
        self.outVoltRangeEntry.delete(0, tk.END)
        self.demodEntry.delete(0, tk.END)
        self.demodFreqEntry.delete(0, tk.END)
        self.filterInputEntry.delete(0, tk.END)
        self.filterdBOctEntry.delete(0, tk.END)
        self.filterTCEntry.delete(0, tk.END)
        self.demodXEntry.delete(0, tk.END)
        self.demodYEntry.delete(0, tk.END)
        self.auxOutXEntry.delete(0, tk.END)
        self.auxOutYEntry.delete(0, tk.END)
        self.auxXScaleEntry.delete(0, tk.END)
        self.auxYScaleEntry.delete(0, tk.END)
        self.auxXEntry.delete(0, tk.END)
        self.auxYEntry.delete(0, tk.END)
        
        # Insert defaults into now-cleared entry fields
        self.inputEntry.insert(0, self.default[0])
        self.inVoltRangeEntry.insert(0, self.default[1])
        self.outputEntry.insert(0, self.default[2])
        self.outVoltRangeEntry.insert(0, self.default[3])
        self.demodEntry.insert(0, self.default[4])
        self.demodFreqEntry.insert(0, self.default[5])
        self.filterInputEntry.insert(0, self.default[6])
        self.filterdBOctEntry.insert(0, self.default[7])
        self.filterTCEntry.insert(0, self.default[8])
        self.demodXEntry.insert(0, self.default[9])
        self.demodYEntry.insert(0, self.default[10])
        self.auxOutXEntry.insert(0, self.default[11])
        self.auxOutYEntry.insert(0, self.default[12])
        self.auxXScaleEntry.insert(0, self.default[13])
        self.auxYScaleEntry.insert(0, self.default[14])
        self.auxXEntry.insert(0, self.default[15])
        self.auxYEntry.insert(0, self.default[16])
    
        
    # Make current values default
    def makeDefault(self):
        self.default[0] = self.inputEntry.get()
        self.default[1] = self.inVoltRangeEntry.get()
        self.default[2] = self.outputEntry.get()
        self.default[3] = self.outVoltRangeEntry.get()
        self.default[4] = self.demodEntry.get()
        self.default[5] = self.demodFreqEntry.get()
        self.default[6] = self.filterInputEntry.get()
        self.default[7] = self.filterdBOctEntry.get()
        self.default[8] = self.filterTCEntry.get()
        self.default[9] = self.demodXEntry.get()
        self.default[10] = self.demodYEntry.get()
        self.default[11] = self.auxOutXEntry.get()
        self.default[12] = self.auxOutYEntry.get()
        self.default[13] = self.auxXScaleEntry.get()
        self.default[14] = self.auxYScaleEntry.get()
        self.default[15] = self.auxXEntry.get()
        self.default[16] = self.auxYEntry.get()
        
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
    pfmGUI = tk.Tk()
    Normal_PFM_GUI(pfmGUI)
    pfmGUI.mainloop()