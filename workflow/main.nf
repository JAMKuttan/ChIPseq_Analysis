#!/usr/bin/env nextflow

// Path to an input file, or a pattern for multiple inputs
// Note - $baseDir is the location of this workflow file main.nf

params.reads = "$baseDir/../test_data/*_R{1,2}.fastq.gz"
params.singleEnd = false


Channel
    .fromFilePairs( params.reads, size: params.singleEnd ? 1 : 2 )
    .ifEmpty { error "Cannot find any reads matching: ${params.reads}\nIf this is single-end data, please specify."}
    .set { read_pairs }

process qc_fastq {
    tag "$name"

    publishDir "$baseDir/output/$name/$task.process", mode: 'copy'

    input:
    set val(name), file(reads) from read_pairs

    output:
    file "*_fastqc.{zip,html}" into qc_fastq_results
    file "qc.log" into qc_fastq_log

    script:
    """
    module load python/3.6.1-2-anaconda
    module load fastqc/0.11.5
    $baseDir/scripts/qc_fastq.py -f $reads
    """
}
