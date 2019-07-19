#!/usr/bin/env python3

import pytest
import os
import utils

test_output_path = os.path.dirname(os.path.abspath(__file__)) + \
                '/../output/experimentQC/'


@pytest.mark.singleend
def test_plot_singleend():
    assert os.path.exists(os.path.join(test_output_path, 'plotProfile.png'))


@pytest.mark.pairedend
def test_plot_pairedend():
    assert os.path.exists(os.path.join(test_output_path, 'computeMatrix.gz'))
