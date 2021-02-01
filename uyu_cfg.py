#!/usr/bin/env python3
# -*- coding: utf8 -*-
""" --- This is only the configuration file ---"""
import sys,os
if sys.argv[0].find('pydoc') > 0 :
  print(__doc__); sys.exit(0)

from datetime import date
from __main__ import prgdir

data = {
  'savetop'  : os.path.join(prgdir,"data"), 
  'savename' : "sumastate.dump",
  'savefile' : '',
  'TrustSystemState' : False,
  'csvfile'  : '',
  'csvname'  : date.today().strftime("%Y-%m-%d") + '_suma.csv', 
  'maxage'   : 15,  # age of statefile in min
  'conn'     : { 
    'usr'       : "",
    'pwd'       : "",
    'url'       : "",
    'key'       : "",
    'ses'       : "",   
  },
  'sumastate'    : {
    'groups'     : {},
    'systems'    : {},
    'patches'    : {
      'sec'      : {},
      'bgf'      : {},
      'enh'      : {},
    },  
    'channels'   : {
      'byLabel'  : {},
      'byParent' : {},
    },
  },
  'patchtypenames' : {
    'sec': "Security Advisory",
    'bgf': "Bug Fix Advisory",
    'enh': "Product Enhancement Advisory"
  },
  'chmap'        : {
    '01_vendorclone'  : {},
    '02_datefreeze'   : {},
    '03_arcmerge'     : {},
    '04_promote'      : {},
  },  
  'contentexcludes'   : {
  },  
  'formats'  : {
    ##### Header mit Format für SystemStatus
    'systemstateheader' : "%-15s %-27s %-10s %-3s %4s %4s %4s %4s  %-10s" % (
                          'Group','Hostname', 
                          'lastboot', 'reb', 
                          'SecP', 'BgfP', 'EnhP', 'Pkgs',
                          'lastchkin'),
    #### Ausgabeformat der Werte für SystemStatus
    'systemstateline'   : "{0:15s} {1:27s} {2:10s} {3:3d} {4:4d} {5:4d} {6:4d} {7:4d}  {8:10s}",
    #####
    'channelheader'     : "%-56s %3s %5s %6s %-s" % (
                          "----- Label -----", "ID", "Pkgs","Errata","systems"),
    'channelparent'     : "\n%-56s %3d %5d %6d %3d",
    'channelchild'      : "\\_ %-53s %3d %5d %6d %3d",
    #####:w

    'patchcsvhead'      : 'Group;Type;Patchname;Description;CVEs;Systems',
    'patchcsvfmt'       : "%-s;%-s;%-s;%-s;%-s;%-s",
    'patchprnfmt'       : "%-12s %-4s %-25s %-25s %-18s %-s",
  },  
}
argdefaults = { 
  'debug'   : 0,
  'verbose' : 0,
  'config'  : 'SRV-default',
  'listmod' : False,
  'module'  : [],

} 