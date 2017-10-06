#!/usr/bin/env python3

'''Align reads to reference genome.'''

import os
import subprocess
import argparse
import shutil
import shlex
import logging
import sys
from multiprocessing import cpu_count
import json
import utils

EPILOG = '''
For more details:
        %(prog)s --help
'''

## SETTINGS

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.propagate = False
logger.setLevel(logging.INFO)

# the order of this list is important.
# strip_extensions strips from the right inward, so
# the expected right-most extensions should appear first (like .gz)
# Modified from J. Seth Strattan
STRIP_EXTENSIONS = ['.gz', '.fq', '.fastq', '_trimmed']


def get_args():
    '''Define arguments.'''
    parser = argparse.ArgumentParser(
        description=__doc__, epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-f', '--fastq',
                        help="The fastq file to run triming on.",
                        nargs='+',
                        required=True)

    parser.add_argument('-r', '--reference',
                        help="The bwa index of the reference genome.",
                        required=True)

    parser.add_argument('-p', '--paired',
                        help="True/False if paired-end or single end.",
                        default=False,
                        action='store_true')

    args = parser.parse_args()
    return args



## Functions

def strip_extensions(filename, extensions):
    '''Strips extensions to get basename of file.'''

    basename = filename
    for extension in extensions:
        basename = basename.rpartition(extension)[0] or basename

    return basename


def check_tools():
    '''Checks for required componenets on user system'''

    logger.info('Checking for required libraries and components on this system')

    bwa_path = shutil.which("bwa")
    if bwa_path:
        logger.info('Found bwa: %s', bwa_path)
    else:
        logger.error('Missing bwa')
        raise Exception('Missing bwa')

    samtools_path = shutil.which("samtools")
    if samtools_path:
        logger.info('Found samtools: %s', samtools_path)
    else:
        logger.error('Missing samtools')
        raise Exception('Missing samtools')


def generate_sa(fastq, reference):
    '''Use BWA to generate Suffix Arrays.'''

    fastq_basename = os.path.basename(strip_extensions(fastq, STRIP_EXTENSIONS))

    bwa_aln_params = '-q 5 -l 32 -k 2'

    sai = '%s.sai' % (fastq_basename)
    with open(sai, 'w') as sai_file:
        bwa_command = "bwa aln %s -t %d %s %s" \
                % (bwa_aln_params, cpu_count(),
                   reference, fastq_basename)

        logger.info("Running bwa with %s", bwa_command)
        subprocess.check_call(shlex.split(bwa_command), stdout=sai_file)

    return sai


def align_se(fastq, sai, reference, fastq_basename):
    '''Use BWA to align SE data.'''

    sam_filename = "%s.sam" % (fastq_basename)

    steps = [
        "bwa samse %s %s %s"
        % (reference, fastq[0], sai[0]),
        "samtools view -@%d -Su -" % (cpu_count()),
        "samtools sort -@%d -o %s"
        % (cpu_count(), fastq_basename)]

    out, err = utils.run_pipe(steps)
    if err:
        logger.error("samse/samtools error: %s" % (err))


def align_pe(fastq, sai, reference, fastq_basename):
    '''Use BWA to align PE data.'''

    sam_filename = "%s.sam" % (fastq_basename)
    badcigar_filename = "%s.badReads" % (fastq_basename)

    # Remove read pairs with bad CIGAR strings and sort by position
    steps = [
            "bwa sampe -P %s %s %s %s %s"
            % (reference, fastq[0], fastq[1],
               sai[0], sai[1]),
            "tee %s" % (sam_filename),
            r"""awk 'BEGIN {FS="\t" ; OFS="\t"} ! /^@/ && $6!="*" { cigar=$6; gsub("[0-9]+D","",cigar); n = split(cigar,vals,"[A-Z]"); s = 0; for (i=1;i<=n;i++) s=s+vals[i]; seqlen=length($10) ; if (s!=seqlen) print $1"\t" ; }'""",
            "sort",
            "uniq"]

    out, err = utils.run_pipe(steps, badcigar_filename)
    if err:
        logger.error("sampe error: %s" % (err))

    steps = [
        "cat %s" % (sam_filename),
        "grep -v -F -f %s" % (badcigar_filename),
        "samtools view -@%d -Su -" % (cpu_count()),
        "samtools sort -@%d -o %s"
        % (cpu_count(), fastq_basename)]

    out, err = utils.run_pipe(steps)
    if err:
        logger.error("samtools error: %s" % (err))


def main():
    args = get_args()

    # Create a file handler
    handler = logging.FileHandler('map.log')
    logger.addHandler(handler)

    # Check if tools are present
    check_tools()

    # Run Suffix Array generation
    sai = []
    for fastq in args.fastq:
        sai_filename = generate_sa(fastq, args.reference)
        sai.append(sai_filename)

    # Run alignment for either PE or SE
    if paired: # paired-end data
        fastq_r1_basename = os.path.basename(
            strip_extensions(fastq[0], STRIP_EXTENSIONS))
        fastq_r2_basename = os.path.basename(
            strip_extensions(fastq[1], STRIP_EXTENSIONS))
        fastq_basename = fastq_r1_basename + fastq_r2_basename

        align_pe(fastq, sai, fastq_basename)

    else:
        fastq_basename = os.path.basename(
            strip_extensions(fastq[0], STRIP_EXTENSIONS))

        align_se(fastq, sai, fastq_basename)

    bam_mapstats_filename = '%s.raw.srt.bam.flagstat.qc' % (fastq_basename)
    with open(raw_bam_mapstats_filename, 'w') as fh:
        subprocess.check_call(
            shlex.split("%s flagstat %s" % (samtools, bam_mapstats_filename)),
            stdout=fh)

    # Remove sai files
    for sai_file in sai:
        os.remove(sai_file)


if __name__ == '__main__':
    main()
