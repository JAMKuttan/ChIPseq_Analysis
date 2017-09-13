#!/usr/bin/env python3
# -*- coding: latin-1 -*-
'''QC check of raw .fastq files using FASTQC.'''

import os
import subprocess
import argparse
import shutil
import logging
import sys
import json

EPILOG = '''
For more details:
        %(prog)s --help
'''

## SETTINGS

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())
LOGGER.propagate = False
LOGGER.setLevel(logging.INFO)


def check_tools():
    '''Checks for required componenets on user system'''

    LOGGER.info('Checking for required libraries and components on this system')

    fastqc_path = shutil.which("fastqc")
    if fastqc_path:
        LOGGER.info('Found fastqc: %s', fastqc_path)
    else:
        print("Please install 'fastqc' before using the tool")
        sys.exit()


def get_args():
    '''Define arguments.'''
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

    LOGGER.info("Running fastqc with %s", qc_command)

    qual_fastq = subprocess.Popen(qc_command, shell=True)
    qual_fastq .communicate()


def main():
    args = get_args()

    # Create a file handler
    handler = logging.FileHandler('qc.log')
    LOGGER.addHandler(handler)

    # Check if tools are present
    check_tools()

    # Run quality checks
    check_qual_fastq(args.fastq)


if __name__ == '__main__':
    main()
