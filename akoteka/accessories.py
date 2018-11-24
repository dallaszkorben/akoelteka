import os
import sys
import json
import re
import configparser
import cgi, cgitb

pattern_media = re.compile("^.+[.](avi|mpg|mkv|mp4|flv)$")
pattern_image = re.compile( "^image[.]jp(eg|g)$" )
pattern_card = re.compile("^card.ini$")

filter_key = {
    "all":{
        "store-mode": "*",
        "key-dict-prefix": "title_",
        "value-dict": False        
    },
    "best":{
        "store-mode": "v",
        "key-dict-prefix": "title_",
        "value-dict": False
    },
    "new":{
        "store-mode": "v",
        "key-dict-prefix": "title_",
        "value-dict": False
    },
    "favorite":{
        "store-mode": "v",
        "key-dict-prefix": "title_",
        "value-dict": False
    },
    "director":{
        "store-mode": "a",
        "key-dict-prefix": "title_",
        "value-dict": False
    },
    "actor": {
        "store-mode": "a",
        "key-dict-prefix": "title_",
        "value-dict": False
    },
    "theme":{
        "store-mode": "a",
        "key-dict-prefix": "title_",
        "value-dict": True,
        "value-dict-prefix": "theme_"
    },
    "genre":{
        "store-mode": "a",
        "key-dict-prefix": "title_",
        "value-dict": True,
        "value-dict-prefix": "genre_"        
    }
}


def read_config_file():
    
    pass
    

#
# 
#    hit_list = {
#        "genre": set(),
#        "theme": set(),
#        "director": set(),
#        "actor": set()        
#    }
#
#
def collect_filters( actual_dir, hit_list ):

    for dirpath, dirnames, filenames in os.walk(actual_dir):

        for name in filenames:
            if pattern_card.match( name ):
                card_path_os = os.path.join(dirpath, name)
                
                parser = configparser.RawConfigParser()
                parser.read(card_path_os)
            
                for category, lst in hit_list.items():
                    fk = filter_key[category]

                    try:
                
                        value = parser.get( "general", category )

                        if fk["store-mode"] == 'v':

                            if value:
                                hit_list[category].add(value.strip())
                                
                        elif fk["store-mode"] == 'a':
                                    
                            values = value.split(",")            
                            for value in values:
                                if value:
                                    
                                    hit_list[category].add(value.strip())
                
                    except (configparser.NoSectionError, configparser.NoOptionError) as e:
                        pass

    return hit_list



def folder_investigation( actual_dir, json_list, f_key, f_value, f_value_store_mode ):
    
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
        
        card = {}            
        parser = configparser.RawConfigParser()
        parser.read(card_path_os)
        try:
            
            # save the http path of the image
            card['image-path'] = image_path_http

            # saves the os path of the media - There is no
            card['media-path'] = None
            
            child_paths = json.loads('[]')
            for folder in dir_list:
                child_paths.append( os.path.join(actual_dir, folder) )
            card['child-paths'] = child_paths
                
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
                
                card['image-path'] = ""
                card['media-path'] = ""
                title_json_list = {}
                title_json_list['hu'] = media_name
                title_json_list['en'] = media_name
                card['child-paths'] = json.loads('[]')
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
        if f_value_store_mode == 'v':
            if card[f_key] != f_value:
                return
        
        # if the filter is for array
        elif f_value_store_mode == 'a':
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
            card['image-path'] = image_path_http

            # saves the os path of the media
            card['media-path'] = media_path_os
            
            child_paths = json.loads('[]')
            card['child-paths'] = child_paths
                
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
                
                card['image-path'] = ""
                card['media-path'] = ""
                card['child-paths'] = json.loads('[]')
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
        if f_value_store_mode == 'v':
            if card[f_key] != f_value:
                return
        
        # if the filter is for array
        elif f_value_store_mode == 'a':
            if f_value not in card[f_key]:
                return
        # the card is saved
        json_list.append(card)


    # if the folder does not contain a media file and a card then it is taken as a simple folder
    else:

        # so it goes through the subfolders, there is any
        for name in dir_list:
            subfolder_path_os = os.path.join(actual_dir, name)            
            folder_investigation( subfolder_path_os, json_list, f_key, f_value, f_value_store_mode )


    # and finaly returns
    return

#
# rootdir   - String    - the path where to start the search
# key       - String    - keywords in the Card file:
#                           best
#                           all - Special value, meaning all Card in the path
#                           favorite
#                           new
#                           actor
#                           director
#                           theme
#                           genre
# value     - String    - the value of the key whose Card you want in the list
# value_store_mode -String    - How the value is stored in the Card file
#                       - a: array
#                       - v: value
#                       - *: there will not be comparision, every card will be loaded
#
def collect_cards( rootdir=None, key=None, value=None, value_store_mode=None ):

    media_list = json.loads('[]')
    folder_investigation(rootdir, media_list, key, value, value_store_mode)

    #print(json.dumps(media_list, sort_keys=True, indent=4) )
    return media_list
