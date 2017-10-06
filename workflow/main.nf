#!/usr/bin/env nextflow

// Path to an input file, or a pattern for multiple inputs
// Note - $baseDir is the location of this workflow file main.nf

// Define Input variables
params.reads = "$baseDir/../test_data/*.fastq.gz"
params.pairedEnd = false
params.designFile = "$baseDir/../test_data/design_ENCSR238SGC_SE.txt"
params.genome = 'GRCh38'
params.genomes = []
params.bwaIndex = params.genome ? params.genomes[ params.genome ].bwa ?: false : false

// Check inputs
if( params.bwaIndex ){
  bwaIndex = Channel
    .fromPath(params.bwaIndex)
    .ifEmpty { exit 1, "BWA index not found: ${params.bwaIndex}" }
} else {
  exit 1, "No reference genome specified."
}

// Define List of Files
readsList = Channel
  .fromPath( params.reads )
  .flatten()
  .map { file -> [ file.getFileName().toString(), file.toString() ].join("\t")}
  .collectFile( name: 'fileList.tsv', newLine: true )

// Define regular variables
pairedEnd = params.pairedEnd
designFile = params.designFile

process checkDesignFile {

  publishDir "$baseDir/output/design", mode: 'copy'

  input:

  designFile
  file readsList

  output:

  file("design.tsv") into designFilePaths

  script:

  if (pairedEnd) {
    """
    python3 $baseDir/scripts/check_design.py -d $designFile -f $readsList -p
    """
  }
  else {
    """
    python $baseDir/scripts/check_design.py -d $designFile -f $readsList
    """
  }

}

// Define channel for raw reads
if (pairedEnd) {
  rawReads = designFilePaths
    .splitCsv(sep: '\t', header: true)
    .map { row -> [ row.sample_id, [row.fastq_read1, row.fastq_read2], row.biosample, row.factor, row.treatment, row.replicate, row.control_id ] }
} else {
rawReads = designFilePaths
  .splitCsv(sep: '\t', header: true)
  .map { row -> [ row.sample_id, [row.fastq_read1], row.biosample, row.factor, row.treatment, row.replicate, row.control_id ] }
}

// Trim raw reads using trimgalore
process trimReads {

  tag "$sampleId-$replicate"
  publishDir "$baseDir/output/${task.process}", mode: 'copy'

  input:

  set sampleId, reads, biosample, factor, treatment, replicate, controlId from rawReads

  output:

  set sampleId, file('*.fq.gz'), biosample, factor, treatment, replicate, controlId into trimmedReads
  file '*trimming_report.txt' into trimgalore_results

  script:

  if (pairedEnd) {
    """
    python3 $baseDir/scripts/trim_reads.py -f ${reads[0]} ${reads[1]} -p
    """
  }
  else {
    """
    python3 $baseDir/scripts/trim_reads.py -f ${reads[0]}
    """
  }

}

// Align trimmed reads using bwa
process alignReads {

  tag "$sampleId-$replicate"
  publishDir "$baseDir/output/{task.process}", mode: 'copy'

  input:

  set sampleId, reads, biosample, factor, treatment, replicate, controlId from trimmedReads
  file index from bwaIndex.first()

  output:

  set sampleId, file('*.bam'), biosample, factor, treatment, replicate, controlId into mappedReads

  script:

  if (pairedEnd) {
    """
    python3 $baseDir/scripts/map_reads.py -f $reads -r ${index}/genome.fa -p
    """
  }
  else {
    """
    python3 $baseDir/scripts/map_reads.py -f $reads -r ${index}/genome.fa
    """
  }

}
