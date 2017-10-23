#!/usr/bin/env python3

import pytest
import os

test_output_path = os.path.dirname(os.path.abspath(__file__)) + \
                '/../output/convertReads/'


def test_convert_reads_singleend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCFF646LXU.tagAlign.gz'))
    assert os.path.exists(os.path.join(test_output_path, 'ENCFF646LXU.bedse.gz'))


def test_map_qc_pairedend():
    # Do the same thing for paired end data
    # Also check that bedpe exists
    pass
