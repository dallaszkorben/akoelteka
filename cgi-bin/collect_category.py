#!/usr/bin/python3

#import glob
import os
import sys
import json
import re
import configparser
import cgi, cgitb


def collect( actual_dir, hit_list, f_section, f_key, f_search ):
    
    for dirpath, dirnames, filenames in os.walk(actual_dir):

        #subfolder_path_os = None
        subfolder = False
        for name in dirnames:
            subfolder_path_os = os.path.join(actual_dir, name)            
            collect( subfolder_path_os, hit_list, f_section, f_key, f_search )
 
        card_path_os = None
        for name in filenames:
            if pattern_card.match( name ):
                card_path_os = os.path.join(actual_dir, name)
  
    
        # if there are card and media in the folder
        if card_path_os:

            parser = configparser.RawConfigParser()
            parser.read(card_path_os)
            try:
                
                if f_search == 'v':
                    hit_list.add( parser.get(f_section, f_key) )
                                    
                elif f_search == 'a':
                    values = parser.get(f_section, f_key).split(",")            
                    for value in values:
                        hit_list.add(value)
                
            except (configparser.NoSectionError, configparser.NoOptionError):
                pass


# Get the Parameters from Ajax
data = cgi.FieldStorage()
f_section=data["section"].value
f_key = data["key"].value
f_search = data["search"].value
rootdir = data["root-dir"].value


#f_section="general"
#f_key = "director"
#f_search = "a"


pattern_card = re.compile("card.ini$")
#rootdir = "../media"

hit_list=set()

collect(rootdir, hit_list, f_section, f_key, f_search)

# add an empty line if there is no
hit_list.add("")

print('Content-Type: application/json')
print()
print( json.dumps( [ h for h in hit_list ] ) )   
