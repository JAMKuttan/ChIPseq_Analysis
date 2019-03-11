#!/usr/bin/env python3

import pytest
import os
import pandas as pd
from io import StringIO
import experiment_qc

test_output_path = os.path.dirname(os.path.abspath(__file__)) + \
                '/../output/experimentQC/'

DESIGN_STRING = """sample_id\texperiment_id\tbiosample\tfactor\ttreatment\treplicate\tcontrol_id\tbam_reads
A_1\tA\tLiver\tH3K27ac\tNone\t1\tB_1\tA_1.bam
A_2\tA\tLiver\tH3K27ac\tNone\t2\tB_2\tA_2.bam
B_1\tB\tLiver\tInput\tNone\t1\tB_1\tB_1.bam
B_2\tB\tLiver\tInput\tNone\t2\tB_2\tB_2.bam
"""


@pytest.fixture
def design_bam():
    design_file = StringIO(DESIGN_STRING)
    design_df = pd.read_csv(design_file, sep="\t")
    return design_df


@pytest.mark.unit
def test_check_update_controls(design_bam):
    new_design = experiment_qc.update_controls(design_bam)
    assert new_design.loc[0, 'control_reads'] == "B_1.bam"


@pytest.mark.singleend
def test_coverage_singleend():
    assert os.path.exists(os.path.join(test_output_path, 'sample_mbs.npz'))
    assert os.path.exists(os.path.join(test_output_path, 'coverage.pdf'))


@pytest.mark.singleend
def test_spearman_singleend():
    assert os.path.exists(os.path.join(test_output_path, 'heatmap_SpearmanCorr.pdf'))


@pytest.mark.singleend
def test_pearson_singleend():
    assert os.path.exists(os.path.join(test_output_path, 'heatmap_PearsonCorr.pdf'))


@pytest.mark.singleend
def test_fingerprint_singleend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCLB144FDT_fingerprint.pdf'))
    assert os.path.exists(os.path.join(test_output_path, 'ENCLB831RUI_fingerprint.pdf'))


@pytest.mark.pairdend
def test_coverage_pairedend():
    assert os.path.exists(os.path.join(test_output_path, 'sample_mbs.npz'))
    assert os.path.exists(os.path.join(test_output_path, 'coverage.pdf'))


@pytest.mark.pairdend
def test_spearman_pairedend():
    assert os.path.exists(os.path.join(test_output_path, 'heatmap_SpearmanCorr.pdf'))


@pytest.mark.pairdend
def test_pearson_pairedend():
    assert os.path.exists(os.path.join(test_output_path, 'heatmap_PearsonCorr.pdf'))


@pytest.mark.pairdend
def test_fingerprint_pairedend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCLB568IYX_fingerprint.pdf'))
    assert os.path.exists(os.path.join(test_output_path, 'ENCLB637LZP_fingerprint.pdf'))
