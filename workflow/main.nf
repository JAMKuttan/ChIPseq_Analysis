#!/usr/bin/env nextflow

// Path to an input file, or a pattern for multiple inputs
// Note - $baseDir is the location of this workflow file main.nf

// Define Input variables
params.reads = "$baseDir/../test_data/*.fastq.gz"
params.pairedEnd = false
params.designFile = "$baseDir/../test_data/design_ENCSR238SGC_SE.txt"
params.genome = 'GRCm38'
params.genomes = []
params.bwaIndex = params.genome ? params.genomes[ params.genome ].bwa ?: false : false
params.genomeSize = params.genome ? params.genomes[ params.genome ].genomesize ?: false : false
params.chromSizes = params.genome ? params.genomes[ params.genome ].chromsizes ?: false : false
params.cutoffRatio = 1.2

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
genomeSize = params.genomeSize
chromSizes = params.chromSizes
cutoffRatio = params.cutoffRatio

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
    .map { row -> [ row.sample_id, [row.fastq_read1, row.fastq_read2], row.experiment_id, row.biosample, row.factor, row.treatment, row.replicate, row.control_id ] }
} else {
rawReads = designFilePaths
  .splitCsv(sep: '\t', header: true)
  .map { row -> [ row.sample_id, [row.fastq_read1], row.experiment_id, row.biosample, row.factor, row.treatment, row.replicate, row.control_id ] }
}

