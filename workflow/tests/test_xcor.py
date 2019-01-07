#!/usr/bin/env python3

import pytest
import os
import pandas as pd

test_output_path = os.path.dirname(os.path.abspath(__file__)) + \
                '/../output/crossReads/'


@pytest.mark.singleend
def test_map_qc_singleend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCFF833BLU.cc.plot.pdf'))
    qc_file = os.path.join(test_output_path,"ENCFF833BLU.cc.qc")
    df_xcor = pd.read_csv(qc_file, sep="\t", header=None)
    assert df_xcor[2].iloc[0] == '190,200,210'
    assert df_xcor[8].iloc[0] == 1.025906
    assert df_xcor[9].iloc[0] == 1.139671


@pytest.mark.pairedend
def test_map_qc_pairedend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCLB568IYX.cc.plot.pdf'))
    qc_file = os.path.join(test_output_path,"ENCLB568IYX.cc.qc")
    df_xcor = pd.read_csv(qc_file, sep="\t", header=None)
    assert df_xcor[2].iloc[0] == '210,220,475'
    assert df_xcor[8].iloc[0] == 1.062032
    assert df_xcor[9].iloc[0] == 3.737722
