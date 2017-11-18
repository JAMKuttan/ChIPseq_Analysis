#!/usr/bin/env python3

import pytest
import pandas as pd
from io import StringIO
import os
import utils
import call_peaks_macs

test_output_path = os.path.dirname(os.path.abspath(__file__)) + \
                '/../output/callPeaksMACS/'


def test_call_peaks_macs_singleend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCLB144FDT.fc_signal.bw'))
    assert os.path.exists(os.path.join(test_output_path, 'ENCLB144FDT.pvalue_signal.bw'))
    peak_file = test_output_path + 'ENCLB144FDT_peaks.narrowPeak'
    assert utils.count_lines(peak_file) == '210349'


def test_call_peaks_macs_pairedend():
    # Do the same thing for paired end data
    pass
