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
    
    filter_clicked = pyqtSignal()
    clear_clicked = pyqtSignal()
    
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

        combobox_short_style_box = '''
            QComboBox { 
                min-width: 40px; border: 1px solid gray; border-radius: 5px;
            }
        '''
        combobox_long_style_box = '''
            QComboBox { 
                min-width: 60px; border: 1px solid gray; border-radius: 5px;
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
        # Title
        #
        # ----------
        self.title_label = QLabel(_('title_title') + ": ")
        self.title_filter = AQFilter(holder)
        self.title_filter.setStyleSheet(filter_style_box)
        holder_layout.addWidget(self.title_label, 0, 0, 1, 1)
        holder_layout.addWidget(self.title_filter, 0, 1, 1, 1)

        # ----------
        #
        # Director
        #
        # ----------
        self.director_label = QLabel(_('title_director') + ": ")
        self.director_filter = AQFilter(holder)
        self.director_filter.setStyleSheet(filter_style_box)
        #self.director_filter.setMinCharsToShowList(0)
        holder_layout.addWidget(self.director_label, 1, 0, 1, 1)
        holder_layout.addWidget(self.director_filter, 1, 1, 1, 1)
        
        # ----------
        #
        # Actors
        #
        # ----------
        self.actor_label = QLabel(_('title_actor') + ": ")
        self.actor_filter = AQFilter(holder)
        self.actor_filter.setStyleSheet(filter_style_box)
        holder_layout.addWidget(self.actor_label, 2, 0, 1, 1)
        holder_layout.addWidget(self.actor_filter, 2, 1, 1, 1)

        # ---
     
        # ----------
        #
        # Genre
        #
        # ----------
        self.genre_label = QLabel(_('title_genre') + ": ")
        self.genre_filter = AQFilter(holder)
        self.genre_filter.setStyleSheet(filter_style_box)
        holder_layout.addWidget(self.genre_label, 0, 2, 1, 1)
        holder_layout.addWidget(self.genre_filter, 0, 3, 1, 1)
        
        # ----------
        #
        # Theme
        #
        # ----------
        self.theme_label = QLabel(_('title_theme') + ": ")
        self.theme_filter = AQFilter(holder)
        self.theme_filter.setStyleSheet(filter_style_box)
        holder_layout.addWidget(self.theme_label, 1, 2, 1, 1)
        holder_layout.addWidget(self.theme_filter, 1, 3, 1, 1)

        # ---
        
        # ----------
        #
        # Sound
        #
        # ----------
        self.sound_label = QLabel(_('title_sound') + ": ")
        self.sound_combobox = QComboBox(self)
        self.sound_combobox.setFocusPolicy(Qt.NoFocus)
        self.sound_combobox.setStyleSheet(combobox_long_style_box + dropdown_style_box)
        self.sound_combobox.setSizeAdjustPolicy(QComboBox.AdjustToContents)
  
        holder_layout.addWidget(self.sound_label, 0, 4, 1, 1)
        holder_layout.addWidget(self.sound_combobox, 0, 5, 1, 1)

        # ----------
        #
        # Subtitle
        #
        # ----------
        self.sub_label = QLabel(_('title_sub') + ": ")
        self.sub_combobox = QComboBox(self)
        self.sub_combobox.setFocusPolicy(Qt.NoFocus)
        self.sub_combobox.setStyleSheet(combobox_long_style_box + dropdown_style_box)
        self.sub_combobox.setSizeAdjustPolicy(QComboBox.AdjustToContents)
  
        holder_layout.addWidget(self.sub_label, 1, 4, 1, 1)
        holder_layout.addWidget(self.sub_combobox, 1, 5, 1, 1)
  
        # ----------
        #
        # Country
        #
        # ----------
        self.country_label = QLabel(_('title_country') + ": ")
        self.country_combobox = QComboBox(self)
        self.country_combobox.setFocusPolicy(Qt.NoFocus)
        self.country_combobox.setStyleSheet(combobox_long_style_box + dropdown_style_box)        
        self.country_combobox.setSizeAdjustPolicy(QComboBox.AdjustToContents)
  
        holder_layout.addWidget(self.country_label, 2, 4, 1, 1)
        holder_layout.addWidget(self.country_combobox, 2, 5, 1, 1)

        # ---
        
        # ----------
        #
        # Year
        #
        # ----------
        self.year_from_label = QLabel(_('title_year') + ": ")
        year_to_label = QLabel('-')
        self.year_from_combobox = QComboBox(self)
        self.year_from_combobox.setFocusPolicy(Qt.NoFocus)
        self.year_from_combobox.setStyleSheet(combobox_short_style_box + dropdown_style_box)
        self.year_from_combobox.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        #self.year_from_combobox.addItem("        ")

        self.year_to_combobox = QComboBox()
        self.year_to_combobox.setFocusPolicy(Qt.NoFocus)
        self.year_to_combobox.setStyleSheet(combobox_short_style_box + dropdown_style_box)
        self.year_to_combobox.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        #self.year_to_combobox.addItem("        ")
  
        holder_layout.addWidget(self.year_from_label, 0, 6, 1, 1)
        holder_layout.addWidget(self.year_from_combobox, 0, 7, 1, 1)
        holder_layout.addWidget(year_to_label, 0, 8, 1, 1)
        holder_layout.addWidget(self.year_to_combobox, 0, 9, 1, 1)

        # ----------
        #
        # Length
        #
        # ----------
        self.length_from_label = QLabel(_('title_length') + ": ")
        length_to_label = QLabel('-')
        self.length_from_combobox = QComboBox()
        self.length_from_combobox.setFocusPolicy(Qt.NoFocus)
        self.length_from_combobox.setStyleSheet(combobox_short_style_box + dropdown_style_box)
        self.length_from_combobox.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        #self.length_from_combobox.addItem("        ")

        self.length_to_combobox = QComboBox()
        self.length_to_combobox.setFocusPolicy(Qt.NoFocus)
        self.length_to_combobox.setStyleSheet(combobox_short_style_box + dropdown_style_box)        
        self.length_to_combobox.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        #self.length_to_combobox.addItem("        ")
  
        holder_layout.addWidget(self.length_from_label, 1, 6, 1, 1)
        holder_layout.addWidget(self.length_from_combobox, 1, 7, 1, 1)
        holder_layout.addWidget(length_to_label, 1, 8, 1, 1)
        holder_layout.addWidget(self.length_to_combobox, 1, 9, 1, 1)

        # ------------------
        #
        # Vertical Separator
        #
        # ------------------
        holder_layout.setColumnStretch(10, 1)
        holder_layout.addWidget(QVLine(), 0, 11, 3, 2)
        holder_layout.setColumnStretch(12, 1)

        # -------------
        #
        # Clear button
        #
        # -------------
        self.clear_button = QPushButton(_('button_clear'))
        holder_layout.addWidget(self.clear_button, 0, 13, 1, 1)
        self.clear_button.clicked.connect(self.clear_button_clicked)
        
        # -------------
        #
        # Search button
        #
        # -------------
        self.filter_button = QPushButton(_('button_filter'))
        holder_layout.addWidget(self.filter_button, 2, 13, 1, 1)
        self.filter_button.clicked.connect(self.filter_button_clicked)

        # ----------
        #
        # Stretch
        #
        # ----------
        holder_layout.setColumnStretch(11, 1)

    def refresh_label(self):
       self.title_label.setText(_('title_title') + ": ")
       self.director_label.setText(_('title_director') + ": ")
       self.actor_label.setText(_('title_actor') + ": ")
       self.genre_label.setText(_('title_genre') + ": ")
       self.theme_label.setText(_('title_theme') + ": ")
       self.sound_label.setText(_('title_sound') + ": ")
       self.sub_label.setText(_('title_sub') + ": ")
       self.country_label.setText(_('title_country') + ": ")
       self.year_from_label.setText(_('title_year') + ": ")
       self.length_from_label.setText(_('title_length') + ": ")
       
    def clear_title(self):
        self.title_filter.clear()

    def clear_director(self):
        self.director_filter.clear()

    def clear_actor(self):
        self.actor_filter.clear()

    def clear_genre(self):
        self.genre_filter.clear()

    def clear_theme(self):
        self.theme_filter.clear()

    def clear_sound(self):
        self.sound_combobox.clear()
        self.sound_combobox.addItem("")
        
    def clear_sub(self):
        self.sub_combobox.clear()
        self.sub_combobox.addItem("")
        
    def clear_country(self):
        self.country_combobox.clear()
        self.country_combobox.addItem("")

    def clear_year(self):
        self.year_from_combobox.clear()
        self.year_to_combobox.clear()
        self.year_from_combobox.addItem("")
        self.year_to_combobox.addItem("")

    def clear_length(self):
        self.length_from_combobox.clear()
        self.length_to_combobox.clear()
        self.length_from_combobox.addItem("")
        self.length_to_combobox.addItem("")

    def clear_fields(self):
        self.clear_title()
        self.clear_director()
        self.clear_actor()
        self.clear_genre()
        self.clear_theme()
        self.clear_sound()
        self.clear_sub()
        self.clear_country()
        self.clear_year()
        self.clear_length()

    # ---
    
    def set_title(self, value):
        self.title_filter.setValue(value)

    def set_genre(self, value):
        self.genre_filter.setValue(value)
    
    def set_theme(self, value):
        self.theme_filter.setValue(value)
        
    def set_director(self, value):
        self.director_filter.setValue(value)
        
    def set_actor(self, value):
        self.actor_filter.setValue(value)

    def select_sound(self, id):
        self.sound_combobox.setCurrentIndex( self.sound_combobox.findText(id) )

    def select_sub(self, id):
        self.sub_combobox.setCurrentIndex( self.sub_combobox.findText(id) )

    def select_country(self, id):
        self.country_combobox.setCurrentIndex( self.country_combobox.findText(id) )

    def select_year_from(self, value):
        self.year_from_combobox.setCurrentIndex( self.year_from_combobox.findText(value) )

    def select_year_to(self, value):
        self.year_to_combobox.setCurrentIndex( self.year_to_combobox.findText(value) )

    def select_length_from(self, value):
        self.length_from_combobox.setCurrentIndex( self.length_from_combobox.findText(value) )

    def select_length_to(self, value):
        self.length_to_combobox.setCurrentIndex( self.length_to_combobox.findText(value) )
    
    # ---
    
    def add_title(self, value):
        self.title_filter.addItemToList(value, value)
    
    def add_director(self, director):
        self.director_filter.addItemToList(director, director)

    def add_actor(self, actor):
        self.actor_filter.addItemToList(actor, actor)

    def add_genre(self, genre, index):
        self.genre_filter.addItemToList(genre, index)
    
    def add_theme(self, theme, index):
        self.theme_filter.addItemToList(theme, index)
    
    def add_sound(self, value, id):
        self.sound_combobox.addItem(value, id)
    
    def add_sub(self, value, id):
        self.sub_combobox.addItem(value, id)
 
    def add_country(self, value, id):
        self.country_combobox.addItem(value, id)
        
    def add_length(self, value):
        self.length_from_combobox.addItem(value, value)
        self.length_to_combobox.addItem(value, value)

    def add_year(self, value):
        self.year_from_combobox.addItem(value, value)
        self.year_to_combobox.addItem(value, value)
        
    # ---
    
    def get_sound_selected_index(self):
        return self.sound_combobox.itemData( self.sound_combobox.currentIndex() )

    def get_sound_selected_value(self):
        return self.sound_combobox.itemText( self.sound_combobox.currentIndex() )

    def get_sub_selected_index(self):
        return self.sub_combobox.itemData( self.sub_combobox.currentIndex() )

    def get_sub_selected_value(self):
        return self.sub_combobox.itemText( self.sub_combobox.currentIndex() )

    def get_country_selected_index(self):
        return self.country_combobox.itemData( self.country_combobox.currentIndex() )

    def get_country_selected_value(self):
        return self.country_combobox.itemText( self.country_combobox.currentIndex() )

    def get_length_from_selected_value(self):
        return self.length_from_combobox.currentText()

    def get_length_to_selected_value(self):
        return self.length_to_combobox.currentText()

    def get_year_from_selected_value(self):
        return self.year_from_combobox.currentText()

    def get_year_to_selected_value(self):
        return self.year_to_combobox.currentText()

    # ---
    
    def filter_button_clicked(self):
        self.filter_clicked.emit()        

    def clear_button_clicked(self):
        self.clear_clicked.emit()        

    def get_filter_selection(self):
        
        # -----------------------------------------------------------------
        #
        # 1st value:    the typed value
        # 2nd value:    
        #               if not from DICT:   None
        #               if from DICT:
        #                               if found: [found, dict, elements]
        #                               if not found: []
        #
        # -----------------------------------------------------------------
        filter_selection = {
            "title":    ["title", self.title_filter.getValue(), None, "a"],
            "genre":    ["genre", self.genre_filter.getValue(), self.genre_filter.getIndexes(), "a"],
            "theme":    ["theme", self.theme_filter.getValue(), self.theme_filter.getIndexes(), "a"],
            "director": ["director", self.director_filter.getValue(), None, "a"],
            "actor":    ["actor", self.actor_filter.getValue(), None, "a"],
            "sound":    ["sound", self.get_sound_selected_value(), [self.get_sound_selected_index()], "a"],
            "sub":      ["sub", self.get_sub_selected_value(), [self.get_sub_selected_index()], "a"],
            "country":  ["country", self.get_country_selected_value(), [self.get_country_selected_index()], "a"],
            "length-from":  ["length", self.get_length_from_selected_value(), None, "gte"],
            "length-to":    ["length", self.get_length_to_selected_value(), None, "lte"],
            "year-from":    ["year", self.get_year_from_selected_value(), None, "gte"],
            "year-to":  ["year", self.get_year_to_selected_value(), None, "lte"],
        }
        return filter_selection

    
    

        




