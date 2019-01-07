#!/usr/bin/env python3

import pytest
import os

test_output_path = os.path.dirname(os.path.abspath(__file__)) + \
                '/../output/convertReads/'


@pytest.mark.singleend
def test_convert_reads_singleend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCFF646LXU.tagAlign.gz'))
    assert os.path.exists(os.path.join(test_output_path, 'ENCFF646LXU.bedse.gz'))


@pytest.mark.pairedend
def test_map_qc_pairedend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCLB568IYX.tagAlign.gz'))
    assert os.path.exists(os.path.join(test_output_path, 'ENCLB568IYX.bedpe.gz'))
