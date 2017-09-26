# Contact

Developer: Jeffrey M. Ede<br>
Contact: JeffreyEde1@outlook.com<br>
Details: PhD student, University of Warwick Microscopy Group


# History
Hysteresis is a python-based application developed by Jeffrey M. Ede to automate <acronym title="Atomic Force Microscope">AFM</acronym> procedures. Full source code for [this](https://github.com/Jeffrey-Ede/Atomic-Force-Microscopy/tree/master/Hysteresis_Measurement "Hysteresis source code") and [other](https://github.com/Jeffrey-Ede/Atomic-Force-Microscopy "AFM program source code") <acronym title="Atomic Force Microscope">AFM</acronym> control programs is available on GitHub. The Hysteresis <acronym title="Graphical User Interface">GUI</acronym> controls a Zurich Instruments [HF2LI lock-in amplifier](https://www.zhinst.com/products/hf2li#overview "Produce information") using a Zurich Instruments python node hierarchy. Hierarchy details are published in the Zurich Instruments HF2 [ziControl](https://www.zhinst.com/sites/default/files/ziHF2_UserManual_ziControl_45800.pdf "ziControl program manual") user manual, with supporting information available in the [LabOne](https://www.zhinst.com/sites/default/files/LabOneProgrammingManual_45917.pdf "LabOne program manual") user manual. [Instrument drivers](https://www.zhinst.com/downloads) for the node hierarchy have been made publically available by Zurich Instruments, along with other required software.

Initially, the software was just designed for <acronym title="Piezoelectric Force Microscopy">PFM</acronym>. It applied an incrementing series of voltages, with optional 0V times inbetween, and recorded the response of an <acronym title="Atomic Force Microscope">AFM</acronym> probe head as a function of time at each voltage by sampling X and Y voltages from the Zurich Instruments lock-in amplifier's demodulators. This is why the application is built on [tkinter](http://www.tkdocs.com/ "Tkinter documentation"): it was expected to be quite small. However, since then, additional functionality has been, and continues to be, added, with the application now supporting current force microscopy, graphing capabilities, various file input/output and Fourier signal analysis. It even has its own website!