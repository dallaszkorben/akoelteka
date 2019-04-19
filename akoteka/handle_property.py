import os
import configparser
from pathlib import Path
#from akoteka.logger import logger

class Property(object):
       
    def __init__(self, file, writable=False, folder=None):
        self.writable = writable
        self.file = file
        self.folder = folder
        self.parser = configparser.RawConfigParser()
        
        # !!! make it CASE SENSITIVE !!! otherwise it duplicates the hit if there was a key with upper and lower cases. Now it throws an exception
        self.parser.optionxform = str

    def __write_file(self):
        
        if self.folder:
            Path(self.folder).mkdir(parents=True, exist_ok=True)
        
        with open(self.file, 'w', encoding='utf-8') as configfile:
            self.parser.write(configfile)


    def get(self, section, key, default_value, writable=None):        

        # if not existing file and we want to create it
        if not os.path.exists(self.file) and self.should_write(writable) :
            #self.log_msg("MESSAGE: No file found FILE NAME: " + self.file + " OPERATION: get")
            
            self.parser[section]={key: default_value}
            self.__write_file()
        self.parser.read(self.file, encoding='utf-8')

        # try to read the key
        try:
            result=self.parser.get(section,key)

        # if does not exist the key
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            #self.log_msg("MESSAGE: " + str(e) + " FILE NAME: " + self.file + " OPERATION: get")

            # if it should be write
            if self.should_write(writable):
                self.update(section, key, default_value)
                result=self.parser.get(section,key)
            else:
                result = default_value
        
        return result

    def getBoolean(self, section, key, default_value, writable=None):
        
        # if not existing file and we want to create it
        if not os.path.exists(self.file) and self.should_write(writable) :
            self.parser[section]={key: default_value}
            self.__write_file()
            
        # read the file
        self.parser.read(self.file, encoding='utf-8')

        # try to read the key
        try:
            result=self.parser.getboolean(section, key)
        
        # if does not exist the key
        except (configparser.NoSectionError, configparser.NoOptionError):

            # if it should be write
            if self.should_write(writable):

                self.update(section, key, default_value)
                # It is strange how it works with get/getboolean
                # Sometimes it reads boolean sometimes it reads string
                # I could not find out what is the problem
                #result=self.parser.get(section,key)
            result=default_value

        return result

    def update(self, section, key, value, source=None):

        # if not existing file        
        if not os.path.exists(self.file):
            #self.log_msg("MESSAGE: No file found FILE NAME: " + self.file + " OPERATION: update SOURCE: " + source if source else "")
            self.parser[section]={key: value}

        # if the file exists
        else:
            
            # read the file
            self.parser.read(self.file, encoding='utf-8')
            
            # try to set the value
            try:
                # if no section -> NoSectionError | if no key -> Create it
                self.parser.set(section, key, value)

            # if there is no such section
            except configparser.NoSectionError as e:
                #self.log_msg("MESSAGE: " + str(e) + " FILE NAME: " + self.file + " OPERATION: update SOURCE: " + source)
                self.parser[section]={key: value}

        # update
        self.__write_file()
        
    def remove_section(self, section):
        self.parser.remove_section(section)

    def remove_option(self, section, option):
        self.parser.read(self.file, encoding='utf-8')
        self.parser.remove_option(section, option)
        self.__write_file()
        
    def get_options(self, section):
        return self.parser.items(section)
    
    def should_write(self, writable):
        return ((writable is None and self.writable) or (writable))

# ====================
#
# Handle dictionary
#
# ====================
class Dict( Property ):
    
    DICT_FILE_PRE = "resources"
    DICT_FILE_EXT = "properties"
    DICT_FOLDER = "dict"
    DICT_SECTION = "dict"

    __instance = None

    def __new__(cls):
        if cls.__instance == None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @classmethod
    def get_instance(cls, lng):
        inst = cls.__new__(cls)
        cls.__init__(cls.__instance, lng)     
        return inst
        
    def __init__(self, lng):
        file = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.__class__.DICT_FOLDER, self.__class__.DICT_FILE_PRE + "_" + lng + "." + self.__class__.DICT_FILE_EXT)
        super().__init__( file )
    
    def _(self, key):
        return self.get(self.__class__.DICT_SECTION, key,  "[" + key + "]")

class Config:
    HOME = str(Path.home())
    CONFIG_FOLDER = '.akoteka'
    
    @staticmethod 
    def get_path_to_config_folder():
        return os.path.join(Config.HOME, Config.CONFIG_FOLDER)

