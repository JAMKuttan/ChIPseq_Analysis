#!/usr/bin/env python3

import pytest
import os


def test_map_reads_singleend():
    aligned_reads_report = os.path.dirname(os.path.abspath(__file__)) + \
                '/../output/alignReads/ENCFF646LXU.srt.bam.flagstat.qc'
    samtools_report = open(aligned_reads_report).readlines()
    assert '80795025 + 0 in total' in samtools_report[0]
    assert '80050072 + 0 mapped (99.08% : N/A)' in samtools_report[4]


def test_map_reads_pairedend():
    # Do the same thing for paired end data
    pass
