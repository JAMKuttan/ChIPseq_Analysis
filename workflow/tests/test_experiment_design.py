#!/usr/bin/env python3

import pytest
import pandas as pd
from io import StringIO
from design_file import experiment_design
import os

test_output_path = os.path.dirname(os.path.abspath(__file__)) + \
                '/../output/design/'

DESIGN_STRING = """sample_id\ttag_align\txcor\tbiosample\tfactor\ttreatment\treplicate\tcontrol_id
A_1\tA_1.tagAlign.gz\tA\tLiver\tH3K27ac\tNone\t1\tB_1
A_2\tA_2.tagAlign.gz\tA\tLiver\tH3K27ac\tNone\t2\tB_2
B_1\tB_1.tagAlign.gz\tB\tLiver\tInput\tNone\t1\tB_1
B_2\tB_2.tagAlign.gz\tB\tLiver\tInput\tNone\t2\tB_2
"""


@pytest.fixture
def design_tag():
    design_file = StringIO(DESIGN_STRING)
    design_df = pd.read_csv(design_file, sep="\t")
    return design_df


@pytest.mark.unit
def test_check_update_controls_tag(design_tag):
    new_design = experiment_design.update_controls(design_tag)
    assert new_design.loc[0, 'control_tag_align'] == "B_1.tagAlign.gz"


@pytest.mark.integration
def test_experiment_design_single_end():
    design_file = os.path.join(test_output_path, 'ENCSR238SGC.tsv')
    assert os.path.exists(design_file)
    design_df = pd.read_csv(design_file, sep="\t")
    assert design_df.shape[0] == 2


@pytest.mark.integration
def test_experiment_design_paired_end():
    # Do the same thing for paired end data
    pass