// Trim raw reads using trimgalore
process trimReads {

  tag "$sampleId-$replicate"
  publishDir "$baseDir/output/${task.process}", mode: 'copy'

  input:

  set sampleId, reads, experimentId, biosample, factor, treatment, replicate, controlId from rawReads

  output:

  set sampleId, file('*.fq.gz'), experimentId, biosample, factor, treatment, replicate, controlId into trimmedReads
  file('*trimming_report.txt') into trimgalore_results

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
  publishDir "$baseDir/output/${task.process}", mode: 'copy'

  input:

  set sampleId, reads, experimentId, biosample, factor, treatment, replicate, controlId from trimmedReads
  file index from bwaIndex.first()

  output:

  set sampleId, file('*.bam'), experimentId, biosample, factor, treatment, replicate, controlId into mappedReads
  file '*.srt.bam.flagstat.qc' into mappedReadsStats

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

// Dedup reads using sambamba
process filterReads {

  tag "$sampleId-$replicate"
  publishDir "$baseDir/output/${task.process}", mode: 'copy'

  input:

  set sampleId, mapped, experimentId, biosample, factor, treatment, replicate, controlId from mappedReads

  output:

  set sampleId, file('*.bam'), file('*.bai'), experimentId, biosample, factor, treatment, replicate, controlId into dedupReads
  set sampleId, file('*.bam'), experimentId, biosample, factor, treatment, replicate, controlId into convertReads
  file '*flagstat.qc' into dedupReadsStats
  file '*pbc.qc' into dedupReadsComplexity
  file '*dup.qc' into dupReads

  script:

  if (pairedEnd) {
    """
    python3 $baseDir/scripts/map_qc.py -b $mapped -p
    """
  }
  else {
    """
    python3 $baseDir/scripts/map_qc.py -b $mapped
    """
  }

}

// Define channel collecting dedup reads into new design file
dedupReads
.map{ sampleId, bam, bai, experimentId, biosample, factor, treatment, replicate, controlId ->
"$sampleId\t$bam\t$bai\t$experimentId\t$biosample\t$factor\t$treatment\t$replicate\t$controlId\n"}
.collectFile(name:'design_dedup.tsv', seed:"sample_id\tbam_reads\tbam_index\texperiment_id\tbiosample\tfactor\ttreatment\treplicate\tcontrol_id\n", storeDir:"$baseDir/output/design")
.into { dedupDesign; preDiffDesign }

// Quality Metrics using deeptools
process experimentQC {

  publishDir "$baseDir/output/${task.process}", mode: 'copy'

  input:

  file dedupDesign

  output:

  file '*.{png,npz}' into deepToolsStats

  script:

  """
  python3 $baseDir/scripts/experiment_qc.py -d $dedupDesign
  """

}

// Convert reads to bam
process convertReads {

  tag "$sampleId-$replicate"
  publishDir "$baseDir/output/${task.process}", mode: 'copy'

  input:

  set sampleId, deduped, experimentId, biosample, factor, treatment, replicate, controlId from convertReads

  output:

  set sampleId, file('*.tagAlign.gz'), file('*.bed{pe,se}.gz'), experimentId, biosample, factor, treatment, replicate, controlId into tagReads

  script:

  if (pairedEnd) {
    """
    python3 $baseDir/scripts/convert_reads.py -b $deduped -p
    """
  }
  else {
    """
    python3 $baseDir/scripts/convert_reads.py -b $deduped
    """
  }

}

// Calculate Cross-correlation using phantompeaktools
process crossReads {

  tag "$sampleId-$replicate"
  publishDir "$baseDir/output/${task.process}", mode: 'copy'

  input:

  set sampleId, seTagAlign, tagAlign, experimentId, biosample, factor, treatment, replicate, controlId from tagReads

  output:

  set sampleId, tagAlign, file('*.cc.qc'), experimentId, biosample, factor, treatment, replicate, controlId into xcorReads
  set file('*.cc.qc'), file('*.cc.plot.pdf') into xcorReadsStats

  script:

  if (pairedEnd) {
    """
    python3 $baseDir/scripts/xcor.py -t $seTagAlign -p
    """
  }
  else {
    """
    python3 $baseDir/scripts/xcor.py -t $seTagAlign
    """
  }

}

// Define channel collecting tagAlign and xcor into design file
xcorDesign = xcorReads
              .map{ sampleId, tagAlign, xcor, experimentId, biosample, factor, treatment, replicate, controlId ->
              "$sampleId\t$tagAlign\t$xcor\t$experimentId\t$biosample\t$factor\t$treatment\t$replicate\t$controlId\n"}
              .collectFile(name:'design_xcor.tsv', seed:"sample_id\ttag_align\txcor\texperiment_id\tbiosample\tfactor\ttreatment\treplicate\tcontrol_id\n", storeDir:"$baseDir/output/design")

// Make Experiment design files to be read in for downstream analysis
process defineExpDesignFiles {

  publishDir "$baseDir/output/design", mode: 'copy'

  input:

  file xcorDesign

  output:

  file '*.tsv' into experimentObjs mode flatten

  script:

  """
  python3 $baseDir/scripts/experiment_design.py -d $xcorDesign
  """

}


// Make Experiment design files to be read in for downstream analysis
process poolAndPsuedoReads {


  tag "${experimentObjs.baseName}"
  publishDir "$baseDir/output/design", mode: 'copy'

  input:

  file experimentObjs

  output:

  file '*.tsv' into experimentPoolObjs

  script:

  if (pairedEnd) {
    """
    python3 $baseDir/scripts/pool_and_psuedoreplicate.py -d $experimentObjs -c $cutoffRatio -p
    """
  }
  else {
    """
    python3 $baseDir/scripts/pool_and_psuedoreplicate.py -d $experimentObjs -c $cutoffRatio
    """
  }

}

// Collect list of experiment design files into a single channel
experimentRows = experimentPoolObjs.collect()
            .splitCsv(sep:'\t', header: true)

// Call Peaks using MACS
process callPeaksMACS {

  tag "$sampleId-$replicate"
  publishDir "$baseDir/output/${task.process}", mode: 'copy'

  input:
  set sampleId, tagAlign, xcor, experimentId, biosample, factor, treatment, replicate, controlId, controlTagAlign from experimentRows

  output:

  set sampleId, file('*.narrowPeak'), file('*.fc_signal.bw'), file('*.pvalue_signal.bw'), experimentId, biosample, factor, treatment, replicate, controlId from experimentRows

  script:

  if (pairedEnd) {
    """
    python3 $baseDir/scripts/call_peaks_macs.py -t $tagAlign -x $xcor -c $controlTagAlign -s $sampleId -g $genomeSize -z $chromSizes -p
    """
  }
  else {
    """
    python3 $baseDir/scripts/call_peaks_macs.py -t $tagAlign -x $xcor -c $controlTagAlign -s $sampleId -g $genomeSize -z $chromSizes -p
    """
  }

}

// Define channel collecting peaks into design file
peaksDesign = experimentRows
              .map{ sampleId, peak, fcSignal, pvalueSignal, experimentId, biosample, factor, treatment, replicate, controlId ->
              "$sampleId\t$peak\t$fcSignal\t$pvalueSignal\t$experimentId\t$biosample\t$factor\t$treatment\t$replicate\t$controlId\n"}
              .collectFile(name:'design_peak.tsv', seed:"sample_id\tpeak\txcor\tfcSignal\tpvalueSignal\texperiment_id\tbiosample\tfactor\ttreatment\treplicate\tcontrol_id\n", storeDir:"$baseDir/output/design")

// Calculate Consensus Peaks
process consensusPeaks {

  publishDir "$baseDir/output/${task.process}", mode: 'copy'

  input:

  file peaksDesign
  file preDiffDesign

  output:

  file '*.replicated.*' into consensusPeaks
  file '*.rejected.*' into rejectedPeaks
  file("design_diffPeaks.tsv") into designFilePaths

  script:

  """
  python3 $baseDir/scripts/overlap_peaks.py -d $peaksDesign -f preDiffDesign
  """

}
