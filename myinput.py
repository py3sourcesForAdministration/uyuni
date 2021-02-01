#!/usr/bin/env python3
# -*- coding: utf-8
""" Module containing input functions

"""    
import ast
import re
import dateparser
import sys
import datetime

##########################################################################
def string_to_pyobj(string):
  """ Function to convert commandline input containing python objects
      (i.e. array, dict) to valid python objects. Nested structures are 
      not implemented. See unittest for valid examples. 

  """
  string = string.replace("'"," ")  
  string = string.replace('"'," ")
  ### match ISO dates (only first part)
  if re.match('^\d{4}-\d{2}-\d{2}.*',string):
    obj = dateparser.parse(string)
  ### everything else   
  else:  
    ### match integers first
    if re.match('^\d+$',string):
      new = string
    ### match lists
    elif string.startswith('['):
      string = string.replace(","," ")  
      parts = string[1:-1].split()
      new = '[ '
      for i in parts:
        new = new + '"' + i + '", '
      new = new[0:-2] + ' ]' 
    ### match dictionaries
    elif string.startswith('{'):
      string = string.replace(","," ") 
      string = re.sub("\s*:\s*",":",string)
      parts = string[1:-1].split()
      new = '{ '
      for p in parts:
        (k,v) = p.split(':')
        new = new + '"' + k + '"' + ":" + v + ', '
      new = new[0:-2] + ' }'
      obj = ast.literal_eval(new)
    ### booleans  
    elif string == 'False':
      return False
    elif string == 'True':
      return True
    ### everything else match strings
    else:
      new = '"'+string+'"'
    ### Convert quoted to object  
    obj = ast.literal_eval(new)
  ### finally return   
  return(obj)

##########################################################################
def query_yes_no(question, default="yes"):
  """Ask a yes/no question via raw_input() and return their answer.

        "question" is a string that is presented to the user.
        "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

        The "answer" return value is True for "yes" or False for "no".
  """
  valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}

  if default is None:
    prompt = " [y/n] "
  elif default == "yes":
    prompt = " [Y/n] "
  elif default == "no":
    prompt = " [y/N] "
  else:
    raise ValueError("invalid default answer: '%s'" % default)

  while True:
    sys.stdout.write(question + prompt)
    choice = input().lower()
    if default is not None and choice == '':
      return valid[default]
    elif choice in valid:
      return valid[choice]
    else:
      sys.stdout.write("Please respond with 'yes' or 'no' "
                       "(or 'y' or 'n').\n")


##########################################################################
def is_int(string):
  ''' check wether string can be an integer
  '''
  try:
    int(string)
    return True
  except ValueError:  
    return False

##########################################################################
def is_number(string):
  ''' check wether string can be floating point number
  '''
  try:
    float(string)
    return True
  except ValueError:
    return False

##########################################################################
