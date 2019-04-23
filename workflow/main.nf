#!/usr/bin/env nextflow

// Path to an input file, or a pattern for multiple inputs
// Note - $baseDir is the location of this workflow file main.nf

// Define Input variables
params.reads = "$baseDir/../test_data/*.fastq.gz"
params.pairedEnd = false
params.designFile = "$baseDir/../test_data/design_ENCSR238SGC_SE.txt"
params.genome = 'GRCm38'
params.cutoffRatio = 1.2
params.outDir= "$baseDir/output"
params.extendReadsLen = 100
params.topPeakCount = 600
params.astrocyte = false
params.skipDiff = false
params.skipMotif = false
params.references = "$baseDir/../docs/references.md"
params.multiqc =  "$baseDir/conf/multiqc_config.yaml"

// Assign variables if astrocyte
if (params.astrocyte) {
  print("Running under astrocyte")
  referenceLocation = "/project/shared/bicf_workflow_ref"
  params.bwaIndex = "$referenceLocation/$params.genome"
  params.chromSizes = "$referenceLocation/$params.genome/genomefile.txt"
  params.fasta = "$referenceLocation/$params.genome/genome.fa.txt"
  if (params.genome == 'GRCh37' || params.genome == 'GRCh38') {
    params.genomeSize = 'hs'
  } else if (params.genome == 'GRCm38') {
    params.genomeSize = 'mm'
  }
} else {
    params.bwaIndex = params.genome ? params.genomes[ params.genome ].bwa ?: false : false
    params.genomeSize = params.genome ? params.genomes[ params.genome ].genomesize ?: false : false
    params.chromSizes = params.genome ? params.genomes[ params.genome ].chromsizes ?: false : false
    params.fasta = params.genome ? params.genomes[ params.genome ].fasta ?: false : false
}



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
multiqc = params.multiqc

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
    module load python/3.6.1-2-anaconda
    python3 $baseDir/scripts/check_design.py -d $designFile -f $readsList -p
    """
  }
  else {
    """
    module load python/3.6.1-2-anaconda
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
    module load python/3.6.1-2-anaconda
    module load trimgalore/0.4.1
    python3 $baseDir/scripts/trim_reads.py -f ${reads[0]} ${reads[1]} -s $sampleId -p
    """
  }
  else {
    """
    module load python/3.6.1-2-anaconda
    module load trimgalore/0.4.1
    python3 $baseDir/scripts/trim_reads.py -f ${reads[0]} -s $sampleId
    """
  }

}

// Align trimmed reads using bwa
process alignReads {

  queue '128GB,256GB,256GBv1'
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
    module load python/3.6.1-2-anaconda
    module load bwa/intel/0.7.12
    module load samtools/1.6
    python3 $baseDir/scripts/map_reads.py -f ${reads[0]} ${reads[1]} -r ${index}/genome.fa -s $sampleId -p
    """
  }
  else {
    """
    module load python/3.6.1-2-anaconda
    module load bwa/intel/0.7.12
    module load samtools/1.6
    python3 $baseDir/scripts/map_reads.py -f $reads -r ${index}/genome.fa -s $sampleId
    """
  }

}

// Dedup reads using sambamba
process filterReads {

  queue '128GB,256GB,256GBv1'
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
    module load python/3.6.1-2-anaconda
    module load samtools/1.6
    module load sambamba/0.6.6
    module load bedtools/2.26.0
    python3 $baseDir/scripts/map_qc.py -b $mapped -p
    """
  }
  else {
    """
    module load python/3.6.1-2-anaconda
    module load samtools/1.6
    module load sambamba/0.6.6
    module load bedtools/2.26.0
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

  queue '128GB,256GB,256GBv1'
  publishDir "$outDir/${task.process}", mode: 'copy'

  input:

  file dedupDesign

  output:

  file '*.{pdf,npz}' into experimentQCStats
  file('version_*.txt') into experimentQCVersions

  script:

  """
  module load python/3.6.1-2-anaconda
  module load deeptools/2.5.0.1
  python3 $baseDir/scripts/experiment_qc.py -d $dedupDesign -e $extendReadsLen
  """

}

