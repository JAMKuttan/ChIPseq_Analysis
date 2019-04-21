#!/usr/bin/env python3

'''Call Motifs on called peaks.'''

import os
import argparse
import logging
import shutil
import subprocess
from multiprocessing import Pool
import pandas as pd
import utils


EPILOG = '''
For more details:
        %(prog)s --help
'''

# SETTINGS

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.propagate = False
logger.setLevel(logging.INFO)


# the order of this list is important.
# strip_extensions strips from the right inward, so
# the expected right-most extensions should appear first (like .gz)
# Modified from J. Seth Strattan
STRIP_EXTENSIONS = ['.narrowPeak', '.replicated']


def get_args():
    '''Define arguments.'''

    parser = argparse.ArgumentParser(
        description=__doc__, epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-d', '--design',
                        help="The design file to run motif search.",
                        required=True)

    parser.add_argument('-g', '--genome',
                        help="The genome FASTA file.",
                        required=True)

    parser.add_argument('-p', '--peak',
                        help="The number of peaks to use.",
                        required=True)

    args = parser.parse_args()
    return args

# Functions


def check_tools():
    '''Checks for required componenets on user system'''

    logger.info('Checking for required libraries and components on this system')

    meme_path = shutil.which("meme")
    if meme_path:
        logger.info('Found meme: %s', meme_path)

        # Get Version
        memechip_version_command = "meme-chip --version"
        memechip_version = subprocess.check_output(memechip_version_command, shell=True)

        # Write to file
        meme_file = open("version_memechip.txt", "wb")
        meme_file.write(b"Version %s" % (memechip_version))
        meme_file.close()
    else:
        logger.error('Missing meme')
        raise Exception('Missing meme')

    bedtools_path = shutil.which("bedtools")
    if bedtools_path:
        logger.info('Found bedtools: %s', bedtools_path)

        # Get Version
        bedtools_version_command = "bedtools --version"
        bedtools_version = subprocess.check_output(bedtools_version_command, shell=True)

        # Write to file
        bedtools_file = open("version_bedtools.txt", "wb")
        bedtools_file.write(bedtools_version)
        bedtools_file.close()
    else:
        logger.error('Missing bedtools')
        raise Exception('Missing bedtools')


def run_wrapper(args):
    motif_search(*args)


def motif_search(filename, genome, experiment, peak):
    '''Run motif serach on peaks.'''

    file_basename = os.path.basename(
        utils.strip_extensions(filename, STRIP_EXTENSIONS))

    out_fa = '%s.fa' % (experiment)
    out_motif = '%s_memechip' % (experiment)

    # Sort Bed file and limit number of peaks
    if peak == -1:
        peak = utils.count_lines(filename)
        peak_no = 'all'
    else:
        peak_no = peak

    sorted_fn = '%s.%s.narrowPeak' % (file_basename, peak_no)

    out, err = utils.run_pipe([
        'sort -k %dgr,%dgr %s' % (5, 5, filename),
        'head -n %s' % (peak)], outfile=sorted_fn)

    # Get fasta file
    out, err = utils.run_pipe([
        'bedtools getfasta -fi %s -bed %s -fo %s' % (genome, sorted_fn, out_fa)])

    if err:
        logger.error("bedtools error: %s", err)

    # Call memechip
    out, err = utils.run_pipe([
        'meme-chip -oc %s -meme-minw 5 -meme-maxw 15 -meme-nmotifs 10 %s -norand' % (out_motif, out_fa)])
    if err:
        logger.error("meme-chip error: %s", err)


def main():
    args = get_args()
    design = args.design
    genome = args.genome
    peak = args.peak

    # Create a file handler
    handler = logging.FileHandler('motif.log')
    logger.addHandler(handler)

    # Check if tools are present
    check_tools()

    # Read files
    design_df = pd.read_csv(design, sep='\t')

    meme_arglist = zip(design_df['Peaks'].tolist(), [genome]*design_df.shape[0], design_df['Condition'].tolist(), [peak]*design_df.shape[0])
    work_pool = Pool(min(12, design_df.shape[0]))
    return_list = work_pool.map(run_wrapper, meme_arglist)
    work_pool.close()
    work_pool.join()


if __name__ == '__main__':
    main()
