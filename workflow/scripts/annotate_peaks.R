#!/bin/Rscript

# Load libraries
library("ChIPseeker")

# Currently mouse or human

library("TxDb.Hsapiens.UCSC.hg19.knownGene")
library("TxDb.Mmusculus.UCSC.mm10.knownGene")
library("TxDb.Hsapiens.UCSC.hg38.knownGene")
library("org.Hs.eg.db")
library("org.Mm.eg.db")


# Create parser object
args <- commandArgs(trailingOnly=TRUE)

# Check input args
if (length(args) != 2) {
  stop("Usage: annotate_peaks.R annotate_design.tsv genome_assembly", call.=FALSE)
}

design_file <- args[1]
genome_assembly <- args[2]

# Load UCSC Known Genes
if(genome_assembly=='GRCh37') {
    txdb <- TxDb.Hsapiens.UCSC.hg19.knownGene
    annodb <- 'org.Hs.eg.db'
} else if(genome_assembly=='GRCm38')  {
    txdb <- TxDb.Mmusculus.UCSC.mm10.knownGene
    annodb <- 'org.Mm.eg.db'
} else if(genome_assembly=='GRCh38')  {
    txdb <- TxDb.Hsapiens.UCSC.hg38.knownGene
    annodb <- 'org.Hs.eg.db'
}

# Output version of ChIPseeker
chipseeker_version = packageVersion('ChIPseeker')
write.table(paste("Version", chipseeker_version), file = "version_ChIPseeker.txt", sep = "\t",
            row.names = FALSE, col.names = FALSE)

# Load design file
design <- read.csv(design_file, sep ='\t')
files <- as.list(as.character(design$Peaks))
names(files) <- design$Condition

# Granges of files

peaks <- lapply(files, readPeakFile, as = "GRanges", header = FALSE)
peakAnnoList <- lapply(peaks, annotatePeak, TxDb=txdb, annoDb=annodb, tssRegion=c(-3000, 3000), verbose=FALSE)

column_names <- c("chr", "start", "end", "width", "strand_1", "name", "score", "strand", "signalValue",
                  "pValue", "qValue", "peak", "annotation", "geneChr", "geneStart", "geneEnd",
                  "geneLength" ,"geneStrand", "geneId", "transcriptId", "distanceToTSS",
                  "ENSEMBL", "symbol", "geneName")

for(index in c(1:length(peakAnnoList))) {
  filename <- paste(names(peaks)[index], ".chipseeker_annotation.tsv", sep="")
  df <- as.data.frame(peakAnnoList[[index]])
  colnames(df) <- column_names
  write.table(df[ , !(names(df) %in% c('strand_1'))], filename, sep="\t" ,quote=F, row.names=F)

  # Draw individual plots

  # Define names of Plots
  pie_name <- paste(names(files)[index],".chipseeker_pie.pdf",sep="")
  upsetplot_name <- paste(names(files)[index],".chipseeker_upsetplot.pdf",sep="")

  # Pie Plots
  pdf(pie_name)
  plotAnnoPie(peakAnnoList[[index]])
  dev.off()

  # Upset Plot
  pdf(upsetplot_name, onefile=F)
  upsetplot(peakAnnoList[[index]])
  dev.off()
}
