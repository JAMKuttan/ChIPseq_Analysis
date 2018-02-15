# BICF ChIP-seq Pipeline

[![Build Status](https://git.biohpc.swmed.edu/BICF/Astrocyte/chipseq_analysis/badges/master/build.svg)](https://git.biohpc.swmed.edu/BICF/Astrocyte/chipseq_analysis/commits/master)
[![Coverage Report](https://git.biohpc.swmed.edu/BICF/Astrocyte/chipseq_analysis/badges/master/coverage.svg)](https://git.biohpc.swmed.edu/BICF/Astrocyte/chipseq_analysis/commits/master)
[![Nextflow](https://img.shields.io/badge/nextflow-%E2%89%A50.24.0-brightgreen.svg
)](https://www.nextflow.io/)
[![Astrocyte](https://img.shields.io/badge/astrocyte-%E2%89%A50.1.0-blue.svg)](https://astrocyte-test.biohpc.swmed.edu/static/docs/index.html)


## Introduction
BICF ChIPseq is a bioinformatics best-practice analysis pipeline used for ChIP-seq (chromatin immunoprecipitation sequencing) data analysis at [BICF](http://www.utsouthwestern.edu/labs/bioinformatics/) at [UT Southwestern Dept. of Bioinformatics](http://www.utsouthwestern.edu/departments/bioinformatics/).

The pipeline uses [Nextflow](https://www.nextflow.io), a bioinformatics workflow tool. It pre-processes raw data from FastQ inputs, aligns the reads and performs extensive quality-control on the results.

This pipeline is primarily used with a SLURM cluster on the [BioHPC Cluster](https://biohpc.swmed.edu/). However, the pipeline should be able to run on any system that Nextflow supports.

Additionally, the pipeline is designed to work with [Astrocyte Workflow System](https://astrocyte-test.biohpc.swmed.edu/static/docs/index.html) using a simple web interface.
