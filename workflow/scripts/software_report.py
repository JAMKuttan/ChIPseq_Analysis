#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''Make YAML of software versions.'''

from __future__ import print_function
from collections import OrderedDict
import re

software_regex = {
    'Trim Galore!': ['version_trimgalore.txt', r"version (\S+)"],
    'Cutadapt': ['version_cutadapt.txt', r"Version (\S+)"],
    'BWA': ['version_bwa.txt', r"Version: (\S+)"],
    'Samtools': ['version_samtools.txt', r"samtools (\S+)"],
    'Sambamba': ['version_sambamba.txt', r"sambamba (\S+)"],
    'BEDTools': ['version_bedtools.txt', r"bedtools v(\S+)"],
    'R': ['version_r.txt', r"R version (\S+)"],
    'SPP': ['version_spp.txt', r"\[1\] ‘(1.14)’"],
    'MACS2': ['version_macs.txt', r"macs2 (\S+)"],
    'bedGraphToBigWig': ['version_bedGraphToBigWig.txt', r"bedGraphToBigWig v (\S+)"],
    'ChIPseeker': ['version_ChIPseeker.txt', r"Version (\S+)\""],
    'MEME-ChIP': ['version_memechip.txt', r"Version (\S+)"],
    'DiffBind': ['version_DiffBind.txt', r"Version (\S+)\""],
    'deepTools': ['version_deeptools.txt', r"deeptools (\S+)"],
}

results = OrderedDict()
results['Trim Galore!'] = '<span style="color:#999999;\">N/A</span>'
results['Cutadapt'] = '<span style="color:#999999;\">N/A</span>'
results['BWA'] = '<span style="color:#999999;\">N/A</span>'
results['Trim Galore!'] = '<span style="color:#999999;\">N/A</span>'
results['Cutadapt'] = '<span style="color:#999999;\">N/A</span>'
results['BWA'] = '<span style="color:#999999;\">N/A</span>'
results['Samtools'] = '<span style="color:#999999;\">N/A</span>'
results['Sambamba'] = '<span style="color:#999999;\">N/A</span>'
results['BEDTools'] = '<span style="color:#999999;\">N/A</span>'
results['R'] = '<span style="color:#999999;\">N/A</span>'
results['SPP'] = '<span style="color:#999999;\">N/A</span>'
results['MACS2'] = '<span style="color:#999999;\">N/A</span>'
results['bedGraphToBigWig'] = '<span style="color:#999999;\">N/A</span>'
results['ChIPseeker'] = '<span style="color:#999999;\">N/A</span>'
results['MEME-ChIP'] = '<span style="color:#999999;\">N/A</span>'
results['DiffBind'] = '<span style="color:#999999;\">N/A</span>'
results['deepTools'] = '<span style="color:#999999;\">N/A</span>'

# Search each file using its regex
for k, v in software_regex.items():
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
)
for k, v in results.items():
    print("        <dt>{}</dt><dd>{}</dd>".format(k, v))
print("        </dl>")
