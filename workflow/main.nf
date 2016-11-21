#!/usr/bin/env nextflow
	
// Default parameter values to run tests
params.bams="$baseDir/../test_data/*.fastq.gz"
params.design="$baseDir/../test_data/design.pe.txt"
params.genome="/project/shared/bicf_workflow_ref/GRCh38/"

design_file = file(params.design)
fastqs=file(params.fastqs)
design_file = file(params.design)
gtf_file = file("$params.genome/gencode.gtf")
genenames = file("$params.genome/genenames.txt")
geneset = file("$params.genome/gsea_gmt/$params.geneset")

// params genome is the directory
// base name for the index is always genome
index_path = file(params.genome)
index_name = "genome"
star_index = 'star_index/'

// Pair handling, helper function taken from rnatoy
// which is covered by the GNU General Public License v3
// https://github.com/nextflow-io/rnatoy/blob/master/main.nf

def fileMap = [:]

fastqs.each {
    final fileName = it.getFileName().toString()
    prefix = fileName.lastIndexOf('/')
    fileMap[fileName] = it
}
def prefix = []
new File(params.design).withReader { reader ->
    def hline = reader.readLine()
    def header = hline.split("\t")
    prefixidx = header.findIndexOf{it == 'SampleID'};
    oneidx = header.findIndexOf{it == 'FullPathToFqR1'};
    twoidx = header.findIndexOf{it == 'FullPathToFqR2'};
    if (twoidx == -1) {
       twoidx = oneidx
       }      
    while (line = reader.readLine()) {
    	   def row = line.split("\t")
	   if (fileMap.get(row[oneidx]) != null) {
	      prefix << tuple(row[prefixidx],fileMap.get(row[oneidx]),fileMap.get(row[twoidx]))
	   }
	  
} 
}
if( ! prefix) { error "Didn't match any input files with entries in the design file" }

if (params.pairs == 'pe') {
Channel
  .from(prefix)
  .set { read_pe }
Channel
  .empty()
  .set { read_se } 
}
if (params.pairs == 'se') {
Channel
  .from(prefix)
  .into { read_se }
Channel
  .empty()
  .set { read_pe }
}

//
// Trim raw reads using trimgalore
//
process trimpe {
  input:
  set pair_id, file(read1), file(read2) from read_pe
  output:
  set pair_id, file("${read1.baseName.split("\\.", 2)[0]}_val_1.fq.gz"), file("${read2.baseName.split("\\.", 2)[0]}_val_2.fq.gz") into trimpe
  script:
  """
  module load trimgalore/0.4.1 cutadapt/1.9.1
  trim_galore --paired -q 25 --illumina --gzip --length 35 ${read1} ${read2}
  """
}
process trimse {
  input:
  set pair_id, file(read1) from read_se
  output:
  set pair_id, file("${read1.baseName.split("\\.", 2)[0]}_trimmed.fq.gz") into trimse
  script:
  """
  module load trimgalore/0.4.1 cutadapt/1.9.1
  trim_galore -q 25 --illumina --gzip --length 35 ${read1}
  """
}

