#!/bin/Rscript

# Load libraries
library("ChIPseeker")

# Currently mouse or human

library("TxDb.Hsapiens.UCSC.hg19.knownGene")
library("TxDb.Mmusculus.UCSC.mm10.knownGene")
library("TxDb.Hsapiens.UCSC.hg38.knownGene")

source("http://bioconductor.org/biocLite.R")
if(!require("ChIPseeker")){
    biocLite("ChIPseeker")
}


# Create parser object
args <- commandArgs(trailingOnly=TRUE)

# Check input args
if (length(args) != 2) {
  stop("Usage: annotate_peaks.r [ annotate_design.tsv ] [ genome_assembly ]", call.=FALSE)
}

design_file <- args[1]
genome <-args[2]

# Load UCSC Known Genes
if(genome=='GRCh37') {
    txdb <- TxDb.Hsapiens.UCSC.hg19.knownGene
} else if(genome=='GRCm38')  {
    txdb <- TxDb.Mmusculus.UCSC.mm10.knownGene
} else if(genome=='GRCh38')  {
    txdb <- TxDb.Hsapiens.UCSC.hg38.knownGene
}

# Load design file
design <- read.csv(design_file, sep ='\t')
files <- as.list(as.character(design$Peaks))
names(files) <- design$Condition


peakAnnoList <- lapply(files, annotatePeak, TxDb=txdb, tssRegion=c(-3000, 3000), verbose=FALSE)

for(index in c(1:length(peakAnnoList))) {
  filename <- paste(names(files)[index],".chipseeker_annotation.xls",sep="")
  write.table(as.data.frame(peakAnnoList[[index]]),filename,sep="\t",quote=F)

  # Draw individual plots

  # Define names of Plots
  pie_name <- paste(names(files)[index],".chipseeker_pie.pdf",sep="")
  vennpie_name <- paste(names(files)[index],".chipseeker_vennpie.pdf",sep="")
  upsetplot_name <- paste(names(files)[index],".chipseeker_upsetplot.pdf",sep="")

  # Pie Plots
  pdf(pie_name)
  plotAnnoPie(peakAnnoList[[index]])
  dev.off()

  # Venn Diagrams
  pdf(vennpie_name)
  vennpie(peakAnnoList[[index]])
  dev.off()

  # Upset Plot
  pdf(upsetplot_name)
  upsetplot(peakAnnoList[[index]])
  dev.off()
}
