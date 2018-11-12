#!/usr/bin/python3

#import glob
import os
import sys
import json
import re
import configparser
import cgi, cgitb

def folder_investigation( actual_dir, json_list, f_key, f_value, f_search ):
    
    # Collect files and and dirs in the current directory
    file_list = [f for f in os.listdir(actual_dir) if os.path.isfile(os.path.join(actual_dir, f))]
    dir_list = [d for d in os.listdir(actual_dir) if os.path.isdir(os.path.join(actual_dir, d))]

    #print(json.dumps( file_list, sort_keys=True, indent=4) )
   
    # now I got to a cartain level of directory structure
    card_path_os = None
    media_path_os = None
    image_path_http = None

    # Go through all files in the folder
    for file_name in file_list:

        # collect the files which count
        if pattern_card.match( file_name ):
            card_path_os = os.path.join(actual_dir, file_name)
        if pattern_media.match(file_name):            
            media_path_os = os.path.join(actual_dir, file_name)
            media_name = file_name
        if pattern_image.match( file_name ):
           image_path_http = actual_dir+ "/" + file_name

    # if there is card but no media and there is at least one dir then it is taken as a Collector (series, season)
    if card_path_os and not media_path_os and dir_list:
        
        # I collect the data from the card and the image if there is and the folders if there are
        
        #print( "!!!!!!!!!!    ", card_path_os, "   !!!!!!!!!!!!!!" )
        
        card = {}            
        parser = configparser.RawConfigParser()
        parser.read(card_path_os)
        try:
            
            # save the http path of the image
            card['image'] = image_path_http

            # saves the os path of the media - There is no
            card['media'] = None
            
            container_json_list = json.loads('[]')
            for folder in dir_list:
                container_json_list.append(os.path.join(actual_dir, folder))
            card['container'] = container_json_list
                
            title_json_list = {}
            title_json_list['hu'] = parser.get("titles", "title_hu")
            title_json_list['en'] = parser.get("titles", "title_en")
            card['title'] = title_json_list
                
            card['year'] = parser.get("general", "year")
                
            director_json_list = json.loads('[]')
            directors = parser.get("general", "director").split(",")            
            for director in directors:
                director_json_list.append(director)
            card['director'] = director_json_list
                
            card['length'] = parser.get("general", "length")
                
            sound_json_list = json.loads('[]')
            sounds = parser.get("general", "sound").split(",")
            for sound in sounds:
                sound_json_list.append(sound)
            card['sound'] = sound_json_list

            sub_json_list = json.loads('[]')
            subs = parser.get("general", "sub").split(",")
            for sub in subs:
                sub_json_list.append(sub)
            card['sub'] = sub_json_list

            genre_json_list = json.loads('[]')
            genres = parser.get("general", "genre").split(",")
            for genre in genres:
                genre_json_list.append(genre)
            card['genre'] = genre_json_list

            theme_json_list = json.loads('[]')
            themes = parser.get("general", "theme").split(",")
            for theme in themes:
                theme_json_list.append(theme)
            card['theme'] = theme_json_list
                
            actor_json_list = json.loads('[]')
            actors = parser.get("general", "actor").split(",")
            for actor in actors:
                actor_json_list.append(actor)
            card['actor'] = actor_json_list

            nationality_json_list = json.loads('[]')
            nationalities = parser.get("general", "nationality").split(",")
            for nationality in nationalities:
                nationality_json_list.append(nationality)
            card['nationality'] = nationality_json_list
                
            card['best'] = parser.get("extra", "best")
            card['new'] = parser.get("extra", "new")
            card['favorite'] = parser.get("extra", "favorite")
                                                
            links = {}
            links['imdb'] = parser.get("links", "imdb")
            card['links'] = links
            
                
        except (configparser.NoSectionError, configparser.NoOptionError):
                
                print(configparser.NoOptionError)
                # TODO It could be more sophisticated, depending what field failed
                
                card['image'] = ""
                card['media'] = ""
                title_json_list = {}
                title_json_list['hu'] = media_name
                title_json_list['en'] = media_name
                card['title'] = title_json_list
                
                card['year'] = ""
                card['director'] = json.loads('[]')
                card['length'] = ""
                card['sound'] = json.loads('[]')
                card['sub'] = json.loads('[]')
                card['genre'] = json.loads('[]')
                card['theme'] = json.loads('[]')
                card['actor'] = json.loads('[]')
                card['nationality'] = json.loads('[]')
                
                card['best'] = ""
                card['new'] = ""
                card['favorite'] = ""
                                        
                card['links'] = {}
           

        # if the filter is for value
        if f_search == 'v':
            if card[f_key] != f_value:
                return
        
        # if the filter is for array
        elif f_search == 'a':
            if f_value not in card[f_key]:
                return
        # the card is saved
        json_list.append(card)
 
    # if the folder contains media file and card then it taken as a leaf
    elif card_path_os and media_path_os:

        # first collect every data from the card
        card = {}            
        parser = configparser.RawConfigParser()
        parser.read(card_path_os)
        try:
            
            # save the http path of the image
            card['image'] = image_path_http

            # saves the os path of the media
            card['media'] = media_path_os
            
            container_json_list = json.loads('[]')
            card['container'] = container_json_list
                
            title_json_list = {}
            title_json_list['hu'] = parser.get("titles", "title_hu")
            title_json_list['en'] = parser.get("titles", "title_en")
            card['title'] = title_json_list
                
            card['year'] = parser.get("general", "year")
                
            director_json_list = json.loads('[]')
            directors = parser.get("general", "director").split(",")            
            for director in directors:
                director_json_list.append(director)
            card['director'] = director_json_list
                
            card['length'] = parser.get("general", "length")
                
            sound_json_list = json.loads('[]')
            sounds = parser.get("general", "sound").split(",")
            for sound in sounds:
                sound_json_list.append(sound)
            card['sound'] = sound_json_list

            sub_json_list = json.loads('[]')
            subs = parser.get("general", "sub").split(",")
            for sub in subs:
                sub_json_list.append(sub)
            card['sub'] = sub_json_list

            genre_json_list = json.loads('[]')
            genres = parser.get("general", "genre").split(",")
            for genre in genres:
                genre_json_list.append(genre)
            card['genre'] = genre_json_list

            theme_json_list = json.loads('[]')
            themes = parser.get("general", "theme").split(",")
            for theme in themes:
                theme_json_list.append(theme)
            card['theme'] = theme_json_list
                
            actor_json_list = json.loads('[]')
            actors = parser.get("general", "actor").split(",")
            for actor in actors:
                actor_json_list.append(actor)
            card['actor'] = actor_json_list

            nationality_json_list = json.loads('[]')
            nationalities = parser.get("general", "nationality").split(",")
            for nationality in nationalities:
                nationality_json_list.append(nationality)
            card['nationality'] = nationality_json_list
                
            card['best'] = parser.get("extra", "best")
            card['new'] = parser.get("extra", "new")
            card['favorite'] = parser.get("extra", "favorite")
                                                
            links = {}
            links['imdb'] = parser.get("links", "imdb")
            card['links'] = links
            
                
        except (configparser.NoSectionError, configparser.NoOptionError):
                
                print(configparser.NoOptionError)
                # TODO It could be more sophisticated, depending what field failed
                
                card['image'] = ""
                card['media'] = ""
                title_json_list = {}
                title_json_list['hu'] = media_name
                title_json_list['en'] = media_name
                card['title'] = title_json_list
                
                card['year'] = ""
                card['director'] = json.loads('[]')
                card['length'] = ""
                card['sound'] = json.loads('[]')
                card['sub'] = json.loads('[]')
                card['genre'] = json.loads('[]')
                card['theme'] = json.loads('[]')
                card['actor'] = json.loads('[]')
                card['nationality'] = json.loads('[]')
                
                card['best'] = ""
                card['new'] = ""
                card['favorite'] = ""
                                        
                card['links'] = {}
           

        # if the filter is for value
        if f_search == 'v':
            if card[f_key] != f_value:
                return
        
        # if the filter is for array
        elif f_search == 'a':
            if f_value not in card[f_key]:
                return
        # the card is saved
        json_list.append(card)


    # if the folder does not contain a media file and a card then it is taken as a simple folder
    else:

        # so it goes through the subfolders, there is any
        for name in dir_list:
            subfolder_path_os = os.path.join(actual_dir, name)            
            folder_investigation( subfolder_path_os, json_list, f_key, f_value, f_search )


    # and finaly returns
    return



# Get the Parameters from Ajax
#data = cgi.FieldStorage()
#f_key = data["key"].value
#f_value = data["value"].value
#f_search = data["search"].value
#rootdir = data["root-dir"].value

f_key='genre'
f_value='animation'
f_search='a'
rootdir='./../media/Films/Mezga.Csalad/S01'


pattern_media = re.compile("^.+[.](avi|mpg|mkv|mp4|flv)$")
pattern_card = re.compile("card.ini$")
pattern_image = re.compile( "^image[.]jp(eg|g)$" )

media_list = json.loads('[]')
folder_investigation(rootdir, media_list, f_key, f_value, f_search)

print('Content-Type: application/json')
print()
print(json.dumps(media_list, sort_keys=True, indent=4) )
