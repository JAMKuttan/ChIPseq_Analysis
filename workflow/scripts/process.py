#!/usr/bin/python
# programmer : bbc
# usage: main function to call all the procedures for chip-seq analysis
import sys
import os
import argparse as ap
import logging
import pandas as pd
import glob
import subprocess
from multiprocessing import Pool
import runDeepTools
import runMemechip
logging.basicConfig(level=10)


def prepare_argparser():
  description = "Make wig file for given bed using bam"
  epilog = "For command line options of each command, type %(prog)% COMMAND -h"
  argparser = ap.ArgumentParser(description=description, epilog = epilog)
  argparser.add_argument("-i","--input",dest = "infile",type=str,required=True, help="input design file")
  argparser.add_argument("-g","--genome",dest = "genome",type=str,required=True, help="genome", default="hg19")
  argparser.add_argument("--top-peak",dest="toppeak",type=int, default=-1, help = "Only use top peaks for motif call")
  #argparser.add_argument("-s","--strandtype",dest="stranded",type=str,default="none", choices=["none","reverse","yes"])
  #argparser.add_argument("-n","--name",dest="trackName",type=str,default="UserTrack",help = "track name for bedgraph header")
  return(argparser)

def memechip_wrapper(args):
  #print args  
  runMemechip.run(*args)

def main():
  argparser = prepare_argparser()
  args = argparser.parse_args()
  #dfile = pd.read_csv(args.infile)

  #for testing, add testing path to all input files
  test_path = "/project/BICF/BICF_Core/bchen4/chipseq_analysis/test/"
  designfile = pd.read_csv(args.infile)
  designfile['Peaks'] = designfile['Peaks'].apply(lambda x: test_path+x)
  designfile['bamReads'] = designfile['bamReads'].apply(lambda x: test_path+x)
  designfile['bamControl'] = designfile['bamControl'].apply(lambda x: test_path+x)
  designfile.to_csv(args.infile+"_new",index=False)
  dfile = pd.read_csv(args.infile+"_new")
  #call deeptools
  runDeepTools.run(args.infile+"_new", args.genome) 
  #call diffbind
  this_script = os.path.abspath(__file__).split("/")
  folder = "/".join(this_script[0:len(this_script)-1])
  
  diffbind_command = "Rscript "+folder+"/runDiffBind.R "+args.infile+"_new"
  #logging.debug(diffbind_command)
  p = subprocess.Popen(diffbind_command, shell=True)
  p.communicate()
  #call chipseeker on original peaks and overlapping peaks
  chipseeker_command = "Rscript "+folder+"/runChipseeker.R "+",".join(dfile['Peaks'].tolist())+" "+",".join(dfile['SampleID'])
#BC##  logging.debug(chipseeker_command)
  p = subprocess.Popen(chipseeker_command, shell=True)
  p.communicate()
  overlapping_peaks = glob.glob('*diffbind.bed')
  overlapping_peak_names = []
  for pn in overlapping_peaks:
    overlapping_peak_names.append(pn.split("_diffbind")[0].replace("!","non"))
  chipseeker_overlap_command = "Rscript "+folder+"/runChipseeker.R "+",".join(overlapping_peaks)+" "+",".join(overlapping_peak_names)
  p = subprocess.Popen(chipseeker_overlap_command, shell=True)
  p.communicate()
  #MEME-chip on all peaks
  meme_arglist =  zip(dfile['Peaks'].tolist(),[test_path+"hg19.2bit"]*dfile.shape[0],[str(args.toppeak)]*dfile.shape[0],dfile['SampleID'].tolist())
#BC#  #print meme_arglist
  work_pool = Pool(min(12,dfile.shape[0]))
  resultList = work_pool.map(memechip_wrapper, meme_arglist)
  work_pool.close()
  work_pool.join()
 

if __name__=="__main__":
  main()
