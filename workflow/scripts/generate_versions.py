#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# * --------------------------------------------------------------------------
# * Licensed under MIT (https://git.biohpc.swmed.edu/BICF/Astrocyte/chipseq_analysis/LICENSE.md)
# * --------------------------------------------------------------------------
#

'''Make YAML of software versions.'''

from __future__ import print_function
from collections import OrderedDict
import re
import os
import logging
import glob
import argparse
import numpy as np

EPILOG = '''
For more details:
        %(prog)s --help
'''

# SETTINGS

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.propagate = False
logger.setLevel(logging.INFO)

SOFTWARE_REGEX = {
    'Nextflow': ['version_nextflow.txt', r"(\S+)"],
    'Trim Galore!': ['trimReads_vf/version_trimgalore.txt', r"version (\S+)"],
    'Cutadapt': ['trimReads_vf/version_cutadapt.txt', r"Version (\S+)"],
    'BWA': ['alignReads_vf/version_bwa.txt', r"Version: (\S+)"],
    'Samtools': ['alignReads_vf/version_samtools.txt', r"samtools (\S+)"],
    'Sambamba': ['filterReads_vf/version_sambamba.txt', r"sambamba (\S+)"],
    'BEDTools': ['convertReads_vf/version_bedtools.txt', r"bedtools v(\S+)"],
    'R': ['crossReads_vf/version_r.txt', r"R version (\S+)"],
    'SPP': ['crossReads_vf/version_spp.txt', r"\[1\] ‘(1.14)’"],
    'MACS2': ['callPeaksMACS_vf/version_macs.txt', r"macs2 (\S+)"],
    'bedGraphToBigWig': ['callPeaksMACS_vf/version_bedGraphToBigWig.txt', r"bedGraphToBigWig v (\S+)"],
    'ChIPseeker': ['peakAnnotation_vf/version_ChIPseeker.txt', r"Version (\S+)\""],
    'MEME-ChIP': ['motifSearch_vf/version_memechip.txt', r"Version (\S+)"],
    'DiffBind': ['diffPeaks_vf/version_DiffBind.txt', r"Version (\S+)\""],
    'deepTools': ['experimentQC_vf/version_deeptools.txt', r"deeptools (\S+)"],
    'MultiQC': ['version_multiqc.txt', r"multiqc, version (\S+)"],
}


def get_args():
    '''Define arguments.'''

    parser = argparse.ArgumentParser(
        description=__doc__, epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-o', '--output',
                        help="The out file name.",
                        required=True)

    parser.add_argument('-t', '--test',
                        help='Used for testing purposes',
                        default=False,
                        action='store_true')

    args = parser.parse_args()
    return args


def check_files(files, test):
    '''Check if version files are found.'''

    logger.info("Running file check.")

    software_files = np.array(list(SOFTWARE_REGEX.values()))[:,0]

    extra_files =  set(files) - set(software_files)

    if len(extra_files) > 0 and test:
            logger.error('Missing regex: %s', list(extra_files))
            raise Exception("Missing regex: %s" % list(extra_files))


def main():
    args = get_args()
    output = args.output
    test = args.test

    out_filename = output + '_mqc.yaml'

    results = OrderedDict()
    results['Nextflow'] = '<span style="color:#999999;\">Not Run</span>'
    results['Trim Galore!'] = '<span style="color:#999999;\">Not Run</span>'
    results['Cutadapt'] = '<span style="color:#999999;\">Not Run</span>'
    results['BWA'] = '<span style="color:#999999;\">Not Run</span>'
    results['Samtools'] = '<span style="color:#999999;\">Not Run</span>'
    results['Sambamba'] = '<span style="color:#999999;\">Not Run</span>'
    results['BEDTools'] = '<span style="color:#999999;\">Not Run</span>'
    results['R'] = '<span style="color:#999999;\">Not Run</span>'
    results['SPP'] = '<span style="color:#999999;\">Not Run</span>'
    results['MACS2'] = '<span style="color:#999999;\">Not Run</span>'
    results['bedGraphToBigWig'] = '<span style="color:#999999;\">Not Run</span>'
    results['ChIPseeker'] = '<span style="color:#999999;\">Not Run</span>'
    results['MEME-ChIP'] = '<span style="color:#999999;\">Not Run</span>'
    results['DiffBind'] = '<span style="color:#999999;\">Not Run</span>'
    results['deepTools'] = '<span style="color:#999999;\">Not Run</span>'
    results['MultiQC'] = '<span style="color:#999999;\">Not Run</span>'

    # list all files
    files = glob.glob('**/*.txt', recursive=True)

    # Check for version files:
    check_files(files, test)

    # Search each file using its regex
    for k, v in SOFTWARE_REGEX.items():
        if os.path.isfile(v[0]):
            with open(v[0]) as x:
                versions = x.read()
                match = re.search(v[1], versions)
                if match:
                    results[k] = "v{}".format(match.group(1))

    # Dump to YAML
    print(
        '''
        id: 'Software Versions'
        section_name: 'Software Versions'
        section_href: 'https://git.biohpc.swmed.edu/BICF/Astrocyte/chipseq_analysis/'
        plot_type: 'html'
        description: 'are collected at run time from the software output.'
        data: |
            <dl class="dl-horizontal">
        '''
    , file = open(out_filename, "w"))

    for k, v in results.items():
        print("            <dt>{}</dt><dd>{}</dd>".format(k, v), file = open(out_filename, "a"))
    print("            </dl>", file = open(out_filename, "a"))


if __name__ == '__main__':
    main()
