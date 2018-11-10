#!/usr/bin/python3

#import glob
#import os
#import sys
#import json
#import re
#import configparser
import cgi, cgitb
from subprocess import call

# Get the Parameters from Ajax
data = cgi.FieldStorage()
player = data["player"].value
try:
    param = data["param"].value
except KeyError:
    param = ""
media = data["media"].value

switch_list = param.split(" ")

param_list = []
param_list.append(player)
param_list += switch_list
param_list.append(media)

#print("param: ", param_list, file=sys.stderr)

call( param_list )
