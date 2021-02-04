#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Docstring: replace
"""
import os, os.path, sys, checkenv
libdir         = checkenv.chk_sufficient()
prgname,prgdir = checkenv.get_names(__file__)
##############################################################################      
#########   F u n t i o n s   ################################################
##############################################################################
def listmodules():
  """ Lookup the available Functions and print out
  """
  dbg.entersub()
  for f in (dir(mysumacalls)):
    if f[0].isupper(): 
      print(f)
  dbg.leavesub()    
##############################################################################
###########   M A I N   ######################################################
##############################################################################
def main():
  """ Main part for doing the work
  """
  dbg.entersub()
  globals()['data'] = cfg.data
### Check Arguments 1 - Get and read config for the wanted server
  dbg.dprint(2, "prgargs: ", prgargs)
  conff = os.path.realpath(os.path.join(prgdir, prgargs.config + ".cfg"))
  dbg.dprint(2, "Conffile:",conff)
  realconfname,ext = os.path.splitext(os.path.basename(conff)) 
  savedir = os.path.join(cfg.data['savetop'],realconfname)
  cfg.data['savedir'] = savedir
  dbg.dprint(2,"Savedir:",savedir)
  try:
    exec(open(conff).read(),globals())
  except:
    dbg.dprint(0,"Unable to read Server conf")
    sys.exit(1)
  finally: 
    dbg.dprint(2,"Realconfname:",realconfname)
    if not os.path.exists(savedir):
      os.makedirs(savedir,exist_ok=True) 
  ### What to do?    
  if prgargs.listmod:
    dbg.dprint(0,"--- Only Show Modules ---")
    listmodules()
  else:  
    modlog = loguru.logger
    modlog.remove()
    globals()['modlog'] = modlog
    if prgargs.log:
      logname = os.path.join(savedir,prgname+".log")
      modlog.add( logname, format="{time:YYYY-MM-DD HH:mm:ss} | {level:7} | {message}")  
    ### Check Arguments 2 - Get Action to execute    
    if prgargs.module[0] in dir(mysumacalls):
      sumaconnect.login(cfg.data['conn'])
      ### name of savefile from config, check(create) and read
      cfg.data['savefile'] = os.path.join(savedir,cfg.data['savename'])
      if prgargs.module[0] != "UpdateStateFile" and prgargs.module[0].startswith("Systems_"):
        old = uyuni_patches.check_savefile(cfg.data['savefile'])
        if old:
          f_age = str(datetime.timedelta(seconds=old))
          dbg.dprint(0, "SystemState is",f_age,"old, Information may be outdated")
          dbg.dprint(0, "Updating Statefile, please wait")
          mysumacalls.UpdateStateFile()
        uyuni_patches.read_savefile(cfg.data['savefile'])
      ### execute the action
      call = getattr(mysumacalls,prgargs.module[0])
      call(*prgargs.module[1:]) 
      sumaconnect.logout(cfg.data['conn'])
    else:
      dbg.dprint(0,"No such Module: ", prgargs.module[0])
      exit(1)
  #if prgargs.verbose:
  #  print("-----     E N D     -----")  
  dbg.leavesub()

###########   D E F A U L T   I N I T   ######################################
if __name__ == "__main__":
  from mydebug.py3dbg import dbg
  from myconf.py3cfg  import init_cfg
  cfg = init_cfg(prgname,prgdir,libdir,dbg)
  exec(cfg.imports)
  exec(cfg.usage)
  main()