# Atomic-Force-Microscopy
Programs controlling aspects of an AFM system. The majority of the code controls LIAs, some controls the current in the superconducting coils.
This work was carried out under the supervision of Dr Dong Jik Kim in professor Marin Alexe's Electronic Functional Materials research group.

## Hysteresis Measurement:
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
