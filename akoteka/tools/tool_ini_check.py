import os
import re
import configparser

from akoteka.handle_property import get_config_ini
from akoteka.handle_property import config_ini
from akoteka.handle_property import Property
from akoteka.handle_property import _

from akoteka.accessories import collect_cards
from akoteka.accessories import get_pattern_video
from akoteka.accessories import get_pattern_audio
from akoteka.accessories import get_pattern_image
from akoteka.accessories import get_pattern_card
from akoteka.accessories import get_pattern_length
from akoteka.accessories import get_pattern_year
from akoteka.accessories import get_pattern_rate

REDCOLOR = '\033[31m'
GREENCOLOR = '\033[0;32m'
COLORBACK = '\033[0;0m'

#def folder_investigation( actual_dir, json_list):
def folder_investigation( actual_dir):
    
    # Collect files and and dirs in the current directory
    file_list = [f for f in os.listdir(actual_dir) if os.path.isfile(os.path.join(actual_dir, f))] if os.path.exists(actual_dir) else []
    dir_list = [d for d in os.listdir(actual_dir) if os.path.isdir(os.path.join(actual_dir, d))] if os.path.exists(actual_dir) else []

    # now I got to a certain level of directory structure
    card_path_os = None
    media_path_os = None
    image_path_os = None
    media_name = None
    
    is_card_dir = True

    # Go through all files in the folder
    for file_name in file_list:

        # find the Card
        if get_pattern_card().match( file_name ):
            card_path_os = os.path.join(actual_dir, file_name)
            
        # find the Media (video or audio)
        if get_pattern_audio().match(file_name) or get_pattern_video().match(file_name):
            media_path_os = os.path.join(actual_dir, file_name)
            media_name = file_name
            
        # find the Image
        if get_pattern_image().match( file_name ):
           image_path_os = os.path.join(actual_dir, file_name)

    card = {}
    
    card['title'] = {}

    card['storyline'] = {}
                
    general_json_list = {}
    general_json_list['director'] = []
    general_json_list['sound'] = []
    general_json_list['sub'] = [] 
    general_json_list['genre'] = []
    general_json_list['theme'] = []
    general_json_list['actor'] = []
    general_json_list['country'] = []
    general_json_list['links'] = []
    card['general'] = general_json_list
                
    card['rating'] = {}
                                        
    extra_json_list = {}    
    extra_json_list['recent-folder'] = actual_dir
    extra_json_list['sub-cards'] = []
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
          
        err = []          
                
         # define the Property file
        card_ini = Property( card_path_os, False )
        
# --- titles ---
        
        title_orig = card_ini.get("titles", "title_orig", None)
        if title_orig is None:
            msg = {
                "message": "Missing",
                "section": "titles",
                "option": "title_orig"
            }
            err.append(msg)
        elif not title_orig:
            msg = {
                "message": "Not set",
                "section": "titles",
                "option": "title_orig"
            }
            err.append(msg)
        
        title_hu = card_ini.get("titles", "title_hu", None)
        if title_hu is None:
            msg = {
                "message": "Missing",
                "section": "titles",
                "option": "title_hu"
            }
            err.append(msg)
        elif not title_hu:
            msg = {
                "message": "Not set",
                "section": "titles",
                "option": "title_hu"
            }
            err.append(msg)

        title_en = card_ini.get("titles", "title_en", None)
        if title_en is None:
            msg = {
                "message": "Missing",
                "section": "titles",
                "option": "title_en"
            }
            err.append(msg)
        elif not title_en:
            msg = {
                "message": "Not set",
                "section": "titles",
                "option": "title_en"
            }
            err.append(msg)

        if err:
            print(GREENCOLOR, "Collector: ", COLORBACK, card_path_os)
            for msg in err:                
                print("    ", msg['message'] + ":", "["+msg['section']+"]", msg['option'])
 
    # --------------------------------
    #
    # it is a MEDIA CARD dir
    #
    # there is:     -Card 
    #               -Media
    # 
    # --------------------------------
    elif card_path_os and media_path_os:

        err = []

        # define the Property file
        card_ini = Property( card_path_os, False )
        
