#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Module containing Helper Functions dealing with Patches for uyuni Systems
"""
import sys
try:
  from __main__ import prgdir,prgname
  import os.path
  exec(open(os.path.join(prgdir,prgname+"_imp.py")).read())
except:
  if sys.argv[0].find('pydoc'):
    pass # we are running from pydoc3

##############################################################################
def get_Patches_for_all_Systems(ses,key,syslist,patlist):
  """ Get all Patchinfo for the Systems in syslist, fillup syslist, create a new dict
      for all patches and return these two dictionaries
  """    
  from __main__ import dbg,prgargs,data
  dbg.entersub()
  typenames = data['patchtypenames']
  checkinlist = ses.system.listSystems(key)
  for sys in checkinlist:
     syslist[sys['name']]['last_boot'] = sys['last_boot']
     syslist[sys['name']]['last_checkin'] = sys['last_checkin']
  reboot = ses.system.listSuggestedReboot(key)
  for sys in reboot:
    syslist[sys['name']]['reboot'] = 1
  ### über alle Systeme  
  for system in syslist:
    sysid    =  syslist[system]['id']
    syslist[system]['old'] = 0
    if 'reboot' not in syslist[system]:
      syslist[system]['reboot'] = 0
    totnum = 0
    for etyp in ('sec','bgf','enh'):
      if etyp not in patlist:
        patlist[etyp] = {}
      errata = ses.system.getRelevantErrataByType(key,sysid,typenames[etyp])
      syslist[system][etyp] = len(errata)
      totnum += len(errata)
      ##### get patches
      for pat in errata:
        pname = pat['advisory_name']
        if 'patches' not in syslist[system]:
          syslist[system]['patches'] = {}
        if etyp not in syslist[system]['patches']:
          syslist[system]['patches'][etyp] = {}
        syslist[system]['patches'][etyp][pname] = syslist[system]['patches'][etyp].get(pname,1)
        if pname not in patlist[etyp]:
          patlist[etyp][pname] = {}
          patlist[etyp][pname]['systems'] = {}
          patlist[etyp][pname]['desc']    = pat
          cves = ses.errata.listCves(key,pname)
          if len(cves) != 0:
            if 'cves' not in patlist[etyp][pname]:
              patlist[etyp][pname]['cves'] = {}
            for cve in cves:
              patlist[etyp][pname]['cves'][cve] = patlist[etyp][pname]['cves'].get(cve,1)
        patlist[etyp][pname]['systems'][system] = patlist[etyp][pname]['systems'].get(system,1)

    updates = ses.system.listLatestUpgradablePackages(key,sysid)
    syslist[system]['updates'] = len(updates)
    totnum += len(updates)
    if totnum > 0:
      syslist[system]['old'] = 1
    else: 
      syslist[system]['old'] = 0

  dbg.leavesub()
  return(syslist,patlist)

##############################################################################
def create_savefile(savefile):
  """ Create a new statefile if it does not yet exist
  """
  from __main__ import dbg,data
  #import mysumacalls
  dbg.entersub()
  mysumacalls.UpdateStateFile(savefile)
  dbg.leavesub()

##############################################################################
def check_savefile(savefile):
  """ checks for the age of statefile. If file is younger than data['maxage'] returns 0,
      else returns the differnce (older than data['maxage']) in seconds.
  """
  from __main__ import prgname,dbg,data
  #import time,os,datetime
  dbg.entersub()
  overdue = 0
  if not os.path.exists(savefile):
    create_savefile(savefile)
    dbg.dprint(0, "Created new Systemstate")
  f_age = time.time() - os.path.getmtime(savefile)
  max_s = (data['maxage'] * 60)
  if ( f_age > max_s ):
    overdue = f_age
    #f_age = str(datetime.timedelta(seconds=f_age))
    #dbg.dprint(0, "SystemState is",f_age,"old, Information may be outdated")
  dbg.leavesub()  
  return(overdue)

##############################################################################
def read_savefile(savefile):
  """ Read the statefile, overwrite data['sumastate']  
  """
  from __main__ import prgname,dbg,data
  #import time,os,pickle
  dbg.entersub()
  with open(savefile,'rb') as f:
    data['sumastate'] = pickle.load(f)

  dbg.dprint(4,"Start data.sumastate", data['sumastate'], "End data.sumastate")
  dbg.leavesub()  
  return()

##############################################################################
def write_savefile(savefile):
  """ write data['sumastate'] to savefile 
  """
  from __main__ import prgname,dbg,data
  #import time,os,pickle
  dbg.entersub()
  with open(savefile,'wb') as f:
    dbg.dprint(2,"Creating fresh Systemstate in",savefile)
    pickle.dump(data['sumastate'],f)

  dbg.leavesub()  
  return()

##############################################################################
def get_patch_difference(source,target):
  """  check errata of source and target channel for differences and print
  the errata names. To prevent problems with clone names, target should be 
  the cloned channel.
  """  
  from __main__ import dbg,prgargs,data
  dbg.entersub()
  #print("LEVEL",dbg.setlvl())
  ses = data['conn']['ses']
  key = data['conn']['key']  
  typenames = data['patchtypenames']
  ##### Check if channels exist
  clist = ses.channel.listSoftwareChannels(key)
  source_exists = next((True for channel in clist if channel['label'] == source),False)
  target_exists = next((True for channel in clist if channel['label'] == target),False)
  if source_exists and target_exists:
    srcerrata = ses.channel.software.listErrata(key,source)
    tgterrata = ses.channel.software.listErrata(key,target)
    srcnames = set(d['advisory_name'].replace('CL-','',1) for d in srcerrata)
    tgtnames = set(d['advisory_name'].replace('CL-','',1) for d in tgterrata)
    srconly  = sorted(list(srcnames.difference(tgtnames)))
    #dbg.dprint(256,'srconly',sorted(srconly))
    #srconly  = sorted(srconly)
    #dbg.dprint(256,type(srconly))
    #return
    #dbg.dprint(0,"Start Missing Errata in target",srconly, "End Missing Errata in target")
    chunknum = 0
    chunk = []
    for errnum in range(0,len(srconly)):
      #if errnum // 10 == chunknum:
        #chunk.append(srconly[errnum])
      #else :
        #dbg.dprint(0, "chunk", chunk)
        #chunk = []
        #chunknum += 1
        #chunk.append(srconly[errnum])
      err = srconly[errnum]
      errdetail = ses.errata.getDetails(key,err)
      errpkgs   = ses.errata.listPackages(key,err)
      #print( "----- {} --- id: {:7d} {}".format(
              #err,errdetail['id'],errdetail['last_modified_date']))
      dbg.dprint(0, f"{err:33s}   id:{errdetail['id']:7d}")
      dbg.dprint(64, f"  Type:                     {errdetail['type']}")
      dbg.dprint(64, f"  Synopsis:                 {errdetail['synopsis']}")
      dbg.dprint(64, f"  Date:                     {errdetail['last_modified_date']}")  
      #print( "  Topic:    {}".format(errdetail['topic']))
      dbg.dprint(128, f"  -- Packages affected")  
      for pkgnum in range(0,len(errpkgs)): 
        pkg = errpkgs[pkgnum]
        pkgstring = "".join( [ f"     Id:{pkg['id']:6d}, ", f"N: {pkg['name']:30}, ",
          #f"V: {pkg['version']:7}, ", f"R: {pkg['release']:7}, ", f"File:{pkg['file']}" ])
          f"V: {pkg['version']:7}, ", f"R: {pkg['release']:7}" ])
        dbg.dprint(128,pkgstring)    
      #dbg.dprint(0, "Start Packages affected",errpkgs, "End Packages affected")  
    #dbg.dprint(0, "chunk", chunk)

  dbg.leavesub()
  return()

