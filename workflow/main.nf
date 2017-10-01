#!/usr/bin/env nextflow

// Path to an input file, or a pattern for multiple inputs
// Note - $baseDir is the location of this workflow file main.nf

// Define Input variables
params.reads = "$baseDir/../test_data/*.fastq.gz"
params.pairedEnd = false
params.designFile = "$baseDir/../test_data/design_ENCSR238SGC_SE.txt"

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
    python $baseDir/scripts/check_design.py -d $designFile -f $readsList -p
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
  .map { row -> [ row.sample_id, [row.fastq_read1, row.fastq_read1], row.biosample, row.factor, row.treatment, row.replicate, row.control_id ] }
}

process fastQc {

  tag "$sampleId-$replicate"
  publishDir "$baseDir/output/", mode: 'copy',
    saveAs: {filename -> filename.indexOf(".zip") > 0 ? "zips/$filename" : "$filename"}

  input:

  set sampleId, reads, biosample, factor, treatment, replicate, controlId from rawReads

  output:

  file '*_fastqc.{zip,html}' into fastqc_results

  script:

  """
  python $baseDir/scripts/qc_fastq.py -f $reads
  """
}
