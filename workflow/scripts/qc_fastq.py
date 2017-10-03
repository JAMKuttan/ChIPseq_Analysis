#!/usr/bin/env python3

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

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.propagate = False
logger.setLevel(logging.INFO)


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


def check_tools():
    '''Checks for required componenets on user system'''

    logger.info('Checking for required libraries and components on this system')

    fastqc_path = shutil.which("fastqc")
    if fastqc_path:
        logger.info('Found fastqc: %s', fastqc_path)
    else:
        logger.error('Missing fastqc')
        raise Exception('Missing fastqc')


def check_qual_fastq(fastq):
    '''Run fastqc on 1 or 2 files.'''
    qc_command = "fastqc -t -f fastq " + " ".join(fastq)

    logger.info("Running fastqc with %s", qc_command)

    qual_fastq = subprocess.Popen(qc_command, shell=True)
    out, err = qual_fastq.communicate()


def main():
    args = get_args()

    # Create a file handler
    handler = logging.FileHandler('qc.log')
    logger.addHandler(handler)

    # Check if tools are present
    check_tools()

    # Run quality checks
    check_qual_fastq(args.fastq)


if __name__ == '__main__':
    main()
