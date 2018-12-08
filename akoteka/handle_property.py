import os
import configparser

class Property(object):
    """
    This singleton handles the package's ini file.
    The object is created by calling the get_instance() method.
    If the ini file is not existing then it will be generated with default values

    It is possible to get a string value of a key by calling the get() method
    If the key is not existing then it will be generated with default value
    The get_boolean() method is to get the boolean values.

    update() method is to update a value of a key. If the key is not existing
    then it will be generated with default value
    """
       
    def __init__(self, file, writable=False):
        self.writable = writable
        self.file = file
        #self.file = os.path.join(os.getcwd(), INI_FILE_NAME)
        self.parser = configparser.RawConfigParser()

    def __write_file(self):
        with open(self.file, 'w') as configfile:
            self.parser.write(configfile)

    def get(self, section, key, default_value):

        # if not existing file
        if not os.path.exists(self.file):
            self.parser[section]={key: default_value}
            self.__write_file()
        self.parser.read(self.file)

        try:
            result=self.parser.get(section,key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            if self.writable:
                self.update(section, key, default_value)
                result=self.parser.get(section,key)
            else:
                result = default_value
        return result

    def getBoolean(self, section, key, default_value):
        if not os.path.exists(self.file):
            self.parser[section]={key: default_value}
            self.__write_file()
        self.parser.read(self.file)

        try:
            result=self.parser.getboolean(section,key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            if self.writable:
                self.update(section, key, default_value)
                # It is strange how it works with get/getboolean
                # Sometimes it reads boolean sometimes it reads string
                # I could not find out what is the problem
                #result=self.parser.get(section,key)
            result=default_value

        return result

    def update(self, section, key, value):
        if not os.path.exists(self.file):
            self.parser[section]={key: value}        
        else:
            self.parser.read(self.file)
            try:
                # if no section -> NoSectionError | if no key -> Create it
                self.parser.set(section, key, value)
            except configparser.NoSectionError:
                self.parser[section]={key: value}

        self.__write_file()

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


class ConfigIni( Property ):
    INI_FILE_NAME="config.ini"

    # (section, key, default)
    LANGUAGE = ("general", "language", "hu")
    MEDIA_PATH = ("media", "media-path", ".")
    MEDIA_PLAYER_VIDEO = ("media", "player-video", "mplayer")
    MEDIA_PLAYER_VIDEO_PARAM = ("media", "player-video-param", "-zoom -fs -framedrop")
    
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
        file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ConfigIni.INI_FILE_NAME)
        super().__init__( file )


    def get_language(self):
        return self.get(self.LANGUAGE[0], self.LANGUAGE[1], self.LANGUAGE[2])

    def get_media_path(self):
        return self.get(self.MEDIA_PATH[0], self.MEDIA_PATH[1], self.MEDIA_PATH[2])

    def get_media_player_video(self):
        return self.get(self.MEDIA_PLAYER_VIDEO[0], self.MEDIA_PLAYER_VIDEO[1], self.MEDIA_PLAYER_VIDEO[2])

    def get_media_player_video_param(self):
        return self.get(self.MEDIA_PLAYER_VIDEO_PARAM[0], self.MEDIA_PLAYER_VIDEO_PARAM[1], self.MEDIA_PLAYER_VIDEO_PARAM[2])

    def set_language(self, lang):
        self.update(self.LANGUAGE[0], self.LANGUAGE[1], lang)

    def set_media_path(self, path):
        self.update(self.MEDIA_PATH[0], self.MEDIA_PATH[1], path)

    def set_media_player_video(self, player):
        self.update(self.MEDIA_PLAYER_VIDEO[0], self.MEDIA_PLAYER_VIDEO[1], player)

    def set_media_player_video_param(self, param):
        self.update(self.MEDIA_PLAYER_VIDEO_PARAM[0], self.MEDIA_PLAYER_VIDEO_PARAM[1], param)





