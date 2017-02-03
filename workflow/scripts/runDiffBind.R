library("DiffBind")

#build dba object from sample sheet and do analysis
args <- commandArgs(TRUE)
data <- dba(sampleSheet=args[1])
data <- dba.count(data)
data <- dba.contrast(data, minMembers = 2, categories=DBA_CONDITION)
data <- dba.analyze(data)

#Draw figures
pdf("diffbind.samples.heatmap.pdf")
plot(data)
dev.off()

pdf("diffbind.samples.pca.pdf")
dba.plotPCA(data, DBA_TISSUE, label=DBA_CONDITION)
dev.off()

#Save peak reads count
normcount <- dba.peakset(data, bRetrieve=T)
write.table(as.data.frame(normcount),"diffbind.normcount.txt",sep="\t",quote=F,row.names=F)

#Retriving the differentially bound sites
#make new design file for chipseeker at the same time
new_SampleID = c()
new_Peaks = c()
for (i in c(1:length(data$contrasts)))
{
 contrast_bed_name = paste(data$contrasts[[i]]$name1,"vs",
                      data$contrasts[[i]]$name2,"diffbind.bed",sep="_")
 contrast_name = paste(data$contrasts[[i]]$name1,"vs",
                      data$contrasts[[i]]$name2,"diffbind.xls",sep="_")
 new_SampleID = c(new_SampleID,paste(data$contrasts[[i]]$name1,"vs",data$contrasts[[i]]$name2,sep="_"))
 new_Peaks = c(new_Peaks, contrast_bed_name)
 report <- dba.report(data, contrast=i, th=1, bCount=TRUE)
 report <- as.data.frame(report)
 print(head(report))
 colnames(report)[1:5]<-c("chrom","peak_start","peak_stop","peak_width","peak_strand")
 #print(head(report))
 write.table(report,contrast_name,sep="\t",quote=F,row.names=F)
 write.table(report,contrast_bed_name,sep="\t",quote=F,row.names=F, col.names=F)
}
#Write new design file
newdesign = data.frame(SampleID=new_SampleID, Peaks=new_Peaks)
write.csv(newdesign,"diffpeak.design",row.names=F,quote=F)
