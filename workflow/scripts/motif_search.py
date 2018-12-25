#!/usr/bin/env python3

'''Call Motifs on called peaks.'''


import sys
import re
from re import sub
import string
import argparse
import logging
import subprocess
import pandas as pd
import utils
from multiprocessing import Pool

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
                        help="The design file to run motif search.",
                        required=True)

    parser.add_argument('-g', '--genome',
                        help="The genome FASTA file.",
                        required=True)

    args = parser.parse_args()
    return args

# Functions

def run_wrapper(args):
  motif_search(*args)

def motif_search(filename, genome, experiment):
    sorted_fn = 'sorted-%s' % (filename)
    out_fa = '%s.fa' % (experiment)
    out_motif = '%s_memechip' % (experiment)

    # Sort Bed file by
    out, err = run_pipe([
        'sort -k %dgr,%dgr %s' % (5, 5, filename)],
        outfile=sorted_fn)

    # Get fasta file
    out, err = utils.run_pipe([
        '"bedtools getfasta -fi %s -bed %s -fo %s' % (genome, sorted_fn, out_fa)])

    #Call memechip
    out, err = utils.run_pipe([
        '"meme-chip -oc %s -meme-minw 5 -meme-maxw 15 -meme-nmotifs 10 %s -meme-norand' % (out_motif, out_fa)])

def main():
    args = get_args()
    design = args.design
    genome = args.genome

    # Read files
    design_df = pd.read_csv(design, sep='\t')

    meme_arglist =  zip(design_df['Peaks'].tolist(),[genome]*design_df.shape[0],design_df['Experiment'].tolist())
    work_pool = Pool(min(12,design_df.shape[0]))
    return_list =  work_pool.map(run_wrapper, meme_arglist)
    work_pool.close()
    work_pool.join()

if __name__=="__main__":
  main()
