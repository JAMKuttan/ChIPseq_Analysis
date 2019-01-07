#!/usr/bin/env python3

import pytest
import pandas as pd
from io import StringIO
import os
import utils

test_output_path = os.path.dirname(os.path.abspath(__file__)) + \
                '/../output/motifSearch/'


@pytest.mark.singleend
def test_motif_search_singleend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCSR238SGC.fa'))
    assert os.path.exists(os.path.join(test_output_path, 'ENCSR238SGC_memechip', 'index.html'))
    peak_file_ENCSR238SGC = test_output_path + 'ENCSR238SGC.600.narrowPeak'
    assert os.path.exists(peak_file_ENCSR238SGC)
    assert utils.count_lines(peak_file_ENCSR238SGC) == 600

@pytest.mark.pairedend
def test_motif_search_pairedend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCSR729LGA.fa'))
    assert os.path.exists(os.path.join(test_output_path, 'ENCSR729LGA_memechip', 'index.html'))
    peak_file_ENCSR729LGA= test_output_path + 'ENCSR729LGA.600.narrowPeak'
    assert os.path.exists(peak_file_ENCSR729LGA)
    assert utils.count_lines(peak_file_ENCSR729LGA) == 600
