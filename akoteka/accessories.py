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



def folder_investigation( actual_dir, json_list, filter_selection ):
    
    # Collect files and and dirs in the current directory
    file_list = [f for f in os.listdir(actual_dir) if os.path.isfile(os.path.join(actual_dir, f))]
    dir_list = [d for d in os.listdir(actual_dir) if os.path.isdir(os.path.join(actual_dir, d))]

    #print(json.dumps( file_list, sort_keys=True, indent=4) )
   
    # now I got to a certain level of directory structure
    card_path_os = None
    media_path_os = None
    image_path_os = None
    media_name = None

    # Go through all files in the folder
    for file_name in file_list:

        # collect the files which count
        if pattern_card.match( file_name ):
            card_path_os = os.path.join(actual_dir, file_name)
        if pattern_media.match(file_name):            
            media_path_os = os.path.join(actual_dir, file_name)
            media_name = file_name
        if pattern_image.match( file_name ):
           image_path_os = os.path.join(actual_dir, file_name)


    card = {}
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

    #
    # if there is card but no media and there is at least one dir then it is taken as a:
    # 
    # COLLECTOR
    #
    # the we stop here
    #
    if card_path_os and not media_path_os and dir_list:
                
        parser = configparser.RawConfigParser()
        parser.read(card_path_os)
        
        # I collect the data from the card and the image if there is and the folders if there are
        try:
            
            # save the http path of the image
            card['image-path'] = image_path_os

            # saves the os path of the media - There is no
            card['media-path'] = None
            
            child_paths = json.loads('[]')
            for folder in dir_list:
                card['child-paths'].append(os.path.join(actual_dir, folder))
            
            card['title']['hu'] = parser.get("titles", "title_hu")
            card['title']['en'] = parser.get("titles", "title_en")
                
        except (configparser.NoSectionError, configparser.NoOptionError):
                
                print(configparser.NoOptionError)
                # TODO It could be more sophisticated, depending what field failed

        json_list.append(card)
        return
 
    #
    # if the folder contains media file and card then it taken as a:
    #
    # MEDIA CARD
    #
    elif card_path_os and media_path_os:

        # first collect every data from the card
        parser = configparser.RawConfigParser()
        parser.read(card_path_os)
        try:
            
            # save the http path of the image
            card['image-path'] = image_path_os

            # saves the os path of the media
            card['media-path'] = media_path_os
            
            child_paths = json.loads('[]')
            card['child-paths'] = child_paths
                
            card['title']['hu'] = parser.get("titles", "title_hu")
            card['title']['en'] = parser.get("titles", "title_en")
                
            card['year'] = parser.get("general", "year")
                
            directors = parser.get("general", "director").split(",")            
            for director in directors:
                card['director'].append(director.strip())
                
            card['length'] = parser.get("general", "length")
                
            sounds = parser.get("general", "sound").split(",")
            for sound in sounds:
                card['sound'].append(sound.strip())

            subs = parser.get("general", "sub").split(",")
            for sub in subs:
                card['sub'].append(sub.strip())

            genres = parser.get("general", "genre").split(",")
            for genre in genres:
                card['genre'].append(genre.strip())

            themes = parser.get("general", "theme").split(",")
            for theme in themes:
                card['theme'].append(theme.strip())
                
            actors = parser.get("general", "actor").split(",")
            for actor in actors:
                card['actor'].append(actor.strip())

            nationalities = parser.get("general", "nationality").split(",")
            for nationality in nationalities:
                card['nationality'].append(nationality.strip())
                
            card['best'] = parser.get("extra", "best")
            card['new'] = parser.get("extra", "new")
            card['favorite'] = parser.get("extra", "favorite")
                                                
            card['links']['imdb'] = parser.get("links", "imdb")
            
                
        except (configparser.NoSectionError, configparser.NoOptionError):
                
                print(configparser.NoOptionError)
                # TODO It could be more sophisticated, depending what field failed

        fits = True
        for category, value in filter_selection.items():
            
            if value != None and value != "":
                
                if filter_key[category]['store-mode'] == 'v':
                    if value != card[category]:
                        fits = False
                elif filter_key[category]['store-mode'] == 'a':
                    if value not in card[category]:
                        fits = False
                else:
                    fits = False
        if fits:
            json_list.append(card)

    #
    # if the folder does not contain a media file and a card then it is taken as a simple folder
    #
    else:

        # so it goes through the subfolders, there is any
        for name in dir_list:
            subfolder_path_os = os.path.join(actual_dir, name)            
            folder_investigation( subfolder_path_os, json_list, filter_selection )


    # and finaly returns
    return

def collect_cards( rootdirs, filter_selection ):
    media_list = json.loads('[]')

    for rootdir in rootdirs:
        folder_investigation(rootdir, media_list, filter_selection)

    return media_list
