#!/usr/bin/env python3

import pytest
import pandas as pd
from io import StringIO
import check_design


DESIGN_STRING = """sample_id\texperiment_id\tbiosample\tfactor\ttreatment\treplicate\tcontrol_id\tfastq_read1
A_1\tA\tLiver\tH3K27ac\tNone\t1\tB_1\tA_1.fastq.gz
A_2\tA\tLiver\tH3K27ac\tNone\t2\tB_2\tA_2.fastq.gz
B_1\tB\tLiver\tInput\tNone\t1\tB_1\tB_1.fastq.gz
B_2\tB\tLiver\tInput\tNone\t2\tB_2\tB_2.fastq.gz
"""

FASTQ_STRING = """
A_1.fastq.gz\t/path/to/file/A_1.fastq.gz
A_2.fastq.gz\t/path/to/file/A_2.fastq.gz
B_1.fastq.gz\t/path/to/file/B_1.fastq.gz
B_2.fastq.gz\t/path/to/file/B_2.fastq.gz
"""


@pytest.fixture
def design():
    design_file = StringIO(DESIGN_STRING)
    design_df = pd.read_csv(design_file, sep="\t")
    return design_df


@pytest.fixture
def fastq_files():
    fastq_file = StringIO(FASTQ_STRING)
    fastq_df = pd.read_csv(fastq_file, sep='\t', names=['name', 'path'])
    return fastq_df


@pytest.fixture
def design_1(design):
    design_df = design.drop('fastq_read1', axis=1)
    return design_df


@pytest.fixture
def design_2(design):
    # Drop Control B_1
    design_df = design.drop(design.index[2])
    return design_df


@pytest.fixture
def design_3(design):
    # Drop A_2 and B_2 and append as fastq_read2
    design_df = design.drop(design.index[[1, 3]])
    design_df['fastq_read2'] = design.loc[[1, 3], 'fastq_read1'].values
    return design_df


@pytest.fixture
def design_4(design):
    # Update replicate 2 for experiment B to be 1
    design.loc[design['sample_id'] == 'B_2', 'replicate'] = 1
    return design


@pytest.fixture
def fastq_files_1(fastq_files):
    # Drop B_2.fastq.gz
    fastq_df = fastq_files.drop(fastq_files.index[3])
    return fastq_df


@pytest.mark.unit
def test_check_headers_singleend(design_1):
    paired = False
    with pytest.raises(Exception) as excinfo:
        check_design.check_design_headers(design_1, paired)
    assert str(excinfo.value) == "Missing column headers: ['fastq_read1']"


@pytest.mark.unit
def test_check_headers_pairedend(design):
    paired = True
    with pytest.raises(Exception) as excinfo:
        check_design.check_design_headers(design, paired)
    assert str(excinfo.value) == "Missing column headers: ['fastq_read2']"


@pytest.mark.unit
def test_check_controls(design_2):
    with pytest.raises(Exception) as excinfo:
        check_design.check_controls(design_2)
    assert str(excinfo.value) == "Missing control experiments: ['B_1']"


@pytest.mark.unit
def test_check_files_missing_files(design, fastq_files_1):
    paired = False
    with pytest.raises(Exception) as excinfo:
        new_design = check_design.check_files(design, fastq_files_1, paired)
    assert str(excinfo.value) == "Missing files from design file: ['B_2.fastq.gz']"


@pytest.mark.unit
def test_check_files_output_singleend(design, fastq_files):
    paired = False
    new_design = check_design.check_files(design, fastq_files, paired)
    assert new_design.loc[0, 'fastq_read1'] == "/path/to/file/A_1.fastq.gz"


@pytest.mark.unit
def test_check_files_output_pairedend(design_3, fastq_files):
    paired = True
    new_design = check_design.check_files(design_3, fastq_files, paired)
    assert new_design.loc[0, 'fastq_read2'] == "/path/to/file/A_2.fastq.gz"



@pytest.mark.unit
def test_check_replicates(design_4):
    paired = False
    with pytest.raises(Exception) as excinfo:
        new_design = check_design.check_replicates(design_4)
    assert str(excinfo.value) == "Duplicate replicates in experiments: ['B']"
