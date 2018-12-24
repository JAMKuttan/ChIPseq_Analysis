#!/usr/bin/env python3

import pytest
import pandas as pd
from io import StringIO
import os
import utils

test_output_path = os.path.dirname(os.path.abspath(__file__)) + \
                '/../output/peakAnnotation/'

DESIGN_STRING = """sample_id\tbam_reads\tbam_index\texperiment_id\tbiosample\tfactor\ttreatment\treplicate\tcontrol_id
A_1\tA_1.bam\tA_1.bai\tA\tLiver\tH3K27ac\tNone\t1\tB_1
A_2\tA_2.bam\tA_2.bai\tA\tLiver\tH3K27ac\tNone\t2\tB_2
B_1\tB_1.bam\tB_1.bai\tB\tLiver\tH3K27ac\tNone\t1\tB_1
B_2\tB_2.bam\tB_2.bai\tB\tLiver\tH3K27ac\tNone\t2\tB_2
"""


@pytest.mark.integration
def test_annotate_peaks_singleend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCSR238SGC.chipseeker_pie.pdf'))
    assert os.path.exists(os.path.join(test_output_path, 'ENCSR238SGC.chipseeker_pie.pdf'))
    assert os.path.exists(os.path.join(test_output_path, 'ENCSR238SGC.chipseeker_pie.pdf'))
    annotation_file = test_output_path + 'ENCSR238SGC.chipseeker_annotation.csv'
    assert os.path.exists(annotation_file)
    assert utils.count_lines(annotation_file) == 152839


@pytest.mark.integration
def test_annotate_peaks_pairedend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCSR217LRF.chipseeker_pie.pdf'))
    assert os.path.exists(os.path.join(test_output_path, 'ENCSR217LRF.chipseeker_pie.pdf'))
    assert os.path.exists(os.path.join(test_output_path, 'ENCSR217LRF.chipseeker_pie.pdf'))
    annotation_file = test_output_path + 'ENCSR217LRF.chipseeker_annotation.csv'
    assert os.path.exists(annotation_file)
    assert utils.count_lines(annotation_file) == 25390
