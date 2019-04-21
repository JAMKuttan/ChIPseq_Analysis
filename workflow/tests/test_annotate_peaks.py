#!/usr/bin/env python3

import pytest
import pandas as pd
from io import StringIO
import os
import utils

test_output_path = os.path.dirname(os.path.abspath(__file__)) + \
                '/../output/peakAnnotation/'


@pytest.mark.singleend
def test_pie_singleend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCSR238SGC.chipseeker_pie.pdf'))


@pytest.mark.singleend
def test_upsetplot_singleend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCSR238SGC.chipseeker_upsetplot.pdf'))


@pytest.mark.singleend
def test_annotation_singleend():
    annotation_file = test_output_path + 'ENCSR238SGC.chipseeker_annotation.tsv'
    assert os.path.exists(annotation_file)
    assert utils.count_lines(annotation_file) == 149284


@pytest.mark.pairedend
def test_pie_pairedend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCSR729LGA.chipseeker_pie.pdf'))


@pytest.mark.pairedend
def test_upsetplot_pairedend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCSR729LGA.chipseeker_upsetplot.pdf'))


@pytest.mark.pairedend
def test_annotation_pairedend():
    annotation_file = test_output_path + 'ENCSR729LGA.chipseeker_annotation.tsv'
    assert os.path.exists(annotation_file)
    assert utils.count_lines(annotation_file) == 25494
