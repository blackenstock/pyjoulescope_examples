import joulescope_ui.widgets.waveform.waveform
from joulescope.data_recorder import DataReader
import sys
import argparse
sys.path.append('../../joulescope_ui/widgets/waveform')
from joulescope_ui.widgets.waveform import waveform

def get_parser():
    p = argparse.ArgumentParser(
        description='Export jls file to png.')
    p.add_argument('--filename', '-f',
                   help='.jls capture filename. ')
    return p

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

