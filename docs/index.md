# BICF ChIP-seq Analysis Workflow

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
    skipDiff - Choose True/False if data if you want to run Differential Peaks
    skipMotif - Choose True/False if data if you want to run Motif Calling


## Design file

 The following columns are necessary, must be named as in template. An design file template can be downloaded [HERE](https://git.biohpc.swmed.edu/BICF/Astrocyte/chipseq_analysis/blob/master/docs/design_example.txt)

    sample_id
        The id of the sample. This will be the name used in output files, please make sure it is concise and informative.
    experiment_id
        The id of the experiment. Used for grouping replicates.
    biosample
        The name of the biological sample.
    factor
        Factor of the experiment.
    treatment
        Treatment used in experiment.
    replicate
        Replicate number.
    control_id
	    The sample_id of the control used for this sample.
    fastq_read1
      File name of fastq file, if paired-end this is read1.
    fastq_read2
      File name of read2 (for paired-end), not needed for single-end data.


### Credits
This worklow is was developed jointly with the [Bioinformatic Core Facility (BICF), Department of Bioinformatics](http://www.utsouthwestern.edu/labs/bioinformatics/)

Please cite in publications: Pipeline was developed by BICF from funding provided by **Cancer Prevention and Research Institute of Texas (RP150596)**.
