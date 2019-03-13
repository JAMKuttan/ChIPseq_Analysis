#!/usr/bin/env python3

import pytest
import os

test_output_path = os.path.dirname(os.path.abspath(__file__)) + \
                '/../output/convertReads/'


@pytest.mark.singleend
def test_tag_reads_singleend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCSR238SGC/ENCLB831RUI.tagAlign.gz'))


@pytest.mark.singleend
def test_bed_reads_singleend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCSR238SGC/ENCLB831RUI.bedse.gz'))


@pytest.mark.pairedend
def test_tag_reads_pairedend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCSR729LGA/ENCLB568IYX.tagAlign.gz'))


@pytest.mark.pairedend
def test_bed_reads_pairedend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCSR729LGA/ENCLB568IYX.bedpe.gz'))
