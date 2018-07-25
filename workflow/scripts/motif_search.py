#!/usr/bin/env python
# programmer : bbc
# usage:

import sys
import re
from re import sub
import string
import argparse as ap
import logging
import subprocess
import pandas as pd
from multiprocessing import Pool
logging.basicConfig(level=10)


def prepare_argparser():
  description = "Run memechip command"
  epilog = "For command line options of each command, type %(prog)% COMMAND -h"
  argparser = ap.ArgumentParser(description=description, epilog = epilog)
  argparser.add_argument("-i","--input",dest = "infile",type=str,required=True, help="input BED file")
#  argparser.add_argument("-o","--output",dest = "outfile",type=str,required=True, help="output")
  argparser.add_argument("-g","--genome",dest = "genome",type=str, help="Genome 2 bit file")
 # argparser.add_argument("-m","--mask",dest = "mask",type=bool,default=False, help="Convert repeats to N")
 # argparser.add_argument("-l","--limit",dest = "limit",type=int,default=-1, help="Top limit of peaks")
  return(argparser)

def rc(seq):
  comps = {'A':"T",'C':"G",'G':"C",'T':"A","N":"N"}
  return ''.join([comps[x] for x in seq.upper()[::-1]])

def main():
  argparser = prepare_argparser()
  args = argparser.parse_args()
  #run(args.infile, args.genome, args.limit, args.output)
  #get Pool ready
  dfile = pd.read_csv(args.infile, sep='\t')
  meme_arglist =  zip(dfile['Peaks'].tolist(),[args.genome]*dfile.shape[0],dfile['Condition'].tolist())
  work_pool = Pool(min(12,dfile.shape[0]))
  resultList =  work_pool.map(run_wrapper, meme_arglist)
  work_pool.close()
  work_pool.join()


def run_wrapper(args):
  run(*args)

def run(infile, genome, output):
  # Get fasta file
  fasta_command = "bedtools getfasta -fi "+genome+' -bed '+infile+' -fo '+output+'.fa'
  p = subprocess.Popen(fasta_command, shell=True)
  p.communicate()

  #Call memechip
  meme_command = "meme-chip -oc "+output+"_memechip"+" -meme-minw 5 -meme-maxw 15 -meme-nmotifs 10 "+output+".fa"
  p = subprocess.Popen(meme_command, shell=True)
  p.communicate()

if __name__=="__main__":
  main()
