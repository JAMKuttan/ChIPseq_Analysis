#!/bin/Rscript

library(ChIPseeker)


# Create parser object
parser <- ArgumentParser()

# Specify our desired options
parser$add_argument("-d", "--design", help = "File path to design file", required = TRUE)
parser$add_argument("-g", "--genome", help = "The genome assembly", required = TRUE)

# Parse arguments
args <- parser$parse_args()


# Load UCSC Known Genes
if(args$genome=='GRCh37') {
    library(TxDb.Hsapiens.UCSC.hg19.knownGene)
    txdb <- TxDb.Hsapiens.UCSC.hg19.knownGene
} else if(args$genome=='GRCm38')  {
    library(TxDb.Mmusculus.UCSC.mm10.knownGene)
    txdb <- TxDb.Mmusculus.UCSC.mm10.knownGene
}
else if(args$genome=='GRCh38')  {
    library(TxDb.Hsapiens.UCSC.hg38.knownGene)
    txdb <- TxDb.Hsapiens.UCSC.hg38.knownGene
}


peakAnnoList <- lapply(files, annotatePeak, TxDb=txdb, tssRegion=c(-3000, 3000), verbose=FALSE)
for(index in c(1:length(peakAnnoList)))
{
  filename<-paste(names(files)[index],".chipseeker_annotation.xls",sep="")
  write.table(as.data.frame(peakAnnoList[[index]]),filename,sep="\t",quote=F)
  #draw individual plot
  pie_name <- paste(names(files)[index],".chipseeker_pie.pdf",sep="")
  vennpie_name <- paste(names(files)[index],".chipseeker_vennpie.pdf",sep="")
  upsetplot_name <- paste(names(files)[index],".chipseeker_upsetplot.pdf",sep="")
  pdf(pie_name)
  plotAnnoPie(peakAnnoList[[index]])
  dev.off()
  pdf(vennpie_name)
  vennpie(peakAnnoList[[index]])
  dev.off()
  pdf(upsetplot_name)
  upsetplot(peakAnnoList[[index]])
  dev.off()


}
