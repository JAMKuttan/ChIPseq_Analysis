args = commandArgs(trailingOnly=TRUE)
#if (length(args)==0) {
#  stop("At least one argument must be supplied (input file).n", call.=FALSE)
#} else if (length(args)==1) {
#  # default output file
#  args[3] = "out.txt"
#}

library(ChIPseeker)
if args[3]=="hg19"
{ 
library(TxDb.Hsapiens.UCSC.hg19.knownGene)
txdb <- TxDb.Hsapiens.UCSC.hg19.knownGene
}
if args[3]=="mm10"
{ 
library(TxDb.Hsapiens.UCSC.mm10.knownGene)
txdb <- TxDb.Hsapiens.UCSC.mm10.knownGene
}
if args[3]=="hg38"
{ 
library(TxDb.Hsapiens.UCSC.hg38.knownGene)
txdb <- TxDb.Hsapiens.UCSC.hg38.knownGene
}

files<-as.list(unlist(strsplit(args[1],",")))
names(files)<-as.list(unlist(strsplit(args[2],",")))
print(files)

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

