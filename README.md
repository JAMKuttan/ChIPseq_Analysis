# **CHIPseq Manual**
## Version 1.0.0
## January 2, 2019

# BICF ChIP-seq Pipeline

[![Build Status](https://git.biohpc.swmed.edu/BICF/Astrocyte/chipseq_analysis/badges/master/build.svg)](https://git.biohpc.swmed.edu/BICF/Astrocyte/chipseq_analysis/commits/master)
[![Coverage Report](https://git.biohpc.swmed.edu/BICF/Astrocyte/chipseq_analysis/badges/master/coverage.svg)](https://git.biohpc.swmed.edu/BICF/Astrocyte/chipseq_analysis/commits/master)
[![Nextflow](https://img.shields.io/badge/nextflow-%E2%89%A50.24.0-brightgreen.svg
)](https://www.nextflow.io/)
[![Astrocyte](https://img.shields.io/badge/astrocyte-%E2%89%A50.1.0-blue.svg)](https://astrocyte-test.biohpc.swmed.edu/static/docs/index.html)


## Introduction
BICF ChIPseq is a bioinformatics best-practice analysis pipeline used for ChIP-seq (chromatin immunoprecipitation sequencing) data analysis at [BICF](http://www.utsouthwestern.edu/labs/bioinformatics/) at [UT Southwestern Dept. of Bioinformatics](http://www.utsouthwestern.edu/departments/bioinformatics/).

The pipeline uses [Nextflow](https://www.nextflow.io), a bioinformatics workflow tool. It pre-processes raw data from FastQ inputs, aligns the reads and performs extensive quality-control on the results.

This pipeline is primarily used with a SLURM cluster on the [BioHPC Cluster](https://portal.biohpc.swmed.edu/content/). However, the pipeline should be able to run on any system that Nextflow supports.

Additionally, the pipeline is designed to work with [Astrocyte Workflow System](https://astrocyte-test.biohpc.swmed.edu/static/docs/index.html) using a simple web interface.

Current version of the software and issue reports are at
https://git.biohpc.swmed.edu/BICF/Astrocyte/chipseq_analysis

To download the current version of the software
```bash
$ git clone git@git.biohpc.swmed.edu:BICF/Astrocyte/chipseq_analysis.git
```

## Input files
##### 1) Fastq Files
  + You will need the full path to the files for the Bash Scipt

##### 2) Design File
  + The Design file is a tab-delimited file with 8 columns for Single-End and 9 columns for Paired-End.  Letter, numbers, and underlines can be used in the names. However, the names can only begin with a letter. Columns must be as follows:
      1. sample_id&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;a short, unique, and concise name used to label output files; will be used as a control_id if it is the control sample
      2. experiment_id&nbsp;&nbsp;&nbsp;&nbsp;biosample_treatment_factor
      3. biosample&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;symbol for tissue type or cell line
      4. factor&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;symbol for antibody target
      5. treatment&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;symbol of treatment applied
      6. replicate&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;a number, usually from 1-3 (i.e. 1)
      7. control_id&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;sample_id name that is the control for this sample
      8. fastq_read1&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;name of fastq file 1 for SE or PC data
      9. fastq_read2&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;name of fastq file 2 for PE data


  + See [HERE](https://git.biohpc.swmed.edu/BICF/Astrocyte/chipseq_analysis/blob/master/test_data/design_ENCSR729LGA_PE.txt) for an example design file, paired-end
  + See [HERE](test_data/design_ENCSR729LGA_PE.txt) for an example design file, paired-end
  + See [HERE](https://git.biohpc.swmed.edu/BICF/Astrocyte/chipseq_analysis/blob/master/test_data/design_ENCSR238SGC_SE.txt) for an example design file, single-end

##### 3) Bash Script
  + You will need to create a bash script to run the CHIPseq pipeline on [BioHPC](https://portal.biohpc.swmed.edu/content/)
  + This pipeline has been optimized for the correct partition
  + See [HERE](https://git.biohpc.swmed.edu/bchen4/chipseq_analysis/raw/master/docs/CHIPseq.sh) for an example bash script
  + The parameters that must be specified are:
      - --reads '/path/to/files/name.fastq.gz' 
      - --designFile '/path/to/file/design.txt', 
      - --genome 'GRCm38', 'GRCh38', or 'GRCh37' (if you need to use another genome contact the [BICF](mailto:BICF@UTSouthwestern.edu))
      - --pairedEnd 'true' or 'false' (where 'true' is PE and 'false' is SE; default 'false')
      - --outDir (optional) path and folder name of the output data, example: /home2/s000000/Desktop/Chipseq_output

## Pipeline
  + There are 11 steps to the pipeline
    1. Check input files
    2. Trim raw reads with trim galore
    3. Aligned trimmed reads with bwa, and sorts/converts to bam with samtools
    4. Mark duplicates with sambamba, and filter reads with samtools
    5. Quality metrics with deep tools
    6. Calculate cross-correlation using phantompeaktools
    7. Call peaks with MACS
    8. Calculate consensus peaks
    9. Annotate Peaks
    10. Calculate Differential Binding Activity
    11. Motif Search Peaks

See [FLOWCHART](https://git.biohpc.swmed.ed/bchen4/chipseq_analysis/raw/master/docs/flowchar.pdf)

## Output Files
Folder | File | Description
--- | --- | ---
design | N/A | Inputs used for analysis; can ignore
trimReads | *_trimming_report.txt | report detailing how many reads were trimmed
trimReads | *_trimmed.fq.gz | trimmed fastq files used for analysis
alignReads | *.srt.bam.flagstat.qc | QC metrics from the mapping process
alignReads | *.srt.bam | sorted bam file
filterReads | *.dup.qc | QC metrics of find duplicate reads (sambamba)
filterReads | *.filt.nodup.bam | filtered bam file with duplicate reads removed
filterReads | *.filt.nodup.bam.bai | indexed filtered bam file
filterReads | *.filt.nodup.flagstat.qc | QC metrics of filtered bam file (mapping stats, samtools)
filterReads | *.filt.nodup.pbc.qc | QC metrics of library complexity
convertReads | *.filt.nodup.bedse.gz | bed alignment in BEDPE format
convertReads | *.filt.nodup.tagAlign.gz | bed alignent in BEDPE format, same as bedse unless samples are paired-end
experimentQC | coverage.pdf | plot to assess the sequencing depth of a given sample
experimentQC | *_fingerprint.pdf | plot to determine if the antibody-treatment enriched sufficiently
experimentQC | heatmeap_SpearmanCorr.pdf | plot of Spearman correlation between samples
experimentQC | heatmeap_PearsonCorr.pdf | plot of Pearson correlation between samples
experimentQC | sample_mbs.npz | array of multiple BAM summaries
crossReads | *.filt.nodup.tagAlign.15.tagAlign.gz.cc.plot.pdf | plot of cross-correlation to assess signal-to-noise ratios
crossReads | *.filt.nodup.tagAlign.15.tagAlign.gz.cc.qc | cross-correlation metrics. File [HEADER](https://git.biohpc.swmed.ed/bchen4/chipseq_analysis/raw/master/docs/xcor_header.txt)
callPeaksMACS | *.fc_signal.bw | bigwig data file; raw fold enrichment of sample/control
callPeaksMACS | *.pvalue_signal.bw | bigwig data file; sample/control signal adjusted for pvalue significance
callPeaksMACS | *_peaks.narrowPeak | peaks file; see [HERE](https://genome.ucsc.edu/FAQ/FAQformat.html#format12) for ENCODE narrowPeak header format
consensusPeaks | design_annotatePeaks.tsv | design file; can ignore
consensusPeaks | design_diffPeaks.csv | design file; can ignore
consensusPeaks | *.rejected.narrowPeak | peaks not supported by multiple testing (replicates and pseudo-replicates)
consensusPeaks | *.replicated.narrowPeak | peaks supported by multiple testing (replicates and pseudo-replicates)
consensusPeaks | unique_experiments.csv | design file; can ignore
peakAnnotation | *.chipseeker_annotation.csv | annotated narrowPeaks file
peakAnnotation | *.chipseeker_pie.pdf | pie graph of where narrow annotated peaks occur
peakAnnotation | *.chipseeker_upsetplot.pdf | upsetplot showing the count of overlaps of the genes with different annotated location
motifSearch | *_memechip/index.html | interactive HTML link of MEME output
motifSearch | sorted-*.replicated.narrowPeak | Top 600 peaks sorted by p-value; input for motifSearch
motifSearch | *_memechip/combined.meme | MEME identified motifs
diffPeaks | heatmap.pdf | Use only for replicated samples; heatmap of relationship of peak location and peak intensity
diffPeaks | normcount_peaksets.txt | Use only for replicated samples; peak set values of each sample
diffPeaks | pca.pdf | Use only for replicated samples; PCA of peak location and peak intensity
diffPeaks | *_diffbind.bed | Use only for replicated samples; bed file of peak locations between replicates
diffPeaks | *_diffbind.csv | Use only for replicated samples; CSV file of peaks between replicates

## Common Quality Control Metrics
  + These are the list of files that should be reviewed before continuing on with the CHIPseq experiment. If your experiment fails any of these metrics, you should pause and re-evaluate whether the data should remain in the study.
    1. filterReads/*.filt.nodup.pbc.qc: follow the ChiP-seq standards [HERE](https://www.encodeproject.org/chip-seq/); NRF>0.9, PBC1>0.9, and PBC2>10
    2. experimentQC/*_fingerprint.pdf: make sure the plots information is correct for your antibody/input. See [HERE](https://deeptools.readthedocs.io/en/develop/content/tools/plotFingerprint.html) for more details.
    3. crossReads/*.filt.nodup.tagAlign.15.tagAlign.gz.cc.plot.pdf: make sure your sample data has the correct signal intensity and location.  See [HERE](https://hbctraining.github.io/Intro-to-ChIPseq/lessons/06_QC_cross_correlation.html) for more details.
    4. crossReads/*.filt.nodup.tagAlign.15.tagAlign.gz.cc.qc: Column 9 (NSC) should be > 1.1 for experiment and < 1.1 for input. Column 10 (RSC) should be > 0.8 for experiment and < 0.8 for input. See [HERE](https://hbctraining.github.io/Intro-to-ChIPseq/lessons/06_QC_cross_correlation.html) for more details.


## Common Errors
If you find an error, please let the [BICF](mailto:BICF@UTSouthwestern.edu) know and we will add it here.

## Programs and Versions
  + python/3.6.1-2-anaconda [website](https://www.anaconda.com/download/#linux) [citation](https://git.biohpc.swmed.edu/bchen4/chipseq_analysis/raw/master/docs/references.txt)
  + trimgalore/0.4.1 [website](https://github.com/FelixKrueger/TrimGalore) [citation](https://git.biohpc.swmed.edu/bchen4/chipseq_analysis/raw/master/docs/references.txt)
  + cutadapt/1.9.1 [website](https://cutadapt.readthedocs.io/en/stable/index.html) [citation](https://git.biohpc.swmed.edu/bchen4/chipseq_analysis/raw/master/docs/references.txt)
  + bwa/intel/0.7.12 [website](http://bio-bwa.sourceforge.net/) [citation](https://git.biohpc.swmed.edu/bchen4/chipseq_analysis/raw/master/docs/references.txt)
  + samtools/1.6 [website](http://samtools.sourceforge.net/) [citation](https://git.biohpc.swmed.edu/bchen4/chipseq_analysis/raw/master/docs/references.txt)
  + sambamba/0.6.6 [website](http://lomereiter.github.io/sambamba/) [citation](https://git.biohpc.swmed.edu/bchen4/chipseq_analysis/raw/master/docs/references.txt)
  + bedtools/2.26.0 [website](https://bedtools.readthedocs.io/en/latest/) [citation](https://git.biohpc.swmed.edu/bchen4/chipseq_analysis/raw/master/docs/references.txt)
  + deeptools/2.5.0.1 [website](https://deeptools.readthedocs.io/en/develop/) [citation](https://git.biohpc.swmed.edu/bchen4/chipseq_analysis/raw/master/docs/references.txt)
  + phantompeakqualtools/1.2 [website](https://github.com/kundajelab/phantompeakqualtools) [citation](https://git.biohpc.swmed.edu/bchen4/chipseq_analysis/raw/master/docs/references.txt)
  + macs/2.1.0-20151222 [website](http://liulab.dfci.harvard.edu/MACS/) [citation](https://git.biohpc.swmed.edu/bchen4/chipseq_analysis/raw/master/docs/references.txt)
  + UCSC_userApps/v317 [website](https://genome.ucsc.edu/util.html) [citation](https://git.biohpc.swmed.edu/bchen4/chipseq_analysis/raw/master/docs/references.txt)
  + R/3.3.2-gccmkl [website](https://www.r-project.org/) [citation](https://git.biohpc.swmed.edu/bchen4/chipseq_analysis/raw/master/docs/references.txt)
  + meme/4.11.1-gcc-openmpi [website](http://meme-suite.org/doc/install.html?man_type=web) [citation](https://git.biohpc.swmed.edu/bchen4/chipseq_analysis/raw/master/docs/references.txt)
  + ChIPseeker [website](https://bioconductor.org/packages/release/bioc/html/ChIPseeker.html) [citation](https://git.biohpc.swmed.edu/bchen4/chipseq_analysis/raw/master/docs/references.txt)
  + DiffBind [website](https://bioconductor.org/packages/release/bioc/html/DiffBind.html) [citation](https://git.biohpc.swmed.edu/bchen4/chipseq_analysis/raw/master/docs/references.txt)


## Credits
This example worklow is derived from original scripts kindly contributed by the Bioinformatic Core Facility ([BICF](https://www.utsouthwestern.edu/labs/bioinformatics/)), in the [Department of Bioinformatics](https://www.utsouthwestern.edu/departments/bioinformatics/).

## Citation
Please cite individual programs and versions used [HERE](https://git.biohpc.swmed.edu/bchen4/chipseq_analysis/raw/master/docs/references.txt). Also, please look out for our pipeline to be published in the future [HERE](https://zenodo.org/).

