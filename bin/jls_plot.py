#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import numpy as np
import sys
import math
import matplotlib.pyplot as plt
from joulescope.data_recorder import DataReader
from joulescope.view import data_array_to_update
from joulescope.units import unit_prefix
from scipy.misc import electrocardiogram
from scipy.signal import find_peaks
#from cupy.scipy import

from matplotlib.ticker import EngFormatter

# Developed for https://forum.joulescope.com/t/automation-of-plotting-long-term-records/415
# numpy and scipy have to be installed using pip not conda. If not got an error "DLL load failed while importing _arpack"


def get_parser():
    p = argparse.ArgumentParser(
        description='Load a JLS file and generate an image plot.')
    p.add_argument('input',
                   help='The input filename path.')
    p.add_argument('--out',
                   help='The output filename path.')
    p.add_argument('--stats',
                   action='store_true',
                   help='Display statistics on the plot.')
    p.add_argument('--show',
                   action='store_true',
                   help='Display the plot.')
    p.add_argument('--sample_count',
                   type=int,
                   default=1000,
                   help='The number of samples to display')
    return p


# Statistics formatting copied from joulescope_ui.widgets.waveform.signal_statistics
def _si_format(names, values, units):
    results = []
    if units is None:
        units = ''
    if len(values):
        values = np.array(values)
        max_value = float(np.max(np.abs(values)))
        _, prefix, scale = unit_prefix(max_value)
        scale = 1.0 / scale
        if not len(prefix):
            prefix = '&nbsp;'
        units_suffix = f'{prefix}{units}'
        for lbl, v in zip(names, values):
            v *= scale
            if abs(v) < 0.000005:  # minimum display re§solution
                v = 0
            v_str = ('%+6f' % v)[:8]
            results.append('%s=%s %s' % (lbl, v_str, units_suffix))
    return results


def si_format(labels):
    results = []
    if not len(labels):
        return results
    units = None
    values = []
    names = []
    for name, d in labels.items():
        value = float(d['value'])
        if name == 'σ2':
            name = 'σ'
            value = math.sqrt(value)
        if d['units'] != units:
            results.extend(_si_format(names, values, units))
            units = d['units']
            values = [value]
            names = [name]
        else:
            values.append(value)
            names.append(name)
    results.extend(_si_format(names, values, units))
    return results

import multiprocessing as mp
def run():
    args = get_parser().parse_args()
    #r = DataReader().open(args.input)
    r = DataReader().open('d:/20220113_144116_testmode_current_pattern.jls')
    #r = DataReader().open('d:/20220120_065401_eco_ro_3times_2msr.jls')
    #r = DataReader().open('d:/20220120_101230_eco_ro_3times_200ksr.jls')
    start_idx, stop_idx = r.sample_id_range
    d_idx = stop_idx - start_idx
    f = r.sampling_frequency
    incr = d_idx // (d_idx // 50) #args.sample_count, see README_export_jls2png.md for evaluating the value
    data = r.data_get(start_idx, stop_idx, incr, units='samples')
    print(data)

    # stat
    x = np.linspace(0.0, d_idx / f, len(data), dtype=np.float64)
    x_limits = [x[0], x[-1]]
    d = data_array_to_update(x_limits, x, data)
    s = r.statistics_get(start_idx, stop_idx)
    s_str = [f't = {x[-1]:.3} s']
    s_str += si_format(s['signals']['current'])
    print(s_str)

    #plot
    xs= d['signals']['current']['µ']['value']

    # list of peak-ranges
    # wakeup every 2s: I_lower<peak<I_higher
    # lorawan tx: I_lower<peak<I

    # find peaks for each range and print list and mark with different color
    #peak2s, peak_heights2s = find_peaks(xs, height=(0.0004, 0.002), distance=5)
    #peak_lora_tx, peak_heights_lora_tx = find_peaks(xs, height=(0.024, 0.04))
    peak_eco_readout, peak_height_eco_readout = find_peaks(xs, height=(0.38, 5),
                                                           distance=150)  # 100us width > 200mA (this level is only reached from ECO peak): 100us/(1/sample_frequency)=100us/(1/2000000)=200 > 200/sample_count=200/i >
    #region
    #cnt=0
    #for peak in peak2s:
    #    print("sample: ",peak)
    #    print("time from 0: ",peak*1/r.sampling_frequency*incr)
    #    print("level: ",peak_heights2s['peak_heights'][cnt])
    #    cnt += 1
    #endregion
    f = plt.figure()
    ax_i=f.add_subplot(1,1,1)
#region
    #plot 2s peaks
    #print("peaklevels:{}",peak_heights2s['peak_heights'])
    ax_i.plot(xs)
    ax_i.plot(peak2s, xs[peak2s], "x", color="brown")
    #plt.plot(np.zeros_like(xs), "--", color="gray")
    #plt.show()
    #plt.savefig("test_2s.png")

    # plot lora tx peaks
    #print("peaklevels:{}", peak_heights_lora_tx['peak_heights'])
    #plt.plot(xs)
    ax_i.plot(peak_lora_tx, xs[peak_lora_tx], "x", color="blue")
    #plt.plot(np.zeros_like(xs), "--", color="gray")
    #plt.show()
    #plt.savefig("test_lora_tx.png")
#endregion
    # plot eco readout peaks
    print("peaklevels:", peak_height_eco_readout['peak_heights'])
    #plt.plot(xs)
    ax_i.plot(peak_eco_readout, xs[peak_eco_readout], "x", color="red")
    #ax_i.plot(np.zeros_like(xs), "--", color="gray")
    #plt.show()
    #plt.savefig("test_eco_readout.png")


    #ax_i = f.add_subplot(1, 1, 1)
    #ax_i = f.add_subplot(plt)
    ax_i.set_title('Current vs Time')
    ax_i.grid(True)
    formatter0 = EngFormatter(unit='A')
    ax_i.yaxis.set_major_formatter(formatter0)
    #ax_i.plot(x, d['signals']['current']['µ']['value'])
    ax_i.set_xlabel('Time (seconds)')
    ax_i.set_ylabel('Current (A)')
    ax_i.set_ylim([-0.1, 0.5])

    # after plotting the data, format the labels
    current_values = plt.gca().get_yticks()
    # using format string '{:.0f}' here but you can choose others
    #plt.gca().set_yticklabels(['{:.0f}'.format(x) for x in current_values])


    if args.stats:
        f.subplots_adjust(right=0.75)
        f.text(0.99, 0.85, '\n'.join(s_str), horizontalalignment='right', verticalalignment='top')
    if args.show:
        plt.show()
        #ax_i.show()
    if args.out:
        f.savefig(args.out)


if __name__ == '__main__':

    sys.exit(run())