// Convert reads to bam
process convertReads {

  queue '128GB,256GB,256GBv1'
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
    module load python/3.6.1-2-anaconda
    module load samtools/1.6
    module load bedtools/2.26.0
    python3 $baseDir/scripts/convert_reads.py -b $deduped -p
    """
  }
  else {
    """
    module load python/3.6.1-2-anaconda
    module load samtools/1.6
    module load bedtools/2.26.0
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
    module load python/3.6.1-2-anaconda
    module load phantompeakqualtools/1.2
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
  module load python/3.6.1-2-anaconda
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
    module load python/3.6.1-2-anaconda
    python3 $baseDir/scripts/pool_and_psuedoreplicate.py -d $experimentObjs -c $cutoffRatio -p
    """
  }
  else {
    """
    module load python/3.6.1-2-anaconda
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
    module load python/3.6.1-2-anaconda
    module load macs/2.1.0-20151222
    module load UCSC_userApps/v317
    module load bedtools/2.26.0
    module load phantompeakqualtools/1.2
    python3 $baseDir/scripts/call_peaks_macs.py -t $tagAlign -x $xcor -c $controlTagAlign -s $sampleId -g $genomeSize -z $chromSizes -p
    """
  }
  else {
    """
    module load python/3.6.1-2-anaconda
    module load macs/2.1.0-20151222
    module load UCSC_userApps/v317
    module load bedtools/2.26.0
    module load phantompeakqualtools/1.2
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
  module load python/3.6.1-2-anaconda
  module load bedtools/2.26.0
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
  module load R/3.3.2-gccmkl
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
  module load R/3.3.2-gccmkl
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
  module load python/3.6.1-2-anaconda
  module load meme/4.11.1-gcc-openmpi
  module load bedtools/2.26.0
  Rscript $baseDir/scripts/diff_peaks.R $designDiffPeaks
  """
}

// Generate Multiqc Report, gerernate Software Versions and references
process multiqcReport {

  publishDir "$outDir/${task.process}", mode: 'copy'

  input:

  file ('trimReads_vf/*') from trimReadsVersions.first()
  file ('alignReads_vf/*') from alignReadsVersions.first()
  file ('filterReads_vf/*') from filterReadsVersions.first()
  file ('convertReads_vf/*') from convertReadsVersions.first()
  file ('crossReads_vf/*') from crossReadsVersions.first()
  file ('callPeaksMACS_vf/*') from callPeaksMACSVersions.first()
  file ('consensusPeaks_vf/*') from consensusPeaksVersions.first()
  file ('peakAnnotation_vf/*') from peakAnnotationVersions.first()
  file ('motifSearch_vf/*') from motifSearchVersions.first().ifEmpty()
  file ('diffPeaks_vf/*') from diffPeaksVersions.first().ifEmpty()
  file ('experimentQC_vf/*') from experimentQCVersions.first()
  file ('trimReads/*') from trimgaloreResults.collect()
  file ('alignReads/*') from mappedReadsStats.collect()
  file ('filterReads/*') from dedupReadsComplexity.collect()
  file ('crossReads/*') from crossReadsStats.collect()

  output:

  file('software_versions_mqc.yaml') into softwareVersions
  file('software_references_mqc.yaml') into softwareReferences
  file "multiqc_report.html" into multiqcReport
  file "*_data" into multiqcData

  script:

  """
  module load python/3.6.1-2-anaconda
  module load pandoc/2.7
  module load multiqc/1.7
  echo $workflow.nextflow.version > version_nextflow.txt
  multiqc --version > version_multiqc.txt
  python3 $baseDir/scripts/generate_references.py -r $references -o software_references
  python3 $baseDir/scripts/generate_versions.py -o software_versions
  multiqc -c $multiqc .
  """
}
