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
params.fasta = params.genome ? params.genomes[ params.genome ].fasta ?: false : false
params.cutoffRatio = 1.2
params.outDir= "$baseDir/output"
params.extendReadsLen = 100
params.topPeakCount = 600
params.skipDiff = false
params.skipMotif = false
params.references = "$baseDir/../docs/references.md"

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
genome = params.genome
chromSizes = params.chromSizes
fasta = params.fasta
cutoffRatio = params.cutoffRatio
outDir = params.outDir
extendReadsLen = params.extendReadsLen
topPeakCount = params.topPeakCount
skipDiff = params.skipDiff
skipMotif = params.skipMotif
references = params.references

// Check design file for errors
process checkDesignFile {

  publishDir "$outDir/design", mode: 'copy'

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
  publishDir "$outDir/${task.process}/${sampleId}", mode: 'copy'

  input:

  set sampleId, reads, experimentId, biosample, factor, treatment, replicate, controlId from rawReads

  output:

  set sampleId, file('*.fq.gz'), experimentId, biosample, factor, treatment, replicate, controlId into trimmedReads
  file('*trimming_report.txt') into trimgaloreResults
  file('version_*.txt') into trimReadsVersions

  script:

  if (pairedEnd) {
    """
    python3 $baseDir/scripts/trim_reads.py -f ${reads[0]} ${reads[1]} -s $sampleId -p
    """
  }
  else {
    """
    python3 $baseDir/scripts/trim_reads.py -f ${reads[0]} -s $sampleId
    """
  }

}

// Align trimmed reads using bwa
process alignReads {

  tag "$sampleId-$replicate"
  publishDir "$outDir/${task.process}/${sampleId}", mode: 'copy'

  input:

  set sampleId, reads, experimentId, biosample, factor, treatment, replicate, controlId from trimmedReads
  file index from bwaIndex.first()

  output:

  set sampleId, file('*.bam'), experimentId, biosample, factor, treatment, replicate, controlId into mappedReads
  file '*.flagstat.qc' into mappedReadsStats
  file('version_*.txt') into alignReadsVersions

  script:

  if (pairedEnd) {
    """
    python3 $baseDir/scripts/map_reads.py -f ${reads[0]} ${reads[1]} -r ${index}/genome.fa -s $sampleId -p
    """
  }
  else {
    """
    python3 $baseDir/scripts/map_reads.py -f $reads -r ${index}/genome.fa -s $sampleId
    """
  }

}

