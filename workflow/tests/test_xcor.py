#!/usr/bin/env python3

import pytest
import os
import pandas as pd

test_output_path = os.path.dirname(os.path.abspath(__file__)) + \
                '/../output/crossReads/'


@pytest.mark.singleend
def test_cross_plot_singleend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCLB144FDT/ENCLB144FDT.cc.plot.pdf'))


@pytest.mark.singleend
def test_cross_qc_singleend():
    qc_file = os.path.join(test_output_path,"ENCLB144FDT/ENCLB144FDT.cc.qc")
    df_xcor = pd.read_csv(qc_file, sep="\t", header=None)
    assert df_xcor[2].iloc[0] == '185,195,205'
    assert df_xcor[8].iloc[0] == 1.02454
    assert df_xcor[9].iloc[0] == 0.8098014


@pytest.mark.pairedend
def test_cross_qc_pairedend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCLB568IYX/ENCLB568IYX.cc.plot.pdf'))


@pytest.mark.pairedend
def test_cross_plot_pairedend():
    qc_file = os.path.join(test_output_path,"ENCLB568IYX/ENCLB568IYX.cc.qc")
    df_xcor = pd.read_csv(qc_file, sep="\t", header=None)
    assert df_xcor[2].iloc[0] == '215,225,455'
    assert round(df_xcor[8].iloc[0],6) == 1.056201
    assert df_xcor[9].iloc[0] == 3.599357
