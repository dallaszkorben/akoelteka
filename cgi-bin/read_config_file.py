#!/usr/bin/python3

#import glob
import os
import sys
import json
import re
import configparser
import cgi, cgitb

# Get the Parameters from Ajax
data = cgi.FieldStorage()
ini_file = data["file"].value

# Read values
parser = configparser.RawConfigParser()
parser.read(ini_file)
try:
    language = parser.get("general", "language")
    path_film = parser.get("media", "path-film")
    player_video = parser.get("media", "player-video")
    player_video_param = parser.get("media", "player-video-param")
except (configparser.NoSectionError, configparser.NoOptionError):
    language = "en"
    path_film = "./"
    player_video = ""
    player_video_param = ""

#pattern_media = re.compile("^.+[.](avi|mpg|mkv|mp4|flv)$")
#pattern_card = re.compile("card.ini$")
#pattern_image = re.compile( "^image[.]jp(eg|g)$" )
#rootdir = "."
#rootdir = "../media"


ini_list = json.loads('{}')
ini_list['language'] = language
ini_list['path-film'] = path_film
ini_list['player-video'] = player_video
ini_list['player-video-param'] = player_video_param

print('Content-Type: application/json')
print()
print(json.dumps(ini_list))   
