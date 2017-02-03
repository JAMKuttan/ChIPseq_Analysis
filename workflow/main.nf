#!/usr/bin/env nextflow
	
// Default parameter values to run tests
// params.bams="$baseDir/../test/*.bam"
   params.testpath="/project/BICF/BICF_Core/bchen4/chipseq_analysis/test/"
   params.design="/project/BICF/BICF_Core/bchen4/chipseq_analysis/test/samplesheet.csv"
   params.genomepath="/project/BICF/BICF_Core/bchen4/chipseq_analysis/test/genome/hg19/"
// design_file = file(params.design)
// bams=file(params.bams)
//gtf_file = file("$params.genome/gencode.gtf")
//genenames = file("$params.genome/genenames.txt")
//geneset = file("$params.genome/gsea_gmt/$params.geneset")


process processdesign {
   publishDir "$baseDir/output/", mode: 'copy'
//   input:
//   file design_file from input
//   file annotation Tdx
   output:
     file "new_design" into deeptools_design
     file "new_design" into diffbind_design

     script:
     """
     module load python/2.7.x-anaconda
     source activate /project/shared/bicf_workflow_ref/chipseq_bchen4/
     python $baseDir/scripts/preprocessDesign.py -i ${params.design} 
     """
}

//process run_deeptools {
//   publishDir "$baseDir/output", mode: 'copy'
//   input:
//     file deeptools_design_file from deeptools_design
//   file annotation Tdx
//   output:
//     stdout result
//     script:
//     """
//     module load python/2.7.x-anaconda
//     source activate /project/shared/bicf_workflow_ref/chipseq_bchen4/
//     module load deeptools/2.3.5 
//     python $baseDir/scripts/runDeepTools.py -i $deeptools_design_file -g ${params.genomepath}}
//"""
//}


process run_diffbind {
//   publishDir "$baseDir/output", mode: 'copy'
   input:
     file diffbind_design_file from diffbind_design
   output:
     file "*_diffbind.bed" into diffpeaks_chipseeker
     file "*_diffbind.bed" into diffpeaks_meme

     script:
     """
     module load python/2.7.x-anaconda
     source activate /project/shared/bicf_workflow_ref/chipseq_bchen4/
     Rscript $baseDir/scripts/runDiffBind.R $diffbind_design_file
"""
}

//process run_chipseeker {
//   publishDir "$baseDir/output", mode: 'copy'
//   input:
//     file diffbind_design_file from diffbind_design
//   file annotation Tdx
//   output:
//     file "*_diffbind.bed" into diffpeaks_chipseeker
//     file "*_diffbind.bed" into diffpeaks_meme
//
//     script:
//     """
//     module load python/2.7.x-anaconda
//     source activate /project/shared/bicf_workflow_ref/chipseq_bchen4/
//     Rscript $baseDir/scripts/runDiffBind.R $diffbind_design_file
//"""
//}

//process run_meme {
//   publishDir "$baseDir/output", mode: 'copy'
//   input:
//     file peaks_meme from diffpeaks_meme.flatten()
//   output:
//     stdout result
//     script:
//     """
//     module load python/2.7.x-anaconda
//     source activate /project/shared/bicf_workflow_ref/chipseq_bchen4/
//     module load meme/4.11.1-gcc-openmpi
//     python $baseDir/scripts/runMemechip.py -i $peaks_meme
//"""
//}
