args = commandArgs(trailingOnly=TRUE)
#if (length(args)==0) {
#  stop("At least one argument must be supplied (input file).n", call.=FALSE)
#} else if (length(args)==1) {
#  # default output file
#  args[3] = "out.txt"
#}

library(ChIPseeker)
library(TxDb.Hsapiens.UCSC.hg19.knownGene)
txdb <- TxDb.Hsapiens.UCSC.hg19.knownGene
#library(clusterProfiler)

#files = list.files(".")
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
#promoter <- getPromoters(TxDb=txdb, upstream=3000, downstream=3000)
#tagMatrixList <- lapply(files, getTagMatrix, windows=promoter)

#plotAvgProf(tagMatrixList, xlim=c(-3000, 3000), facet="row")

#overlappeakfiles <- as.list(list.files("overlappeaks/"))

