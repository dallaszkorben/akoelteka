import os
import gettext

#from pkg_resources import resource_string
from iso639 import to_name
from optparse import OptionParser
import configparser

from PyQt5.QtWidgets import QAbstractButton, QSizePolicy, QPushButton
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import QSize

LOCALES_DIR='locales'
PACKAGE_NAME='akoteka'

class Translation(object):
    """
    This singleton handles the translation.
    The object is created by calling the get_instance() method.
    The language is defined in the ini file's [languages] section as "language" key
    The _() method is to get back the translated string.
    If the translation file or the translation in the file is not there then the 
    string in the parameter will we used instead of raiseing error
    Using this Object directly is not necessary. There is a _() method defined out of the class
    which creates the instance and calls the _() method.
    """
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
        self.config_ini=ConfigIni.getInstance()
        localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), LOCALES_DIR)
        self.translate = gettext.translation(PACKAGE_NAME, localedir=localedir, languages=self.__get_language_code(), fallback=True)

    def __get_language_code(self):
	    return [self.config_ini.getLanguage()]

    def _(self, text):
        return self.translate.gettext(text)

def _(text):
    return Translation.get_instance()._(text)

class Enum(object):   
   
    def __init__(self, **named_values):
        self.named_values=named_values
        for k, v in named_values.items():
            exec("self.%s = %s" % (k, v))

    def size(self):
        return len(self.named_values)



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
    __instance = None

    def __new__(cls):
        if cls.__instance == None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @classmethod
    def getInstance(cls, file):
        inst = cls.__new__(cls)
        cls.__init__(cls.__instance, file)     
        return inst
        
    def __init__(self, file):
        self.file=file
        #self.file = os.path.join(os.getcwd(), INI_FILE_NAME)
        self.parser = configparser.RawConfigParser()

    def __write_file(self):
        with open(self.file, 'w') as configfile:
            self.parser.write(configfile)

    def get(self, section, key, default_value):
        if not os.path.exists(self.file):
            self.parser[section]={key: default_value}
            self.__write_file()
        self.parser.read(self.file)

        try:
            result=self.parser.get(section,key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            self.update(section, key, default_value)
            result=self.parser.get(section,key)

        return result

    def getBoolean(self, section, key, default_value):
        if not os.path.exists(self.file):
            self.parser[section]={key: default_value}
            self.__write_file()
        self.parser.read(self.file)

        try:
            result=self.parser.getboolean(section,key)
        except (configparser.NoSectionError, configparser.NoOptionError):
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

    def __str__(self):
        self.parser.read(self.file)
        out=[]
        for s, vs in self.parser.items():
            out += ["[" + s + "]"] + ["  " + k + "=" + v for k, v in vs.items()]
        return "\n".join(out)

class ConfigIni( Property ):
    INI_FILE_NAME="config.ini"

    # (section, key, default)
    LANGUAGE = ("languages", "language", "en")
    BASE_LANGUAGE = ("languages", "base_language", "en")
    LEARNING_LANGUAGE = ("languages", "learning_language", "sv")
    SAY_OUT = ("general", "say_out", True)
    SHOW_NOTE = ("general", "show_note", True)
    SHOW_PATTERN = ("general", "show_pattern", True)

    @classmethod
    def getInstance( cls ):
        file = os.path.join(os.getcwd(), ConfigIni.INI_FILE_NAME)
        return super().getInstance( file )

    def getLanguage(self):
        return self.get(self.LANGUAGE[0], self.LANGUAGE[1], self.LANGUAGE[2])

    def getBaseLanguage(self):
        return self.get(self.BASE_LANGUAGE[0], self.BASE_LANGUAGE[1], self.BASE_LANGUAGE[2])

    def getLearningLanguage(self):
        return self.get(self.LEARNING_LANGUAGE[0], self.LEARNING_LANGUAGE[1], self.LEARNING_LANGUAGE[2])

    def isSayOut(self):
        return self.getBoolean(self.SAY_OUT[0], self.SAY_OUT[1], self.SAY_OUT[2])

    def isShowNote(self):
        return self.getBoolean(self.SHOW_NOTE[0], self.SHOW_NOTE[1], self.SHOW_NOTE[2])

    def isShowPattern(self):
        return self.getBoolean(self.SHOW_PATTERN[0], self.SHOW_PATTERN[1], self.SHOW_PATTERN[2])
        
    def setLanguage(self, lang):
        self.update(self.LANGUAGE[0], self.LANGUAGE[1], lang)

    def setBaseLanguage(self, lang):
        self.update(self.BASE_LANGUAGE[0], self.BASE_LANGUAGE[1], lang)

    def setLearningLanguage(self, lang):
        self.update(self.LEARNING_LANGUAGE[0], self.LEARNING_LANGUAGE[1], lang)
        
    def setSayOut(self, enabled):
        self.update(self.SAY_OUT[0], self.SAY_OUT[1], enabled)

    def setShowNote(self, enabled):
        self.update(self.SHOW_NOTE[0], self.SHOW_NOTE[1], enabled)

    def setShowPattern(self, enabled):
        self.update(self.SHOW_PATTERN[0], self.SHOW_PATTERN[1], enabled)



def xzip(a, b, string_filler=""):
    """
    Returns a list of tuples, where the i-th tuple contains the i-th element 
    from each of the argument sequences or iterables. 
    If the argument sequences are of unequal lengths, then the shorter list
    will be complemented
    """
    #zipped_list= list(zip( 
    #a + [" "*len(i) for i in b][len(a):], 
    #b + [" "*len(i) for i in a][len(b):] ) )
    zipped_list= list(zip( 
    a + ["" for i in b][len(a):], 
    b + ["" for i in a][len(b):] ) )

    if string_filler:
        zipped_list = [ (
            str(i[0]) + (string_filler*len(str(i[1])))[len(str(i[0])):] , 
            str(i[1]) + (string_filler*len(str(i[0])))[len(str(i[1])):] ) 
                for i in zipped_list]
    return zipped_list
#file=os.path.join(os.getcwd(),'config.inii')
#p=Property(file)
#p.update("language4", "newe#from iso3166 import countries


class PicButton(QPushButton):
    WIDTH = 100
    HEIGHT = 30
    
    """
    Button
    """
    def __init__(self, pixmap, pixmap_focus, pixmap_hover, pixmap_pressed, parent=None):
        super().__init__(parent)
        self.pixmap = pixmap
        self.pixmap_focus = pixmap_focus
        self.pixmap_hover = pixmap_hover
        self.pixmap_pressed = pixmap_pressed

        self.pressed.connect(self.update)
        self.released.connect(self.update)
    
        self.setAutoDefault(False)
        self.setDefault(True)        

        #self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        #self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumWidth( PicButton.WIDTH )
        self.setMaximumWidth( PicButton.WIDTH )

        self.setMinimumHeight( PicButton.HEIGHT )
        self.setMaximumHeight( PicButton.HEIGHT )

    def paintEvent(self, event):
        #pix = self.pixmap_hover if self.underMouse() else self.pixmap
        #pix = self.pixmap_hover if self.hasFocus() else self.pixmap
        pix = self.pixmap_hover if self.underMouse() else self.pixmap_focus if self.hasFocus() else self.pixmap
        if self.isDown():
            pix = self.pixmap_pressed


        painter = QPainter(self)
        painter.drawPixmap(event.rect(), pix)

    def enterEvent(self, event):
        self.update()

    def leaveEvent(self, event):
        self.update()

    #def sizeHint(self):        
    #    return QSize(100,38)

def removeControlChars( string ):
    mpa = dict.fromkeys(range(32))
    return string.translate(mpa)