#!/bin/Rscript

#*
#* --------------------------------------------------------------------------
#* Licensed under MIT (https://git.biohpc.swmed.edu/BICF/Astrocyte/chipseq_analysis/LICENSE.md)
#* --------------------------------------------------------------------------
#*

#Currently Human or Mouse

# Load libraries
library("ChIPseeker")
library(GenomicFeatures)

# Create parser object
args <- commandArgs(trailingOnly=TRUE)

# Check input args
if (length(args) != 4) {
  stop("Usage: annotate_peaks.R annotate_design.tsv genome_assembly gtf geneNames", call.=FALSE)
}

design_file <- args[1]
genome_assembly <- args[2]
gtf <- args[3]
geneNames <- args[4]

# Load UCSC Known Genes
txdb <- makeTxDbFromGFF(gtf)
sym <- read.table(geneNames, header=T, sep='\t') [,4:5]

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
peakAnnoList <- lapply(peaks, annotatePeak, TxDb=txdb, tssRegion=c(-3000, 3000), verbose=FALSE)

column_names <- c("chr", "start", "end", "width", "strand_1", "name", "score", "strand", "signalValue",
                  "pValue", "qValue", "peak", "annotation", "geneChr", "geneStart", "geneEnd",
                  "geneLength" ,"geneStrand", "geneId", "transcriptId", "distanceToTSS", "symbol")

for(index in c(1:length(peakAnnoList))) {
  filename <- paste(names(peaks)[index], ".chipseeker_annotation.tsv", sep="")
  df <- as.data.frame(peakAnnoList[[index]])
  df_final <- merge(df, sym, by.x="geneId", by.y="ensembl", all.x=T)
  colnames(df_final) <- column_names
  write.table(df_final[ , !(names(df_final) %in% c('strand_1'))], filename, sep="\t" ,quote=F, row.names=F)

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
