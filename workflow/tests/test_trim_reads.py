#!/usr/bin/env python3

import pytest
import os

test_data_path = os.path.dirname(os.path.abspath(__file__)) + \
                '/../../test_data/'
test_output_path = os.path.dirname(os.path.abspath(__file__)) + \
                '/../output/trimReads/'



@pytest.mark.singleend
def test_trim_reads_singleend():
    raw_fastq = test_data_path + 'ENCFF833BLU.fastq.gz'
    trimmed_fastq = test_output_path + 'ENCLB144FDT_R1_trimmed.fq.gz'


@pytest.mark.singleend
def test_trim_report_singleend():
    trimmed_fastq_report = test_output_path + \
                            'ENCLB144FDT_R1_trimmed.fq.gz_trimming_report.txt'
    assert os.path.getsize(raw_fastq) != os.path.getsize(trimmed_fastq)
    assert os.path.getsize(trimmed_fastq) == 2512853101
    assert 'Trimming mode: single-end' in open(trimmed_fastq_report).readlines()[4]


@pytest.mark.pairedend
def test_trim_reads_pairedend():
    raw_fastq = test_data_path + 'ENCFF582IOZ.fastq.gz'
    trimmed_fastq = test_output_path + 'ENCLB637LZP_R2_val_2.fq.gz'


@pytest.mark.pairedend
def test_trim_report_pairedend():
    trimmed_fastq_report = test_output_path + \
                            'ENCLB637LZP_R2.fastq.gz_trimming_report.txt'
    assert os.path.getsize(raw_fastq) != os.path.getsize(trimmed_fastq)
    assert os.path.getsize(trimmed_fastq) == 2229312710
    assert 'Trimming mode: paired-end' in open(trimmed_fastq_report).readlines()[4]
