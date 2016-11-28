#!/usr/bin/env nextflow
	
// Default parameter values to run tests
params.bams="$baseDir/../test/*.bam"
params.design="$baseDir/../test/samplesheet.csv"
#params.genome="/project/shared/bicf_workflow_ref/GRCh37/"

design_file = file(params.design)
bams=file(params.bams)
#gtf_file = file("$params.genome/gencode.gtf")
#genenames = file("$params.genome/genenames.txt")
#geneset = file("$params.genome/gsea_gmt/$params.geneset")


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
    def header = hline.split(",")
    prefixidx = header.findIndexOf{it == 'Condition'};
    peakidx = header.findIndexOf{it == 'Peaks'};
    bamipidx = header.findIndexOf{it == 'bamReads'};
    bamctrlidx = header.findIndexOf{it == 'bamControl'};
    if (bamctrlidx == -1) {
       error "Must provide control BAM file"
       }      
    if (peakidx == -1) {
       error "Must provide peak file"
       }
    while (line = reader.readLine()) {
    	   def row = line.split(",")
	   if (fileMap.get(row[bamipidx]) != null) {
	      prefix << tuple(row[prefixidx],fileMap.get(row[peakidx]),fileMap.get(row[bamipidx]),fileMap.get(row[bamctrlidx]))
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


process peakanno {
   publishDir "$baseDir/output", mode: 'copy'
   input:
   file peak_file from greencenter
   file design_file from input
   file annotation Tdx
   output:
   set peak_id, file("${pattern}_annotation.xls"), file("${pattern}_peakTssDistribution.png") into peakanno
   """
   module load R/3.2.1-intel
   Rscript $baseDir/scripts/runchipseeker.R
   """
}

//Run deeptools for QC and other plots
//Since this problem also need all input files, need to build another channel?
process deeptools {
   publishDir "$baseDir/output", mode: 'copy'
   input: 
   file peak_file from input
   file bam_file from imput
   output:
   set

}

//Need to do it with more than 1 condition
process diffbind {
   publishDir "$baseDir/output", mode: 'copy'
   input:
   file peak_file from input
   file design_file name 'design.txt'
   file bam_file from input
   output:
   file "*.txt" into txtfiles
   file "*.png" into psfiles
   file "*"
   """
   module load R/3.2.1-intel
   #cp design.txt design.shiny.txt
   #cp geneset.gmt geneset.shiny.gmt
   Rscript  $baseDir/scripts/runDiffBind.R
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


