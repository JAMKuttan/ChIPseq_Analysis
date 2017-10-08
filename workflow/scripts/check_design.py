#!/usr/bin/env python3

'''Check if design file is correctly formatted and matches files list.'''

import argparse
import logging
import pandas as pd

EPILOG = '''
For more details:
        %(prog)s --help
'''

# SETTINGS

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.propagate = False
logger.setLevel(logging.INFO)


def get_args():
    '''Define arguments.'''
    parser = argparse.ArgumentParser(
        description=__doc__, epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-d', '--design',
                        help="The design file to run QC (TSV format).",
                        required=True)

    parser.add_argument('-f', '--fastq',
                        help="File with list of fastq files (csv format).",
                        required=True)

    parser.add_argument('-p', '--paired',
                        help="True/False if paired-end or single end.",
                        default=False,
                        action='store_true')

    args = parser.parse_args()
    return args


def check_design_headers(design, paired):
    '''Check if design file conforms to sequencing type.'''

    # Default headers
    design_template = [
        'sample_id',
        'biosample',
        'factor',
        'treatment',
        'replicate',
        'control_id',
        'fastq_read1']

    design_headers = list(design.columns.values)

    if paired:  # paired-end data
        design_template.extend(['fastq_read2'])

    # Check if headers
    logger.info("Running header check.")

    missing_headers = set(design_template) - set(design_headers)

    if len(missing_headers) > 0:
        logger.error('Missing column headers: %s', list(missing_headers))
        raise Exception("Missing column headers: %s" % list(missing_headers))


def check_controls(design):
    '''Check if design file has the correct control mapping.'''

    logger.info("Running control check.")

    missing_controls = set(design['control_id']) - set(design['sample_id'])

    if len(missing_controls) > 0:
        logger.error('Missing control experiments: %s', list(missing_controls))
        raise Exception("Missing control experiments: %s" %
                        list(missing_controls))


def check_files(design, fastq, paired):
    '''Check if design file has the files found.'''

    logger.info("Running file check.")

    if paired:  # paired-end data
        files = list(design['fastq_read1']) + list(design['fastq_read2'])
    else:  # single-end data
        files = design['fastq_read1']

    files_found = fastq['name']

    missing_files = set(files) - set(files_found)

    if len(missing_files) > 0:
        logger.error('Missing files from design file: %s', list(missing_files))
        raise Exception("Missing files from design file: %s" %
                        list(missing_files))
    else:
        file_dict = fastq.set_index('name').T.to_dict()

        design['fastq_read1'] = design['fastq_read1'] \
                                .apply(lambda x: file_dict[x]['path'])
        if paired:  # paired-end data
            design['fastq_read2'] = design['fastq_read2'] \
                                    .apply(lambda x: file_dict[x]['path'])
    return design


def main():
    args = get_args()

    # Create a file handler
    handler = logging.FileHandler('design.log')
    logger.addHandler(handler)

    # Read files
    design_file = pd.read_csv(args.design, sep='\t')
    fastq_file = pd.read_csv(args.fastq, sep='\t', names=['name', 'path'])

    # Check design file
    check_design_headers(design_file, args.paired)
    check_controls(design_file)
    new_design = check_files(design_file, fastq_file, args.paired)

    # Write out new design file
    new_design.to_csv('design.tsv', header=True, sep='\t', index=False)


if __name__ == '__main__':
    main()
