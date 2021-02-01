#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Module containing Helper Functions dealing with uyuni System Groups
"""
import sys
try:
  from __main__ import prgdir,prgname
  import os.path
  exec(open(os.path.join(prgdir,prgname+"_imp.py")).read())
except:
  if sys.argv[0].find('pydoc'):
    pass # we are running from pydoc3
#######################################################################################      
#######################################################################################      
def get_systems_wo_group(ses,key,grplist,syslist,curgroup):
  """ Unterfunktion für Systeme, die in keiner Gruppe enthalten sind
  """
  from __main__ import dbg,prgargs,data
  dbg.entersub()
  nogrpsystems = ses.system.listUngroupedSystems(key)
  if len(nogrpsystems):
    curgroup = 'No_Group'
    grplist[curgroup] = {}
    grplist[curgroup]['description'] = "Systeme ohne Gruppenzuordnung"
    grplist[curgroup]['system_count'] = len(nogrpsystems)
    grplist[curgroup]['systems'] = {}
    for href in nogrpsystems:
      cursys = href['name']
      grplist[curgroup]['systems'][cursys] = 1
      if cursys not in syslist:
        syslist[cursys] = {}
        syslist[cursys]['group'] = curgroup
      for k2 in href: 
        if k2 not in ("name"):
          syslist[cursys][k2] = href[k2] 
  dbg.leavesub()      
  return(grplist,syslist)

#######################################################################################      
#######################################################################################      
def get_systems_by_group(ses,key,grplist,syslist,curgroup):
  """ Unterfunktionen für Systeme, die in Gruppen enthalten sind
  """
  from __main__ import dbg,prgargs,data
  dbg.entersub()
  systems = ses.systemgroup.listSystemsMinimal(key,curgroup)
  for shash in systems:
    cursys = shash['name']
    if cursys not in grplist[curgroup]['systems']:
      grplist[curgroup]['systems'][cursys] = 0
    grplist[curgroup]['systems'][cursys] += 1
    if cursys not in syslist:
      syslist[cursys] = {}
      syslist[cursys]['group'] = curgroup
    for k2 in shash:
      if k2 not in ("name"):
        syslist[cursys][k2] = shash[k2]
  dbg.leavesub()      
  return(grplist,syslist)

#######################################################################################      
#######################################################################################      
def get_all_sysgroups(ses,key,grplist,syslist):
  """ Hilfsfunktion zur Ermittlung der Systemgruppen.
  """
  from __main__ import dbg,prgargs,data
  dbg.entersub()
  groups  = ses.systemgroup.listAllGroups(key)
  for ghash in groups:
    curgroup = ghash['name']
    grplist[curgroup] = {}
    if 'systems' not in grplist[curgroup]:
      grplist[curgroup]['systems'] = {}
    for k in ghash :
      if k not in ("name"):
        grplist[curgroup][k] = ghash[k]
  dbg.leavesub()      
  return(grplist,syslist)

#######################################################################################      
#######################################################################################      
def Get_Group_List(ses,key,grplist,syslist):
  """ Creates two dictionaries for Systems and Systemgroups found on the uyuni server
      and returns them. If Systems without group exist, they will be sorted into the 
      special group 'No_Group'. 
  """    
  from __main__ import dbg,prgargs,data
  dbg.entersub()
  (grplist,syslist) = get_all_sysgroups(ses,key,grplist,syslist)
  for g in grplist:
    if g != 'No_Group':
      (grplist,syslist) = get_systems_by_group(ses,key,grplist,syslist,g)
  (grplist,syslist) = get_systems_wo_group(ses,key,grplist,syslist,'No_Group') 
  dbg.leavesub()
  return(grplist,syslist)

