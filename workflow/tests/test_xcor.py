#!/usr/bin/env python3

import pytest
import os
import pandas as pd

test_output_path = os.path.dirname(os.path.abspath(__file__)) + \
                '/../output/crossReads/'


@pytest.mark.singleend
def test_cross_plot_singleend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCSR238SGC/ENCLB144FDT.cc.plot.pdf'))


@pytest.mark.singleend
def test_cross_qc_singleend():
    qc_file = os.path.join(test_output_path,"ENCSR238SGC/ENCLB144FDT.cc.qc")
    df_xcor = pd.read_csv(qc_file, sep="\t", header=None)
    assert df_xcor[2].iloc[0] == '190,200,210'
    assert df_xcor[8].iloc[0] == 1.025906
    assert round(df_xcor[9].iloc[0], 6) == 1.139671


@pytest.mark.pairedend
def test_cross_qc_pairedend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCSR729LGA/ENCLB568IYX.cc.plot.pdf'))


@pytest.mark.pairedend
def test_cross_plot_pairedend():
    qc_file = os.path.join(test_output_path,"ENCSR729LGA/ENCLB568IYX.cc.qc")
    df_xcor = pd.read_csv(qc_file, sep="\t", header=None)
    assert df_xcor[2].iloc[0] == '220,430,475'
    assert round(df_xcor[8].iloc[0],6) == 1.060018
    assert df_xcor[9].iloc[0] == 4.099357