// Dedup reads using sambamba
process filterReads {

  tag "$sampleId-$replicate"
  publishDir "$outDir/${task.process}/${sampleId}", mode: 'copy'

  input:

  set sampleId, mapped, experimentId, biosample, factor, treatment, replicate, controlId from mappedReads

  output:

  set sampleId, file('*.bam'), file('*.bai'), experimentId, biosample, factor, treatment, replicate, controlId into dedupReads
  set sampleId, file('*.bam'), experimentId, biosample, factor, treatment, replicate, controlId into convertReads
  file '*.flagstat.qc' into dedupReadsStats
  file '*.pbc.qc' into dedupReadsComplexity
  file '*.dedup.qc' into dupReads
  file('version_*.txt') into filterReadsVersions

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
.collectFile(name:'design_dedup.tsv', seed:"sample_id\tbam_reads\tbam_index\texperiment_id\tbiosample\tfactor\ttreatment\treplicate\tcontrol_id\n", storeDir:"$outDir/design")
.into { dedupDesign; preDiffDesign }

// Quality Metrics using deeptools
process experimentQC {

  publishDir "$outDir/${task.process}", mode: 'copy'

  input:

  file dedupDesign

  output:

  file '*.{pdf,npz}' into experimentQCStats
  file('version_*.txt') into experimentQCVersions

  script:

  """
  python3 $baseDir/scripts/experiment_qc.py -d $dedupDesign -e $extendReadsLen
  """

}

// Convert reads to bam
process convertReads {

  tag "$sampleId-$replicate"
  publishDir "$outDir/${task.process}/${sampleId}", mode: 'copy'

  input:

  set sampleId, deduped, experimentId, biosample, factor, treatment, replicate, controlId from convertReads

  output:

  set sampleId, file('*.tagAlign.gz'), file('*.bed{pe,se}.gz'), experimentId, biosample, factor, treatment, replicate, controlId into tagReads
  file('version_*.txt') into convertReadsVersions

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
  publishDir "$outDir/${task.process}/${sampleId}", mode: 'copy'

  input:

  set sampleId, seTagAlign, tagAlign, experimentId, biosample, factor, treatment, replicate, controlId from tagReads

  output:

  set sampleId, seTagAlign, tagAlign, file('*.cc.qc'), experimentId, biosample, factor, treatment, replicate, controlId into xcorReads
  set file('*.cc.qc'), file('*.cc.plot.pdf') into crossReadsStats
  file('version_*.txt') into crossReadsVersions

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
              .map{ sampleId, seTagAlign, tagAlign, xcor, experimentId, biosample, factor, treatment, replicate, controlId ->
              "$sampleId\t$seTagAlign\t$tagAlign\t$xcor\t$experimentId\t$biosample\t$factor\t$treatment\t$replicate\t$controlId\n"}
              .collectFile(name:'design_xcor.tsv', seed:"sample_id\tse_tag_align\ttag_align\txcor\texperiment_id\tbiosample\tfactor\ttreatment\treplicate\tcontrol_id\n", storeDir:"$outDir/design")

// Make Experiment design files to be read in for downstream analysis
process defineExpDesignFiles {

  publishDir "$outDir/design", mode: 'copy'

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
  publishDir "$outDir/design", mode: 'copy'

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
experimentRows = experimentPoolObjs
                .splitCsv(sep:'\t', header:true)
                .map { row -> [ row.sample_id, row.tag_align, row.xcor, row.experiment_id, row.biosample, row.factor, row.treatment, row.replicate, row.control_id, row.control_tag_align] }

// Call Peaks using MACS
process callPeaksMACS {

  tag "$sampleId-$replicate"
  publishDir "$outDir/${task.process}/${experimentId}/${replicate}", mode: 'copy'

  input:
  set sampleId, tagAlign, xcor, experimentId, biosample, factor, treatment, replicate, controlId, controlTagAlign from experimentRows

  output:

  set sampleId, file('*.narrowPeak'), file('*.fc_signal.bw'), file('*.pvalue_signal.bw'), experimentId, biosample, factor, treatment, replicate, controlId into experimentPeaks
  file '*.xls' into callPeaksMACSsummit
  file('version_*.txt') into callPeaksMACSVersions

  script:

  if (pairedEnd) {
    """
    python3 $baseDir/scripts/call_peaks_macs.py -t $tagAlign -x $xcor -c $controlTagAlign -s $sampleId -g $genomeSize -z $chromSizes -p
    """
  }
  else {
    """
    python3 $baseDir/scripts/call_peaks_macs.py -t $tagAlign -x $xcor -c $controlTagAlign -s $sampleId -g $genomeSize -z $chromSizes
    """
  }

}

// Define channel collecting peaks into design file
peaksDesign = experimentPeaks
              .map{ sampleId, peak, fcSignal, pvalueSignal, experimentId, biosample, factor, treatment, replicate, controlId ->
              "$sampleId\t$peak\t$fcSignal\t$pvalueSignal\t$experimentId\t$biosample\t$factor\t$treatment\t$replicate\t$controlId\n"}
              .collectFile(name:'design_peak.tsv', seed:"sample_id\tpeaks\tfc_signal\tpvalue_signal\texperiment_id\tbiosample\tfactor\ttreatment\treplicate\tcontrol_id\n", storeDir:"$outDir/design")

// Calculate Consensus Peaks
process consensusPeaks {

  publishDir "$outDir/${task.process}", mode: 'copy'
  publishDir "$outDir/design", mode: 'copy',  pattern: '*.{csv|tsv}'

  input:

  file peaksDesign
  file preDiffDesign

  output:

  file '*.replicated.*' into consensusPeaks
  file '*.rejected.*' into rejectedPeaks
  file 'design_diffPeaks.csv'  into designDiffPeaks
  file 'design_annotatePeaks.tsv'  into designAnnotatePeaks, designMotifSearch
  file 'unique_experiments.csv' into uniqueExperiments
  file('version_*.txt') into consensusPeaksVersions

  script:

  """
  python3 $baseDir/scripts/overlap_peaks.py -d $peaksDesign -f $preDiffDesign
  """

}

// Annotate Peaks
process peakAnnotation {

  publishDir "$outDir/${task.process}", mode: 'copy'

  input:

  file designAnnotatePeaks

  output:

  file "*chipseeker*" into peakAnnotation
  file('version_*.txt') into peakAnnotationVersions

  script:

  """
  Rscript $baseDir/scripts/annotate_peaks.R $designAnnotatePeaks $genome
  """

}

// Motif Search Peaks
process motifSearch {

  publishDir "$outDir/${task.process}", mode: 'copy'

  input:

  file designMotifSearch

  output:

  file "*memechip" into motifSearch
  file "*narrowPeak" into filteredPeaks
  file('version_*.txt') into motifSearchVersions

  when:
  !skipMotif

  script:

  """
  python3 $baseDir/scripts/motif_search.py -d $designMotifSearch -g $fasta -p $topPeakCount
  """
}

// Define channel to find number of unique experiments
uniqueExperimentsList = uniqueExperiments
                      .splitCsv(sep: '\t', header: true)

// Calculate Differential Binding Activity
process diffPeaks {

  publishDir "$outDir/${task.process}", mode: 'copy'

  input:

  file designDiffPeaks
  val noUniqueExperiments from uniqueExperimentsList.count()

  output:

  file '*_diffbind.bed' into diffPeaks
  file '*_diffbind.csv' into diffPeaksCounts
  file '*.pdf' into diffPeaksStats
  file 'normcount_peaksets.txt' into normCountPeaks
  file('version_*.txt') into diffPeaksVersions

  when:
  noUniqueExperiments > 1 && !skipDiff

  script:
  """
  Rscript $baseDir/scripts/diff_peaks.R $designDiffPeaks
  """
}

// Collect Software Versions and references
process softwareReport {

  publishDir "$outDir/${task.process}", mode: 'copy'

  input:

  file trimReads_vf from trimReadsVersions.collect()
  file alignReads_vf from alignReadsVersions.collect()
  file filterReads_vf from filterReadsVersions.collect()
  file convertReads_vf from convertReadsVersions.collect()
  file crossReads_vf from crossReadsVersions.collect()
  file callPeaksMACS_vf from callPeaksMACSVersions.collect()
  file consensusPeaks_vf from consensusPeaksVersions.collect()
  file peakAnnotation_vf from peakAnnotationVersions.collect()
  file motifSearch_vf from motifSearchVersions.collect()
  file diffPeaks_vf from diffPeaksVersions.collect()
  file experimentQC_vf from experimentQCVersions.collect()

  output:

  file('*_mqc.yaml') into softwareVersions
  file('*_mqc.txt') into softwareReferences

  script:
  """
  echo $workflow.nextflow.version > version_nextflow.txt
  python3 $baseDir/scripts/generate_references.py -r $references -o software_references
  python3 $baseDir/scripts/generate_versions.py -f $trimReads_vf \
                                                  $alignReads_vf \
                                                  $filterReads_vf \
                                                  $convertReads_vf \
                                                  $crossReads_vf \
                                                  $callPeaksMACS_vf \
                                                  $consensusPeaks_vf \
                                                  $motifSearch_vf \
                                                  $diffPeaks_vf \
                                                  $experimentQC_vf \
                                                  version_nextflow.txt \
                                                  -o software_versions

  """
}
