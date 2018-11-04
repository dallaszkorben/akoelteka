#!/usr/bin/python3

#import glob
import os
import sys
import json
import re
import configparser

#root_dir="/home/akoel/Projects/python/akoelteka/media/"
#for filename in glob.iglob(root_dir + '**/*', recursive=True):
#     print(filename)

def folder_investigation( actual_dir, json_list ):
    
    for dirpath, dirnames, filenames in os.walk(actual_dir):

        #subfolder_path_os = None
        subfolder = False
        for name in dirnames:
            subfolder_path_os = os.path.join(actual_dir, name)            
            folder_investigation( subfolder_path_os, json_list )
            
            subfolder = True

        # if there is/are any sub-folder in the folder, then I media/card should not be there 
        if subfolder:
            return

        card_path_os = None
        media_path_http = None
        for name in filenames:
            if pattern_card.match( name ):
                card_path_os = os.path.join(actual_dir, name)
            if pattern_media.match(name):
                media_path_http = actual_dir+ "/" + name
                media_name = name
    
        # if there are card and media in the folder
        if card_path_os and media_path_http:

            data = {}            
            parser = configparser.RawConfigParser()
            parser.read(card_path_os)
            try:
                title_json_list = {}
                title_json_list['hu'] = parser.get("titles", "title_hu")
                title_json_list['en'] = parser.get("titles", "title_en")
                data['title'] = title_json_list
                
                #data['title_en'] = parser.get("titles", "title_en")
                #data['title_hu'] = parser.get("titles", "title_hu")
                
                data['year'] = parser.get("general", "year")
                
                director_json_list = json.loads('[]')
                directors = parser.get("general", "director").split(",")            
                for director in directors:
                    director_json_list.append(director)
                data['director'] = director_json_list
                
                data['length'] = parser.get("general", "length")
                
                sound_json_list = json.loads('[]')
                sounds = parser.get("general", "sound").split(",")
                for sound in sounds:
                    sound_json_list.append(sound)
                data['sound'] = sound_json_list

                sub_json_list = json.loads('[]')
                subs = parser.get("general", "sub").split(",")
                for sub in subs:
                    sub_json_list.append(sub)
                data['sub'] = sub_json_list

                genre_json_list = json.loads('[]')
                genres = parser.get("general", "genre").split(",")
                for genre in genres:
                    genre_json_list.append(genre)
                data['genre'] = genre_json_list

                theme_json_list = json.loads('[]')
                themes = parser.get("general", "theme").split(",")
                for theme in themes:
                    theme_json_list.append(theme)
                data['theme'] = theme_json_list
                
                actor_json_list = json.loads('[]')
                actors = parser.get("general", "actor").split(",")
                for actor in actors:
                    actor_json_list.append(actor)
                data['actor'] = actor_json_list
                
                data['best'] = parser.get("extra", "best")
                data['new'] = parser.get("extra", "new")
                data['favorite'] = parser.get("extra", "favorite")
                                                
                links = {}
                links['imdb'] = parser.get("links", "imdb")
                data['links'] = links
                
            except (configparser.NoSectionError, configparser.NoOptionError):
                data['title.en'] = parser.get("titles", "title.en")
                data['title.hu'] = parser.get("titles", "title.hu")
                
                data['year'] = ""
                data['director'] = json.loads('[]')
                data['length'] = ""
                data['sound'] = json.loads('[]')
                data['sub'] = json.loads('[]')
                data['genre'] = json.loads('[]')
                data['theme'] = json.loads('[]')
                data['actors'] = json.loads('[]')
                
                data['best'] = ""
                data['new'] = ""
                data['favorite'] = ""
                                        
                data['links'] = {}
           
            json_list.append(data)


pattern_media = re.compile("^.+[.](avi|mpg|mkv|mp4|flv)$")
pattern_card = re.compile("card.ini$")
rootdir = "."
#rootdir = "../media"


#data["title.en"] = "angol";

media_list = json.loads('[]')
#media_list = json.loads('[{"starting":"value"}]')
#data ={}
#data["els"]="elem"
#data["elem"]="masodik"
#media_list.append(data)





folder_investigation(rootdir, media_list)

print('Content-Type: application/json')
print()
print(json.dumps(media_list))   
