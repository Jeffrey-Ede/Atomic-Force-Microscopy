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

class SweepGUI(tk.Frame):

    # Initialise main window
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.sweepGUI = parent
        self.sweepGUI.title("Sweeper")
        self.backClr = "#a1dbcd"
        self.btnClr = "#73c6b6"
        self.sweepGUI.configure(background=self.backClr)
        
        # Intrinsic parameters
        self.deviceID = 'dev801'
        self.sweepDir = ('Sequential', 'Binary', 'Bidirectional', 'Reverse')
        self.sweepOver = ('Freq', 'Phase', 'TC', 'Amplitude', 'Aux Offset', 'PID Setpoint')
        self.osc = ('1', '2', '3', '4', '5', '6')
        
        # Measurements to sample
        self.sweepBadNames = ('r', 'auxin1', 'auxin0pwr', 'bandwidth', 'auxin0', 'ypwr', 'auxin0stddev', 
                            'settimestamp', 'xpwr', 'rstddev', 'frequency', 'x', 'auxin1pwr', 'tcmeas', 
                            'grid', 'tc', 'auxin1stddev', 'nexttimestamp', 'rpwr', 'xstddev', 'phasepwr', 
                            'count', 'ystddev', 'settling', 'frequencypwr', 'y', 'frequencystddev', 'phase', 
                            'phasestddev')
        # Nicer names for sweep sample
        self.sweepSample = ('R', 'Aux In 1', 'Aux In 0 Power', 'Bandwidth', 'Aux In 0', 'Y Power', 'Aux In 0 Std Dev',
                          'Set Timestamp', 'X Power', 'R Std Dev', 'Frequency', 'X', 'Aux In 1 Power', 'TC Meas',
                          'Grid', 'TC', 'Aux In 1 Std Dev', 'Next Timestamp', 'R Power', 'X Std Dev', 'Phase Power',
                          'Count', 'Y Std Dev', 'Settling', 'Frequency Power', 'Y', 'Freq Std Dev', 'Phase',
                          'Phase Std Dev')
        
        # Make dictionary to look up nice name for bad name from
        self.naughtyToNice = {}
        for i in range(len(self.sweepSample)):
            self.naughtyToNice[self.sweepBadNames[i]] = self.sweepSample[i]

        
        # Dictionary storing measurements
        self.measurements = {}
        for key in self.sweepSample:
            self.measurements[key] = np.empty((0))
            
        
        # Read default values from file
        self.defaultFile = 'sweep_default_values.txt'
        sweepDefaultVal = open(self.defaultFile, 'r')
        self.default = sweepDefaultVal.read().splitlines()
        
        # Instantiate widgets
        # Sweep Range
        self.sweepRangeLabel = tk.Label(self.sweepGUI, text="Sweep Range", font=("bold", 10), bg=self.backClr)
        
       # Start
        self.startLabel = tk.Label(self.sweepGUI, text="Start", bg=self.backClr)
        self.startUnit = tk.Label(self.sweepGUI, text="", bg=self.backClr)
        self.startEntry = tk.Entry(self.sweepGUI, validate="key")
        self.startEntry['validatecommand'] = (self.startEntry.register(self.testVal),'%P','%i','%d')
        
        # End
        self.endLabel = tk.Label(self.sweepGUI, text="End", bg=self.backClr)
        self.endUnit = tk.Label(self.sweepGUI, text="", bg=self.backClr)
        self.endEntry = tk.Entry(self.sweepGUI, validate="key")
        self.endEntry['validatecommand'] = (self.endEntry.register(self.testVal),'%P','%i','%d')
        
        # Number of points
        self.numPointsLabel = tk.Label(self.sweepGUI, text="Num Points", bg=self.backClr)
        self.numPointsUnit = tk.Label(self.sweepGUI, text="", bg=self.backClr)
        self.numPointsEntry = tk.Entry(self.sweepGUI, validate="key")
        self.numPointsEntry['validatecommand'] = (self.numPointsEntry.register(self.testValPosInteg),'%P','%i','%d')
        
        # Sweep direction
        self.sweepDirLabel = tk.Label(self.sweepGUI, text="Sweep Direction", bg=self.backClr)
        self.sweepDirUnit = tk.Label(self.sweepGUI, text="", bg=self.backClr)
        self.sweepDirEntry = tk.ttk.Combobox(self.sweepGUI, values=self.sweepDir)
        
        # Number of loops
        self.numLoopsLabel = tk.Label(self.sweepGUI, text="Num Loops", bg=self.backClr)
        self.numLoopsUnit = tk.Label(self.sweepGUI, text="", bg=self.backClr)
        self.numLoopsEntry = tk.Entry(self.sweepGUI, validate="key")
        self.numLoopsEntry['validatecommand'] = (self.numLoopsEntry.register(self.testValPosInteg),'%P','%i','%d')
        
        # Log Sweep
        self.logSweep = tk.IntVar()
        self.logSweepLabel = tk.Label(self.sweepGUI, text="Log Sweep", bg=self.backClr)
        self.logSweepEntry = tk.Checkbutton(self.sweepGUI, text="", variable=self.logSweep, onvalue=1,
                                            offvalue=0, bg=self.backClr)
        
        # Execution buttons
        self.executeButton = tk.Button(self.sweepGUI, text='Execute', command=self.execute,
                                       bg=self.btnClr)
        self.restoreDefaultButton = tk.Button(self.sweepGUI, text='Restore Default Values',
                                              command=self.restoreDefault, bg=self.btnClr)
        self.makeDefaultButton = tk.Button(self.sweepGUI, text='Make Values Default',
                                           command=self.makeDefault, bg=self.btnClr)
        
        # Sweep Parameters
        self.dummyLabel = tk.Label(self.sweepGUI, text="", bg=self.backClr)
        self.sweepParamLabel = tk.Label(self.sweepGUI, text="Sweep Parameters", font=("bold", 10), bg=self.backClr)
        
        # Sync
        self.sync = tk.IntVar()
        self.syncLabel = tk.Label(self.sweepGUI, text="Sync", bg=self.backClr)
        self.syncEntry = tk.Checkbutton(self.sweepGUI, text="", variable=self.sync, onvalue=1, 
                                        offvalue=0, bg=self.backClr)
        
        # Sweep Over
        self.sweepOverLabel = tk.Label(self.sweepGUI, text="Sweep Over", bg=self.backClr)
        self.sweepOverEntry = tk.ttk.Combobox(self.sweepGUI, values=self.sweepOver)
        
        # Oscillator
        self.oscLabel = tk.Label(self.sweepGUI, text="Oscillator", bg=self.backClr)
        self.oscEntry = tk.ttk.Combobox(self.sweepGUI, values=self.osc)
        
        # Plot
        self.plotButton = tk.Button(self.sweepGUI, text='Plot', command=self.plot, bg=self.btnClr)
        self.clearPlotButton = tk.Button(self.sweepGUI, text='Clear Plot', command=self.clear_meas, bg=self.btnClr)
        self.resButton = tk.Button(self.sweepGUI, text='Find Resonance', command=self.res, bg=self.btnClr)
        self.plotAndResButton = tk.Button(self.sweepGUI, text='Plot + Resonance', command=self.plotAndRes, bg=self.btnClr)
        
        # Plot data
        self.plotLabel = tk.Label(self.sweepGUI, text="Plot", font=("bold", 10), bg=self.backClr)
        
        # Boxcar size
        self.boxSizeLabel = tk.Label(self.sweepGUI, text="Boxcar Size", bg=self.backClr)
        self.boxSizeUnit = tk.Label(self.sweepGUI, text="", bg=self.backClr)
        self.boxSizeEntry = tk.Entry(self.sweepGUI, validate="key")
        self.boxSizeEntry['validatecommand'] = (self.boxSizeEntry.register(self.testValPosInteg),'%P','%i','%d')
        
        # Horizontal Axis
        self.plotxLabel = tk.Label(self.sweepGUI, text="Horizontal Axis", bg=self.backClr)
        self.plotxUnit = tk.Label(self.sweepGUI, text="", bg=self.backClr)
        self.plotxEntry = tk.ttk.Combobox(self.sweepGUI, values=self.sweepSample)
        
        # Vertical Axis
        self.plotyLabel = tk.Label(self.sweepGUI, text="Vertical Axis", bg=self.backClr)
        self.plotyUnit = tk.Label(self.sweepGUI, text="", bg=self.backClr)
        self.plotyEntry = tk.ttk.Combobox(self.sweepGUI, values=self.sweepSample)
       
        # Resonance
        self.resLabel = tk.Label(self.sweepGUI, text="Resonance", font=("bold", 10), bg=self.backClr)
        
        # Resonance value
        self.resValLabel = tk.Label(self.sweepGUI, text="Resonance Value", bg=self.backClr)
        self.resValUnit = tk.Label(self.sweepGUI, text="", bg=self.backClr)
        self.resValEntry = tk.Entry(self.sweepGUI, validate="key")
        self.numLoopsEntry['validatecommand'] = (self.resValEntry.register(self.testValPos),'%P','%i','%d')
        
        # Perform boxcar average
        self.boxcar = tk.IntVar()
        self.boxcarLabel = tk.Label(self.sweepGUI, text="Boxcar Smooth", bg=self.backClr)
        self.boxcarEntry = tk.Checkbutton(self.sweepGUI, text="", variable=self.boxcar, onvalue=1,
                                          offvalue=0, bg=self.backClr)
        
        # Average over repeated values
        self.avgRepeatedx = tk.IntVar()
        self.avgRepeatedxLabel = tk.Label(self.sweepGUI, text="Avg Horiz Repeats", bg=self.backClr)
        self.avgRepeatedxEntry = tk.Checkbutton(self.sweepGUI, text="", variable=self.avgRepeatedx, onvalue=1, 
                                                offvalue=0, bg=self.backClr)
        
        # Average over repeated y values
        self.avgRepeatedy = tk.IntVar()
        self.avgRepeatedyLabel = tk.Label(self.sweepGUI, text="Avg Vert Repeats", bg=self.backClr)
        self.avgRepeatedyEntry = tk.Checkbutton(self.sweepGUI, text="", variable=self.avgRepeatedy, onvalue=1,
                                                offvalue=0, bg=self.backClr)
        
        
        #############################################
        # Grid positions of labels, entry boxes, etc.
        # Sweep Range
        self.sweepRangeLabel.grid(row=0, column=0, sticky=tk.W)
        
        # Start
        self.startLabel.grid(row=1, column=0, sticky=tk.W)
        self.startUnit.grid(row=1, column=2, sticky=tk.W)
        self.startEntry.grid(row=1, column=1, sticky=tk.E+tk.W)
        
        # End
        self.endLabel.grid(row=1, column=3, sticky=tk.W)
        self.endUnit.grid(row=1, column=5, sticky=tk.W)
        self.endEntry.grid(row=1, column=4, sticky=tk.E+tk.W)
        
        # Number of points
        self.numPointsLabel.grid(row=2, column=0, sticky=tk.W)
        self.numPointsUnit.grid(row=2, column=2, sticky=tk.W)
        self.numPointsEntry.grid(row=2, column=1, sticky=tk.E+tk.W)
        
        # Sweep direction
        self.sweepDirLabel.grid(row=2, column=3, sticky=tk.W)
        self.sweepDirUnit.grid(row=2, column=5, sticky=tk.W)
        self.sweepDirEntry.grid(row=2, column=4, sticky=tk.E+tk.W)
        
        # Execution buttons
        self.executeButton.grid(row=0, column=7, sticky=tk.E+tk.W)
        self.restoreDefaultButton.grid(row=1, column=7, sticky=tk.E+tk.W)
        self.makeDefaultButton.grid(row=2, column=7, sticky=tk.E+tk.W)
        
        # Number of loops
        self.numLoopsLabel.grid(row=3, column=0, sticky=tk.W)
        self.numLoopsUnit.grid(row=3, column=2, sticky=tk.W)
        self.numLoopsEntry.grid(row=3, column=1, sticky=tk.E+tk.W)
        
        # Log sweep
        self.logSweepLabel.grid(row=3, column=3, sticky=tk.E)
        self.logSweepEntry.grid(row=3, column=4, sticky=tk.W)
        
        # Sweep parameters
        self.dummyLabel.grid(row=5, column=5, sticky=tk.E+tk.W)
        self.sweepParamLabel.grid(row=4, column=0, sticky=tk.W)
        
        # Sync
        self.syncLabel.grid(row=5, column=6, sticky=tk.E)
        self.syncEntry.grid(row=5, column=7, sticky=tk.W)
        
        # Sweep Over
        self.sweepOverLabel.grid(row=5, column=0, sticky=tk.W)
        self.sweepOverEntry.grid(row=5, column=1, sticky=tk.W)
        
        # Oscillator
        self.oscLabel.grid(row=5, column=3, sticky=tk.W)
        self.oscEntry.grid(row=5, column=4, sticky=tk.W)
        
        # Plot
        self.plotButton.grid(row=7, column=7, sticky=tk.E+tk.W)
        self.clearPlotButton.grid(row=8, column=7, sticky=tk.E+tk.W)
        self.resButton.grid(row=10, column=7, sticky=tk.E+tk.W)
        self.plotAndResButton.grid(row=11, column=7, sticky=tk.E+tk.W)
        
        # Plot label
        self.plotLabel.grid(row=6, column=0, sticky=tk.W)
        
        # Resonance label
        self.resLabel.grid(row=10, column=0, sticky=tk.W)
        
        # Boxcar size
        self.boxSizeLabel.grid(row=7, column=0, sticky=tk.W)
        self.boxSizeUnit.grid(row=7, column=2, sticky=tk.W)
        self.boxSizeEntry.grid(row=7, column=1, sticky=tk.E+tk.W)
        
        # Resonance value
        self.resValLabel.grid(row=11, column=0, sticky=tk.W)
        self.resValUnit.grid(row=11, column=2, sticky=tk.W)
        self.resValEntry.grid(row=11, column=1, sticky=tk.E+tk.W)
        
        # Boxcar checkbox
        self.boxcarLabel.grid(row=7, column=3, sticky=tk.E)
        self.boxcarEntry.grid(row=7, column=4, sticky=tk.W)
        
        # Horizontal axis
        self.plotxLabel.grid(row=8, column=0, sticky=tk.W)
        self.plotxUnit.grid(row=8, column=2, sticky=tk.W)
        self.plotxEntry.grid(row=8, column=1, sticky=tk.W)
        
        # Vertical axis
        self.plotyLabel.grid(row=9, column=0, sticky=tk.W)
        self.plotyUnit.grid(row=9, column=2, sticky=tk.W)
        self.plotyEntry.grid(row=9, column=1, sticky=tk.W)
        
        # Average repeated x values
        self.avgRepeatedxLabel.grid(row=8, column=3, sticky=tk.E)
        self.avgRepeatedxEntry.grid(row=8, column=4, sticky=tk.W)
        
        # Average repeated y values
        self.avgRepeatedyLabel.grid(row=9, column=3, sticky=tk.E)
        self.avgRepeatedyEntry.grid(row=9, column=4, sticky=tk.W)
        
        
        # Configure grid spacing
        for row_num in range(self.sweepGUI.grid_size()[1]):
            self.sweepGUI.rowconfigure(row_num, pad=4)
            
        for col_num in range(self.sweepGUI.grid_size()[0]):
            self.sweepGUI.columnconfigure(col_num, pad=5)
            
        
        # Initialise entry fields with default values
        self.startEntry.insert(0, self.default[0])
        self.endEntry.insert(0, self.default[1])
        self.numPointsEntry.insert(0, self.default[2])
        self.sweepDirEntry.insert(0, self.default[3])
        self.logSweep.set(self.default[4])
        self.sweepOverEntry.insert(0, self.default[5])
        self.oscEntry.insert(0, self.default[6])
        self.sync.set(self.default[7])
        self.numLoopsEntry.insert(0, self.default[8])
        self.boxSizeEntry.insert(0, self.default[9])
        self.plotxEntry.insert(0, self.default[10])
        self.plotyEntry.insert(0, self.default[11])
        self.boxcar.set(self.default[12])
        self.avgRepeatedx.set(self.default[13])
        self.avgRepeatedy.set(self.default[14])
        self.resValEntry.insert(0, self.default[15])
        
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
        
    # Boxcar average and find maximum
    def res(self):
        print("sdfs2")
        
    # Plot Sweep, then boxcar average and find resonance
    def plotAndRes(self):
        print("sdfs2")
        
    # Perform Sweep procedure
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
        
        
        # Check that entries are correctly formatted; assume they are within physical bounds
        try:
            startEntry = float(self.startEntry.get())
        except ValueError:
            errText.insert(tk.END, "Start is not a float\n")
            
        try:
            endEntry = float(self.endEntry.get())
        except ValueError:
            errText.insert(tk.END, "End is not a float\n")
            
        try:
            numPointsEntry = int(self.numPointsEntry.get())
        except ValueError:
            errText.insert(tk.END, "Num Points is not an int\n")
            
        if not self.sweepDirEntry.get() in self.sweepDir:
            errText.insert(tk.END, "Sweep Direction is not in "+str(self.sweepDir)+"\n")
            
        if not self.sweepOverEntry.get() in self.sweepOver:
            errText.insert(tk.END, "Sweep Over is not in "+str(self.sweepOver)+"\n")
        
        if not self.oscEntry.get() in self.osc:
            errText.insert(tk.END, "Oscillator not in "+str(self.osc)+"\n")
            
        try:
            numLoopsEntry = int(self.numLoopsEntry.get())
        except ValueError:
            errText.insert(tk.END, "Num Loops is not an int\n")
            
        if not self.plotxEntry.get() in self.sweepSample:
            errText.insert(tk.END, "Horizontal Axis not in "+str(self.sweepSample)+"\n")
            
        if not self.plotyEntry.get() in self.sweepSample:
            errText.insert(tk.END, "Vertical Axis not in "+str(self.sweepSample)+"\n")
            
        # Do not open error message window if all entries are valid
        if len(errText.get("1.0", "end-1c")) == 0:
            errDialogueBox.destroy()
            
            # Prepare measurement parameter array to be passed to hyst_meas
            sweepParam = [None]*9
            sweepParam[0] = startEntry
            sweepParam[1] = endEntry
            sweepParam[2] = numPointsEntry
            sweepParam[3] = self.sweepDirEntry.get()
            sweepParam[4] = str(self.logSweep.get())
            sweepParam[5] = self.sweepOverEntry.get()
            sweepParam[6] = self.oscEntry.get()
            sweepParam[7] = str(self.sync.get())
            sweepParam[8] = numLoopsEntry
            
            self.sweep_meas(self.deviceID, sweepParam, 0.1)
        
        
    # Restore default entry values
    def restoreDefault(self):
        
        # Clear the entry fields
        self.startEntry.delete(0, tk.END)
        self.endEntry.delete(0, tk.END)
        self.numPointsEntry.delete(0, tk.END)
        self.sweepDirEntry.delete(0, tk.END)
        self.sweepOverEntry.delete(0, tk.END)
        self.oscEntry.delete(0, tk.END)
        self.numLoopsEntry.delete(0, tk.END)
        self.boxSizeEntry.delete(0, tk.END)
        self.plotxEntry.delete(0, tk.END)
        self.plotyEntry.delete(0, tk.END)
        self.resValEntry.delete(0, tk.END)
        
        # Insert defaults into now-cleared entry fields
        self.startEntry.insert(0, self.default[0])
        self.endEntry.insert(0, self.default[1])
        self.numPointsEntry.insert(0, self.default[2])
        self.sweepDirEntry.insert(0, self.default[3])
        self.logSweep.set(self.default[4])
        self.sweepOverEntry.insert(0, self.default[5])
        self.oscEntry.insert(0, self.default[6])
        self.sync.set(self.default[7])
        self.numLoopsEntry.insert(0, self.default[8])
        self.boxSizeEntry.insert(0, self.default[9])
        self.plotxEntry.insert(0, self.default[10])
        self.plotyEntry.insert(0, self.default[11])
        self.boxcar.set(self.default[12])
        self.avgRepeatedx.set(self.default[13])
        self.avgRepeatedy.set(self.default[14])
        self.resValEntry.insert(0, self.default[15])

    
    # Make current values default
    def makeDefault(self):
        
        self.default[0] = self.startEntry.get()
        self.default[1] = self.endEntry.get()
        self.default[2] = self.numPointsEntry.get()
        self.default[3] = self.sweepDirEntry.get()
        self.default[4] = str(self.logSweep.get())
        self.default[5] = self.sweepOverEntry.get()
        self.default[6] = self.oscEntry.get()
        self.default[7] = str(self.sync.get())
        self.default[8] = self.numLoopsEntry.get()
        self.default[9] = self.boxSizeEntry.get()
        self.default[10] = self.plotxEntry.get()
        self.default[11] = self.plotyEntry.get()
        self.default[12] = str(self.boxcar.get())
        self.default[13] = str(self.avgRepeatedx.get())
        self.default[14] = str(self.avgRepeatedy.get())
        self.default[15] = self.resValEntry.get()
        
        defaults = open(self.defaultFile, 'w')
        for default in self.default:
            defaults.write(default+'\n')
            
            
    def sweep_meas(self, device_id, sweepParam, amplitude):
        
        # Measurement parameters
        startVal = float(sweepParam[0])
        endVal = float(sweepParam[1])
        numPoints = int(sweepParam[2])
        sweepDir = sweepParam[3]
        logSweep = int(sweepParam[4])
        sweepOver = sweepParam[5]
        osc = int(sweepParam[6])
        sync = int(sweepParam[7])
        numLoops = int(sweepParam[8])


        if sweepDir == 'Sequential':
            sweepDirVal = 0
        elif sweepDir == 'Binary':
            sweepDirVal = 1
        elif sweepDir == 'Bidirectional':
            sweepDirVal = 2
        elif sweepDir == 'Reverse':
            sweepDirVal = 3

        
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
        out_channel = 0
        out_mixer_channel = zhinst.utils.default_output_mixer_channel(props)
        in_channel = 0
        demod_index = 0
        demod_rate = 10e3
        time_constant = 0.01
        exp_setting = [['/%s/sigins/%d/ac'             % (device, in_channel), 0],
                       ['/%s/sigins/%d/range'          % (device, in_channel), 2*amplitude],
                       ['/%s/demods/%d/enable'         % (device, demod_index), 1],
                       ['/%s/demods/%d/rate'           % (device, demod_index), demod_rate],
                       ['/%s/demods/%d/adcselect'      % (device, demod_index), in_channel],
                       ['/%s/demods/%d/order'          % (device, demod_index), 4],
                       ['/%s/demods/%d/timeconstant'   % (device, demod_index), time_constant],
                       ['/%s/demods/%d/oscselect'      % (device, demod_index), osc],
                       ['/%s/demods/%d/harmonic'       % (device, demod_index), 1],
                       ['/%s/sigouts/%d/on'            % (device, out_channel), 1],
                       ['/%s/sigouts/%d/enables/%d'    % (device, out_channel, out_mixer_channel), 1],
                       ['/%s/sigouts/%d/range'         % (device, out_channel), 1],
                       ['/%s/sigouts/%d/amplitudes/%d' % (device, out_channel, out_mixer_channel), amplitude]]
        # Some other device-type dependent configuration may be required. For
        # example, disable the signal inputs `diff` and the signal outputs `add` for
        # HF2 instruments.
        if props['devicetype'].startswith('HF2'):
            exp_setting.append(['/%s/sigins/%d/diff'      % (device, in_channel), 0])
            exp_setting.append(['/%s/sigouts/%d/add'      % (device, out_channel), 0])
        daq.set(exp_setting)
    
        # Create an instance of the Sweeper Module (ziDAQSweeper class).
        sweeper = daq.sweep()
    
        # Configure the Sweeper Module's parameters.
        # Set the device that will be used for the sweep - this parameter must be set.
        sweeper.set('sweep/device', device)
        # Specify the `gridnode`: The instrument node that we will sweep, the device
        # setting corresponding to this node path will be changed by the sweeper.
        if sweepOver == 'Freq':
            sweeper.set('sweep/gridnode', 'oscs/%d/freq' % osc)
        elif sweepOver == 'Phase':
            sweeper.set('sweep/gridnode', 'oscs/%d/freq' % osc)
        elif sweepOver == 'TC':
            sweeper.set('sweep/gridnode', 'oscs/%d/freq' % osc)
        elif sweepOver == 'Amplitude':
            sweeper.set('sweep/gridnode', 'oscs/%d/freq' % osc)
        elif sweepOver == 'Aux Offset':
            sweeper.set('sweep/gridnode', 'oscs/%d/freq' % osc)
        elif sweepOver == 'PID Setpoint':
            sweeper.set('sweep/gridnode', 'oscs/%d/freq' % osc)
        
        # Set the `start` and `stop` values of the gridnode value interval we will use in the sweep.
        sweeper.set('sweep/start', startVal)
        sweeper.set('sweep/stop', endVal)
        
        # Set the number of points to use for the sweep, the number of gridnode
        # setting values will use in the interval (`start`, `stop`).
        sweeper.set('sweep/samplecount', numPoints)
        
        sweeper.set('sweep/xmapping', logSweep)
        # Automatically control the demodulator bandwidth/time constants used.
        # 0=manual, 1=fixed, 2=auto
        # Note: to use manual and fixed, sweep/bandwidth has to be set to a value > 0.
        sweeper.set('sweep/bandwidthcontrol', 2)
        # Sets the bandwidth overlap mode (default 0). If enabled, the bandwidth of
        # a sweep point may overlap with the frequency of neighboring sweep
        # points. The effective bandwidth is only limited by the maximal bandwidth
        # setting and omega suppression. As a result, the bandwidth is independent
        # of the number of sweep points. For frequency response analysis bandwidth
        # overlap should be enabled to achieve maximal sweep speed (default: 0). 0 =
        # Disable, 1 = Enable.
        sweeper.set('sweep/bandwidthoverlap', 0)
    
        # Sequential scanning mode (as opposed to binary or bidirectional).
        sweeper.set('sweep/scan', sweepDirVal)
        # Specify the number of sweeps to perform back-to-back.
        sweeper.set('sweep/loopcount', numLoops)
        # We don't require a fixed sweep/settling/time since there is no DUT
        # involved in this example's setup (only a simple feedback cable), so we set
        # this to zero. We need only wait for the filter response to settle,
        # specified via sweep/settling/inaccuracy.
        sweeper.set('sweep/settling/time', 0)
        # The sweep/settling/inaccuracy' parameter defines the settling time the
        # sweeper should wait before changing a sweep parameter and recording the next
        # sweep data point. The settling time is calculated from the specified
        # proportion of a step response function that should remain. The value
        # provided here, 0.001, is appropriate for fast and reasonably accurate
        # amplitude measurements. For precise noise measurements it should be set to
        # ~100n.
        # Note: The actual time the sweeper waits before recording data is the maximum
        # time specified by sweep/settling/time and defined by
        # sweep/settling/inaccuracy.
        sweeper.set('sweep/settling/inaccuracy', 0.001)
        # Set the minimum time to record and average data to 10 demodulator
        # filter time constants.
        sweeper.set('sweep/averaging/tc', 10)
        # Minimal number of samples that we want to record and average is 100. Note,
        # the number of samples used for averaging will be the maximum number of
        # samples specified by either sweep/averaging/tc or sweep/averaging/sample.
        sweeper.set('sweep/averaging/sample', 10)
        # Sets up sinc filter
        sweeper.set('sweep/sincfilter', sync)
    
        # Now subscribe to the nodes from which data will be recorded. Note, this is
        # not the subscribe from ziDAQServer; it is a Module subscribe. The Sweeper
        # Module needs to subscribe to the nodes it will return data for.x
        path = '/%s/demods/%d/sample' % (device, demod_index)
        sweeper.subscribe(path)
    
        # Start the Sweeper's thread
        sweeper.execute()

        while not sweeper.finished():  # Wait until the sweep is complete
            time.sleep(0.2)

        
        # Read the sweep data. This command can also be executed whilst sweeping
        # (before finished() is True), in this case sweep data up to that time point
        # is returned. It's still necessary still need to issue read() at the end to
        # fetch the rest.
        return_flat_dict = True
        data = sweeper.read(return_flat_dict)
        sweeper.unsubscribe(path)
        
        # Stop the sweeper thread and clear the memory.
        sweeper.clear()
    
        # Check the dictionary returned is non-empty.
        assert data, "read() returned an empty data dictionary, did you subscribe to any paths?"
        # Note: data could be empty if no data arrived, e.g., if the demods were
        # disabled or had rate 0.
        assert path in data, "No sweep data in data dictionary: it has no key '%s'" % path
        samples = data[path]
        assert len(samples) == numLoops, \
            "The sweeper returned an unexpected number of sweeps: `%d`. Expected: `%d`." % (len(samples), numLoops)
                        
        self.record_meas(samples)
            
            
    # Record all relevant measurements in dictionary        
    def record_meas(self, samples):
        
        # Go through array layers to read data
        for key1 in samples:
            for key2 in key1:
                for key3 in key2:
                    if key3 in self.sweepSample:
                        # Convert key3 name to nicer name using naughtyToNice function
                        self.measurements[self.naughtyToNice[key3]] = np.append(self.measurements[self.naughtyToNice[key3]], key2[key3])
                        print(key3)
        
        
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
        if self.avgRepeatedx == 1:
            x, y = self.avg_xrepeats(self.measurements[x1], self.measurements[y1])
        if self.avgRepeatedy == 1:
            y, x = self.avg_xrepeats(self.measurements[y1], self.measurements[x1])
            

        if self.boxcar:
            x = self.boxcar_avg(x, int(self.boxSizeEntry.get()))
            y = self.boxcar_avg(y, int(self.boxSizeEntry.get()))

        # Prepare graph
        a.plot(x, y)
        
        # Add a tk.DrawingArea
        canvas = FigureCanvasTkAgg(f, master=plot)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        toolbar = NavigationToolbar2TkAgg(canvas, plot)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
    
    # Boxcar averages an array to smooth data
    def boxcar_avg(self, array, boxsize):
        
        boxcarAvg = [None]*(len(array)-boxsize+1+5)   # Hack +5 fix
        
        # Sum first boxsize elements of the array
        sum=0
        for i in range(boxsize):
            sum += array[i]
        boxcarAvg[0] = sum/boxsize
            
        # Move boxcar through the array
        for j in range(boxsize, len(array)):
            sum -= array[j-boxsize]
            sum += array[j]
            boxcarAvg[j] = sum/boxsize
            
        return boxcarAvg
       
    # Average over repeated x values. Can average over y by passing x and y the other way around
    def avg_xrepeats(self, x, y):
        
        avgedx, avgedy = np.empty((0)), np.empty((0))
        
        total = 0
        start, end = 0, 1   # Average between y[start] and y[end] so x and y have same lengths
        
        prevx = x[0]
        avgedx = np.append(avgedx, prevx)

        # If the next value of x is not the same as the previous, add it to the array
        for i in range(1, len(x)):
            if x[i] == prevx:
                end += 1
                    
                # Check if this is the last element of the array
                if i == len(x)-1:
                    avgedx = np.append(avgedx, prevx)
                        
                    for j in range(start, end):
                        total += x[i]
                    avgedy = np.append(avgedy, total/(end-start))
                        
                    total = 0
                    
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
            
if __name__ == "__main__":
    sweepGUI = tk.Tk()
    SweepGUI(sweepGUI)
    sweepGUI.mainloop()