# --- titles ---
        
        title_orig = card_ini.get("titles", "title_orig", None)
        if title_orig is None:
            msg = {
                "message": "Missing",
                "section": "titles",
                "option": "title_orig"
            }
            err.append(msg)
        elif not title_orig:
            msg = {
                "message": "Not set",
                "section": "titles",
                "option": "title_orig"
            }
            err.append(msg)
        
        title_hu = card_ini.get("titles", "title_hu", None)
        if title_hu is None:
            msg = {
                "message": "Missing",
                "section": "titles",
                "option": "title_hu"
            }
            err.append(msg)
        elif not title_hu:
            msg = {
                "message": "Not set",
                "section": "titles",
                "option": "title_hu"
            }
            err.append(msg)

        title_en = card_ini.get("titles", "title_en", None)
        if title_en is None:
            msg = {
                "message": "Missing",
                "section": "titles",
                "option": "title_en"
            }
            err.append(msg)
        elif not title_en:
            msg = {
                "message": "Not set",
                "section": "titles",
                "option": "title_en"
            }
            err.append(msg)
        
# --- media ---
        
        media = card_ini.get("general", "media", None)
        if media is None:
            msg = {
                "message": "Missing",
                "section": "general",
                "option": "media"
            }
            media = 'video'
            err.append(msg)
        elif not media:
            msg = {
                "message": "Not set",
                "section": "general",
                "option": "media"
            }
            media = 'video'
            err.append(msg)
            
        elif "_" in _("media_" + media): 
            msg = {
                "message": "Wrong value '" + media + "' in ",
                "section": "general",
                "option": "media"
            }
            media = 'video'
            err.append(msg)

# --- category ---
        
        category = card_ini.get("general", "category", None)
        if category is None:
            msg = {
                "message": "Missing",
                "section": "general",
                "option": "category"
            }
            category = 'movie'
            err.append(msg)
        elif not category:
            msg = {
                "message": "Not set",
                "section": "general",
                "option": "category"
            }
            category = 'movie'
            err.append(msg)
            
        elif "_" in _("category_" + category): 
            msg = {
                "message": "Wrong value '" + category + "' in ",
                "section": "general",
                "option": "category"
            }
            media = 'movie'
            err.append(msg)
        
# --- storyline ---
        
        storyline_en = card_ini.get("storyline", "storyline_en", None)
        if storyline_en is None:
            msg = {
                "message": "Missing",
                "section": "storyline",
                "option": "storyline_en"
            }
            err.append(msg)
        storyline_hu = card_ini.get("storyline", "storyline_hu", None)
        if storyline_hu is None:
            msg = {
                "message": "Missing",
                "section": "storyline",
                "option": "storyline_hu"
            }
            err.append(msg)
    
# --- year ---

        year = card_ini.get("general", "year", None)
        if year is None:
            msg = {
                "message": "Missing",
                "section": "general",
                "option": "year"
            }
            err.append(msg)
        elif not year:
            msg = {
                "message": "Not set",
                "section": "general",
                "option": "year"
            }
            err.append(msg)
        elif not get_pattern_year().match( year ):    
            msg = {
                "message": "Wrong format '" + year + "' in ",
                "section": "general",
                "option": "year"
            }
            err.append(msg)

# --- length ---

        length = card_ini.get("general", "length", None)
        if length is None:
            msg = {
                "message": "Missing",
                "section": "general",
                "option": "length"
            }
            err.append(msg)
        elif not length:
            msg = {
                "message": "Not set",
                "section": "general",
                "option": "length"
            }
            err.append(msg)
        elif not get_pattern_length().match( length ):    
            msg = {
                "message": "Wrong format '" + length + "' in ",
                "section": "general",
                "option": "length"
            }
            err.append(msg)

# --- director ---

        if category == 'movie':
            
            director = card_ini.get("general", "director", None)
            if director is None:
                msg = {
                    "message": "Missing",
                    "section": "general",
                    "option": "director"
                }
                err.append(msg)
            elif not director:
                msg = {
                    "message": "Not set",
                    "section": "general",
                    "option": "director"
                }
                err.append(msg)
            elif len(director.split(",")) < 1: 
                msg = {
                    "message": "Wrong format: " + director,
                    "section": "general",
                    "option": "director"
                }
                err.append(msg)

# --- actor ---

        if category == 'movie':
            
            actor = card_ini.get("general", "actor", None)
            if actor is None:
                msg = {
                    "message": "Missing",
                    "section": "general",
                    "option": "actor"
                }
                err.append(msg)
#            elif not actor:
#                msg = {
#                    "message": "Not set",
#                    "section": "general",
#                    "option": "actor"
#                }
#                err.append(msg)
#            elif len(actor.split(",")) < 1: 
#                msg = {
#                    "message": "Wrong format: " + actor,
#                    "section": "general",
#                    "option": "actor"
#                }
#                err.append(msg)
   
