#!/usr/bin/env python3

import pytest
import os
import pandas as pd

test_output_path = os.path.dirname(os.path.abspath(__file__)) + \
                '/../output/filterReads/'


@pytest.mark.singleend
def test_map_qc_singleend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCFF646LXU.filt.nodup.bam'))
    assert os.path.exists(os.path.join(test_output_path, 'ENCFF646LXU.filt.nodup.bam.bai'))
    filtered_reads_report = test_output_path + 'ENCFF646LXU.filt.nodup.flagstat.qc'
    samtools_report = open(filtered_reads_report).readlines()
    assert '64962570 + 0 in total' in samtools_report[0]
    assert '64962570 + 0 mapped (100.00%:N/A)' in samtools_report[4]
    library_complexity = test_output_path + 'ENCFF646LXU.filt.nodup.pbc.qc'
    df_library_complexity = pd.read_csv(library_complexity, sep='\t')
    assert  df_library_complexity["NRF"].iloc[0] == 0.926192
    assert  df_library_complexity["PBC1"].iloc[0] == 0.926775
    assert  df_library_complexity["PBC2"].iloc[0] == 13.706885


@pytest.mark.pairedend
def test_map_qc_pairedend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCFF293YFE_val_2ENCFF330MCZ_val_1.filt.nodup.bam'))
    assert os.path.exists(os.path.join(test_output_path, 'ENCFF293YFE_val_2ENCFF330MCZ_val_1.filt.nodup.bambai'))
    filtered_reads_report = test_output_path + 'ENCFF293YFE_val_2ENCFF330MCZ_val_1.filt.nodup.flagstat.qc'
    samtools_report = open(filtered_reads_report).readlines()
    assert '47389080 + 0 in total' in samtools_report[0]
    assert '47389080 + 0 mapped (100.00%:N/A)' in samtools_report[4]
    library_complexity = test_output_path + 'ENCFF293YFE_val_2ENCFF330MCZ_val_1.filt.nodup.pbc.qc'
    df_library_complexity = pd.read_csv(library_complexity, sep='\t')
    assert  df_library_complexity["NRF"].iloc[0] == 0.947064
    assert  df_library_complexity["PBC1"].iloc[0] == 0.946724
    assert  df_library_complexity["PBC2"].iloc[0] == 18.643039
