#!/usr/bin/python3

#import glob
import os
import sys
import json
import re
import configparser
import cgi, cgitb
from subprocess import call

# Get the Parameters from Ajax
data = cgi.FieldStorage()
media = data["media"].value

#media = "../media/films/a/OnceUpponATimeInWest.avi"

call(["mplayer", media])
#os.system("mplayer " + media)
