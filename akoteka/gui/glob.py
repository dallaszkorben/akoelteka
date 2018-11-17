from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtWidgets import QDesktopWidget
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QSpacerItem
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QApplication

from PyQt5.QtGui import QFont
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QPalette
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QPainter

from PyQt5 import QtCore

from PyQt5.QtCore import Qt

from akoteka.handle_property import ConfigIni
from akoteka.handle_property import Dict

# Read config.ini
config_ini = ConfigIni.get_instance()
language = config_ini.get_language()
media_path_film = config_ini.get_media_path_film()
media_player_video = config_ini.get_media_player_video()
media_player_video_param = config_ini.get_media_player_video_param()

# Get the dictionary
dic = Dict.get_instance( language )

def _(word):
    return dic._(word)

