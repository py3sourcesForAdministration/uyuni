#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""  Helper routine to check wether the environment is usable 
to run a program that depends on pydevlib project. 
"""
import os, os.path, sys, pprint

def set_libdir(libdir):
  """ inserts a new lib path into sys.path """
  if libdir not in sys.path: 
    sys.path.insert(0, libdir)

def chk_sufficient():
  """ routine to test for: python version and pydevlib
  if pydevlib is found inserts it into sys.path 
  Returns either the path of pydevlib or stops the program. """
  libdir = ''
  ### check if python version is sufficient
  if sys.version_info < (3,6):
    print("python should be at least version 3.6") ; sys.exit(1)
  ### check if pydevlib is available
  if 'PYDEVLIB' not in os.environ:
    print("you need to set os.environ['PYDEVLIB']") ;
  else:
    libdir = os.environ['PYDEVLIB']
    # print("found libdir in os.environ['PYDEVLIB']")
  if not libdir:
    sys.exit(1)
  else:     
    set_libdir(libdir)
    return libdir

def get_names(file):
  """ Returns the basename and the realpath of file. """
  (prgdir,fname) = os.path.split(os.path.realpath(file))
  (prgname,ext) = os.path.splitext(fname)
  return(prgname,prgdir)    



if __name__ == "__main__": 
  import platform
  libdir = chk_sufficient()
  print("ok - Python Version:", platform.python_version())  
  print("ok - libdir        :", libdir)  
  (prgname,prgdir) = get_names(__file__)
  print("ok - prgdir        :", prgdir)  
  if prgname:
    print("-------- ok --------\n")