#!/usr/bin/env python3

import pytest
import os
import utils
import yaml

test_output_path = os.path.dirname(os.path.abspath(__file__)) + \
                '/../output/multiqcReport/'


@pytest.mark.singleend
def test_software_references():
    assert os.path.exists(os.path.join(test_output_path, 'software_references_mqc.txt'))
