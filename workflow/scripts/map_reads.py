#!/usr/bin/env python3

#
# * --------------------------------------------------------------------------
# * Licensed under MIT (https://git.biohpc.swmed.edu/BICF/Astrocyte/chipseq_analysis/LICENSE.md)
# * --------------------------------------------------------------------------
#

'''Align reads to reference genome.'''

import os
import subprocess
import argparse
import shutil
import shlex
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

    parser.add_argument('-s', '--sample',
                        help="The name of the sample.",
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

    bwa_path = shutil.which("bwa")
    if bwa_path:
        logger.info('Found bwa: %s', bwa_path)

        # Get Version
        bwa_version_command = "bwa"
        try:
            subprocess.check_output(bwa_version_command, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            bwa_version = e.output

        # Write to file
        bwa_file = open("version_bwa.txt", "wb")
        bwa_file.write(bwa_version)
        bwa_file.close()
    else:
        logger.error('Missing bwa')
        raise Exception('Missing bwa')

    samtools_path = shutil.which("samtools")
    if samtools_path:
        logger.info('Found samtools: %s', samtools_path)

        # Get Version
        samtools_version_command = "samtools --version"
        samtools_version = subprocess.check_output(samtools_version_command, shell=True)

        # Write to file
        samtools_file = open("version_samtools.txt", "wb")
        samtools_file.write(samtools_version)
        samtools_file.close()
    else:
        logger.error('Missing samtools')
        raise Exception('Missing samtools')


def generate_sa(fastq, reference):
    '''Use BWA to generate Suffix Arrays.'''

    fastq_basename = os.path.basename(utils.strip_extensions(fastq, STRIP_EXTENSIONS))

    bwa_aln_params = '-q 5 -l 32 -k 2'

    sai = '%s.sai' % (fastq_basename)
    with open(sai, 'w') as sai_file:
        bwa_command = "bwa aln %s -t %d %s %s" \
                % (bwa_aln_params, cpu_count(),
                   reference, fastq)

        logger.info("Running bwa with %s", bwa_command)
        subprocess.check_call(shlex.split(bwa_command), stdout=sai_file)

    return sai


def align_se(fastq, sai, reference, fastq_basename):
    '''Use BWA to align SE data.'''

    bam_filename = '%s.bam' % (fastq_basename)

    steps = [
        "bwa samse %s %s %s"
        % (reference, sai[0], fastq[0]),
        "samtools view -@%d -Su -" % (cpu_count()),
        "samtools sort -@%d -o %s"
        % (cpu_count(), bam_filename)]

    out, err = utils.run_pipe(steps)
    if err:
        logger.error("samse/samtools error: %s", err)

    return bam_filename


def align_pe(fastq, sai, reference, fastq_basename):
    '''Use BWA to align PE data.'''

    sam_filename = "%s.sam" % (fastq_basename)
    badcigar_filename = "%s.badReads" % (fastq_basename)
    bam_filename = '%s.bam' % (fastq_basename)

    # Remove read pairs with bad CIGAR strings and sort by position
    steps = [
        "bwa sampe -P %s %s %s %s %s"
        % (reference, sai[0], sai[1],
           fastq[0], fastq[1]),
        "tee %s" % (sam_filename),
        r"""awk 'BEGIN {FS="\t" ; OFS="\t"} ! /^@/ && $6!="*" { cigar=$6; gsub("[0-9]+D","",cigar); n = split(cigar,vals,"[A-Z]"); s = 0; for (i=1;i<=n;i++) s=s+vals[i]; seqlen=length($10) ; if (s!=seqlen) print $1"\t" ; }'""",
        "sort",
        "uniq"]

    out, err = utils.run_pipe(steps, badcigar_filename)
    if err:
        logger.error("sampe error: %s", err)

    steps = [
        "cat %s" % (sam_filename),
        "grep -v -F -f %s" % (badcigar_filename),
        "samtools view -@%d -Su -" % (cpu_count()),
        "samtools sort -@%d -o %s"
        % (cpu_count(), bam_filename)]

    out, err = utils.run_pipe(steps)
    if err:
        logger.error("samtools error: %s", err)

    return bam_filename


def main():
    args = get_args()
    paired = args.paired
    fastq = args.fastq
    reference = args.reference
    sample = args.sample

    # Create a file handler
    handler = logging.FileHandler('map.log')
    logger.addHandler(handler)

    # Check if tools are present
    check_tools()

    # Run Suffix Array generation
    sai = []
    for fastq_file in fastq:
        sai_filename = generate_sa(fastq_file, reference)
        sai.append(sai_filename)

    # Make file basename
    fastq_basename = sample

    # Run alignment for either PE or SE
    if paired:  # paired-end data
        bam_filename = align_pe(fastq, sai, reference, fastq_basename)

    else:
        bam_filename = align_se(fastq, sai, reference, fastq_basename)

    bam_mapstats_filename = '%s.flagstat.qc' % (fastq_basename)
    with open(bam_mapstats_filename, 'w') as temp_file:
        subprocess.check_call(
            shlex.split("samtools flagstat %s" % (bam_filename)),
            stdout=temp_file)

    #Genome/Bad fastq File Check
    file_check = open(bam_mapstats_filename).readlines()
    percent = file_check[4].split('(')[1]
    percent = percent.split('%')[0]
    if float(percent) < 10:
        raise Exception ('Mapped Genes too low: Check for correct Genotype')

    # Remove sai files
    for sai_file in sai:
        os.remove(sai_file)


if __name__ == '__main__':
    main()