//
// Align trimmed reads to genome indes with hisat2
// Sort and index with samtools
// QC aligned reads with fastqc
// Alignment stats with samtools
//
process alignpe {

  publishDir "$baseDir/output", mode: 'copy'
  cpus 32

  input:
  set pair_id, file(fq1), file(fq2) from trimpe
  output:
  set pair_id, file("${pair_id}.bam") into alignpe
  file("${pair_id}.flagstat.txt") into alignstats_pe
  file("${pair_id}.hisatout.txt") into hsatoutpe
  set file("${pair_id}_fastqc.zip"),file("${pair_id}_fastqc.html") into fastqcpe
  script:
  if (params.align == 'hisat')
  """
  module load hisat2/2.0.1-beta-intel samtools/intel/1.3 fastqc/0.11.2 picard/1.127 speedseq/20160506
  hisat2 -p 30 --no-unal --dta -x ${index_path}/${index_name} -1 ${fq1} -2 ${fq2} -S out.sam 2> ${pair_id}.hisatout.txt
  sambamba view -t 30 -f bam -S -o output.bam out.sam
  sambamba sort -t 30 -o ${pair_id}.bam output.bam
  sambamba flagstat -t 30 ${pair_id}.bam > ${pair_id}.flagstat.txt
  fastqc -f bam ${pair_id}.bam
  """
  else
  """
  module load star/2.4.2a samtools/intel/1.3 fastqc/0.11.2 picard/1.127 speedseq/20160506
  STAR --genomeDir ${index_path}/${star_index} --readFilesIn ${fq1} ${fq2} --readFilesCommand zcat --genomeLoad NoSharedMemory --outFilterMismatchNmax 999 --outFilterMismatchNoverReadLmax 0.04 --outFilterMultimapNmax 20 --alignSJoverhangMin 8 --alignSJDBoverhangMin 1 --alignIntronMin 20 --alignIntronMax 1000000 --alignMatesGapMax 1000000 --outSAMheaderCommentFile COfile.txt --outSAMheaderHD @HD VN:1.4 SO:coordinate --outSAMunmapped Within --outFilterType BySJout --outSAMattributes NH HI AS NM MD --outSAMstrandField intronMotif --outSAMtype BAM SortedByCoordinate --quantMode TranscriptomeSAM --sjdbScore 1 --limitBAMsortRAM 60000000000 --outFileNamePrefix out
  mv outLog.final.out ${pair_id}.hisatout.txt
  sambamba sort -t 30 -o ${pair_id}.bam outAligned.sortedByCoord.out.bam
  sambamba flagstat -t 30 ${pair_id}.bam > ${pair_id}.flagstat.txt
  fastqc -f bam ${pair_id}.bam
  """
}
process alignse {

  publishDir "$baseDir/output", mode: 'copy'
  cpus 32

  input:
  set pair_id, file(fq1) from trimse
  output:
  set pair_id, file("${pair_id}.bam") into alignse
  file("${pair_id}.flagstat.txt") into alignstats_se
  file("${pair_id}.hisatout.txt") into hsatoutse
  set file("${pair_id}_fastqc.zip"),file("${pair_id}_fastqc.html") into fastqcse
  script:
  if (params.align == 'hisat')
  """
  module load hisat2/2.0.1-beta-intel samtools/intel/1.3 fastqc/0.11.2 speedseq/20160506 picard/1.127
  hisat2 -p 30 --no-unal --dta -x ${index_path}/${index_name} -U ${fq1} -S out.sam 2> ${pair_id}.hisatout.txt
  sambamba view -t 30 -f bam -S -o output.bam out.sam
  sambamba sort -t 30 -o ${pair_id}.bam output.bam
  sambamba flagstat -t 30 ${pair_id}.bam > ${pair_id}.flagstat.txt
  fastqc -f bam ${pair_id}.bam
  """
  else
  """
  module load star/2.4.2a samtools/intel/1.3 fastqc/0.11.2 picard/1.127 speedseq/20160506
  STAR --genomeDir ${index_path}/${star_index} --readFilesIn ${fq1} --readFilesCommand zcat --genomeLoad NoSharedMemory --outFilterMismatchNmax 999 --outFilterMismatchNoverReadLmax 0.04 --outFilterMultimapNmax 20 --alignSJoverhangMin 8 --alignSJDBoverhangMin 1 --alignIntronMin 20 --alignIntronMax 1000000 --alignMatesGapMax 1000000 --outSAMheaderCommentFile COfile.txt --outSAMheaderHD @HD VN:1.4 SO:coordinate --outSAMunmapped Within --outFilterType BySJout --outSAMattributes NH HI AS NM MD --outSAMstrandField intronMotif --outSAMtype SAM --quantMode TranscriptomeSAM --sjdbScore 1 --limitBAMsortRAM 60000000000 --outFileNamePrefix out
  mv outLog.final.out ${pair_id}.hisatout.txt
  sambamba view -t 30 -f bam -S -o output.bam outAligned.out.sam
  sambamba sort -t 30 -o ${pair_id}.bam output.bam
  sambamba flagstat -t 30 ${pair_id}.bam > ${pair_id}.flagstat.txt
  fastqc -f bam ${pair_id}.bam
  """
}

