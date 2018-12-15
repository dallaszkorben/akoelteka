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
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QStyleFactory
from PyQt5.QtWidgets import QFileDialog


from PyQt5.QtGui import QFont
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QPalette
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QPainter
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QCursor

from PyQt5 import QtCore

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QSize
from PyQt5.QtCore import QAbstractTableModel
from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import QVariant
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal

from akoteka.handle_property import ConfigIni
from akoteka.handle_property import Dict

# Read config.ini
config_ini = ConfigIni.get_instance()
language = config_ini.get_language()
media_path = config_ini.get_media_path()
media_player_video = config_ini.get_media_player_video()
media_player_video_param = config_ini.get_media_player_video_param()



# Get the dictionary
dic = Dict.get_instance( language )

def _(word):
    return dic._(word)

SECTION_RATING = 'rating'
SECTION_GENERAL = 'general'
SECTION_TITLE = 'title'
SECTION_EXTRA = 'extra'

RATING_KEY_FAVORITE = 'favorite'
RATING_KEY_NEW = 'new'
RATING_KEY_BEST = 'best'

FILE_CARD_INI = 'card.ini'

