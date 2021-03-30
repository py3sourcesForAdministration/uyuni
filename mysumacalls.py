#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Module containing the procedures to handle uyuni server management
    on the commandline. 
"""   
##### Avoid pydoc errors
import os, os.path, sys
try:
  from __main__ import prgdir,prgname
  import os.path
  exec(open(os.path.join(prgdir,prgname+"_imp.py")).read())
except:
  if sys.argv[0].find('pydoc'):
    pass # we are running from pydoc3
##### Module Start
###----- Sample how to test a new function
###----- create new function name, import file from testprogs, call testprog function
#def Systems_ShowPkgs_N(*args): 
#  sys.path.append('/home/ap/pydev/uyuni/testprogs')
#  import test_Systems_ShowPkgs 
#  test_Systems_ShowPkgs.Systems_ShowPkgs_new(*args)

################################################################
def Patches_DeleteManual(*args):
  """      Delete Patches from a Cloned Channel if they have a CM- advisory
  """
  from __main__ import dbg,prgargs,cfg
  #  import sumaconnect
  dbg.entersub()
  dbg.dprint(2,"ARGS",args)
  if len(args):
    if "help" in args:
      print(f"Usage: {dbg.myself().__name__} Channel") 
      print(f"{dbg.myself().__doc__}") 
      dbg.leavesub()
      return
    else:
      chan = args[0]
      ### Create new arglist
  else:
    print( "no valid channel")
    print(f"Usage: {dbg.myself().__name__} Channel")
    print(f"{dbg.myself().__doc__}")
    dbg.leavesub() 
    return
  ses = data['conn']['ses']
  key = data['conn']['key']
  clist = ses.channel.listSoftwareChannels(key)

  source_exists = next((True for channel in clist if channel['label'] == chan),False)
  if source_exists:
    srcerrata = ses.channel.software.listErrata(key,chan)
    #    dbg.dprint(256,"List of Errata", srcerrata)
    for ref in srcerrata:
      print(ref['advisory_name'])
      if ref['advisory_name'].startswith('CM'):
        print("Delete: ",ref['advisory_name'])
        ses.errata.delete(key,ref['advisory_name'])
  else:
    print( "no valid channel: ",channel)
  dbg.leavesub()
  return

##############################################################################
def TEST_API(*args):
  """      calls the spacewalk api and prints the answer
  examples: api.getApiNamespaces
            api.getApiNamespaceCallList system
            errata.getDetails CESA-2019:2029
  """
  from __main__ import dbg,prgargs,data
  #  import sumaconnect
  dbg.entersub()
  dbg.dprint(2,"ARGS",args)
  if len(args) > 0:
    if "help" in args:
      print(f"Usage: {dbg.myself().__name__} some.api.call [args]") 
      print(f"{dbg.myself().__doc__}") 
      dbg.leavesub()
      return
    else:
      dbg.setlvl(3)
      ### Create new arglist
      call = args[0] 
      rest = args[1:]
      dbg.dprint(0, F"Call {call} with {rest}")     
      sumaconnect.docall(args[0],*rest)
      dbg.setlvl()
  else:
    print( "no valid input")
  dbg.leavesub()
  return

##############################################################################
def Actions_Show(*args):
  """       lists actions scheduled in the last num days
       Input may be floating point number
  """      
  from __main__ import dbg,prgargs,data
  #  import datetime,time,sumaconnect
  dbg.entersub()
  dbg.dprint(2,"ARGS",args)
  ses = data['conn']['ses']
  key = data['conn']['key']
  days = 1 ;
  if len(args) > 0:
    if "help" in args:
      print(f"Usage: {dbg.myself().__name__} [num of days]") 
      print(f"{dbg.myself().__doc__}") 
      print("Default:",days,"days\n")
      dbg.leavesub()
      return
    elif myinput.is_number(args[0]):
      days = float(args[0])
    else:
      print( "no valid input")
      dbg.leavesub()
      return

  tframe = float(days)*24*3600
  currts = time.time()
  startts = currts - tframe
  #    readable = datetime.datetime.fromtimestamp(1569750774).isoformat()
  readable = time.ctime(startts)
  print("----- Startdate:", readable) 
  actions = sumaconnect.docall('schedule.listAllActions')
  outfmt  = "%-20s %-27s %4s %4s %4s %8s %-s"    
  header  = ('Date', 'Hostname', 'InPr', 'Comp', 'Fail', 'Number','Description')
  print(outfmt % header)
  for a in actions:
    name         = "multi"
    failmessages = []
    shortfail    = []
    exects       = datetime.datetime.timestamp(a['earliest'])
    if  exects >= startts: 
      #      dbg.dprint(4,"Current Action",a)
      if a['inProgressSystems'] + a['completedSystems'] + a['failedSystems'] == 1 :
        if a['inProgressSystems'] == 1 : 
          #          host = sumaconnect.docall(data['conn'],'schedule.listInProgressSystems',a['id']
          host = ses.schedule.listInProgressSystems(key,a['id'])
          dbg.dprint(4,"Actionid:", a['id'], "Host:", host)
          if host[0]['server_name'] :
            name = host[0]['server_name'] 
          else:
            name = "changed state"
        elif  a['completedSystems'] == 1 :
          host = ses.schedule.listCompletedSystems(key,a['id'])
          name = host[0]['server_name'] 
        elif a['failedSystems'] == 1 :
          host = ses.schedule.listFailedSystems(key,a['id'])
          name = host[0]['server_name'] 

      if a['failedSystems'] :
        fails = ses.schedule.listFailedSystems(key,a['id'])
        for sys in fails:
          buf1 = "%-20s %-s" % ( '  Fail  -->   ', sys['server_name'])
          buf2 = "%-25s %-s" % ( sys['server_name'] ,sys['message'])
          shortfail.append(buf1)
          failmessages.append(buf2)
      print(outfmt % (a['earliest'], name, a['inProgressSystems'], a['completedSystems'], 
                      a['failedSystems'],a['id'], a['type'] ))
      if len(failmessages) > 0 :
        if prgargs.verbose:
          print("\n".join(failmessages))
        else:  
          print("\n".join(shortfail))
    else:
      break
  dbg.leavesub()
  return

##############################################################################
def Actions_Archive(*args):
  """       archives actions older than num days.
  """
  from __main__ import dbg,prgargs,data
  #  import datetime,time,sumaconnect
  dbg.entersub()
  dbg.dprint(2,"ARGS",args)
  days = 7
  ses = data['conn']['ses']
  key = data['conn']['key']
  if len(args) > 0:
    if "help" in args:
      print(f"Usage: {dbg.myself().__name__} [num of days]") 
      print(f"{dbg.myself().__doc__}") 
      print("Default:",days,"days\n")
      dbg.leavesub()
      return
    elif myinput.is_number(args[0]):
      days = float(args[0])
    else:
      print( "no valid input")
      dbg.leavesub()
      return

  tframe = float(days)*24*3600
  currts = time.time()
  startts = currts - tframe
  readable = time.ctime(startts)
  archlist = []
  totalact = 0
  print("----- Startdate:", readable)
  calllist = { 'completed' : ses.schedule.listCompletedActions, 
               'failed'    : ses.schedule.listFailedActions }
  for k in calllist:
    actions  = calllist[k](key)  
    numact   = len(actions)
    totalact += numact 
    for a in actions:
      exects       = datetime.datetime.timestamp(a['earliest'])
      if exects >= startts :
        continue
      print("added Action", a['id'], a['earliest'], 'from', k)
      archlist.append(a['id'])
  
  ret = ses.schedule.archiveActions(key,archlist)
  if myinput.is_number(ret) and ret == 1 :
    print("archived", len(archlist), "of", totalact, "Actions")
  else:
    print(ret)

  dbg.leavesub()
  return

##############################################################################
def Actions_Delete(*args):
  """       deletes archived actions older than num days.
  """
  from __main__ import dbg,prgargs,data
  #  import datetime,time,sumaconnect
  dbg.entersub()
  dbg.dprint(2,"ARGS",args)
  days = 30
  ses = data['conn']['ses']
  key = data['conn']['key']
  if len(args) > 0:
    if "help" in args:
      print(f"Usage: {dbg.myself().__name__} [num of days]") 
      print(f"{dbg.myself().__doc__}") 
      print("Default:",days,"days\n")
      dbg.leavesub()
      return
    elif myinput.is_number(args[0]):
      days = float(args[0])
    else:
      print( "no valid input")
      dbg.leavesub()
      return

  tframe = float(days)*24*3600
  currts = time.time()
  startts = currts - tframe
  readable = time.ctime(startts)
  archlist = []
  totala = 0
  ret = 0
  print("----- Startdate:", readable)

  actions = ses.schedule.listArchivedActions(key)
  totala  = len(actions)
  for a in actions:
    exects       = datetime.datetime.timestamp(a['earliest'])
    if exects >= startts :
      continue
    print("added Action", a['id'], a['earliest'])
    archlist.append(a['id'])
    #  try :
    #    for aid in archlist:
    #      dbg.dprint(0,"Aid",aid, "Type", type(aid)) 
    #      sumaconnect.docall('schedule.deleteActions',str(aid))
    #      ret += ses.schedule.deleteActions(key,tuple(aid))
  ret = ses.schedule.deleteActions(key,archlist)
  #  except Error as e: 
  #    print ("no success,e")


  if myinput.is_number(ret) and ret == 1 :
    print("deleted", len(archlist), "of", totala, "Actions")
  else:
    print(ret)

  dbg.leavesub()
  return

##############################################################################
def Systems_ShowPatches(*args):
  """       Creates a csvfile and also a screenoutput of the
       available patches sorted by systemgroup and patchtype.
       without args shows all Patches for all Groups.
  """
  from __main__ import dbg,prgargs,data
  #  import os,uyuni_patches
  dbg.entersub()
  dbg.dprint(2,"ARGS",args)
  #---- Settings and params
  ses = data['conn']['ses']
  key = data['conn']['key']
  grplist = data['sumastate']['groups']
  syslist = data['sumastate']['systems']
  patlist = data['sumastate']['patches']
  sysorgroup = {}
  nextheader = 1
  dbg.dprint(4, "SAVEDIR",data['savedir'])
  csvfile = os.path.join(data['savedir'],data['csvname'])
  dbg.dprint(4, "CSVfile:", csvfile) 

  if len(args):
    if "help" in args:
      print(f"Usage: {dbg.myself().__name__} [sysorgroup [sysorgroup] ...]") 
      print(f"{dbg.myself().__doc__}") 
      dbg.leavesub()
      return
    else:
      for sog in args:
        if sog in syslist:
          group = syslist[sog]['group'] 
          sysorgroup[group] = sysorgroup.get(group,1)
        elif sog in grplist:
          sysorgroup[sog] = sysorgroup.get(sog,1)
        else:
          dbg.dprint(0,sog,"is not a known group or system")
  else:
    sysorgroup = grplist
  
  dbg.dprint(2,"Resulting Group",sysorgroup, "End Resulting Group")
  if len(sysorgroup) < 1:
    dbg.dprint(0,"No Group recognized from input")
    dbg.leavesub()
    return

  with open(csvfile,'w') as f:
    print(data['formats']['patchcsvhead'],file=f)
    for grp in sorted(sysorgroup):
      if nextheader: 
        print("-----------------------------------------------------")
        print(data['formats']['patchprnfmt'] % (
                          'Group','Type','Patchname','Description','CVEs','Systems'))
      nextheader = 0
      for etyp in sorted(data['patchtypenames']): 
        if etyp not in patlist: continue
        for p in sorted(patlist[etyp]):
          systems = []
          for s in sorted(patlist[etyp][p]['systems']):
            if s in grplist[grp]['systems']:
              systems.append(s)
          if 'cves' in patlist[etyp][p]:
            cvestr = ', '.join(sorted(patlist[etyp][p]['cves']))
          else:
            cvestr = '- no CVEs -'
          
          if len(systems):
            nextheader = 1
            sysstr = ', '.join(systems)
            desc   = patlist[etyp][p]['desc']['advisory_synopsis']
            print(data['formats']['patchprnfmt'] % ( 
                grp, etyp, p[0:25],desc[0:25],cvestr[0:18],sysstr)) 
            print(data['formats']['patchcsvfmt'] % ( 
                grp, etyp, p,desc,cvestr,sysstr), file=f) 
  dbg.leavesub()
  return

##############################################################################
def Systems_ShowPkgs(*args):
  """       Prints out the upgradable packages of Systems or groups
       Argstring can be a blank separated list of Systems and/or groups
       Default: Without args prints all systems of the default dumpfile
       extraargs: 
         -x channelfilter  -- print only if any providing channel matches filter
         -x cf patchfilter -- print only if channel and errata filter match
       -v shows the providing channels, filter with -x channelfilter
       -vv shows the errata also, filter with -x channelfilter patchfilter 
  """
  from __main__ import dbg,prgargs,data,prgname
  dbg.entersub()
  dbg.dprint(2,"ARGS",args)
  #---- Settings
  ses = data['conn']['ses']
  key = data['conn']['key']
  grplist = data['sumastate']['groups']
  syslist = data['sumastate']['systems']
  patlist = data['sumastate']['patches']
  sysorgroup = {}
  #print(prgargs.verbose)
  if len(args):
    if "help" in args:
      print(f"Usage: {dbg.myself().__name__} [sysorgroup [sysorgroup] ...] [-vv] [-x channelfilter [patchfilter]]") 
      print(f"{dbg.myself().__doc__}") 
      dbg.leavesub()
      return
    else:
      for sog in args:
        if sog in grplist:
          for s in grplist[sog]['systems']:
            sysorgroup[s] = sysorgroup.get(s,1)
        elif sog in syslist:
          sysorgroup[sog] = sysorgroup.get(sog,1)
        else:
          dbg.dprint(0,sog,"is not a known group or system")
  else:
    sysorgroup = syslist 
  #----  
  #dbg.dprint(0,'verbose:',prgargs.verbose, 'xargs',prgargs.xargs, type(prgargs.xargs)) 
  providers = aDict()
  channelmatch = ''
  patchmatch   = ''
  if len(prgargs.xargs) == 2:
    channelmatch = prgargs.xargs[0]
    patchmatch   = prgargs.xargs[1]
  elif len(prgargs.xargs) == 1: 
    channelmatch = prgargs.xargs[0]
  else:
    pass

  dbg.setlvl(+1)
  for system in sorted(sysorgroup):
    curid = syslist[system]['id']
    dbg.dprint(0,f"{system:35}",", ID:",curid)
    printout = 1
    pkgs = []
    try:
      pkgs = ses.system.listLatestUpgradablePackages(key,curid)
      #print(pkgs)
    except:
      dbg.dprint(0, "Call listLatestUpgradablePackages did not succeed for system")
      continue
    for pkg in pkgs:
      pkgnum = pkg['to_package_id']
      pkgline = f"{pkgnum:8}, {pkg['name']:35} {pkg['from_version']:8}- {pkg['from_release']:8} -> {pkg['to_version']:8}- {pkg['to_release']:8}"
      channlp = [] ; cblock = []
      erratap = [] ; eblock = []
      if not providers.get(pkgnum):
        try:
          channlp = ses.packages.listProvidingChannels(key,pkgnum)
          erratap = ses.packages.listProvidingErrata(key,pkgnum)
        except:
          dbg.dprint(0, "call for providers did not succeed")
          continue
        for c in channlp:
          label = c['label']
          providers[pkgnum].channels[label] = providers[pkgnum].channels.get(label,1)
        for e in erratap:
          advisory = e['advisory'].replace('CL-','',1)
          providers[pkgnum].errata[advisory] = providers[pkgnum].errata.get(advisory,e['synopsis'])
      ### end of information aquirement for a new pkg
      ### Start Printing
      pmatch = 0 ; cmatch = 0
      for label in providers[pkgnum].channels.keys():
        if len(prgargs.xargs) == 0:
          cmatch = 1
          cblock.append(f"         Channel: {label}")
        elif len(prgargs.xargs) and channelmatch in label:
          cmatch = 1
          cblock.append(f"         Channel: {label}")
       
      for adv in providers[pkgnum].errata.keys():
        if len(prgargs.xargs) < 2:
          pmatch = 1  
          eblock.append(f"         Errata: {adv} Syn: {providers[pkgnum].errata[adv]}") 
        elif len(prgargs.xargs) >1 and patchmatch in adv:
          pmatch = 1
          eblock.append(f"         Errata: {adv} Syn: {providers[pkgnum].errata[adv]}") 

      ### allow print if pmatch is 0, because pkg is just an update
      if len(providers[pkgnum].errata.keys()) == 0 and len(prgargs.xargs) < 2:
        pmatch = 1          
      ### Print pkginfo 
      if cmatch and pmatch:
        dbg.dprint(1,  pkgline)
        for l in cblock:
          dbg.dprint(64,  l)
        for l in eblock:
          dbg.dprint(128, l)

  dbg.setlvl()
  dbg.leavesub()
  return
      
##############################################################################
def Systems_Status(*args):
  """       Prints out the state of Systems
       Argstring can be a blank separated list of Systems and/or groups
       Default: Without args prints all systems of the default dumpfile
  """
  from __main__ import dbg,prgargs,data
  dbg.entersub()
  dbg.dprint(2,"ARGS",args)
  #---- Settings
  ses = data['conn']['ses']
  key = data['conn']['key']
  grplist = data['sumastate']['groups']
  syslist = data['sumastate']['systems']
  patlist = data['sumastate']['patches']
  sysorgroup = {}
  if len(args):
    if "help" in args:
      print(f"Usage: {dbg.myself().__name__} [sysorgroup [sysorgroup] ...]") 
      print(f"{dbg.myself().__doc__}") 
      dbg.leavesub()
      return
    else:
      for sog in args:
        if sog in grplist:
          for s in grplist[sog]['systems']:
            sysorgroup[s] = sysorgroup.get(s,1)
        elif sog in syslist:
          sysorgroup[sog] = sysorgroup.get(sog,1)
        else:
          dbg.dprint(0,sog,"is not a known group or system")
  else:
    sysorgroup = syslist 
  #----   
  #  old = uyuni_patches.check_savefile(data['savefile'])
  #  if old :
  #    dbg.dprint(0, "Updating Statefile, please wait")
  #    UpdateStateFile()
  print(data['formats']['systemstateheader'])
  for system in sorted(sysorgroup): 
    print(data['formats']['systemstateline'].format( 
                         syslist[system]['group'], 
                         system, 
                         syslist[system]['last_boot'].strftime("%Y-%m-%d"),
                         syslist[system]['reboot'], 
                         syslist[system]['sec'], syslist[system]['bgf'], syslist[system]['enh'],
                         syslist[system]['updates'],
                         syslist[system]['last_checkin'].strftime("%Y-%m-%d")))
  dbg.leavesub()
  return
  
##############################################################################
def UpdateStateFile(*args):
  """       Gathers needed information for all managed systems,
       their patches and states and saves it first in the
       global dictionary data['sumastate'], then dumps this
       dictionary to dumpfile for later use.
  """
  from __main__ import dbg,prgargs,data
  #  import sys,pickle,uyuni_groups,uyuni_channels,uyuni_patches
  dbg.entersub()
  dbg.dprint(2,"ARGS",args)
  dumpfile = data['savefile']
  if "help" in args:
    print(f"Usage: {dbg.myself().__name__} [dumpfile]") 
    print(f"{dbg.myself().__doc__}") 
    print("Default:",dumpfile)
    print("")
    dbg.leavesub()
    return

  if len(args): 
    dumpfile = args[0]
    
  dbg.dprint(4,dumpfile)
  dbg.dprint(4,data)
  ses = data['conn']['ses']
  key = data['conn']['key']
  ### get new values in fresh dictionaries
  grplist = {}
  syslist = {}
  patlist = {}
  chnlist = {}
  (grplist,syslist) = uyuni_groups.Get_Group_List(ses,key,grplist,syslist)
  (syslist,patlist) = uyuni_patches.get_Patches_for_all_Systems(ses,key,syslist,patlist)
  (chnlist)         = uyuni_channels.Get_Channel_List(ses,key)
  ### write the updated values from memory to disk
  data['sumastate']['groups']   = grplist
  data['sumastate']['systems']  = syslist
  data['sumastate']['patches']  = patlist
  data['sumastate']['channels'] = chnlist
  uyuni_patches.write_savefile(dumpfile)
  dbg.leavesub()
  return

##############################################################################
def Channel_List(*args):
  """       lists channels matching search     
       without args show all known channels
  """
  from __main__ import dbg,prgargs,data
  #  import uyuni_channels
  dbg.entersub()
  dbg.dprint(2,"ARGS",args)
  ses = data['conn']['ses']
  key = data['conn']['key']
  search  = ''
  chnlist = {}
  arglist = list(args)

  if len(arglist) > 0:
    if "help" in args:
      print(f"Usage: {dbg.myself().__name__} [search]") 
      print(f"{dbg.myself().__doc__}") 
      dbg.leavesub()
      return
    else:
      search = arglist[0]
  (chnlist)  = uyuni_channels.Get_Channel_List(ses,key)
  chbylabel  = chnlist['byLabel']
  chbyparent = chnlist['byParent']
  print(data['formats']['channelheader'],end="")
  for pa in sorted(chbyparent):
    if search in pa or [key for key in chbyparent[pa] if search in key]:
      print(data['formats']['channelparent'] % ( 
                  pa, chbylabel[pa]['id'],
                  chbylabel[pa]['pkg'],chbylabel[pa]['errata'], 
                  chbylabel[pa]['sys']))
      for cl in sorted(chbyparent[pa]): 
        if search in cl:
          print(data['formats']['channelchild'] % ( 
                    cl,chbylabel[cl]['id'],
                    chbylabel[cl]['pkg'],chbylabel[cl]['errata'],
                    chbylabel[cl]['sys']))
  print()
    
  dbg.leavesub()
  return(chbylabel)

##############################################################################
def Channel_01_MergeVendor(*args):
  """       merge vendor channels according to the settings"
       in the server config to the appointed channel.
       if test is given only shows what will be done.
       if merge is given merges the errata instead of cloning.
       help -vv shows additional commandline hints
  """
  addontext="""
  ------------------- Additional Hints using commandline ----------------------
  A. clone a vendor tree:
    spacecmd -u user -p pwd -s osv9-suse-mgmt.voip.sen -- \\
      softwarechannel_clonetree  --source -channel sles12-sp4-pool-x86_64 -p "itg-"

  B. Add SuSE Channel
    mgr-sync -v add channel sles12-sp3-ltss-updates-x86

  C. Remove suse Channels
    spacewalk-remove-channel -c sles12-sp2-ltss-updates-x86_64
    + spacecmd repo_delete sles12-sp2-ltss-updates-x86_64

  D. remove custom channels 
    spacecmd softwarechannel_delete itg-sles12-sp2-ltss-updates-x86_64
  """
  from __main__ import dbg,prgargs,data,modlog
  #  import uyuni_channels
  dbg.entersub()
  dbg.dprint(2,"ARGS",args)
  ses = data['conn']['ses']
  key = data['conn']['key']
  chmap  = data['chmap']['01_vendorclone']
  chlist = data['sumastate']['channels']
  t  = False
  cl = True
  if len(args) > 0:
    if "help" in args:
      print(f"Usage: {dbg.myself().__name__} [test] [merge] [-v]") 
      print(f"{dbg.myself().__doc__}") 
      dbg.dprint(64,"current config from data.chmap.01_vendorclone",data['chmap']['01_vendorclone'],"End data['chmap']['01_vendorclone']")
      dbg.dprint(128,addontext)
      print("")
      dbg.leavesub()
      return
    if "test" in args:
      t = True
    if "merge" in args:
      cl = False

  #  dbg.dprint(256,t,p,cl)
  modlog.info(f"----> {dbg.myself().__name__}")
  for (source,target,parent) in chmap:
    modlog.info(f"{source} -> {target}")
    ok = uyuni_channels.Merge_Channel(source,target,parent,test=t,clone=cl)
    if not ok:
      dbg.dprint(256,F"MergeVendor to {target} did not succeed")
      modlog.error(F"MergeVendor to {target} did not succeed")
  modlog.info(f"<---- {dbg.myself().__name__}")
  dbg.leavesub()
  return

##############################################################################
def Channel_02_UpdateArchive(*args):
  """       create or update archive channels according to the settings
       in the server config to the appointed channel.
       if test is given only shows what will be done.
       Errata are always cloned for Archives.
  """
  from __main__ import dbg,prgargs,data,modlog
  dbg.entersub()
  dbg.dprint(2,"ARGS", args)
  ses = data['conn']['ses']
  key = data['conn']['key']
  chmap  = data['chmap']['02_datefreeze']
  chlist = data['sumastate']['channels']
  testonly = False
  printout = False
  clone    = True
  ###### Check args and do it ################################################
  if len(args) > 0:
    if "help" in args:
      print(f"Usage: {dbg.myself().__name__} [test] [-v]") 
      print(f"{dbg.myself().__doc__}") 
      dbg.dprint(64,"current config from data.chmap.02_datefreeze",chmap,"End data['chmap']['02_datefreeze']")
      print("")
      dbg.leavesub()
      return
    elif "test" in args:
      testonly = 1
    else:
      pass
  modlog.info(f"----> {dbg.myself().__name__}")
  for (source,target,parent) in chmap:
    modlog.info(f"{source} -> {target}")
    ok = uyuni_channels.Merge_Channel(source,target,parent,test=testonly,clone=clone)
    if not ok:
      dbg.dprint(256,F"ArchiveUpdate to {target} did not succeed")
      modlog.error( F"ArchiveUpdate to {target} did not succeed" )
  modlog.info(f"<---- {dbg.myself().__name__}")
  dbg.leavesub()
  return

##############################################################################
def Channel_02_applyExcludes(*args):
  """       Apply the Content Exclude settings in the server configuration file
       to the named channels. 
       ->   'test' : only shows all packages and errata that will be removed
       ->   'yes'  : silently removes errata and all packages found by 'test'.
       -> Without args asks for confirmation of each pkg referend by an 
       erratum.

  Note: if you confirm the deletion of any pkg the referencing
        erratum will be removed as well without further confirmation.
  """
  # Note: If there is a cloned erratum in some other channel, but not in the 
  #            requested one, packages are deleted nevertheless.
  from __main__ import dbg,prgargs,data,modlog
  import re
  dbg.entersub()
  dbg.dprint(2,"ARGS",args)
  ses = data['conn']['ses']
  key = data['conn']['key']
  confirm = True
  test    = False
  rest = []
  ### Set default debug to show everyhing for interactive use
  dbg.setlvl(6)
  ###### Check args  #################################################
  modlog.info(f"----> {dbg.myself().__name__}")
  for i in range(0,len(args)):
    if args[i] == "help":
      print(f"Usage: {dbg.myself().__name__} [ test | yes ]") 
      print(f"{dbg.myself().__doc__}") 
      dbg.dprint(192,"current config from data.contentexcludes",data['contentexcludes'],"End data['contentexcludes']")
      dbg.leavesub()
      return
    elif args[i] == "test":
      test = True
      # dbg.setlvl(6)
    elif args[i] == "yes":
      confirm = False
      dbg.setlvl(0)
    else:
      pass
  ###### Execute  #################################################

  for channel in data['contentexcludes'].keys():
    modlog.info(f"Working on {channel}")
    excludes = data['contentexcludes'][channel]
    fpats   = {}
    fpkgs   = {}
    regexes = {}
    names   = list()
    for (name,rstring,vcompare,version) in excludes:
      if name not in regexes:
        regexes[name] = {}
        regexes[name]['regex']    = re.compile(rstring) 
        regexes[name]['operator'] = vcompare 
        regexes[name]['version']  = version 
      names.append(rstring)
    channelregex  = re.compile('|'.join(names))
      #    dbg.dprint(0,"Start regex", regex,"End regex" )
    dbg.dprint(2,"-----" ,channel)
    pkgs = ses.channel.software.listAllPackages(key,channel)
    for pkg in pkgs:
      ### If the name matches any excluderegex
      if channelregex.search(pkg['name']):
        pkgid = pkg['id']
        ### get the matching part of channelregex
        symname = ''
        for name in regexes:
          if regexes[name]['regex'].search(pkg['name']):
            symname = name
            break
        ### prepare to compare version of this package
        p1 = packaging.version.parse( pkg['version'] )
        p2 = packaging.version.parse( regexes[symname]['version'] )
        compare = regexes[symname]['operator'] 
        cstring = repr(compare).replace("<built-in function ","" )
        cstring = cstring.replace(">","")
        if compare(p1,p2):
          dbg.dprint(4, 
              f"{pkg['name']} Id: {pkgid}, v: {p1} found. excluding because {cstring} {p2}")
          ##### get the errata of this package, only handle cloned ones and 
          ##### only remove them from this channel
          errata = ses.packages.listProvidingErrata(key,pkgid)
          if len(errata):
            for err in errata:
              advisory = err['advisory']
              if advisory.startswith("CL-"):
                dbg.dprint(4, " ",advisory, "found for pkg", pkg['name'])
                if advisory not in fpats: 
                  fpats[advisory] = dict() #fpats.get(advisory,dict())
                else:  
                  dbg.dprint(4,"  ", "is Duplicate erratum")
                  break
                pkgs_to_remove = ses.errata.listPackages(key,advisory)
                for p in pkgs_to_remove:
                  dbg.dprint(4,f"    remove {p['name']}, v: {p['version']}, id: {p['id']}")
                  fpats[advisory][p['id']] = fpats[advisory].get(p['id'],0) +1
                  fpkgs[p['id']] = fpkgs.get(p['id'],dict())
                  fpkgs[p['id']]['version'] = p['version']
                  fpkgs[p['id']]['name']    = p['name']
                  fpkgs[p['id']]['release'] = p['release']
                  fpkgs[p['id']]['refby']   = fpkgs[p['id']].get('refby',list())
                  fpkgs[p['id']]['refby'].append(advisory) 
          else: # no erratum for this package
            fpkgs[pkgid] = fpkgs.get(pkgid,dict())
            fpkgs[pkgid]['version'] = pkg['version']
            fpkgs[pkgid]['name']    = pkg['name']
            fpkgs[pkgid]['release'] = pkg['release']
    pkgs_to_remove = list()
    pats_to_remove = list()
    ### show patches and packages and query for remove
    if test or confirm:
      dbg.dprint(2,"---------------------------------------------") 
      dbg.dprint(2,"Would remove",len(fpats.keys()),"patches and",len(fpkgs.keys()),"Packages") 
      dbg.dprint(2,"------------  Patches to remove  ------------") 
      pkglist = list()
      for patch in sorted(fpats):
        dbg.dprint(2,patch)
        for pkid in sorted(fpats[patch]):
          pkglist.append(pkid)
          dbg.dprint(2,"  ",pkid,fpkgs[pkid]['name'],fpkgs[pkid]['version'],fpkgs[pkid]['release'])
          if confirm:
            remove = myinput.query_yes_no("            Mark this package for removal","no")
            if remove:
              pkgs_to_remove.append(pkid)
              if patch not in pats_to_remove:
                pats_to_remove.append(patch)

      dbg.dprint(2,"------------  Packages to remove  -----------") 
      for pkid in sorted(fpkgs):
        if pkid not in pkglist:
          dbg.dprint(2,"  ", pkid,fpkgs[pkid]['name'],fpkgs[pkid]['version'],fpkgs[pkid]['release'])
          if confirm:
            remove = myinput.query_yes_no("            Mark this package for removal","no")
            if remove:
              pkgs_to_remove.append(pkid)
    ### yes is set, just take the complete lists         
    else:
      pats_to_remove = list(fpats)
      pkgs_to_remove = list(fpkgs)
    
    if test:
      dbg.dprint(0,'pats_to_remove', pats_to_remove, "End pats_to_remove")
      dbg.dprint(0,'pkgs_to_remove', pkgs_to_remove, "pkgs_to_remove")
    else:  
      ### Remove patches and packages in the to_remove lists 
      if len(pats_to_remove):
        dbg.dprint(2, "pats_to_remove",pats_to_remove, "End pats_to_remove")
        try:
          result = ses.channel.software.removeErrata(key,channel,pats_to_remove,False)
          modlog.info(f"Errata removed  : {len(pats_to_remove)}")
        except:
          dbg.dprint(256, "Removing" , pats_to_remove, "failed") 
          modlog.error(f"Removing {pats_to_remove} failed")
      if len(pkgs_to_remove):
        dbg.dprint(2,"pkgs_to_remove", pkgs_to_remove, "pkgs_to_remove")
        try:
          result = ses.channel.software.removePackages(key,channel,pkgs_to_remove)
          modlog.info(f"Packages removed: {len(pkgs_to_remove)}")
        except:
          dbg.dprint(256, "Removing", pkgs_to_remove, "failed" ) 
          modlog.error(f"Removing {pkgs_to_remove} failed")

  modlog.info(f"<---- {dbg.myself().__name__}")
  dbg.setlvl()
  dbg.leavesub()
  return

##############################################################################
def Channel_03_MergeArchive(*args):
  """       merge the latest archive channel into the test channel.
       See server config data['chmap']['03_arcmerge']
       if test is given only shows what will be done.
  """
  from __main__ import dbg,prgargs,data,modlog
  dbg.entersub()
  dbg.dprint(2,"ARGS",args)
  ses = data['conn']['ses']
  key = data['conn']['key']
  clone    = False
  testonly = False
  if len(args) > 0:
    if "help" in args: 
      print(f"Usage: {dbg.myself().__name__} [test] [-v]") 
      print(f"{dbg.myself().__doc__}") 
      dbg.leavesub()
      return
    if "test" in args:
      testonly = True

  chmap = data['chmap']['03_arcmerge']
  modlog.info(f"----> {dbg.myself().__name__}")
  for (source,target,parent) in chmap:
    modlog.info(f"{source} -> {target}")
    ok = uyuni_channels.Merge_Channel(source,target,parent,
                                      test=testonly,clone=clone)
    if not ok:
      line = F"Merging {source} to {target} did not succeed"
      dbg.dprint(256,line)
      modlog.error(line)
  modlog.info(f"<---- {dbg.myself().__name__}")
  dbg.leavesub()
  return

##############################################################################
def Channel_ShowPkgDiff(*args):
  """       Show the package difference between source and target channel. 
       To avoid problems the channel containing more pkgs should be the 
       first param <source>. To be able to compare original and cloned 
       channels a leading CL- is cut off in both channels.
       -v adds verbosity.
  """
  from __main__ import dbg,prgargs,data
  dbg.entersub()
  dbg.dprint(2,"ARGS",args)
  ses = data['conn']['ses']
  key = data['conn']['key']

  rest = []
  for i in range(0,len(args)):
    if args[i] == "help":
      print(f"Usage: {dbg.myself().__name__} <SourceChannel> <TargetChannel> [-v[v]]") 
      print(f"{dbg.myself().__doc__}") 
      dbg.leavesub()
      return
    else:
      if re.match('\w+',args[i]):
        if (len(rest) <=2):
          rest.append(args[i])
  
  if len(rest) == 2:
    source, target = rest
    print(f"Source: {source}")
    print(f"Target: {target}")
    uyuni_channels.get_pkg_difference(source,target)
  else:
    dbg.dprint(0,"not enough Arguments")
        
  dbg.leavesub()
  return
  
##############################################################################
def Channel_ShowPatchDiff(*args):
  """       Show the errata difference between source and target channel. 
       To avoid problems the channel containing more errata should be the 
       first param <source>. To be able to compare original and cloned 
       channels the leading CL- is cut off in both channels.
       -v adds verbosity. 
  """
  from __main__ import dbg,prgargs,data,prgname
  dbg.entersub()
  dbg.dprint(2,"ARGS",args)
  ses = data['conn']['ses']
  key = data['conn']['key']

  rest = []
  for i in range(0,len(args)):
    if args[i] == "help":
      print(f"Usage: {dbg.myself().__name__} <SourceChannel> <TargetChannel> [-v[v]]") 
      print(f"{dbg.myself().__doc__}") 
      dbg.leavesub()
      return
    else:
      if re.match('\w+',args[i]):
        if (len(rest) <=2):
          rest.append(args[i])

  if len(rest) == 2:
    source, target = rest
    print(f"Source: {source}")
    print(f"Target: {target}")
    uyuni_patches.get_patch_difference(source,target)
  else:
    dbg.dprint(0,"not enough Arguments")
        
  dbg.leavesub()
  return
  
