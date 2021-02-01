#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" --- This is only the usage file ---"""
import argparse,sys,os
if sys.argv[0].find('pydoc') > 0 :
  print(__doc__); sys.exit(0)

from __main__ import prgname,dbg,cfg
class myFormatter(argparse.RawTextHelpFormatter,argparse.ArgumentDefaultsHelpFormatter): 
  pass

parser = argparse.ArgumentParser(formatter_class=myFormatter)
parser.add_argument('-d', type=int,default=cfg.argdefaults.debug, 
                          metavar="debug", dest="debug",        
                        help="set debug level to num\n\t\t")

args = parser.parse_args()
globals()['prgargs']  = args
dbg._initlvl(prgargs.debug) 
dbg.dprint(2, "prgargs" , prgargs)
