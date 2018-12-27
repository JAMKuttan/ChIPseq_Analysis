#!/usr/bin/env python3

import pytest
import os
import pandas as pd

test_output_path = os.path.dirname(os.path.abspath(__file__)) + \
                '/../output/crossReads/'


@pytest.mark.singleend
def test_convert_reads_singleend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCFF833BLU.filt.nodup.tagAlign.15.tagAlign.gz.cc.plot.pdf'))
    qc_file = os.path.join(test_output_path,"ENCFF833BLU.filt.nodup.tagAlign.15.tagAlign.gz.cc.qc")
    df_xcor = pd.read_csv(qc_file, sep="\t", header=None)
    assert df_xcor[2].iloc[0] == '195,215,230'
    assert df_xcor[8].iloc[0] == 1.024836
    assert df_xcor[9].iloc[0] == 1.266678


@pytest.mark.pairedend
def test_map_qc_pairedend():
    assert os.path.exists(os.path.join(test_output_path, 'ENCFF582IOZ_val_2ENCFF957SQS_val_1.filt.nodup.tagAlign.15.tagAlign.gz.cc.plot.pdf'))
    qc_file = os.path.join(test_output_path,"ENCFF582IOZ_val_2ENCFF957SQS_val_1.filt.nodup.tagAlign.15.tagAlign.gz.cc.qc")
    df_xcor = pd.read_csv(qc_file, sep="\t", header=None)
    assert df_xcor[2].iloc[0] == '205,410,430'
    assert df_xcor[8].iloc[0] == 1.060266
    assert df_xcor[9].iloc[0] == 4.308793
