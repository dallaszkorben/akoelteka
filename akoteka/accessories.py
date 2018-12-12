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
        "value-dict": False,
        "section": "rating"
    },
    "new":{
        "store-mode": "v",
        "key-dict-prefix": "title_",
        "value-dict": False,
        "section": "rating"
    },
    "favorite":{
        "store-mode": "v",
        "key-dict-prefix": "title_",
        "value-dict": False,
        "section": "rating"
    },
    "director":{
        "store-mode": "a",
        "key-dict-prefix": "title_",
        "value-dict": False,
        "section": "general"
    },
    "actor": {
        "store-mode": "a",
        "key-dict-prefix": "title_",
        "value-dict": False,
        "section": "general"
    },
    "theme":{
        "store-mode": "a",
        "key-dict-prefix": "title_",
        "value-dict": True,
        "value-dict-prefix": "theme_",
        "section": "general"
    },
    "genre":{
        "store-mode": "a",
        "key-dict-prefix": "title_",
        "value-dict": True,
        "value-dict-prefix": "genre_",
        "section": "general"
    }
}

def folder_investigation( actual_dir, json_list):
    
    # Collect files and and dirs in the current directory
    file_list = [f for f in os.listdir(actual_dir) if os.path.isfile(os.path.join(actual_dir, f))]
    dir_list = [d for d in os.listdir(actual_dir) if os.path.isdir(os.path.join(actual_dir, d))]

    # now I got to a certain level of directory structure
    card_path_os = None
    media_path_os = None
    image_path_os = None
    media_name = None
    
    is_card_dir = True

    # Go through all files in the folder
    for file_name in file_list:

        #
        # collect the files which count
        #
        
        # find the Card
        if pattern_card.match( file_name ):
            card_path_os = os.path.join(actual_dir, file_name)
            
        # find the Media
        if pattern_media.match(file_name):            
            media_path_os = os.path.join(actual_dir, file_name)
            media_name = file_name
            
        # find the Image
        if pattern_image.match( file_name ):
           image_path_os = os.path.join(actual_dir, file_name)


    card = {}
    
    title_json_list = {}
    title_json_list['hu'] = media_name
    title_json_list['en'] = media_name
    card['title'] = title_json_list
                
    general_json_list = {}
    general_json_list['year'] = ""
    general_json_list['director'] = json.loads('[]')
    general_json_list['length'] = ""
    general_json_list['sound'] = json.loads('[]')
    general_json_list['sub'] = json.loads('[]')
    general_json_list['genre'] = json.loads('[]')
    general_json_list['theme'] = json.loads('[]')
    general_json_list['actor'] = json.loads('[]')
    general_json_list['country'] = json.loads('[]')
    card['general'] = general_json_list
                
    rating_json_list = {}
    rating_json_list['best'] = ""
    rating_json_list['new'] = ""
    rating_json_list['favorite'] = ""
    card['rating'] = rating_json_list
                                        
    card['links'] = {}

    extra_json_list = {}    
    extra_json_list['image-path'] = ""
    extra_json_list['media-path'] = ""
    extra_json_list['recent-folder'] = actual_dir
    extra_json_list['sub-cards'] = json.loads('[]')
    card['extra'] = extra_json_list


    # ----------------------------------
    #
    # it is a COLLECTOR CARD dir
    #
    # there is:     -Card 
    #               -at least one Dir
    # ther is NO:   -Media
    #  
    # ----------------------------------
    if card_path_os and not media_path_os and dir_list:
                
        parser = configparser.RawConfigParser()
        parser.read(card_path_os)
        
        # I collect the data from the card and the image if there is and the folders if there are
        try:
            
            # save the http path of the image
            card['extra']['image-path'] = image_path_os

            # saves the os path of the media - There is no
            card['extra']['media-path'] = None
            
            card['title']['hu'] = parser.get("titles", "title_hu")
            card['title']['en'] = parser.get("titles", "title_en")
                
        except (configparser.NoSectionError, configparser.NoOptionError) as nop_err:
            print(nop_err, "in ", card_path_os)
                # TODO It could be more sophisticated, depending what field failed

        json_list.append(card)
        
    # --------------------------------
    #
    # it is a MEDIA CARD dir
    #
    # there is:     -Card 
    #               -Media
    # 
    # --------------------------------
    elif card_path_os and media_path_os:

        # first collect every data from the card
        parser = configparser.RawConfigParser()
        parser.read(card_path_os)
        try:
            
            # save the http path of the image
            card['extra']['image-path'] = image_path_os

            # saves the os path of the media
            card['extra']['media-path'] = media_path_os
            
            card['title']['hu'] = parser.get("titles", "title_hu")
            card['title']['en'] = parser.get("titles", "title_en")
                
            card['general']['year'] = parser.get("general", "year")
                
            directors = parser.get("general", "director").split(",")            
            for director in directors:
                card['general']['director'].append(director.strip())
                
            card['general']['length'] = parser.get("general", "length")
                
            sounds = parser.get("general", "sound").split(",")
            for sound in sounds:
                card['general']['sound'].append(sound.strip())

            subs = parser.get("general", "sub").split(",")
            for sub in subs:
                card['general']['sub'].append(sub.strip())

            genres = parser.get("general", "genre").split(",")
            for genre in genres:
                card['general']['genre'].append(genre.strip())

            themes = parser.get("general", "theme").split(",")
            for theme in themes:
                card['general']['theme'].append(theme.strip())
                
            actors = parser.get("general", "actor").split(",")
            for actor in actors:
                card['general']['actor'].append(actor.strip())

            countries = parser.get("general", "country").split(",")
            for country in countries:
                card['general']['country'].append(country.strip())
                
            card['rating']['best'] = parser.get("rating", "best")
            card['rating']['new'] = parser.get("rating", "new")
            card['rating']['favorite'] = parser.get("rating", "favorite")
                                                
            card['links']['imdb'] = parser.get("links", "imdb")
            
                
        except (configparser.NoSectionError, configparser.NoOptionError) as nop_err:
            print(nop_err, "in ", card_path_os)
            # TODO It could be more sophisticated, depending what field failed

        json_list.append(card)

    # ----------------------------------
    #
    # it is NO CARD dir
    #
    # ----------------------------------
    else:
        
        is_card_dir = False
        
    # ----------------------------
    #
    # Through the Sub-directories
    #
    # ----------------------------    
    for name in dir_list:
        subfolder_path_os = os.path.join(actual_dir, name)
        folder_investigation( subfolder_path_os, card['extra']['sub-cards'] if is_card_dir else json_list )

    # and finaly returns
    return

def collect_cards( rootdirs ):    
    media_list = json.loads('[]')

    for rootdir in rootdirs:
        folder_investigation(rootdir, media_list)

    #print (media_list)
    return media_list
