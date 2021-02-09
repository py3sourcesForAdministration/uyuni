#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Module containing Helper Functions dealing with uyuni Channels
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
def Get_Channel_List(ses,key,*args):
  """ Creates a dictionary of all manageable channels found on the uyuni server
      and returns it. The dictionary has two keys 'byLabel' and 'byParent', containing
      the channels and their most important detail information.
  """    
  from __main__ import dbg,prgargs,data
  dbg.entersub()
  dbg.dprint(2,args)
  chnlist    = {}
  chbyparent = {}
  chbylabel  = {}

  for elem in ses.channel.listSoftwareChannels(key):
    label = elem['label']
    chbylabel[label]           = chbylabel.get(label,{}) 
    chbylabel[label]['arch']   = elem['arch']
    chbylabel[label]['parent'] = elem['parent_label']
    chbylabel[label]['errata'] = len(ses.channel.software.listErrata(key,label))
 
  for elem in ses.channel.listAllChannels(key):
    label = elem['label']
    chbylabel[label]['id']  = elem['id']
    chbylabel[label]['pkg'] = elem['packages']
    chbylabel[label]['sys'] = elem['systems']

  for label in chbylabel:
    parent = chbylabel[label]['parent']
    if not parent:
      chbyparent[label] = chbyparent.get(label,{})
    else:
      chbyparent[parent] = chbyparent.get(parent,{}) 
      chbyparent[parent][label] = 1
      
  chnlist['byLabel']  = chbylabel
  chnlist['byParent'] = chbyparent

  dbg.leavesub()
  return(chnlist)

