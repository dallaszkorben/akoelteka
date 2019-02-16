import sys
import os
import importlib
from threading import Thread
from pkg_resources import resource_string, resource_filename
from functools import cmp_to_key
import locale

from cardholder.cardholder import CardHolder
from cardholder.cardholder import Card
from cardholder.cardholder import CollectCardsThread

from aqfilter.aqfilter import AQFilter

from akoteka.gui.pyqt_import import *
from akoteka.gui.card_panel import CardPanel
from akoteka.gui.configuration_dialog import ConfigurationDialog
from akoteka.gui.control_buttons_holder import ControlButtonsHolder

from akoteka.accessories import collect_cards
from akoteka.accessories import filter_key
from akoteka.accessories import clearLayout
from akoteka.accessories import FlowLayout

from akoteka.constants import *
from akoteka.setup.setup import getSetupIni

from akoteka.handle_property import _
from akoteka.handle_property import re_read_config_ini
from akoteka.handle_property import config_ini
from akoteka.handle_property import get_config_ini


# =======================
#
# Advanced Filter HOLDER
#
# =======================
class AdvancedFilterHolder(QWidget):
    
    changed = pyqtSignal()
    
    def __init__(self, parent):
        super().__init__(parent)

        self_layout = QVBoxLayout(self)
        self.setLayout( self_layout )
        self_layout.setContentsMargins(0, 0, 0, 0)
        self_layout.setSpacing(0)    

        holder = QWidget(self)
        holder_layout = QGridLayout(holder)
        holder.setLayout( holder_layout )
        holder_layout.setContentsMargins(0, 0, 0, 0)
        holder_layout.setSpacing(1)

        self_layout.addWidget(QHLine())
        self_layout.addWidget(holder)
        
        filter_style_box = '''
            AQFilter { 
                max-width: 200px; min-width: 200px; border: 1px solid gray; border-radius: 5px;
            }
        '''

        combobox_style_box = '''
            QComboBox { 
                max-width: 200px; min-width: 200px; border: 1px solid gray; border-radius: 5px;
            }
        '''
        
        dropdown_style_box ='''
            QComboBox QAbstractItemView::item { 
                color: red;
                max-height: 15px;
            }
        '''            

        # ----------
        #
        # Director
        #
        # ----------
        director_label = QLabel(_('title_director'))
        self.director_filter = AQFilter(holder)
        self.director_filter.setStyleSheet(filter_style_box)
        #self.director_filter.setMinCharsToShowList(0)
        holder_layout.addWidget(director_label, 0, 0, 1, 1)
        holder_layout.addWidget(self.director_filter, 0, 1, 1, 1)
        
        # ----------
        #
        # Actors
        #
        # ----------
        actor_label = QLabel(_('title_actor'))
        self.actor_filter = AQFilter(holder)
        self.actor_filter.setStyleSheet(filter_style_box)
        holder_layout.addWidget(actor_label, 1, 0, 1, 1)
        holder_layout.addWidget(self.actor_filter, 1, 1, 1, 1)
     
        # ----------
        #
        # Genre
        #
        # ----------
        genre_label = QLabel(_('title_genre'))
        self.genre_filter = AQFilter(holder)
        self.genre_filter.setStyleSheet(filter_style_box)
        holder_layout.addWidget(genre_label, 2, 0, 1, 1)
        holder_layout.addWidget(self.genre_filter, 2, 1, 1, 1)
        
        # ----------
        #
        # Theme
        #
        # ----------
        theme_label = QLabel(_('title_theme'))
        self.theme_filter = AQFilter(holder)
        self.theme_filter.setStyleSheet(filter_style_box)
        holder_layout.addWidget(theme_label, 3, 0, 1, 1)
        holder_layout.addWidget(self.theme_filter, 3, 1, 1, 1)

        # ----------
        #
        # Sound
        #
        # ----------
        sound_label = QLabel(_('title_sound'))
        self.sound_dropdown = QComboBox(self)
        self.sound_dropdown.setFocusPolicy(Qt.NoFocus)
        self.sound_dropdown.setStyleSheet(combobox_style_box + dropdown_style_box)
  
        holder_layout.addWidget(sound_label, 0, 2, 1, 1)
        holder_layout.addWidget(self.sound_dropdown, 0, 3, 1, 1)

        # ----------
        #
        # Subtitle
        #
        # ----------
        sub_label = QLabel(_('title_sub'))
        self.sub_dropdown = QComboBox(self)
        self.sub_dropdown.setFocusPolicy(Qt.NoFocus)
        self.sub_dropdown.setStyleSheet(combobox_style_box + dropdown_style_box)
  
        holder_layout.addWidget(sub_label, 1, 2, 1, 1)
        holder_layout.addWidget(self.sub_dropdown, 1, 3, 1, 1)
  
        # ----------
        #
        # Country
        #
        # ----------
        country_label = QLabel(_('title_country'))
        self.country_dropdown = QComboBox(self)
        self.country_dropdown.setFocusPolicy(Qt.NoFocus)
        self.country_dropdown.setStyleSheet(combobox_style_box + dropdown_style_box)
  
        holder_layout.addWidget(country_label, 2, 2, 1, 1)
        holder_layout.addWidget(self.country_dropdown, 2, 3, 1, 1)

        # ----------
        #
        # Country
        #
        # ----------
        country_label = QLabel(_('title_country'))
  
        holder_layout.addWidget(country_label, 2, 2, 1, 1)

        # ----------
        #
        # Stretch
        #
        # ----------
        holder_layout.setColumnStretch(4, 1)

    def clear_director(self):
        self.director_filter.clear()

    def clear_actor(self):
        self.actor_filter.clear()

    def clear_genre(self):
        self.genre_filter.clear()

    def clear_theme(self):
        self.theme_filter.clear()

    def clear_sound(self):
        self.sound_dropdown.clear()
        
    def clear_sub(self):
        self.sub_dropdown.clear()
        
    def clear_country(self):
        self.country_dropdown.clear()

    
    def add_director(self, director):
        self.director_filter.addItemToList(director, director)

    def add_actor(self, actor):
        self.actor_filter.addItemToList(actor, actor)

    def add_genre(self, genre, index):
        self.genre_filter.addItemToList(genre, index)
    
    def add_theme(self, theme, index):
        self.theme_filter.addItemToList(theme, index)
    
    def add_sound(self, value, id):
        self.sound_dropdown.addItem(value, id)

    def add_sub(self, value, id):
        self.sub_dropdown.addItem(value, id)
 
    def add_country(self, value, id):
        self.country_dropdown.addItem(value, id)

    
    

        