# --- sound ---

        if media == 'video' or media == 'audio':
            
            sounds = card_ini.get("general", "sound", None)
            if sounds is None:
                msg = {
                    "message": "Missing",
                    "section": "general",
                    "option": "sound"
                }
                err.append(msg)
            elif sounds: 
                
                soundslist = sounds.split(",")
                for sound in soundslist:
                    if sound:
                        if "lang_" in _("lang_" + sound.strip()):
                            msg = {
                                "message": "Wrong format: " + sound,
                                "section": "general",
                                "option": "sound"
                            }
                            err.append(msg)

# --- subtitle ---

        if media == 'video':
            
            subs = card_ini.get("general", "sub", None)
            if subs is None:
                msg = {
                    "message": "Missing",
                    "section": "general",
                    "option": "sub"
                }
                err.append(msg)
            elif subs: 
                
                sublist = subs.split(",")
                for sub in sublist:
                    if sub:
                        if "lang_" in _("lang_" + sub.strip()):
                            msg = {
                                "message": "Wrong format: " + sub,
                                "section": "general",
                                "option": "sub"
                            }
                            err.append(msg)

# --- genre ---

        genres = card_ini.get("general", "genre", None)
        if genres is None:
            msg = {
                "message": "Missing",
                "section": "general",
                "option": "genre"
            }
            err.append(msg)
        if not genres:
            msg = {
                "message": "Not set",
                "section": "general",
                "option": "genre"
            }
            err.append(msg)
            
        else:                 
            genrelist = genres.split(",")
            for genre in genrelist:
                if genre:
                    if "genre_" in _("genre_" + genre.strip()):
                        msg = {
                            "message": "Wrong format: " + genre,
                            "section": "general",
                            "option": "genre"
                        }
                        err.append(msg)

# --- country ---

        countries = card_ini.get("general", "country", None)
        if countries is None:
            msg = {
                "message": "Missing",
                "section": "general",
                "option": "country"
            }
            err.append(msg)
        if not countries:
            msg = {
                "message": "Not set",
                "section": "general",
                "option": "country"
            }
            err.append(msg)
            
        else:                 
            countrylist = countries.split(",")
            for country in countrylist:
                if country:
                    if "country_" in _("country_" + country.strip()):
                        msg = {
                            "message": "Wrong format: " + country,
                            "section": "general",
                            "option": "country"
                        }
                        err.append(msg)

# --- rating-new ---

        new = card_ini.get("rating", "new", None)
        if new is None:
            msg = {
                "message": "Missing",
                "section": "rating",
                "option": "new"
            }
            err.append(msg)
        if not new:
            msg = {
                "message": "Not set",
                "section": "rating",
                "option": "new"
            }
            err.append(msg)
            
        elif new != 'y' and new != 'n':                 
            msg = {
                "message": "Wrong value: " + new,
                "section": "rating",
                "option": "new"
            }
            err.append(msg)

# --- rating-favorite ---

        favorite = card_ini.get("rating", "favorite", None)
        if favorite is None:
            msg = {
                "message": "Missing",
                "section": "rating",
                "option": "favorite"
            }
            err.append(msg)
        if not favorite:
            msg = {
                "message": "Not set",
                "section": "rating",
                "option": "favorite"
            }
            err.append(msg)            
        elif favorite != 'y' and favorite != 'n':                 
            msg = {
                "message": "Wrong value: " + favorite,
                "section": "rating",
                "option": "favorite"
            }
            err.append(msg)

# --- rating-rate ---

        rate = card_ini.get("rating", "rate", None)
        if rate is None:
            msg = {
                "message": "Missing",
                "section": "rating",
                "option": "rate"
            }
            err.append(msg)
        elif not rate:
            msg = {
                "message": "Not set",
                "section": "rating",
                "option": "rate"
            }
            err.append(msg)
        elif not get_pattern_rate().match( rate ):    
            msg = {
                "message": "Wrong format '" + rate + "' in ",
                "section": "rating",
                "option": "rate"
            }
            err.append(msg)

        # show error
        if err:
            print(REDCOLOR, "Media Card: ", COLORBACK, card_path_os)
            for msg in err:                
                print( "    ", msg['message'] + ":", "["+msg['section']+"]", msg['option'])

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
        folder_investigation( subfolder_path_os )

    # and finally returns
    return

    
def main():    
    config_ini_function = get_config_ini()
    paths = config_ini_function.get_media_path()
    folder_investigation(paths)
