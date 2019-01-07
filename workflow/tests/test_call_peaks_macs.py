#!/usr/bin/env python3

import pytest
import os
import utils

test_output_path = os.path.dirname(os.path.abspath(__file__)) + \
                '/../output/callPeaksMACS/'


@pytest.mark.singleend
def test_call_peaks_macs_singleend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCLB144FDT.fc_signal.bw'))
    assert os.path.exists(os.path.join(test_output_path, 'ENCLB144FDT.pvalue_signal.bw'))
    assert os.path.exists(os.path.join(test_output_path, 'ENCLB144FDT.xls'))
    peak_file = test_output_path + 'ENCLB144FDT.narrowPeak'
    assert utils.count_lines(peak_file) == 227389


@pytest.mark.pairedend
def test_call_peaks_macs_pairedend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCLB568IYX.fc_signal.bw'))
    assert os.path.exists(os.path.join(test_output_path, 'ENCLB568IYX.pvalue_signal.bw'))
    assert os.path.exists(os.path.join(test_output_path, 'ENCLB568IYX.xls'))
    peak_file = test_output_path + 'ENCLB568IYX.narrowPeak'
    assert utils.count_lines(peak_file) == 138827
