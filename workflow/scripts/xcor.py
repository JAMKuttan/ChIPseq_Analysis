#!/usr/bin/env python3

#
# * --------------------------------------------------------------------------
# * Licensed under MIT (https://git.biohpc.swmed.edu/BICF/Astrocyte/chipseq_analysis/LICENSE.md)
# * --------------------------------------------------------------------------
#

'''Compute cross-correlation analysis.'''

import os
import argparse
import shutil
import subprocess
import logging
from multiprocessing import cpu_count
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
STRIP_EXTENSIONS = ['.gz', '.tagAlign', '.bedse', '.bedpe']


def get_args():
    '''Define arguments.'''

    parser = argparse.ArgumentParser(
        description=__doc__, epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-t', '--tag',
                        help="The tagAlign file to qc on.",
                        required=True)

    parser.add_argument('-p', '--paired',
                        help="True/False if paired-end or single end.",
                        default=False,
                        action='store_true')

    args = parser.parse_args()
    return args

# Functions


def check_tools():
    '''Checks for required componenets on user system'''

    logger.info('Checking for required libraries and components on this system')

    r_path = shutil.which("R")
    if r_path:
        logger.info('Found R: %s', r_path)

        # Get Version
        r_version_command = "R --version"
        r_version = subprocess.check_output(r_version_command, shell=True)

        # Write to file
        r_file = open("version_r.txt", "wb")
        r_file.write(r_version)
        r_file.close()
    else:
        logger.error('Missing R')
        raise Exception('Missing R')

    phantompeak_path = shutil.which("run_spp.R")
    if phantompeak_path:
        logger.info('Found phantompeak: %s', phantompeak_path)

        # Get Version
        spp_version_command = "R -e \"packageVersion('spp')\""
        spp_version = subprocess.check_output(spp_version_command, shell=True)

        # Write to file
        spp_file = open("version_spp.txt", "wb")
        spp_file.write(spp_version)
        spp_file.close()
    else:
        logger.error('Missing phantompeak')
        raise Exception('Missing phantompeak')


def xcor(tag, paired):
    '''Use spp to calculate cross-correlation stats.'''

    tag_basename = os.path.basename(utils.strip_extensions(tag, STRIP_EXTENSIONS))
    uncompressed_tag_filename = tag_basename

    # Subsample tagAlign file
    number_reads = 20000000
    subsampled_tag_filename = \
        tag_basename + ".%d.tagAlign.gz" % (number_reads/1000000)

    tag_extended = 'cat.tagAlign.gz'
    out, err = utils.run_pipe([
        "zcat %s %s %s" %
        (tag, tag, tag)
    ], outfile=tag_extended)

    steps = [
        'zcat %s' % (tag),
        'grep -v "chrM"',
        'shuf -n %d --random-source=%s' % (number_reads, tag_extended)]

    if paired:
        steps.extend([r"""awk 'BEGIN{OFS="\t"}{$4="N";$5="1000";print $0}'"""])

    steps.extend(['gzip -nc'])

    out, err = utils.run_pipe(steps, outfile=subsampled_tag_filename)

    # Calculate Cross-correlation QC scores
    cc_scores_filename = tag_basename + ".cc.qc"
    cc_plot_filename = tag_basename + ".cc.plot.pdf"

    # CC_SCORE FILE format
    # Filename <tab>
    # numReads <tab>
    # estFragLen <tab>
    # corr_estFragLen <tab>
    # PhantomPeak <tab>
    # corr_phantomPeak <tab>
    # argmin_corr <tab>
    # min_corr <tab>
    # phantomPeakCoef <tab>
    # relPhantomPeakCoef <tab>
    # QualityTag

    run_spp_command = shutil.which("run_spp.R")
    out, err = utils.run_pipe([
        "Rscript %s -c=%s -p=%d -filtchr=chrM -savp=%s -out=%s" %
        (run_spp_command, subsampled_tag_filename, cpu_count(),
         cc_plot_filename, cc_scores_filename)
    ])

    return cc_scores_filename


def main():
    args = get_args()
    paired = args.paired
    tag = args.tag

    # Create a file handler
    handler = logging.FileHandler('xcor.log')
    logger.addHandler(handler)

    # Check if tools are present
    check_tools()

    # Calculate Cross-correlation
    xcor(tag, paired)


if __name__ == '__main__':
    main()
