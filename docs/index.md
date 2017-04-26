# Astrocyte ChIPseq analysis Workflow Package

This SOP describes the analysis pipeline of downstream analysis of ChIP-seq sequencing data. This pipeline includes (1) Quality control using Deeptools, (2) Peak annotation, (3) Differential peak analysis, and (4) motif analysis. BAM files and SORTED peak BED files selected as input. For each sample this workflow:

    1) Annotate all peaks using ChipSeeker
    2) Qulity control and signal profiling with Deeptools 
    3) Find differential expressed peaks using DiffBind
    4) Annotate all differentially expressed peaks
    5) Using MEME-ChIP in motif finding for both original peaks and differently expressed peaks



## Annotations used in the pipeline

    ChipSeeker - Known gene from Bioconductor [TxDb annotation](https://bioconductor.org/packages/release/BiocViews.html#___TxDb)
    Deeptools - RefGene downloaded from UCSC Table browser


 

## Workflow Parameters

    bam - Choose all ChIP-seq alignment files for analysis.
    genome - Choose a genomic reference (genome).
    peaks - Choose all the peak files for analysis. All peaks should be sorted by the user
    design - Choose the file with the experiment design information. CSV format
    toppeak - The number of top peaks used for motif analysis. Default is all
    


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


