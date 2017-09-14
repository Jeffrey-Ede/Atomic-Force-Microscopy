"""
Zurich Instruments LabOne Python API Example

Demonstrate how to obtain scope data from an HF2's signal outputs using
ziDAQServer's blocking (synchronous) poll() command.
"""

# Copyright 2016 Zurich Instruments AG

from __future__ import print_function
import warnings
import numpy as np
import zhinst.utils


def run_example(device_id, amplitude=0.5, sigouts_range=1.0, do_plot=False):
    """
    Run the example: Connect to a Zurich Instruments device via the Data Server,
    generate a sine wave on the signal outputs and obtain the waveform from the
    signal outputs by polling data from the scope using ziDAQServer's blocking
    (synchronous) poll() command.

    Note: This is an HF2 example and uses API level 1; users of other device
      classes are recommended to connect via API level 4, particularly when
      obtaining scope data.

    Arguments:

      amplitude (float, optional): The amplitude to set on the signal output.

      sigouts_range (float, optional): The range to use on the signal output.

      do_plot (bool, optional): Specify whether to plot the polled data. Default
        is no plot output.

    Returns:

      shots (list of dict): A list containing the polled scope shots, each entry
        is a dictionary holding the various data associated with a shot.

    Raises:

      RuntimeError: If the device is not "discoverable" from the API.

      RuntimeError: If the specified device is not an HF2.

    See the "LabOne Programing Manual" for further help, available:
      - On Windows via the Start-Menu:
        Programs -> Zurich Instruments -> Documentation
      - On Linux in the LabOne .tar.gz archive in the "Documentation"
        sub-folder.

    """

    # The API level supported by this example. Note, the HF2 data server
    # only supports API Level 1.
    apilevel_example = 1
    # Call a zhinst utility function that returns:
    # - an API session `daq` in order to communicate with devices via the data server.
    # - the device ID string that specifies the device branch in the server's node hierarchy.
    # - the device's discovery properties.
    err_msg = "This example only supports HF2 Instruments."
    (daq, device, props) = zhinst.utils.create_api_session(device_id, apilevel_example, required_devtype='HF2',
                                                           required_err_msg=err_msg)
    zhinst.utils.api_server_version_check(daq)

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
    demod_rate = 1e3
    time_constant = 0.01
    frequency = 1e6
    exp_setting = [['/%s/sigins/%d/ac'             % (device, in_channel), 0],
                   ['/%s/sigins/%d/range'          % (device, in_channel), 2*amplitude],
                   ['/%s/sigins/%d/diff'           % (device, in_channel), 0],
                   ['/%s/sigouts/%d/add'           % (device, out_channel), 0],
                   ['/%s/demods/%d/enable'         % (device, demod_index), 1],
                   ['/%s/demods/%d/rate'           % (device, demod_index), demod_rate],
                   ['/%s/demods/%d/adcselect'      % (device, demod_index), in_channel],
                   ['/%s/demods/%d/order'          % (device, demod_index), 4],
                   ['/%s/demods/%d/timeconstant'   % (device, demod_index), time_constant],
                   ['/%s/demods/%d/oscselect'      % (device, demod_index), osc_index],
                   ['/%s/demods/%d/harmonic'       % (device, demod_index), 1],
                   ['/%s/oscs/%d/freq'             % (device, osc_index), frequency],
                   ['/%s/sigouts/%d/on'            % (device, out_channel), 1],
                   ['/%s/sigouts/%d/enables/%d'    % (device, out_channel, out_mixer_channel), 1],
                   ['/%s/sigouts/%d/range'         % (device, out_channel), sigouts_range],
                   ['/%s/sigouts/%d/amplitudes/%d' % (device, out_channel, out_mixer_channel), amplitude/sigouts_range]]
    daq.set(exp_setting)

    # The settings for the scope.
    #
    # The scope's sampling rate is configured by specifying the ``time`` node
    # (/devN/scopes/0/time). The rate is equal to 210e6/2**time, where 210e6 is
    # the HF2 ADC's sampling rate (whose value can be read from the device's
    # clockbase node, /devX/clockbase). ``time`` is an integer in range(0,16).
    #
    # Since the length of a scope shot is fixed (2048) on an HF2, specifying the
    # rate also specifies the time duration of a scope shot,
    # t_shot=2048*1./rate=2048*2**time/210e6.
    #
    # Therefore, if we would like to obtain (at least) 10 periods of the signal
    # generated by Oscillator 1, we need to set the scope's time parameter as
    # following:
    clockbase = float(daq.getInt('/%s/clockbase' % device))  # 210e6 for HF2
    desired_t_shot = 10./frequency
    scope_time = np.ceil(np.max([0, np.log2(clockbase*desired_t_shot/2048.)]))
    if scope_time > 15:
        scope_time = 15
        warnings.warn("Can't not obtain scope durations of %.3f s, scope shot duration will be %.3f."
                      % (desired_t_shot, 2048.*2**scope_time/clockbase))
    print("Will set /%s/scopes/0/time to %d." % (device, scope_time))

    scope_settings = [['/%s/scopes/0/channel'         % (device), 2],  # 2=Signal Output 1
                      ['/%s/scopes/0/trigchannel'     % (device), 2],
                      ['/%s/scopes/0/triglevel'       % (device), 0.0],
                      ['/%s/scopes/0/trigholdoff'     % (device), 0.1],
                      # Enable bandwidth limiting: avoid antialiasing effects due to
                      # sub-sampling when the scope sample rate is less than the input
                      # channel's sample rate.
                      ['/%s/scopes/0/bwlimit'         % (device), 1],
                      # Set the sampling rate.
                      ['/%s/scopes/0/time'            % (device), scope_time],
                      # Enable the scope
                      ['/%s/scopes/0/enable' % device, 1]]
    daq.set(scope_settings)

    # Perform a global synchronisation between the device and the data server:
    # Ensure that 1. the settings have taken effect on the device before issuing
    # the poll() command and 2. clear the API's data buffers.
    daq.sync()

    # Subscribe to the scope wave node, this contains the scope output.
    path = '/%s/scopes/0/wave' % (device)
    daq.subscribe(path)

    # Poll data for 1s
    poll_length = 1  # [s]
    poll_timeout = 500  # [ms]
    poll_flags = 0
    poll_return_flat_dict = True
    data = daq.poll(poll_length, poll_timeout, poll_flags, poll_return_flat_dict)

    # Unsubscribe from all paths.
    daq.unsubscribe('*')
    # Disable the scope.
    daq.setInt('/%s/scopes/0/enable' % device, 0)

    # Check the dictionary returned is non-empty.
    assert data, "poll() returned an empty data dictionary, scope's trigger criteria not violated?"
    # Note, the data could be empty if no data arrived, e.g., if the scope was
    # disabled.
    assert path in data, "The data dictionary returned by poll() has no key '%s'" % path
    # The data returned by poll is a dictionary whose keys correspond to the
    # subscribed node paths. Looking up a key in the dictionary returns the data
    # associated with that node.
    shots = data[path]
    # The scope data polled from the node /devN/scopes/0/wave, here ``shots``,
    # is a list of dictionaries; the length of ``shots`` is the number of scope
    # shots that were returned by poll().
    print("poll() returned", len(shots), "scope shots.")
    assert len(shots) >= 0, "len(data[%s]) is 0: It doesn't contain any scope shots." % path

    # The values of the scope shot are 16-bit integers.
    min_val = np.min(shots[0]['wave'])
    max_val = np.max(shots[0]['wave'])
    # In order to obtain the physical value of the wave we need to scale
    # accordingly:
    sigouts_range_set = daq.getDouble('/%s/sigouts/0/range' % device)
    scale = sigouts_range_set/(2**15)  # The scope's wave are 16-bit integers
    print("Maximum value of first shot: {:+d} (int16), scaled: {:+.3f} V.".format(min_val, scale*min_val))
    print("Minimum value of first shot: {:+d} (int16), scaled: {:+.3f} V.".format(max_val, scale*max_val))

    if do_plot:
        import matplotlib.pyplot as plt
        # Create plot
        plt.clf()
        plt.grid(True)
        for shot in shots:
            t = np.linspace(0, shot['dt']*len(shot['wave']), len(shot['wave']))
            # Plot the shots, scaling accordingly.
            plt.plot(t, scale*shot['wave'])
        plt.title('Poll returned %d scope shots' % len(shots))
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude (V)')
        plt.ylim([-sigouts_range_set, sigouts_range_set])
        plt.draw()
        plt.show()

    return shots

run_example('DEV801', do_plot = True)