##############################################################################
def Merge_Channel(source,target,parent,test=False,verbose=False,clone=False):
  """ Merge content and errata from source channel to target channel. All 
      channel parameters are label strings. parent is the label of target's parent.
      In addition the kwargs verbose, test and clone are accepted with boolean values.
      Returns 0 on failure, in case of test or success returns 1
  """    
  from __main__ import dbg,prgargs,data,modlog
  dbg.entersub()
  dbg.dprint(2,"verbose :",verbose,", test :", test,",clone :",clone)
  #dbg.dprint(256,dbg.myname())
  ses = data['conn']['ses']
  key = data['conn']['key']
  if verbose:
    dbg.setlvl(7)
  ##### Falls test angegeben wurde nur die Aktionen ausgeben
  if test:
    dbg.setlvl(+1)
    #dbg.dprint(1,"Would merge",source, "to", target)
  ##### Check if channels exist
  clist = ses.channel.listSoftwareChannels(key)
  source_exists = next((True for channel in clist if channel['label'] == source),False)
  target_exists = next((True for channel in clist if channel['label'] == target),False)
  clone_stat = 0
  ##### stop if no source
  if not source_exists:
    dbg.dprint(0,"Cannot merge non existing",source)
    modlog.error(f"Cannot merge non existing {source}")
    dbg.setlvl()
    dbg.leavesub()
    return clone_stat
  ##### If clone is set, clone channel completely if channel does not yet exist, 
  ##### otherwise merge packages, but clone errata
  if clone :
    dbg.dprint(1,"Clone:",clone, "   ",source, "->", target)
    ##### Clone is set, but channel already exists 
    if target_exists:
      dbg.dprint(1,"Channel exists, clone pkgs + errata")
      if test :
        dbg.dprint(1,"  - OK - Would merge packages and clone errata...")
        clone_stat = 1
      else:  
        ### get the missing errata 
        srcerrata = ses.channel.software.listErrata(key,source)
        tgterrata = ses.channel.software.listErrata(key,target)
        srcnames = set(d['advisory_name'] for d in srcerrata)
        tgtnames = set(d['advisory_name'].replace('CL-','',1) for d in tgterrata)
        srconly  = sorted(list(srcnames.difference(tgtnames))) 
        dbg.dprint(1,"Missing Errata:",srconly)
        failure = 0
        try:
          resultMP = ses.channel.software.mergePackages(key,source,target)
          dbg.dprint(1, "Packages merged :", len(resultMP))
          modlog.info(f"Packages merged : {len(resultMP)}")
        except:
          dbg.dprint(256,"Merging Packages did not succeed")
          modlog.error("Merging Packages did not succeed")
          failure += 1
        ### break patchlist into chunks
        chunknum = 0
        chunk = []
        for errnum in range(0,len(srconly)):
          if errnum // 10 == chunknum:
            chunk.append(srconly[errnum])
          else :  
            try:
              resultCE = ses.errata.clone(key,target,chunk)
              dbg.dprint(1, "Errata chunk ",chunknum, "cloned   :", len(resultCE))
              #modlog.info(f"Errata chunk {chunknum} cloned   : {len(resultCE)}")
            except: 
              dbg.dprint(256, "Errata chunk ",chunknum, "could not be cloned")
              modlog.error(f"Errata chunk {chunknum} could not be cloned") 
              dbg.dprint(0, "chunk", chunknum, chunk)
              failure += 1
            chunk = []
            chunknum += 1
            chunk.append(srconly[errnum])  
        ### proces last chunk 
        if len(chunk):
          try:
            resultCE = ses.errata.clone(key,target,chunk)
            dbg.dprint(1, "Errata chunk ",chunknum, "cloned   :", len(resultCE))
            modlog.info(f"Errata chunk {chunknum} cloned   : {len(resultCE)}")
          except: 
            dbg.dprint(256, "Errata chunk ",chunknum, "could not be cloned")
            modlog.error(f"Errata chunk {chunknum} could not be cloned") 
            dbg.dprint(0, "chunk", chunknum, chunk)
            failure += 1
        if failure:  
          dbg.dprint(256,"Merging packages or cloning errata did not succeed")
          modlog.error(f"Merging packages or cloning errata did not succeed") 
          clone_stat = 0
        else:
          result = f"Errata cloned   : {len(srconly)}" 
          dbg.dprint(1,result)
          modlog.info(f"{result}")
          clone_stat = 1
          
    ##### clone is set, target does not exist
    else:
      srcdetails = ses.channel.software.getDetails(key,source)
      dbg.dprint(0,"Arch_label of source", srcdetails['arch_label'])
      ### only if parent is not "" and not existing create an empty parent
      if parent:
        parent_exists = next((True for channel in clist if channel['label'] == parent),False)
        if not parent_exists:
          dbg.dprint(0,"Targets parent does not exist")
          psumm       = 'custom parent channel'
          parch       = srcdetails['arch_label']
          try:
            result = ses.channel.software.create(key,parent,parent,psumm,parch,"")
            dbg.dprint(1,"Parent Channel", parent, "created",result)
            modlog.info(f"Parent Channel {parent} created")
          except:
            err = "error exit: \"{0}\" in {1}".format(sys.exc_info()[1],sys.exc_info()[2:])
            dbg.dprint(256,err)
            modlog.error(f"{err}")
            dbg.setlvl()
            dbg.leavesub()
            return clone_stat
      ### non empty parent was created
      details = {
              'label'        : target,
              'name'         : target,
              'summary'      : "Clone of "+source,
              'description'  : "Created at "+datetime.date.today().strftime("%Y-%m-%d"),
              'parent_label' : parent,
              'checksum'     : srcdetails['checksum_label'],
      }  
      try:
        result = ses.channel.software.clone(key,source,details,False)
        dbg.dprint(1,"Channel geclont mit der ID ",result)
        modlog.info(f"Channel geclont mit der ID {result}")
        clone_stat = 1
      except: 
        err = "error exit: \"{0}\" in {1}".format(sys.exc_info()[1],sys.exc_info()[2:])
        dbg.dprint(256,err)
        modlog.error(f"{err}")
        dbg.dprint(256,"Could not clone",source,"to",target,"with Error")

  ##### Clone ist nicht gesetzt => nur mergen
  else:
    dbg.dprint(1,"Merge:",source,"->", target)
    if target_exists:
      dbg.dprint(1,"Channels ok, merge pkgs + errata:" )
      if test:
        dbg.dprint(1,"  - OK - Would merge packages and errata...")
        clone_stat = 1
      else:
        try: 
          resultMP = ses.channel.software.mergePackages(key,source,target)
          dbg.dprint(1, "Packages merged :", len(resultMP))
          modlog.info(f"Packages merged : {len(resultMP)}")
          resultME = ses.channel.software.mergeErrata(key,source,target) 
          dbg.dprint(1, "Errata merged   :", len(resultME))
          modlog.info(f"Errata merged   : {len(resultME)}")
          clone_stat = 1
        except:
          err = "error exit: \"{0}\" in {1}".format(sys.exc_info()[1],sys.exc_info()[2:])
          dbg.dprint(256,err)
          modlog.error(f"{err}")
          dbg.dprint(256,"Could not merge",target,"with Error")

    ##### Target does not exist 
    else:
      dbg.dprint(0,"Cannot merge",source,"to non existing",target)
      modlog.error(f"Cannot merge {source} to non existing {target}")
      if test:
        dbg.dprint(1,"Would try to create new channel",target)
        clone_stat = 1
      else:
        dbg.dprint(0,"Trying to create new channel:",target)  
        try:
          archLabel  = 'channel-' + target.split('-')[-1]
          summary    = "Created from "+source
          clone_stat = ses.channel.software.create(key,target,target,summary,archLabel,parent)
          if clone_stat:
            dbg.dprint(0,"Channel Creation succeeded. Run again to merge channels!") 
            modlog.warning("Channel Creation succeeded. Run again to merge channels!")
        except: 
          dbg.dprint(256,"Could not create Channel",target)
          modlog.error(f"Could not create Channel {target}")
      
  ##### Cleanup and return status
  dbg.dprint(1,"----------- Status: ",clone_stat, " --------------------")
  #modlog.info(f"--- Status: {clone_stat}")
  dbg.setlvl()
  dbg.leavesub()
  return clone_stat

