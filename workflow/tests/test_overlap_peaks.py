#!/usr/bin/env python3

import pytest
import pandas as pd
from io import StringIO
import os
import utils
import overlap_peaks

test_output_path = os.path.dirname(os.path.abspath(__file__)) + \
                '/../output/consensusPeaks/'

DESIGN_STRING = """sample_id\tbam_reads\tbam_index\texperiment_id\tbiosample\tfactor\ttreatment\treplicate\tcontrol_id
A_1\tA_1.bam\tA_1.bai\tA\tLiver\tH3K27ac\tNone\t1\tB_1
A_2\tA_2.bam\tA_2.bai\tA\tLiver\tH3K27ac\tNone\t2\tB_2
B_1\tB_1.bam\tB_1.bai\tB\tLiver\tH3K27ac\tNone\t1\tB_1
B_2\tB_2.bam\tB_2.bai\tB\tLiver\tH3K27ac\tNone\t2\tB_2
"""


@pytest.fixture
def design_diff():
    design_file = StringIO(DESIGN_STRING)
    design_df = pd.read_csv(design_file, sep="\t")
    return design_df


@pytest.mark.unit
def test_check_update_design(design_diff):
    new_design = overlap_peaks.update_design(design_diff)
    assert new_design.shape[0] == 2
    assert new_design.loc[0, 'control_bam_reads'] == "B_1.bam"
    assert new_design.loc[0, 'peak_caller'] == "bed"


@pytest.mark.singleend
def test_overlap_peaks_singleend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCSR238SGC.rejected.narrowPeak'))
    peak_file = test_output_path + 'ENCSR238SGC.replicated.narrowPeak'
    assert utils.count_lines(peak_file) == 149291


@pytest.mark.pairedend
def test_overlap_peaks_pairedend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCSR729LGA.rejected.narrowPeak'))
    peak_file = test_output_path + 'ENCSR729LGA.replicated.narrowPeak'
    assert utils.count_lines(peak_file) == 25758
