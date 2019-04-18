#!/usr/bin/env python3

import pytest
import os
import pandas as pd

test_output_path = os.path.dirname(os.path.abspath(__file__)) + \
                '/../output/filterReads/'


@pytest.mark.singleend
def test_dedup_files_singleend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCLB831RUI/ENCLB831RUI.dedup.bam'))
    assert os.path.exists(os.path.join(test_output_path, 'ENCLB831RUI/ENCLB831RUI.dedup.bam.bai'))
    assert os.path.exists(os.path.join(test_output_path, 'ENCLB831RUI/ENCLB831RUI.dedup.qc'))


@pytest.mark.singleend
def test_map_qc_singleend():
    filtered_reads_report = test_output_path + 'ENCLB831RUI/ENCLB831RUI.dedup.flagstat.qc'
    samtools_report = open(filtered_reads_report).readlines()
    assert '64962570 + 0 in total' in samtools_report[0]
    assert '64962570 + 0 mapped (100.00%:N/A)' in samtools_report[4]


@pytest.mark.singleend
def test_library_complexity_singleend():
    library_complexity = test_output_path + 'ENCLB831RUI/ENCLB831RUI.pbc.qc'
    df_library_complexity = pd.read_csv(library_complexity, sep='\t')
    assert  df_library_complexity["NRF"].iloc[0] == 0.926192
    assert  df_library_complexity["PBC1"].iloc[0] == 0.926775
    assert  df_library_complexity["PBC2"].iloc[0] == 13.706885


@pytest.mark.pairedend
def test_dedup_files_pairedend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCLB568IYX/ENCLB568IYX.dedup.bam'))
    assert os.path.exists(os.path.join(test_output_path, 'ENCLB568IYX/ENCLB568IYX.dedup.bam.bai'))
    assert os.path.exists(os.path.join(test_output_path, 'ENCLB568IYX/ENCLB568IYX.dedup.qc'))


@pytest.mark.pairedend
def test_map_qc_pairedend():
    filtered_reads_report = test_output_path + 'ENCLB568IYX/ENCLB568IYX.dedup.flagstat.qc'
    samtools_report = open(filtered_reads_report).readlines()
    assert '47388510 + 0 in total' in samtools_report[0]
    assert '47388510 + 0 mapped (100.00%:N/A)' in samtools_report[4]


@pytest.mark.pairedend
def test_library_complexity_pairedend():
    library_complexity = test_output_path + 'ENCLB568IYX/ENCLB568IYX.pbc.qc'
    df_library_complexity = pd.read_csv(library_complexity, sep='\t')
    assert  df_library_complexity["NRF"].iloc[0] == 0.947064
    assert  round(df_library_complexity["PBC1"].iloc[0],6) == 0.946723
    assert  round(df_library_complexity["PBC2"].iloc[0],6) == 18.642645
