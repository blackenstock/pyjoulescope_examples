#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from joulescope import scan_require_one
from joulescope.data_recorder import DataReader
import sys
import argparse
import queue
import signal
from PySide2 import QtCore, QtGui, QtWidgets
from joulescope_ui.main import MainWindow
from joulescope_ui.command_processor import CommandProcessor
from joulescope_ui.preferences_def import preferences_def
import joulescope_ui.widgets.waveform.waveform
from joulescope_ui.recording_viewer_factory import factory
import joulescope_ui.main
import joulescope_ui.entry_points.ui

from joulescope.units import three_sig_figs
#sys.path.append('../../joulescope_ui/widgets/waveform')
from joulescope_ui.widgets.waveform import waveform

def get_parser():
    p = argparse.ArgumentParser(
        description='Export jls file to png.')
    p.add_argument('--filename', '-f',
                   help='.jls capture filename. ')
    return p
# run the application
def testrunAndShowDirectly():
    filename = "../testdata/test_1s.jls"
    rc = joulescope_ui.main.run(None, None, None, filename, None)

# run ui and call the save image function
def testrunAndShowAndSaveDirectly():
    filename_data = "../testdata/test_1s.jls"
    filename_pic = "../testdata/artifacts/df.png"
    app = QtWidgets.QApplication(sys.argv)
    cmdp = CommandProcessor()
    cmdp = preferences_def(cmdp)
    ui = MainWindow(app, None, cmdp, None)
    wv = joulescope_ui.widgets.waveform.WaveformWidget(ui, cmdp, None)


    png = wv._export_as_image()
    png.save(filename_pic)


# aim: without showing up the window
def runWaveformDirectly():
    filename = "../testdata/test_1s.jls"

def run():
    args = get_parser().parse_args()
    filename = args.filename
    r = DataReader().open(filename)
    start_idx, stop_idx = r.sample_id_range
    incr = (stop_idx - start_idx) // 1000
    data = r.data_get(start_idx, stop_idx, incr, units='samples')
    i = data[:,0]
    print("loaded")
    print("{} i-len", i.size)
    test = factory("../testdata/test_1s.jls")

    test.open()


if __name__ == '__main__':
    testrunAndShowAndSaveDirectly()