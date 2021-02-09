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
parser.set_defaults(**cfg.argdefaults)

parser.add_argument('-d', type=int,default=cfg.argdefaults.debug, 
                          metavar="debug", dest="debug",        
                        help="set debug level to num\t")
parser.add_argument('-v', action='count', dest="verbose", 
                            help="increase verbosity\t") 
parser.add_argument('-L', action='store_true', dest="log",
                        help="write log file \t\t")
parser.add_argument('-c', type=str,default="SRV-default",metavar="Config",
                            dest="config",       
                            help="configuration to use\t")                        
parser.add_argument('-x', nargs='+',metavar="xargs",default=[],
                            dest="xargs",       
                            help="filter args for module\t")                        
req = parser.add_argument_group('required')
group = req.add_mutually_exclusive_group(required=True)
group.add_argument('-l',action='store_true', dest="listmod",default=argparse.SUPPRESS,
                        help="show the available modules to execute")
group.add_argument('-e',nargs='+', default=argparse.SUPPRESS, 
                        metavar=("mod","opt") , dest="module", 
                        help="module and options execute\n\n")
                      
args = parser.parse_args()
globals()['prgargs']  = args
dbg._initlvl(prgargs.debug,verbose=prgargs.verbose) 
dbg.dprint(2, "prgargs" , prgargs)
