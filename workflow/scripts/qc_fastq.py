#!/usr/bin/env python3
# -*- coding: latin-1 -*-
'''QC check of raw .fastq files using FASTQC.'''

import os
import subprocess
import argparse
import shlex
import shutil
from multiprocessing import cpu_count
import logging
import sys
import json

EPILOG = '''
For more details:
        %(prog)s --help
'''

## SETTINGS

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.propagate = False
logger.setLevel(logging.INFO)


def check_tools():
    '''Checks for required componenets on user system'''

    logger.info('Checking for required libraries and components on this system')

    fastqc_path = shutil.which("fastqc")
    if fastqc_path:
        logger.info('Found fastqc:%s' % (fastqc_path))
    else:
        print("Please install 'fastqc' before using the tool")
        sys.exit()


def get_args():
    parser = argparse.ArgumentParser(
        description=__doc__, epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-f', '--fastq',
        help="The fastq file to run QC check on.",
        nargs='+',
        required=True)

    args = parser.parse_args()
    return args


def check_qual_fastq(fastq):
    '''Run fastqc on 1 or 2 files.'''
    qc_command = "fastqc -t -f fastq " + " ".join(fastq)

    logger.info("Running fastqc with %s" % (qc_command))

    p = subprocess.Popen(qc_command, shell=True)
    p.communicate()


def main():
    args = get_args()

    # create a file handler
    handler = logging.FileHandler('qc.log')
    logger.addHandler(handler)

    check_qual_fastq(args.fastq)


if __name__ == '__main__':
    main()
