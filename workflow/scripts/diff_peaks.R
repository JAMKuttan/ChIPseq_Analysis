#!/bin/Rscript

# Load libraries
library("DiffBind")

# Create parser object
args <- commandArgs(trailingOnly=TRUE)

# Check input args
if (length(args) != 1) {
  stop("Usage: diff_peaks.R annotate_design.tsv ", call.=FALSE)
}

# Build DBA object from design file
data <- dba(sampleSheet=args[1])
data <- dba.count(data)
data <- dba.contrast(data, minMembers = 2, categories=DBA_CONDITION)
data <- dba.analyze(data)

# Draw figures
pdf("heatmap.pdf")
plot(data)
dev.off()

pdf("pca.pdf")
dba.plotPCA(data, DBA_TISSUE, label=DBA_CONDITION)
dev.off()

# Save peak reads count
normcount <- dba.peakset(data, bRetrieve=T)
write.table(as.data.frame(normcount),"normcount_peaksets.txt",sep="\t",quote=F,row.names=F)

# Reteriving the differentially bound sites
# Make new design file for peakAnnotation at the same time
new_SampleID = c()
new_Peaks = c()
for (i in c(1:length(data$contrasts))) {
 contrast_bed_name = paste(data$contrasts[[i]]$name1,"vs",
                      data$contrasts[[i]]$name2,"diffbind.bed",sep="_")
 contrast_name = paste(data$contrasts[[i]]$name1,"vs",
                      data$contrasts[[i]]$name2,"diffbind.csv",sep="_")
 new_SampleID = c(new_SampleID,paste(data$contrasts[[i]]$name1,"vs",data$contrasts[[i]]$name2,sep="_"))
 new_Peaks = c(new_Peaks, contrast_bed_name)
 report <- dba.report(data, contrast=i, th=1, bCount=TRUE)
 report <- as.data.frame(report)
 colnames(report)[1:5]<-c("chrom","peak_start","peak_stop","peak_width","peak_strand")

 write.table(report,contrast_name,sep="\t",quote=F,row.names=F)
 write.table(report[,c(1:3)],contrast_bed_name,sep="\t",quote=F,row.names=F, col.names=F)
}