# =====================
#
# Handle config.ini
#
# =====================
class ConfigIni( Property ):
    INI_FILE_NAME="config.ini"

    # (section, key, default)
    DEFAULT_LANGUAGE = ("general", "language", "hu")
    DEFAULT_SHOW_ORIGINAL_TITLE = ("general", "show-original-title", "n")
    DEFAULT_MEDIA_PATH = ("media", "media-path", ".")
    DEFAULT_MEDIA_PLAYER_VIDEO = ("media", "player-video", "mplayer")
    DEFAULT_MEDIA_PLAYER_VIDEO_PARAM = ("media", "player-video-param", "-zoom -fs -framedrop")
    DEFAULT_MEDIA_PLAYER_VIDEO_EXT = ("media", "player-video-ext", "divx,mkv,avi,mp4,webm")
    DEFAULT_MEDIA_PLAYER_AUDIO = ("media", "player-audio", "rhythmbox")
    DEFAULT_MEDIA_PLAYER_AUDIO_PARAM = ("media", "player-audio-param", "")
    DEFAULT_MEDIA_PLAYER_AUDIO_EXT = ("media", "player-audio-ext", "mp3,ogg")
    
    __instance = None    

    def __new__(cls):
        if cls.__instance == None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @classmethod
    def get_instance(cls):
        inst = cls.__new__(cls)
        cls.__init__(cls.__instance)
        return inst
        
    def __init__(self):
        folder = os.path.join(Config.HOME, Config.CONFIG_FOLDER)
        file = os.path.join(folder, ConfigIni.INI_FILE_NAME)
        super().__init__( file, True, folder )

    def get_language(self):
        return self.get(self.DEFAULT_LANGUAGE[0], self.DEFAULT_LANGUAGE[1], self.DEFAULT_LANGUAGE[2])

    def get_show_original_title(self):
        return self.get(self.DEFAULT_SHOW_ORIGINAL_TITLE[0], self.DEFAULT_SHOW_ORIGINAL_TITLE[1], self.DEFAULT_SHOW_ORIGINAL_TITLE[2])

    def get_media_path(self):
        return self.get(self.DEFAULT_MEDIA_PATH[0], self.DEFAULT_MEDIA_PATH[1], self.DEFAULT_MEDIA_PATH[2])

    def get_media_player_video(self):
        return self.get(self.DEFAULT_MEDIA_PLAYER_VIDEO[0], self.DEFAULT_MEDIA_PLAYER_VIDEO[1], self.DEFAULT_MEDIA_PLAYER_VIDEO[2])

    def get_media_player_video_param(self):
        return self.get(self.DEFAULT_MEDIA_PLAYER_VIDEO_PARAM[0], self.DEFAULT_MEDIA_PLAYER_VIDEO_PARAM[1], self.DEFAULT_MEDIA_PLAYER_VIDEO_PARAM[2])

    def get_media_player_video_ext(self):
        return self.get(self.DEFAULT_MEDIA_PLAYER_VIDEO_EXT[0], self.DEFAULT_MEDIA_PLAYER_VIDEO_EXT[1], self.DEFAULT_MEDIA_PLAYER_VIDEO_EXT[2])

    def get_media_player_audio(self):
        return self.get(self.DEFAULT_MEDIA_PLAYER_AUDIO[0], self.DEFAULT_MEDIA_PLAYER_AUDIO[1], self.DEFAULT_MEDIA_PLAYER_AUDIO[2])

    def get_media_player_audio_param(self):
        return self.get(self.DEFAULT_MEDIA_PLAYER_AUDIO_PARAM[0], self.DEFAULT_MEDIA_PLAYER_AUDIO_PARAM[1], self.DEFAULT_MEDIA_PLAYER_AUDIO_PARAM[2])

    def get_media_player_audio_ext(self):
        return self.get(self.DEFAULT_MEDIA_PLAYER_AUDIO_EXT[0], self.DEFAULT_MEDIA_PLAYER_AUDIO_EXT[1], self.DEFAULT_MEDIA_PLAYER_AUDIO_EXT[2])


    def set_language(self, lang):
        self.update(self.DEFAULT_LANGUAGE[0], self.DEFAULT_LANGUAGE[1], lang)

    def set_show_original_title(self, show):
        self.update(self.DEFAULT_SHOW_ORIGINAL_TITLE[0], self.DEFAULT_SHOW_ORIGINAL_TITLE[1], show)

    def set_media_path(self, path):
        self.update(self.DEFAULT_MEDIA_PATH[0], self.DEFAULT_MEDIA_PATH[1], path)

    def set_media_player_video(self, player):
        self.update(self.DEFAULT_MEDIA_PLAYER_VIDEO[0], self.DEFAULT_MEDIA_PLAYER_VIDEO[1], player)

    def set_media_player_video_param(self, param):
        self.update(self.DEFAULT_MEDIA_PLAYER_VIDEO_PARAM[0], self.DEFAULT_MEDIA_PLAYER_VIDEO_PARAM[1], param)

    def set_media_player_video_ext(self, param):
        self.update(self.DEFAULT_MEDIA_PLAYER_VIDEO_EXT[0], self.DEFAULT_MEDIA_PLAYER_VIDEO_EXT[1], param)

    def set_media_player_audio(self, player):
        self.update(self.DEFAULT_MEDIA_PLAYER_AUDIO[0], self.DEFAULT_MEDIA_PLAYER_AUDIO[1], player)

    def set_media_player_audio_param(self, param):
        self.update(self.DEFAULT_MEDIA_PLAYER_AUDIO_PARAM[0], self.DEFAULT_MEDIA_PLAYER_AUDIO_PARAM[1], param)

    def set_media_player_audio_ext(self, param):
        self.update(self.DEFAULT_MEDIA_PLAYER_AUDIO_EXT[0], self.DEFAULT_MEDIA_PLAYER_AUDIO_EXT[1], param)

config_ini = {}

def get_config_ini():
    return ConfigIni.get_instance()

def re_read_config_ini():
    global config_ini
    global dic
    
    ci = get_config_ini()
    
    # Read config.ini    
    config_ini['language'] = ci.get_language()
    config_ini['show_original_title'] = ci.get_show_original_title()
    config_ini['media_path'] = ci.get_media_path()
    config_ini['media_player_video'] = ci.get_media_player_video()
    config_ini['media_player_video_param'] = ci.get_media_player_video_param()
    config_ini['media_player_video_ext'] = ci.get_media_player_video_ext()
    config_ini['media_player_audio'] = ci.get_media_player_audio()
    config_ini['media_player_audio_param'] = ci.get_media_player_audio_param()
    config_ini['media_player_audio_ext'] = ci.get_media_player_audio_ext()

    # Get the dictionary
    dic = Dict.get_instance( config_ini['language'] )
    
re_read_config_ini()

# --------------------------------------------------------
# --------------------------------------------------------
#
# Gives back the translation of the word
#
# word      word which should be translated
#
# --------------------------------------------------------
# --------------------------------------------------------
def _(word):
    return dic._(word)