// From here on we are the same for PE and SE, so merge channels and carry on

Channel
  .empty()
  .mix(alignse, alignpe)
  .tap { aligned2 }
  .set { aligned }

Channel
  .empty()
  .mix(alignstats_se, alignstats_pe)
  .set { alignstats }

Channel
  .empty()
  .mix(hsatoutse, hsatoutpe)
  .set { hsatout }

//
// Summarize all flagstat output
//
process parse_alignstat {

  publishDir "$baseDir/output", mode: 'copy'

  input:
  file(txt) from alignstats.toList()
  file(txt) from  hsatout.toList()

  output:
  file('alignment.summary.txt')

  """
  perl $baseDir/scripts/parse_flagstat.pl *.flagstat.txt
  """
}

//
// Identify duplicate reads with Picard
//
process markdups {

  memory '4GB'
  publishDir "$baseDir/output", mode: 'copy'

  input:
  set pair_id, file(sbam) from aligned
  output:
  set pair_id, file("${pair_id}.dedup.bam") into deduped1
  set pair_id, file("${pair_id}.dedup.bam") into deduped2
  script:
  if (params.markdups == 'mark')
  """
  module load picard/1.127 speedseq/20160506
  sambamba markdup -t 20 -r ${sbam} ${pair_id}.dedup.bam
  """
  else
  """
  cp ${sbam} ${pair_id}.dedup.bam
  """
}

//
// Read summarization with subread
//
process featurect {

  publishDir "$baseDir/output", mode: 'copy'
  cpus 32

  input:
  set pair_id, file(dbam) from deduped1
  file gtf_file
  output:
  file("${pair_id}.cts")  into counts
  """
  module load module subread/1.5.0-intel
  featureCounts -s params.stranded -T 30 -p -g gene_name -a ${gtf_file} -o ${pair_id}.cts ${dbam}
  """
}

//
// Assemble transcripts with stringtie
//

process stringtie {

  publishDir "$baseDir/output", mode: 'copy'
  cpus 32

  input:
  set pair_id, file(dbam) from deduped2
  file gtf_file
  output:
  file("${pair_id}_stringtie") into strcts
  """
  module load stringtie/1.1.2-intel
  mkdir ${pair_id}_stringtie
  cd ${pair_id}_stringtie
  stringtie ../${dbam} -p 30 -G ../${gtf_file} -B -e -o denovo.gtf -A ../geneabund.stringtie.tab
  """
}

process statanal {
   publishDir "$baseDir/output", mode: 'copy'
   input:
   file count_file from counts.toList()
   file design_file name 'design.txt'
   file genenames
   file geneset name 'geneset.gmt'
   output:
   file "*.txt" into txtfiles
   file "*.png" into psfiles
   file "*"
   """
   module load R/3.2.1-intel
   perl $baseDir/scripts/concat_cts.pl -o ./ *.cts
   cp design.txt design.shiny.txt
   cp geneset.gmt geneset.shiny.gmt
   Rscript  $baseDir/scripts/dea.R
   perl $baseDir/scripts/concat_edgeR.pl *.edgeR.txt
 """
}

process buildrda {
   publishDir "$baseDir/output", mode: 'copy'
   input:
   file stringtie_dir from strcts.toList()
   file design_file name 'design.txt'
   output:
   file "bg.rda" into rdafiles
   """
   module load R/3.2.1-intel
   Rscript $baseDir/scripts/build_ballgown.R *_stringtie
   """
 }


