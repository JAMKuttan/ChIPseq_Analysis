#!/usr/bin/env python3

#
# * --------------------------------------------------------------------------
# * Licensed under MIT (https://git.biohpc.swmed.edu/BICF/Astrocyte/chipseq_analysis/LICENSE.md)
# * --------------------------------------------------------------------------
#

'''Generate naive overlap peak files and design file for downstream processing.'''

import os
import argparse
import logging
import shutil
import subprocess
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


def get_args():
    '''Define arguments.'''

    parser = argparse.ArgumentParser(
        description=__doc__, epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-d', '--design',
                        help="The design file of peaks (tsv format).",
                        required=True)

    parser.add_argument('-f', '--files',
                        help="The design file of with bam files (tsv format).",
                        required=True)

    args = parser.parse_args()
    return args


def check_tools():
    '''Checks for required componenets on user system.'''

    logger.info('Checking for required libraries and components on this system')

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


def update_design(design):
    '''Update design file for diffBind and remove controls.'''

    logger.info("Running control file update.")

    file_dict = design[['sample_id', 'bam_reads']] \
                .set_index('sample_id').T.to_dict()

    design['control_bam_reads'] = design['control_id'] \
                                .apply(lambda x: file_dict[x]['bam_reads'])

    logger.info("Removing rows that are there own control.")

    design = design[design['control_id'] != design['sample_id']]

    logger.info("Removing columns that are there own control.")

    design = design.drop('bam_index', axis=1)

    logger.info("Adding peaks column.")

    design = design.assign(peak='', peak_caller='bed')

    return design


def overlap(experiment, design):
    '''Calculate the overlap of peaks'''

    logger.info("Determining consenus peaks for experiment %s.", experiment)

    # Output File names
    peak_type = 'narrowPeak'
    overlapping_peaks_fn = '%s.replicated.%s' % (experiment, peak_type)
    rejected_peaks_fn = '%s.rejected.%s' % (experiment, peak_type)

    # Intermediate File names
    overlap_tr_fn = 'replicated_tr.%s' % (peak_type)
    overlap_pr_fn = 'replicated_pr.%s' % (peak_type)

    # Assign Pooled and Psuedoreplicate peaks
    pool_peaks = design.loc[design.replicate == 'pooled', 'peaks'].values[0]
    pr1_peaks = design.loc[design.replicate == '1_pr', 'peaks'].values[0]
    pr2_peaks = design.loc[design.replicate == '2_pr', 'peaks'].values[0]

    # Remove non true replicate rows
    not_replicates = ['1_pr', '2_pr', 'pooled']
    design_true_reps = design[~design['replicate'].isin(not_replicates)]
    true_rep_peaks = design_true_reps.peaks.unique()

    # Find overlaps
    awk_command = r"""awk 'BEGIN{FS="\t";OFS="\t"}{s1=$3-$2; s2=$13-$12; if (($21/s1 >= 0.5) || ($21/s2 >= 0.5)) {print $0}}'"""
    cut_command = 'cut -f 1-10'

    # Find pooled peaks that overlap Rep1 and Rep2
    # where overlap is defined as the fractional overlap
    # with any one of the overlapping peak pairs  >= 0.5

    steps_true = ['intersectBed -wo -a %s -b %s' % (pool_peaks, true_rep_peaks[0]),
                  awk_command,
                  cut_command,
                  'sort -u']

    iter_true_peaks = iter(true_rep_peaks)
    next(iter_true_peaks)

    if len(true_rep_peaks) > 1:
        for true_peak in true_rep_peaks[1:]:
            steps_true.extend(['intersectBed -wo -a stdin -b %s' % (true_peak),
                               awk_command,
                               cut_command,
                               'sort -u'])

    out, err = utils.run_pipe(steps_true, outfile=overlap_tr_fn)
    print("%d peaks overlap with both true replicates" %
          (utils.count_lines(overlap_tr_fn)))

    # Find pooled peaks that overlap PseudoRep1 and PseudoRep2
    # where overlap is defined as the fractional overlap
    # with any one of the overlapping peak pairs  >= 0.5

    steps_pseudo = ['intersectBed -wo -a %s -b %s' % (pool_peaks, pr1_peaks),
                    awk_command,
                    cut_command,
                    'sort -u',
                    'intersectBed -wo -a stdin -b %s' % (pr2_peaks),
                    awk_command,
                    cut_command,
                    'sort -u']

    out, err = utils.run_pipe(steps_pseudo, outfile=overlap_pr_fn)
    print("%d peaks overlap with both pooled pseudoreplicates"
          % (utils.count_lines(overlap_pr_fn)))

    # Make union of peak lists
    out, err = utils.run_pipe([
                'cat %s %s' % (overlap_tr_fn, overlap_pr_fn),
                'sort -u'
                ], overlapping_peaks_fn)
    print("%d peaks overlap with true replicates or with pooled pseudorepliates"
          % (utils.count_lines(overlapping_peaks_fn)))

    # Make rejected peak list
    out, err = utils.run_pipe([
        'intersectBed -wa -v -a %s -b %s' % (pool_peaks, overlapping_peaks_fn)
        ], rejected_peaks_fn)
    print("%d peaks were rejected" % (utils.count_lines(rejected_peaks_fn)))

    # Remove temporary files
    os.remove(overlap_tr_fn)
    os.remove(overlap_pr_fn)

    return os.path.abspath(overlapping_peaks_fn)


def main():
    args = get_args()
    design = args.design
    files = args.files

    # Create a file handler
    handler = logging.FileHandler('consensus_peaks.log')
    logger.addHandler(handler)

    # Check if tools are present
    check_tools()

    # Read files as dataframes
    design_peaks_df = pd.read_csv(design, sep='\t')
    design_files_df = pd.read_csv(files, sep='\t')

    # Make a design file for differential binding
    design_diff = update_design(design_files_df)

    # Make a design file for annotating Peaks
    anno_cols = ['Condition', 'Peaks']
    design_anno = pd.DataFrame(columns=anno_cols)

    # Find consenus overlap peaks for each experiment
    for experiment, df_experiment in design_peaks_df.groupby('experiment_id'):
        replicated_peak = overlap(experiment, df_experiment)
        design_diff.loc[design_diff.experiment_id == experiment, "peak"] = replicated_peak
        design_anno.loc[experiment] = [experiment, replicated_peak]

    # Write out design files
    design_diff.columns = ['SampleID',
                           'bamReads',
                           'Condition',
                           'Tissue',
                           'Factor',
                           'Treatment',
                           'Replicate',
                           'ControlID',
                           'bamControl',
                           'Peaks',
                           'PeakCaller']

    design_diff.to_csv("design_diffPeaks.csv", header=True, sep=',', index=False)
    design_anno.to_csv("design_annotatePeaks.tsv", header=True, sep='\t', index=False)

    # Write the unique conditions
    unique_experiments = pd.DataFrame(design_diff['Condition'].unique().tolist(), columns=['Condition'])
    unique_experiments.to_csv('unique_experiments.csv', index=False)


if __name__ == '__main__':
    main()
