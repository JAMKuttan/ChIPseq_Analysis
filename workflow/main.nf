#!/usr/bin/env nextflow
	
// Default parameter values to run tests
// params.bams="$baseDir/../test/*.bam"
   params.testpath="/project/BICF/BICF_Core/bchen4/chipseq_analysis/test/"
   params.design="/project/BICF/BICF_Core/bchen4/chipseq_analysis/test/samplesheet.csv"
   params.genome="/project/shared/bicf_workflow_ref/GRCh37/"

// design_file = file(params.design)
// bams=file(params.bams)
//gtf_file = file("$params.genome/gencode.gtf")
//genenames = file("$params.genome/genenames.txt")
//geneset = file("$params.genome/gsea_gmt/$params.geneset")



process run_chipseq_analysis {
//   publishDir "$baseDir/output", mode: 'copy'
//   input:
//   file design_file from input
//   file annotation Tdx
   output:
     stdout result
     script:
     """
     module load python/2.7.x-anaconda
     module load meme/4.11.1-gcc-openmpi
     source activate /project/shared/bicf_workflow_ref/chipseq_bchen4/
     module load deeptools/2.3.5 
     module load meme/4.11.1-gcc-openmpi     
     python $baseDir/scripts/process.py -i ${params.design} -g hg19 --top-peak 200
"""
}

