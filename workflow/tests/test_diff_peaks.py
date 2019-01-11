#!/usr/bin/env python3

import pytest
import pandas as pd
from io import StringIO
import os
import utils

test_output_path = os.path.dirname(os.path.abspath(__file__)) + \
                '/../output/diffPeaks/'


@pytest.mark.singleend
def test_diff_peaks_singleend_single_rep():
    assert os.path.isdir(test_output_path) == False

@pytest.mark.pairedend
def test_annotate_peaks_pairedend_single_rep():
    assert os.path.isdir(test_output_path) == False

@pytest.mark.singlediff
def test_diff_peaks_singleend_multiple_rep():
    assert os.path.exists(os.path.join(test_output_path, 'heatmap.pdf'))
    assert os.path.exists(os.path.join(test_output_path, 'pca.pdf'))
    assert os.path.exists(os.path.join(test_output_path, 'normcount_peaksets.txt'))
    if os.path.isfile(os.path.join(test_output_path, 'ENCSR272GNQ_vs_ENCSR238SGC_diffbind.bed')):
        assert os.path.exists(os.path.join(test_output_path, 'ENCSR272GNQ_vs_ENCSR238SGC_diffbind.bed'))
        diffbind_file = test_output_path + 'ENCSR272GNQ_vs_ENCSR238SGC_diffbind.csv'
    else os.path.isfile(os.path.join(test_output_path, 'ENCSR238SGC_vs_ENCSR272GNQ_diffbind.bed')):
        assert os.path.exists(os.path.join(test_output_path, 'ENCSR238SGC_vs_ENCSR272GNQ_diffbind.bed'))
        diffbind_file = test_output_path + 'ENCSR238SGC_vs_ENCSR272GNQ_diffbind.csv'
    assert os.path.exists(diffbind_file)
    assert utils.count_lines(diffbind_file) == 201039

@pytest.mark.paireddiff
def test_annotate_peaks_pairedend_single_rep():
    assert os.path.exists(os.path.join(test_output_path, 'heatmap.pdf'))
    assert os.path.exists(os.path.join(test_output_path, 'pca.pdf'))
    assert os.path.exists(os.path.join(test_output_path, 'normcount_peaksets.txt'))
    if os.path.isfile(os.path.join(test_output_path, 'ENCSR757EMK_vs_ENCSR729LGA_diffbind.bed')):
        assert os.path.exists(os.path.join(test_output_path, 'ENCSR757EMK_vs_ENCSR729LGA_diffbind.bed'))
        diffbind_file = test_output_path + 'ENCSR757EMK_vs_ENCSR729LGA_diffbind.csv'
    else os.path.isfile(os.path.join(test_output_path, 'ENCSR729LGA_vs_ENCSR757EMK_diffbind.bed')):
        assert os.path.exists(os.path.join(test_output_path, 'ENCSR729LGA_vs_ENCSR757EMK_diffbind.bed'))
        diffbind_file = test_output_path + 'ENCSR729LGA_vs_ENCSR757EMK_diffbind.csv'
    assert os.path.exists(diffbind_file)
    assert utils.count_lines(diffbind_file) == 66201
