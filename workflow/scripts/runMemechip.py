#!/qbrc/software/Python-2.7.7/bin/python
# programmer : bbc
# usage:

import sys
import re
from re import sub
import string
import argparse as ap
import logging
import twobitreader
import subprocess
import pybedtools
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
logging.basicConfig(level=10)


def prepare_argparser():
  description = "Run memechip command"
  epilog = "For command line options of each command, type %(prog)% COMMAND -h"
  argparser = ap.ArgumentParser(description=description, epilog = epilog)
  argparser.add_argument("-i","--input",dest = "infile",type=str,required=True, help="input BED file")
  argparser.add_argument("-o","--output",dest = "outfile",type=str,required=True, help="output")
  argparser.add_argument("-g","--genome",dest = "genome",type=str, help="Genome 2 bit file")
  argparser.add_argument("-m","--mask",dest = "mask",type=bool,default=False, help="Convert repeats to N")
  argparser.add_argument("-l","--limit",dest = "limit",type=int,default=-1, help="Top limit of peaks")
  return(argparser)

def rc():
  comps = {'A':"T",'C':"G",'G':"C",'T':"A","N":"N"}
  return ''.join([comps[x] for x in seq.upper()[::-1]])

def main():
  argparser = prepare_argparser()
  args = argparser.parse_args()
  run(args.infile, args.genome, args.limit, args.output)

def run(infile, genome, limit, output):
  infile = pybedtools.BedTool(infile)
  genome = twobitreader.TwoBitFile(genome)
  outfile = open(output+".fa","w")
  rowcount = 1
  limit = int(limit)
  if limit ==-1:
    limit = len(infile)
  for record in infile:
    while rowcount <=limit:
      rowcount += 1
      try:
        seq = genome[record.chrom][record.start:record.stop]
      except:
        pass
      else:
        if record.strand == "-":
          seq = rc(seq)
        newfa_name = record.name#"_".join(record.fields)
        newfa = SeqRecord(Seq(seq),newfa_name,description="")
        SeqIO.write(newfa,output+".fa","fasta")
    outfile.close()
  #Call memechip
  meme_command = "meme-chip -oc "+output+"_memechip"+" -meme-minw 5 -meme-maxw 15 -meme-nmotifs 10 "+output+".fa"
  p = subprocess.Popen(meme_command, shell=True)
  p.communicate()
 
if __name__=="__main__":
  main()
