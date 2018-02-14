#!/usr/bin/env python3

import pytest
import os

test_output_path = os.path.dirname(os.path.abspath(__file__)) + \
                '/../output/convertReads/'


@pytest.mark.acceptance
def test_convert_reads_singleend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCFF646LXU.filt.nodup.tagAlign.gz'))
    assert os.path.exists(os.path.join(test_output_path, 'ENCFF646LXU.filt.nodup.bedse.gz'))


@pytest.mark.integration
def test_map_qc_pairedend():
    # Do the same thing for paired end data
    # Also check that bedpe exists
    pass
