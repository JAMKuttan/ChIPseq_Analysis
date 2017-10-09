#!/usr/bin/env python3

import pytest
import os


def test_map_reads_singleend():
    aligned_reads_report = os.path.dirname(os.path.abspath(__file__)) + \
                '/../output/alignReads/ENCFF646LXU.srt.bam.flagstat.qc'
    samtools_report = open(aligned_reads_report).readlines()
    assert '80795025' in samtools_report[1]
    assert '80050072' in samtools_report[5]


def test_map_reads_pairedend():
    # Do the same thing for paired end data
    pass
