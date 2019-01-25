#!/bin/bash

#SBATCH --job-name=CHIPseq
#SBATCH --partition=super
#SBATCH --output=CHIPseq.%j.out
#SBATCH --error=CHIPseq.%j.err

module load nextflow/0.31.0
module add  python/3.6.1-2-anaconda

nextflow run workflow/main.nf \
--reads '/path/to/*fastq.gz' \
--designFile '/path/to/design.txt' \
--genome 'GRCm38' \
--pairedEnd 'true'
