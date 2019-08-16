#!/bin/bash
#plotProfile.sh

bws=$(ls *.bw)
gtf=$(ls *.gtf *.bed)

computeMatrix reference-point \
	--referencePoint TSS \
	-S $bws \
	-R $gtf \
	--skipZeros \
	-o computeMatrix.gz
	-p max/2

plotProfile -m computeMatrix.gz \
	-out plotProfile.png \
