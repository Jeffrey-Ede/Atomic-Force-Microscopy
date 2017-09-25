# Features
This nested list breaks down Hysteresis' functionality into features, subfeatures, subsubfeatures and so on.

* Stepwise bias incrementation
    * Stepwise biases applied to probe and bottom electrode separately
        * Can have different minimum and maximum voltages
        * Different auxiliary outputs
        * Auxiliary output channels can be changed
    * Highly controllable bias times
        * Bias time where a bias is applied and data is polled
            * Optional: set bias time to 0ms to turn this feature off
        * Bias wait where a bias is applied and no data is polled
            * Optional: set bias wait to 0ms to turn this feature off
        * 0V time where 0V is applied and data is polled
            * Optional: set 0V time to 0ms to turn this feature off
        * 0V wait where 0V is applied and no data is polled
            * Optional: set 0V wait to 0ms to turn this feature off
    * Probe output channel can be changed
    * Multiple bias incrementation patterns
        * Min-Max
        * Min-Max-Min
        * 0-Max-0-Min-0
        * Patterns are flipable
* Data plotting
    * Choose a dataset to be plotted live as it is polled
        * Change data displayed during data aquisition
    * Separate plot window
        * Save graph
        * Zoom in/out with rescaling axes
        * Change plot shape
        * Plot resizes with window
        * Flick between multiple views
        * Home button to return to original zoom
        * Several options for x and y axis data
    * Average repeating x or y values in plot
    * Plot shows new and previous measurements
        * Optional: clear previous measurements
    * Create multiple plots
    * Use save as dialog to save raw plot data
        * Application settings metadata inserted at start of file
        * Optional: average repeated values in saved data
* <acronym title="Current Force Microscopy">CFM</acronym> mode
    * Optional: turn <acronym title="Current Force Microscopy">CFM</acronym> mode on or off
    * Choose where to append <acronym title="Current Force Microscopy">CFM</acronym> data to
        * Optional: data aquisition can be turned off
    * Scoped voltage input can be changed
    * Bandwidth limiting to prevent antialising
        * Optional: bandwidth limiting can be turned off
    * Select from a range of sampling rates
    * Optioal: <acronym title="Lock-in Amplifier">LIA</acronym> resynchronisation can be turned off for faster measurement
    * Open <acronym title="Current Force Microscopy">CFM</acronym> data in user's default text editor
    * Use Save As dialog to change <acronym title="Current Force Microscopy">CFM</acronym> data save location
        * Settings metadata inserted at start of file
    * Button to clear <acronym title="Current Force Microscopy">CFM</acronym> save location
    * Metadata describing the current voltages, time, etc. is inserted before each sample
    * CFM data is filterable
        * Optional: filtering can automatically be applied after data aquisition
        * Select from a range filters
        * Select data subset to apply filters to
        * Choose filter parameters
        * Highly customisable filtering
            * Apply multiple filters separately
            * Apply multiple filters at once
            * Apply a combination of filters separately or at once
            * metadata describing filter inserted before each filter output
        * Optional: replace raw <acronym title="Current Force Microscopy">CFM</acronym> data with filtered data
            * Supports repeaded filtering with successive filters
            * Multiple filters can be applied at once
            * A combination of single and compound filters can be successively applied
        * Choose location to append filter data to
            * Optional: filtering can be turned off
        * Fourier analysis of <acronym title="Current Force Microscopy">CFM</acronym> data
            * Optional: 'None' mode for Fourier analysis without any filtering
        * Filter code is highy modular:
            * New filters are easy to add
        * Filter can be applied to CFM at click of a button
        * Open filter data in user's default text editor
        * Use Save As dialog to change filter data save location
            * Settings metadata inserted at start of file
        * Button to clear filter save location
        * <acronym title="Current Force Microscopy">CFM</acronym> data can be plotted against demodulator data
* Clear all button to clear all data
* Every entry field, combobox, checkbox and button has a tooltip explaining what it does
* Settings
    * Default values saved to hard drive
    * Button to restore default values
    * Use save as dialog to save current settings
    * Use open dialog to load new settings
* Help
    * Help pages
    * Tooltips
    * [GitHub documentation](https://github.com/Jeffrey-Ede/Atomic-Force-Microscopy "AFM system control documentation")
    
