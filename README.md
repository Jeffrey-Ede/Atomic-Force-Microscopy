# Atomic-Force-Microscopy
Programmatic atomic force microscrope system control. The code controls lock-in amplifiers (LIAs) and the superconducting magnetic coils.

This work was carried out under the supervision of Dr Dong Jik Kim in professor Marin Alexe's Electronic Functional Materials research group at the University of Warwick.

## Note:

The SR865A LIA was abandoned in favor of the Zurich Instruments (ZI) HF2LI LIA as two SR865As would be needed to support dual frequency resonance tracking (DFRT) and we don't have a second. Only one HF2LI is needed to support DFRT. Additionally, the SR865A outputs are more dependent on preamplification or T junctions to get the higher voltages desired for piezoelectric force microscopy (PFM), adding complications. The HF2LI can operate over larger parameter ranges in almost all instances.

The code relies on relevant instrument drivers being installed. Figuring out how to or which drivers to install via manufacturers' websites can be lengthly, so it's probably best to just ask me.


## Hysteresis_Measurement

Contents: Python source code, batch file to start graphical user interface, icon for batch shortcut, text file containing default values and tooltips module.

### Intrument:

ZI HF2LI LIA. 

### Description:

A GUI for hysteresis measurement via PFM. It allows the user to setup stepwise voltage increases and loop them as desired. Additional functionality, such as DFRT, can be implimented via ziControl.

### Features:

The user can specify 0V periods between voltage steps. Additionally, intermission times can be specified separately for non-0V and 0V to allow the system to settle before data is recorded.

Various configuration setting of the LIA, including signal outputs and input terminals, can be changed.

The GUI field parameters can be saved to a text file as defaults for future use.

The GUI has graphing capabilities. Graphs can be zoomed into and saved as images. Multiple successive measurements can be plotted on the same graph.

Sampled data can be outputted to a file via a save as dialogue.

Tooltips give helpful hints about how to use the entry fields. The tooltips module is built on tkinter.

## Superconductor_Fields

Contents: Labview virtual instruments

### Instrument:

APS100 Magnetic Power Supply

### Description:

MagPowSup.vi allows the user to enter algebraic coeffients describing the 3D evolution of a magnetic field vector. The other instruments are subVIs. The code has not been tested yet due to technical difficulties with the AFM.

### Features:

Allows algebraic description of magnetic field evolution. Multiple algebraic expressions can be queued for different times and looped.

Checks that the rate of change in field doesn't exceed the maximum at any point in the expressions by simulating the vector sweep beforehand. If it does, a warning is given and the program refuses to execute.

3D comet plot of magnet field evolution. 2D x-y, x-z or y-z views are optional.

## Hysteresis.vi

Labview virtual instrument

### Instrument:

Stanford Research SR865A LIA

### Description:

Allows hysteresis measurement via PFM. It allows the user to setup stepwise voltage increases and loop them as desired. DFRT could be incorporated by using a second LIA.

### Features

The user can specify 0V periods between voltage steps. Additionally, intermission times can be specified separately for non-0V and 0V to allow the system to settle before data is recorded.

Various configuration setting of the LIA, including signal outputs and input terminals, can be changed.

There are 10 graphing panes so that all the outputs, which are dynamically updated, are always immediately available rather than the user having to switch what a single graph displays. 

Outputs can be outputted to files via save as dialogues.

## LIA-SR865A.vi

Labview virtual instrument

### Instrument: 

Stanford Research SR865A LIA

### Description:

A GUI that allows the user to remotely control the LIA.

### Features:

Virtual control panel offering easier configuration control, in some cases, than the physical control panel. Input and output clusters have been wired in anticipation of contacting other programs as part of a larger GUI.

## Resonance.vi

Labview virtual instrument.

### Instrument:

Stanford Research SR865A LIA

### Description:

Boxcar averages sweep data and outputs the maximum. It outputs the highest resonance if there are multiple. 

### Features

Graphs sweep, allowing visual interpretation of the resonance value. It performs an R-Freq scan; however, this can be programmatically adjusted to other types of scan.

### SweepOver.vi

Labview virtual instrument

### Instrument:

Stanford Research SR865A LIA

### Description

Highly customisable sweeper. It can sweep over 5 paramters and lock into 17. Can perform single, up-down or continuous sweeps.

### Features

Designed to be easily wired to the Resonance VI.
