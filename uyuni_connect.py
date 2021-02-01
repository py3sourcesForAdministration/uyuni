#!/usr/bin/env python3
# -*- coding: utf-8 
""" Module containing basic connection functions 
    for uyuni xmlrpc server
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
##############################################################################
def login(conndict):
  """ Login with username and pass, do not strictly enforce cert verification
  """
  from __main__ import dbg
  dbg.entersub()
  context = ssl.SSLContext()
  session = xmlrpc.client.ServerProxy(conndict['url'], verbose=0,
                                      context=context, use_datetime=True) 
  key  = session.auth.login(conndict['usr'],conndict['pwd'])
  conndict['ses'] = session
  conndict['key'] = key
  dbg.leavesub()
  return(session,key)

##############################################################################
def logout(conndict):
  """ Logout from currently active session.
  """
  from __main__ import dbg
  dbg.entersub()
  session = conndict['ses']
  key = conndict['key']
  session.auth.logout(key)
  dbg.leavesub()

##############################################################################
def docall(name,*args):
  """ execute a known function by name. Convert string args into 
      python objects before. return the answer of the call.
  """    
  from __main__ import dbg,data
  dbg.entersub()
  ses = data['conn']['ses']
  key = data['conn']['key']
  dbg.dprint(2,"name:", name)
  dbg.dprint(2,"args:", args, ", type of args: ",type(args))
  call = getattr(ses, name)
  if len(args) == 0:
    answer = call(key)
  else:
    newargs = []
    count = 1
    ### create objects and append them to new array
    for a in args:
      dbg.dprint(4,"    {:02d}a - {} - {}".format(count,a,type(a)))
      obj = myinput.string_to_pyobj(a)
      newargs.append(obj)
      count += 1
    ### Call the xmlrpc function on server  
    answer = call(key,*newargs[0:])     
  ### print answer and return
  dbg.dprintref(2,answer, "answer for "+name)
  dbg.leavesub()
  return(answer)

