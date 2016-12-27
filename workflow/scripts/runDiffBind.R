library("DiffBind")

#build dba object from sample sheet and do analysis
data <- dba(sampleSheet="samplesheet.csv")
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
for (i in c(1:length(data$contrasts)))
{
 contrast_name = paste(data$contrasts[[i]]$name1,"vs",
                      data$contrasts[[i]]$name2,"diffbind.xls",sep="_")
 report <- dba.report(data, contrast=i, th=1, bCount=TRUE)
 write.table(as.data.frame(report),contrast_name,sep="\t",quote=F,row.names=F)
}

