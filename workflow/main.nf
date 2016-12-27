#!/usr/bin/env nextflow
	
// Default parameter values to run tests
// params.bams="$baseDir/../test/*.bam"
params.design="$baseDir/../test/samplesheet.csv"
// params.genome="/project/shared/bicf_workflow_ref/GRCh37/"

// design_file = file(params.design)
// bams=file(params.bams)
//gtf_file = file("$params.genome/gencode.gtf")
//genenames = file("$params.genome/genenames.txt")
//geneset = file("$params.genome/gsea_gmt/$params.geneset")



process peakanno {
//   publishDir "$baseDir/output", mode: 'copy'
//   input:
//   file design_file from input
//   file annotation Tdx
   output:
     stdout result
//   set peak_id, file("${pattern}_annotation.xls"), file("${pattern}_peakTssDistribution.png") into peakanno
     script:
     """
     module load R/3.2.1-intel
     python $baseDir/scripts/process.py
     #Rscript /project/BICF/BICF_Core/bchen4/chipseq_analysis/workflow/scripts/runchipseeker.R     
"""
}

