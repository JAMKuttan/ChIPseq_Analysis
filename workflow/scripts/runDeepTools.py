#!/usr/bin/python
# programmer : bbc
# usage:

import sys
import argparse as ap
import logging
import subprocess
import pandas as pd
from multiprocessing import Pool
logging.basicConfig(level=10)


def prepare_argparser():
  description = "Make wig file for given bed using bam"
  epilog = "For command line options of each command, type %(prog)% COMMAND -h"
  argparser = ap.ArgumentParser(description=description, epilog = epilog)
  argparser.add_argument("-i","--input",dest = "infile",type=str,required=True, help="input BAM file")
  argparser.add_argument("-g","--genome",dest = "genome",type=str,required=True, help="genome", default="hg19")
  #argparser.add_argument("-b","--bed",dest="bedfile",type=str,required=True, help = "Gene locus in bed format")
  #argparser.add_argument("-s","--strandtype",dest="stranded",type=str,default="none", choices=["none","reverse","yes"])
  #argparser.add_argument("-n","--name",dest="trackName",type=str,default="UserTrack",help = "track name for bedgraph header")
  return(argparser)

def run_qc(files, controls, labels):
  mbs_command = "multiBamSummary bins --bamfiles "+' '.join(files)+" -out sample_mbs.npz"
  p = subprocess.Popen(mbs_command, shell=True)
  #logging.debug(mbs_command)
  p.communicate()
  pcor_command = "plotCorrelation -in sample_mbs.npz --corMethod spearman --skipZeros --plotTitle \"Spearman Correlation of Read Counts\" --whatToPlot heatmap --colorMap RdYlBu --plotNumbers  -o experiment.deeptools.heatmap_spearmanCorr_readCounts_v2.png --labels "+" ".join(labels)
  #logging.debug(pcor_command)
  p = subprocess.Popen(pcor_command, shell=True)
  p.communicate()
  #plotCoverage
  pcov_command = "plotCoverage -b "+" ".join(files)+" --plotFile experiment.deeptools_coverage.png -n 1000000 --plotTitle \"sample coverage\" --ignoreDuplicates --minMappingQuality 10"
  p = subprocess.Popen(pcov_command, shell=True)
  p.communicate()
  #draw fingerprints plots
  for treat,ctrl,name in zip(files,controls,labels):
    fp_command = "plotFingerprint -b "+treat+" "+ctrl+" --labels "+name+" control --plotFile "+name+".deeptools_fingerprints.png"
    p = subprocess.Popen(fp_command, shell=True)
    p.communicate()

def bam2bw_wrapper(command):
  p = subprocess.Popen(command, shell=True)
  p.communicate()

def run_signal(files, labels, genome):
  #compute matrix and draw profile and heatmap
  gene_bed = "/project/BICF/BICF_Core/bchen4/chipseq_analysis/test/genome/"+genome+"/gene.bed"
  bw_commands = []
  for f in files:
    bw_commands.append("bamCoverage -bs 10 -b "+f+" -o "+f.replace("bam","bw"))
  work_pool = Pool(min(len(files), 12))
  work_pool.map(bam2bw_wrapper, bw_commands)
  work_pool.close()
  work_pool.join()
  
  cm_command = "computeMatrix scale-regions -R "+gene_bed+" -a 3000 -b 3000 --regionBodyLength 5000 --skipZeros -S *.bw -o samples.deeptools_generegionscalematrix.gz"
  p = subprocess.Popen(cm_command, shell=True)
  p.communicate()
  hm_command = "plotHeatmap -m samples.deeptools_generegionscalematrix.gz -out samples.deeptools_readsHeatmap.png"
  p = subprocess.Popen(hm_command, shell=True)
  p.communicate()  

def run(dfile,genome):
  #parse dfile, suppose data files are the same folder as design file
  dfile = pd.read_csv(dfile)
  #QC: multiBamSummary and plotCorrelation
  run_qc(dfile['bamReads'], dfile['bamControl'], dfile['SampleID']) 
  #signal plots
  run_signal(dfile['bamReads'],dfile['SampleID'],genome)

def main():
  argparser = prepare_argparser()
  args = argparser.parse_args()
  run(args.infile, args.genome)
  

if __name__=="__main__":
  main()
