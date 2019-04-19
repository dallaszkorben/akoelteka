import os
import re
import configparser

from akoteka.handle_property import Property
from akoteka.handle_property import get_config_ini
from akoteka.handle_property import config_ini
from akoteka.handle_property import _

from akoteka.accessories import collect_cards
from akoteka.accessories import get_pattern_video
from akoteka.accessories import get_pattern_audio
from akoteka.accessories import get_pattern_image
from akoteka.accessories import get_pattern_card
from akoteka.accessories import get_pattern_length
from akoteka.accessories import get_pattern_year

HIGHLIGHT = '\033[31m'
COLORBACK = '\033[0;0m'

#def folder_investigation( actual_dir, json_list):
def folder_investigation( actual_dir, category):
    
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

        card_ini = Property( card_path_os, True )

        # --- title ---
        title_orig = card_ini.get('titles', 'title_orig', '')
        title_en = card_ini.get('titles', 'title_en', '')
        title_hu = card_ini.get('titles', 'title_hu', '')
        print(card_ini.get('titles', 'title_en', ''),end=': ')

        if not title_orig:
            card_ini.update("titles", 'title_orig', title_en)
        
        # --- orderby ---
        orderby = 'title'
        orderby = card_ini.get("control", 'orderby', 'title', False)
        card_ini.update("control", 'orderby', orderby)
        print('.', end='')

    # --------------------------------
    #
    # it is a MEDIA CARD dir
    #
    # there is:     -Card 
    #               -Media
    # 
    # --------------------------------
    elif card_path_os and media_path_os:

#        err = []
        card_ini = Property( card_path_os, True )

# === [titles] ===

        # --- title ---

        title_orig = card_ini.get('titles', 'title_orig', '')
        title_en = card_ini.get('titles', 'title_en', '')
        title_hu = card_ini.get('titles', 'title_hu', '')
        print(card_ini.get('titles', 'title_en', ''),end=': ')

        if not title_orig:
            card_ini.update("titles", 'title_orig', title_en)

# === [general] ===


# === [rating] ===
            
        # --- Rate ---
        rate = card_ini.get('rating', 'rate', '0', False)
        card_ini.update('rating', 'rate', str(int(rate.split('.')[0])))
        print('.', end='')
 
# === [control] ===
           
        # --- media ---
        if get_pattern_audio().match(media_name):
            media = 'audio'

        elif get_pattern_video().match(media_name):
            media = 'video'

        else:
            media = 'video'

        media = card_ini.get("general", 'media', media, False)
        card_ini.update("control", 'media', media)
        print('.', end='')

        # --- category ---
        card_ini.update("control", 'category', category)
        print('.', end='')
        
        # --- orderby ---
        orderby = 'title'
        orderby = card_ini.get("control", 'orderby', 'title', False)
        card_ini.update("control", 'orderby', orderby)
        print('.', end='')
        
# -----------            
# --- FIX ---
# -----------

        # --- music+talk genre fix ---
        genres = card_ini.get('general', 'genre', '', False)
        genrelist = genres.split(',')
        newgenrelist = []

        for genre in genrelist:
            if genre[:len(category) + 1] != category + "_":
                genre = category + "_" + genre
            newgenrelist.append(genre)
        newgenre = ",".join(newgenrelist)

        if genres and (category == 'music' or category == 'talk'):

            card_ini.update('general', 'genre', newgenre)
            print('.', end='')
            
        # --- remove [general]media
        card_ini.remove_option('general', 'media')
        
        # --- remove [general]category
        card_ini.remove_option('general', 'category')
        
        
        
        
        
        
        # --- fix [links] ---
        # --- Links ---

        #links = card_ini.get("general", 'links', "", False).split(",")
        #for link in links:
        #    linkblock = link.split('>')
        #    if len(linkblock) == 2:
        #        card_ini.update("links", linkblock[0], linkblock[1])
        #print('.', end='')
        #card_ini.remove_option("general", "links")



    

        print('')
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
        folder_investigation( subfolder_path_os, category )

    # and finaly returns
    return

def main():
    paths = "/media/akoel/Movies/Final/03.Talk"
    folder_investigation(paths, 'talk')

    paths = "/media/akoel/Movies/Final/02.Music"
    folder_investigation(paths, 'music')

    paths = "/media/akoel/Movies/Final/01.Movie"
    folder_investigation(paths, 'movie')
