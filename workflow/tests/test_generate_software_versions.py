#!/usr/bin/env python3

import pytest
import os
import utils
import yaml

test_output_path = os.path.dirname(os.path.abspath(__file__)) + \
                '/../output/multiqcReport/'


@pytest.mark.singleend
def test_software_versions():
    assert os.path.exists(os.path.join(test_output_path, 'software_versions_mqc.yaml'))


@pytest.mark.singleend
def test_software_versions_output():
    software_versions = os.path.join(test_output_path, 'software_versions_mqc.yaml')
    with open(software_versions, 'r') as stream:
        data_loaded = yaml.load(stream)

    assert  len(data_loaded['data'].split('<dt>')) == 18