##############################################################################
def get_pkg_difference(source,target,verbose=0):
  """ Get package difference between two software channels.
  """
  from __main__ import dbg,prgargs,data
  dbg.entersub()
  ses = data['conn']['ses']
  key = data['conn']['key']  
  #### Check if channels exist
  clist = ses.channel.listSoftwareChannels(key)
  source_exists = next((True for channel in clist if channel['label'] == source),False)
  target_exists = next((True for channel in clist if channel['label'] == target),False)
  if source_exists and target_exists:
    srclist = ses.channel.software.listAllPackages(key,source)
    tgtlist = ses.channel.software.listAllPackages(key,target)
    srcids = set(d['id'] for d in srclist)
    tgtids = set(d['id'] for d in tgtlist)
    srconly  = list(srcids.difference(tgtids))
    tgtonly  = list(tgtids.difference(srcids))
    dbg.setlvl(verbose)
    for pkgnum in range(0,len(srconly)):
      pkgid = srconly[pkgnum]
      pkgdict = ses.packages.getDetails(key,pkgid)
      dbg.dprint(0, f"{pkgdict['name']:55} {pkgid:7d}")
      dbg.dprint(1, f"  V: {pkgdict['version']:15}, R: {pkgdict['release']:10}, E: {pkgdict['epoch']}") 
      dbg.dprint(3, f"  Description: {pkgdict['description']}") 

  dbg.setlvl()
  dbg.leavesub()
  return

######### Maybe no longer needed after this line ?
  ##############################################################################
  ##############################################################################
  #def Clone_Channel(source,target,parent,**kwargs):
  #  """ Create a new Channel with all content and errata from source channel to target 
  #      channel. All parameters are label strings. parent is the label of target's parent.
  #      Only recognized keyword is checksum.
  #      Returns 0 on failure else 1
  #  """    
  #  from __main__ import dbg,prgargs,data
  #  import sys
  #  dbg.entersub()
  #  dbg.dprint(2,"Start kwargs",kwargs,"End optional kwargs")
  #  ses = data['conn']['ses']
  #  key = data['conn']['key']
  #  checksum = 'sha256'
  #  if 'checksum' in kwargs:
  #    checksum = kwargs['checksum']
  #  details = { 
  #    'name'         : target,
  #    'label'        : target,
  #    'summary'      : "Clone of "+source,
  #    'parent_label' : parent,
  #    'checksum'     : checksum,
  #  }
  #  try: 
  #    ok = ses.channel.software.clone(key,source,details,False) 
  #  except:
  #    dbg.dprint(0,"Could not clone channel", source, "to",target)
  #    dbg.dprint(0,"error exit: \"{0}\" in {1}".format(sys.exc_info()[1],sys.exc_info()[2:] ))
  #    dbg.dprint(0,"Could not clone Channel",target,"with Error:",xmlrpc.exc_info()[0])
  #    dbg.leavesub()
  #    return(0)
  #  else:
  #    dbg.leavesub()
  #    return(1)
  #
  ##############################################################################
  ##############################################################################
  #def Create_Channel(source,target,parent,*args):
  #  """ Create a new empty Channel. Only useful for custom channels without errata. All 
  #      parameters are label strings.
  #      Returns 0 on failure else 1
  #  """    
  #  from __main__ import dbg,prgargs,data
  #  import sys
  #  dbg.entersub()
  #  dbg.dprint(2,args)
  #  ses = data['conn']['ses']
  #  key = data['conn']['key']
  #  archLabel   = 'channel-' + target.split('-')[-1]
  #  if source == '' and parent == '':
  #    description = "custom parent channel"
  #  else:
  #    description = "Created from "+source
  #  try:
  #    ses.channel.software.create(key,target,target,description,archLabel,parent)
  #  except:  
  #    if "already in use" in sys.exc_info()[2:]:
  #      dbg.leavesub()
  #      return(1)
  #    else:
  #      dbg.dprint(0,"Could not create channel", target)
  #      dbg.dprint(0,"error exit: \"{0}\" in {1}".format(sys.exc_info()[1],sys.exc_info()[2:] ))
  #      dbg.dprint(0,"Could not create Channel",target,"with Error:",sys.exc_info()[0])
  #      dbg.leavesub()
  #      return(0)
  #  else:  
  #    dbg.dprint(0,"Created channel", target)  
  #
  #  dbg.leavesub()
  #  return(1)
  #    
  