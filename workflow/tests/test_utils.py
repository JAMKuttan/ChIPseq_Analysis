#!/usr/bin/env python3

import pytest
import utils


STRIP_EXTENSIONS = ['.gz', '.fq', '.fastq', '.fa', '.fasta']


@pytest.fixture
def steps():
    steps = []
    return steps


@pytest.fixture
def steps_1(steps):
    design_file = "test_data/design_ENCSR238SGC_SE.txt"
    step = [
        "grep H3K4me1 %s " % (design_file)]
    return step


@pytest.fixture
def steps_2(steps_1):
    steps_1.extend([
        "cut -f8"
    ])
    return steps_1


def test_run_one_step(steps_1, capsys):
    check_output = 'ENCBS844FSC\tENCSR238SGC\tlimb\tH3K4me1\tNone\t1\tENCBS844FSC\tENCFF833BLU.fastq.gz'.encode('UTF-8')
    out, err = utils.run_pipe(steps_1)
    output, errors = capsys.readouterr()
    assert "first step shlex to stdout" in output
    assert check_output in out


def test_run_two_step(steps_2, capsys):
    check_output = 'ENCFF833BLU.fastq.gz\nENCFF646LXU.fastq.gz'.encode('UTF-8')
    out, err = utils.run_pipe(steps_2)
    output, errors = capsys.readouterr()
    assert "intermediate step 2 shlex to stdout" in output
    assert check_output in out


def test_run_last_step_file(steps_2, capsys, tmpdir):
    check_output = 'ENCFF833BLU.fastq.gz\nENCFF646LXU.fastq.gz'
    tmp_outfile = tmpdir.join('output.txt')
    out, err = utils.run_pipe(steps_2, tmp_outfile.strpath)
    output, errors = capsys.readouterr()
    assert "last step shlex" in output
    assert check_output in tmp_outfile.read()


def test_strip_extensions():
    filename = utils.strip_extensions('ENCFF833BLU.fastq.gz', STRIP_EXTENSIONS)
    assert filename == 'ENCFF833BLU'


def test_strip_extensions_not_valid():
    filename = utils.strip_extensions('ENCFF833BLU.not.valid', STRIP_EXTENSIONS)
    assert filename == 'ENCFF833BLU.not.valid'


def test_strip_extensions_missing_basename():
    filename = utils.strip_extensions('.fastq.gz', STRIP_EXTENSIONS)
    assert filename == '.fastq'
