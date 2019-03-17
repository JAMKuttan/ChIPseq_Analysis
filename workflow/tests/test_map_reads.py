#!/usr/bin/env python3

import pytest
import os

test_output_path = os.path.dirname(os.path.abspath(__file__)) + \
                '/../output/alignReads/'


@pytest.mark.singleend
def test_map_reads_singleend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCLB831RUI/ENCLB831RUI.bam'))
    aligned_reads_report = test_output_path + 'ENCLB831RUIENCLB831RUI/ENCLB831RUI.flagstat.qc'
    samtools_report = open(aligned_reads_report).readlines()
    assert '80795025 + 0 in total' in samtools_report[0]
    assert '80050072 + 0 mapped (99.08% : N/A)' in samtools_report[4]


@pytest.mark.pairedend
def test_map_reads_pairedend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCLB678IDC/ENCLB678IDC.bam'))
    aligned_reads_report = test_output_path + 'ENCLB678IDC/ENCLB678IDC.flagstat.qc'
    samtools_report = open(aligned_reads_report).readlines()
    assert '72660890 + 0 in total' in samtools_report[0]
    assert '72053925 + 0 mapped (99.16% : N/A)' in samtools_report[4]
    assert '71501126 + 0 properly paired (98.40% : N/A)' in samtools_report[8]
