# Atomic-Force-Microscopy
Programmic AFM system control. The majority of the code controls LIAs; some controls the current in the superconducting coils.

This work was carried out under the supervision of Dr Dong Jik Kim in professor Marin Alexe's Electronic Functional Materials research group.

## Hysteresis Measurement

Contents: Python source code, batch file to start GUI, icon for batch shortcut and a text file containing default values.

### Intrument:

Zurich Instruments HF2LI LIA. 

### Description:

A GUI for hysteresis measurement via PFM. It allows the user to setup stepwise voltage increases and loop them as desired. Additional functionality, such as DFRT, can be implimented via ziControl.

### Features:

The user can specify 0V periods between voltage steps. Additionally, intermission times can be specified separately for non-0V and 0V to allow the system to settle before data is recorded.

Various configuration setting of the LIA, including signal outputs and input terminals, can be changed.

The GUI field parameters can be saved to a text file as defaults for future use.

The GUI has graphing capabilities. Graphs can be zoomed into and saved as images. Multiple successive measurements can be plotted on the same graph.

Sampled data can be outputted to a file via a save as dialogue.

## LIA-SR865A

Contents: Labview virtual instrument

### Instrument: 

Stanford Research SR865A LIA

### Description:

A GUI that allows the user to remotely control the LIA.

### Features:

Virtual control panel offering easier configuration control, in some cases, than the physical control panel. Input and output clusters have been wired in anticipation of contacting other programs as part of a larger GUI.

### Note:

This LIA was abandoned in favor of the ZI HF2LI LIA as 2 SR865As would be needed to support DFRT and we don't have a second one lying around. Only one HF2LI is needed to support DFRT. Additionally, the SR865A outputs are more dependent on preamplification or T junctions to get the higher voltages desired for PFM, adding complications. The HF2LI can operate over larger parameter ranges in almost all instances.

