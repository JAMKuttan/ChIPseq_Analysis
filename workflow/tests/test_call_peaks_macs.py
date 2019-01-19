#!/usr/bin/env python3

import pytest
import os
import utils

test_output_path = os.path.dirname(os.path.abspath(__file__)) + \
                '/../output/callPeaksMACS/'


@pytest.mark.singleend
def test_fc_signal_singleend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCLB144FDT.fc_signal.bw'))


@pytest.mark.singleend
def test_pvalue_signal_singleend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCLB144FDT.pvalue_signal.bw'))


@pytest.mark.singleend
def test_peaks_xls_singleend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCLB144FDT_peaks.xls'))


@pytest.mark.singleend
def test_peaks_bed_singleend():
    peak_file = test_output_path + 'ENCLB144FDT.narrowPeak'
    assert utils.count_lines(peak_file) == 227389


@pytest.mark.pairedend
def test_fc_signal_pairedend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCLB568IYX.fc_signal.bw'))


@pytest.mark.pairedend
def test_pvalue_signal_pairedend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCLB568IYX.pvalue_signal.bw'))


@pytest.mark.pairedend
def test_peaks_xls_pairedend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCLB568IYX_peak.xls'))


@pytest.mark.pairedend
def test_peaks_bed_pairedend():
    peak_file = test_output_path + 'ENCLB568IYX.narrowPeak'
    assert utils.count_lines(peak_file) == 113821
