# Astrocyte ChIPseq analysis Workflow Package

## Introduction
**ChIP-seq Analysis** is a bioinformatics best-practice analysis pipeline used for chromatin immunoprecipitation (ChIP-seq) data analysis.

The pipeline uses [Nextflow](https://www.nextflow.io), a bioinformatics workflow tool. It pre-processes raw data from FastQ inputs, aligns the reads and performs extensive quality-control on the results.

### Pipeline Steps

1) Trim adaptors TrimGalore!
2) Align with BWA
3) Filter reads with Sambamba  S
4) Quality control with DeepTools
5) Calculate Cross-correlation using SPP and PhantomPeakQualTools
6) Signal profiling using MACS2
7) Call consenus peaks
8) Annotate all peaks using ChipSeeker
9) Use MEME-ChIP to find motifs in original peaks
10) Find differential expressed peaks using DiffBind (If more than 1 experiment)


## Workflow Parameters

    reads - Choose all ChIP-seq fastq files for analysis.
    pairedEnd - Choose True/False if data is paired-end
    design - Choose the file with the experiment design information. TSV format
    genome - Choose a genomic reference (genome).


## Design file

 The following columns are necessary, must be named as in template. An design file template can be downloaded [HERE](https://git.biohpc.swmed.edu/bchen4/chipseq_analysis/raw/master/docs/design_example.csv)

    SampleID
        The id of the sample. This will be the header in output files, please make sure it is concise
    Tissue
        Tissue of the sample
    Factor
        Factor of the experiment
    Condition
	    This is the group that will be used for pairwise differential expression analysis
	Replicate
	    Replicate id
    Peaks
        The file name of the peak file for this sample
    bamReads
        The file name of the IP BAM for this sample
    bamControl
        The file name of the control BAM for this sample
    ContorlID
        The id of the control sample
    PeakCaller
        The peak caller used



### Credits
This example worklow is derived from original scripts kindly contributed by the Bioinformatic Core Facility (BICF), Department of Bioinformatics

### References

* ChipSeeker: http://bioconductor.org/packages/release/bioc/html/ChIPseeker.html
* DiffBind: http://bioconductor.org/packages/release/bioc/html/DiffBind.html
* Deeptools: https://deeptools.github.io/
* MEME-ChIP: http://meme-suite.org/doc/meme-chip.html
