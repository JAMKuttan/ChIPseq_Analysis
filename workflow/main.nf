#!/usr/bin/env nextflow
   params.design="$baseDir/../test_data/samplesheet.csv"
   params.bams = "$baseDir/../test_data/*.bam"
   params.bais = "$baseDir/../test_data/*.bai"
   params.peaks = "$baseDir/../test_data/*.broadPeak"
   params.genomepath="/project/shared/bicf_workflow_ref/hg19/"
   species = "hg19"
   toppeakcount = 200
   design_file = file(params.design)
   deeptools_design = Channel.fromPath(params.design)
   diffbind_design = Channel.fromPath(params.design)
   chipseeker_design = Channel.fromPath(params.design)
   meme_design = Channel.fromPath(params.design)
   index_bams = Channel.fromPath(params.bams)
   deeptools_bams = Channel.fromPath(params.bams) 
   deeptools_peaks = Channel.fromPath(params.peaks) 
   chipseeker_peaks = Channel.fromPath(params.peaks) 
   diffbind_bams = Channel.fromPath(params.bams) 
   diffbind_peaks = Channel.fromPath(params.peaks) 
   meme_peaks = Channel.fromPath(params.peaks)
   deeptools_bamindex = Channel.fromPath(params.bais)
   diffbind_bamindex = Channel.fromPath(params.bais) 

//process bamindex {
//   publishDir "$baseDir/output/", mode: 'copy'
//   input:
//     file index_bam_files from index_bams
//   output:
//     file "*bai" into deeptools_bamindex
//     file "*bai" into diffbind_bamindex
//
//   script:
//     """
//     module load python/2.7.x-anaconda
//     module load R/3.3.2-gccmkl
//     module load samtools/intel/1.3
//     samtools index $index_bam_files
//     """
//}

process run_deeptools {
   publishDir "$baseDir/output", mode: 'copy'
   input:
     file deeptools_design_file from deeptools_design
     file deeptools_bam_files from deeptools_bams.toList()
     file deeptools_peak_files from deeptools_peaks.toList()
     file deeptools_bam_indexes from deeptools_bamindex.toList()
   output:
     file "*deeptools*" into deeptools_output
     script:
     """
     module load python/2.7.x-anaconda
     module load R/3.3.2-gccmkl
     module load deeptools/2.3.5
     python $baseDir/scripts/runDeepTools.py -i ${params.design} -g ${params.genomepath}}
"""
}


process run_diffbind {
   publishDir "$baseDir/output", mode: 'copy'
   input:
     file diffbind_design_file from diffbind_design
     file diffbind_bam_files from diffbind_bams.toList()
     file diffbind_peak_files from diffbind_peaks.toList()
     file diffbind_bam_indexes from diffbind_bamindex.toList()
   output:
     file "diffpeak.design" into diffpeaksdesign_chipseeker
     file "diffpeak.design" into diffpeaksdesign_meme
     file "*_diffbind.bed" into diffpeaks_meme
     file "*_diffbind.bed" into diffpeaks_chipseeker
   script:
     """
     module load python/2.7.x-anaconda
     module load R/3.3.2-gccmkl
     Rscript $baseDir/scripts/runDiffBind.R $diffbind_design_file
"""
}

process run_chipseeker_diffpeak {
   publishDir "$baseDir/output", mode: 'copy'
   input:
     file diffpeak_design_file from diffpeaksdesign_chipseeker
     file diffpeaks from diffpeaks_chipseeker
   output:
     file "*chipseeker*" into chipseeker_diffpeak_output
   script:
     """
     module load python/2.7.x-anaconda
     module load R/3.3.2-gccmkl
     Rscript $baseDir/scripts/runChipseeker.R $diffpeak_design_file hg19
"""
}

process run_chipseeker_originalpeak {
   publishDir "$baseDir/output", mode: 'copy'
   input:
     file design_file from chipseeker_design
     file chipseeker_peak_files from chipseeker_peaks.toList()
   output:
     file "*chipseeker*" into chipseeker_originalpeak_output
   script:
     """
     module load python/2.7.x-anaconda
     module load R/3.3.2-gccmkl
     Rscript $baseDir/scripts/runChipseeker.R $design_file ${species}
"""
}

process run_meme_original {
   publishDir "$baseDir/output", mode: 'copy'
   input:
     file design_meme from meme_design
     file meme_peak_files from meme_peaks.toList()
   output:
     file "*meme*" into meme_original_output
   script:
     """
     module load python/2.7.x-anaconda
     module load R/3.3.2-gccmkl
     module load meme/4.11.1-gcc-openmpi
     python $baseDir/scripts/runMemechip.py -i $design_meme -g ${params.genomepath} -l ${toppeakcount}
"""
}

process run_meme_diffpeak {
   publishDir "$baseDir/output", mode: 'copy'
   input:
     file peaks_meme from diffpeaks_meme
     file diffpeak_design from diffpeaksdesign_meme
   output:
     file "*meme*" into meme_diffpeak_output
   script:
     """
     module load python/2.7.x-anaconda
     module load R/3.3.2-gccmkl
     module load meme/4.11.1-gcc-openmpi
     python $baseDir/scripts/runMemechip.py -i $diffpeak_design -g ${params.genomepath} -l ${toppeakcount}
"""
}

