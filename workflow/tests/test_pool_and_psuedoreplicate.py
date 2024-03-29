#!/usr/bin/env python3

import pytest
import pandas as pd
from io import StringIO
import os
import pool_and_psuedoreplicate
import shutil

test_design_path = os.path.dirname(os.path.abspath(__file__)) + \
		'/../../test_data/'
test_output_path = os.path.dirname(os.path.abspath(__file__)) + \
                '/../output/design/'

DESIGN_STRING = """sample_id\tse_tag_align\ttag_align\txcor\texperiment_id\tbiosample\tfactor\ttreatment\treplicate\tcontrol_id\tcontrol_tag_align
A_1\tA_1.tagAlign.gz\tA_1.bedse.gz\tA_1.cc.qc\tA\tLiver\tH3K27ac\tNone\t1\tB_1\tB_1.bedse.gz
A_2\tA_2.tagAlign.gz\tA_2.bedse.gz\tA_2.cc.qc\tA\tLiver\tH3K27ac\tNone\t2\tB_2\tB_2.bedse.gz
"""

@pytest.fixture
def design_experiment():
    design_file = StringIO(DESIGN_STRING)
    design_df = pd.read_csv(design_file, sep="\t")
    return design_df


@pytest.fixture
def design_experiment_2(design_experiment):
    # Drop Replicate A_2
    design_df = design_experiment.drop(design_experiment.index[1])
    return design_df


@pytest.fixture
def design_experiment_3(design_experiment):
    # Update second control to be same as first
    design_experiment.loc[1, 'control_tag_align'] = 'B_1.bedse.gz'
    return design_experiment


@pytest.mark.unit
def test_check_replicates(design_experiment):
    no_reps = pool_and_psuedoreplicate.check_replicates(design_experiment)
    assert no_reps == 2


@pytest.mark.unit
def test_check_replicates_single(design_experiment_2):
    no_reps = pool_and_psuedoreplicate.check_replicates(design_experiment_2)
    assert no_reps == 1


@pytest.mark.unit
def test_check_controls(design_experiment):
    no_controls = pool_and_psuedoreplicate.check_controls(design_experiment)
    assert no_controls == 2


@pytest.mark.unit
def test_check_controls_single(design_experiment_3):
    no_controls = pool_and_psuedoreplicate.check_controls(design_experiment_3)
    assert no_controls == 1


@pytest.mark.unit
def test_single_rep(design_experiment_2):
    cwd = os.getcwd()
    shutil.copy(test_design_path + 'A_1.bedse.gz', cwd)
    shutil.copy(test_design_path + 'B_1.bedse.gz', cwd)
    shutil.copy(test_design_path + 'A_1.tagAlign.gz', cwd)
    shutil.copy(test_design_path + 'B_1.tagAlign.gz', cwd)
    single_rep = pool_and_psuedoreplicate.generate_design('false', 1.2, design_experiment_2, cwd, 1, 1)
    assert single_rep.shape[0] == 4

@pytest.mark.singleend
def test_pool_and_psuedoreplicate_singleend():
    design_file = os.path.join(test_output_path, 'ENCSR238SGC_ppr.tsv')
    assert os.path.exists(design_file)
    design_df = pd.read_csv(design_file, sep="\t")
    assert design_df.shape[0] == 5


@pytest.mark.pairedend
def test_experiment_design_pairedend():
    design_file = os.path.join(test_output_path, 'ENCSR729LGA_ppr.tsv')
    assert os.path.exists(design_file)
    design_df = pd.read_csv(design_file, sep="\t")
    assert design_df.shape[0] == 5
