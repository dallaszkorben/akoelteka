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
    card['image-path'] = ""
    card['media-path'] = ""
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
    card['country'] = json.loads('[]')
                
    card['best'] = ""
    card['new'] = ""
    card['favorite'] = ""
                                        
    card['links'] = {}

    card['recent-folder'] = actual_dir
    card['sub-cards'] = json.loads('[]')


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
            card['image-path'] = image_path_os

            # saves the os path of the media - There is no
            card['media-path'] = None
            
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
            card['image-path'] = image_path_os

            # saves the os path of the media
            card['media-path'] = media_path_os
            
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

            countries = parser.get("general", "country").split(",")
            for country in countries:
                card['country'].append(country.strip())
                
            card['best'] = parser.get("rating", "best")
            card['new'] = parser.get("rating", "new")
            card['favorite'] = parser.get("rating", "favorite")
                                                
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
        folder_investigation( subfolder_path_os, card['sub-cards'] if is_card_dir else json_list )

    # and finaly returns
    return

def collect_cards( rootdirs ):    
    media_list = json.loads('[]')

    for rootdir in rootdirs:
        folder_investigation(rootdir, media_list)

    #print (media_list)
    return media_list
