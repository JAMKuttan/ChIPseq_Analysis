#!/usr/bin/env python3

import pytest
import pandas as pd
from io import StringIO
import os
import utils

test_output_path = os.path.dirname(os.path.abspath(__file__)) + \
                '/../output/peakAnnotation/'


@pytest.mark.singleend
def test_annotate_peaks_singleend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCSR238SGC.chipseeker_pie.pdf'))
    assert os.path.exists(os.path.join(test_output_path, 'ENCSR238SGC.chipseeker_upsetplot.pdf'))
    annotation_file = test_output_path + 'ENCSR238SGC.chipseeker_annotation.csv'
    assert os.path.exists(annotation_file)
    assert utils.count_lines(annotation_file) == 152840


@pytest.mark.pairedend
def test_annotate_peaks_pairedend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCSR729LGA.chipseeker_pie.pdf'))
    assert os.path.exists(os.path.join(test_output_path, 'ENCSR729LGA.chipseeker_upsetplot.pdf'))
    annotation_file = test_output_path + 'ENCSR729LGA.chipseeker_annotation.csv'
    assert os.path.exists(annotation_file)
    assert utils.count_lines(annotation_file) == 25614
