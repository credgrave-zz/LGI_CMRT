import os
import sys

def ifnull(var, val):
  if var is None:
    return val
  return var