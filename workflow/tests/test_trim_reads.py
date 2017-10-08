#!/usr/bin/env python3

import pytest
import os
import gzip


def test_trim_reads_singleend():
    # assert os.path.getsize('sample1_R1.fastq.gz') != os.path.getsize('sample1_R1.trim.fastq.gz')
    # check the size of the lines using
    # a = sum(1 for _ in gzip.open('input_2.small_R1.fastq.gz'))
    pass


def test_trim_reads_pairedend():
    # Do the same thing for paired end data
    pass
