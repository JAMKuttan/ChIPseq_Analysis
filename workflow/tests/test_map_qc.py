#!/usr/bin/env python3

import pytest
import os
import pandas as pd

test_output_path = os.path.dirname(os.path.abspath(__file__)) + \
                '/../output/filterReads/'


@pytest.mark.integration
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


@pytest.mark.integration
def test_map_qc_pairedend():
    # Do the same thing for paired end data
    pass
