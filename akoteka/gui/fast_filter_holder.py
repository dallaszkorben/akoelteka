import sys
import os
import importlib
#from threading import Thread
from pkg_resources import resource_string, resource_filename
from functools import cmp_to_key
import locale

from cardholder.cardholder import CardHolder
from cardholder.cardholder import Card
from cardholder.cardholder import CollectCardsThread

from akoteka.gui.pyqt_import import *
from akoteka.gui.card_panel import CardPanel
from akoteka.gui.configuration_dialog import ConfigurationDialog
from akoteka.gui.control_buttons_holder import ControlButtonsHolder

from akoteka.accessories import collect_cards
from akoteka.accessories import clearLayout
from akoteka.accessories import FlowLayout

from akoteka.constants import *
from akoteka.setup.setup import getSetupIni

from akoteka.handle_property import _
from akoteka.handle_property import re_read_config_ini
from akoteka.handle_property import config_ini
from akoteka.handle_property import get_config_ini


# ==================
#
# Fast Filter HOLDER
#
# ==================
class FastFilterHolder(QWidget):
    
    changed = pyqtSignal()
    clear_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        self_layout = QVBoxLayout(self)
        self.setLayout( self_layout )
        self_layout.setContentsMargins(0, 0, 0, 0)
        self_layout.setSpacing(0)    

        holder = QWidget(self)
        holder_layout = QHBoxLayout(holder)
        holder.setLayout( holder_layout )
        holder_layout.setContentsMargins(0, 0, 0, 0)
        holder_layout.setSpacing(8)    

        self_layout.addWidget(QHLine())
        self_layout.addWidget(holder)        

        # ----------
        #
        # Dropdowns 
        #
        # ----------

        #
        # Dropdown - title
        #
#        self.filter_dd_title = FilterDropDownSimple(_('title_title'))
#        holder_dropdown_gt = FilterDropDownHolder()
#      
#        holder_dropdown_gt.add_dropdown(self.filter_dd_title)
#        
#        holder_layout.addWidget(holder_dropdown_gt)        

        # -------------------------------
        #
        # Dropdown - title+director+actor
        #
        # -------------------------------
        self.filter_dd_title = FilterDropDownSimple(_('title_title') + ": ")
        self.filter_dd_director = FilterDropDownSimple(_('title_director') + ": ")
        self.filter_dd_actor = FilterDropDownSimple(_('title_actor') + ": ")
        
        holder_dropdown_da = FilterDropDownHolder()
        
        holder_dropdown_da.add_dropdown(self.filter_dd_title)
        holder_dropdown_da.add_dropdown(self.filter_dd_director)
        holder_dropdown_da.add_dropdown(self.filter_dd_actor)
        
        holder_layout.addWidget(holder_dropdown_da)

        # ----------------------
        #
        # Dropdown - genre+theme
        #
        # ----------------------
        self.filter_dd_category = FilterDropDownSimple(_('title_category') + ": ")
        self.filter_dd_genre = FilterDropDownSimple(_('title_genre') + ": ")
        self.filter_dd_theme = FilterDropDownSimple(_('title_theme') + ": ")
        
        holder_dropdown_gt = FilterDropDownHolder()

        holder_dropdown_gt.add_dropdown(self.filter_dd_category)        
        holder_dropdown_gt.add_dropdown(self.filter_dd_genre)
        holder_dropdown_gt.add_dropdown(self.filter_dd_theme)
        
        holder_layout.addWidget(holder_dropdown_gt) 
 
        # ----------
        #
        # Ratings
        #
        # ----------
        self.filter_section_rating = RatingSection(_('title_favorite') + ": ", _('title_new') + ": ", _('title_rate') + ": ")
        self.filter_section_rating.favorite_cb.stateChanged.connect(self.state_changed)
        self.filter_section_rating.new_cb.stateChanged.connect(self.state_changed)
        self.filter_section_rating.rate_cb.currentIndexChanged.connect(self.state_changed)
        
        
        
#        self.filter_cb_favorite = FilterCheckBox(_('title_favorite') + ": ")
##        self.filter_cb_best = FilterCheckBox(_('title_best') + ": ")
#        self.filter_cb_new = FilterCheckBox(_('title_new') + ": ")
#        self.filter_dd_rate = FilterDropDownSimple(_('title_rate') + ": ")
#                        
#        holder_checkbox = FilterCheckBoxHolder()
#        
#        holder_checkbox.add_checkbox(self.filter_cb_favorite)
##        holder_checkbox.add_checkbox(self.filter_cb_best)
#        holder_checkbox.add_checkbox(self.filter_cb_new)
#        holder_checkbox.add_checkbox(self.filter_dd_rate)
#



                
#        # Listener
#        self.filter_cb_favorite.stateChanged.connect(self.state_changed)
#        self.filter_cb_new.stateChanged.connect(self.state_changed)
#                        
        holder_layout.addWidget(self.filter_section_rating)
 
        # ----------
        #
        # Stretch
        #
        # ----------
        holder_layout.addStretch(1)
        holder_layout.addWidget(QVLine()) 
        holder_layout.addStretch(1)
        
        # ------------
        #
        # Clear button
        #
        # ------------
        self.clear_button = QPushButton(_('button_clear'))
        holder_layout.addWidget(self.clear_button)
        self.clear_button.clicked.connect(self.clear_button_clicked)

        # Listeners
        self.filter_dd_title.state_changed.connect(self.state_changed)
        self.filter_dd_category.state_changed.connect(self.state_changed)
        self.filter_dd_genre.state_changed.connect(self.state_changed)
        self.filter_dd_theme.state_changed.connect(self.state_changed)
        self.filter_dd_director.state_changed.connect(self.state_changed)
        self.filter_dd_actor.state_changed.connect(self.state_changed)

    def refresh_label(self):
        self.filter_dd_title.refresh_label(_('title_title'))
        self.filter_dd_category.refresh_label(_('title_category'))
        self.filter_dd_genre.refresh_label(_('title_genre'))
        self.filter_dd_theme.refresh_label(_('title_theme'))
        self.filter_dd_director.refresh_label(_('title_director'))
        self.filter_dd_actor.refresh_label(_('title_actor'))
        self.filter_section_rating.refresh_favorite_label(_('title_favorite'))
        self.filter_section_rating.refresh_new_label(_('title_new'))
        self.filter_section_rating.refresh_rate_label(_('title_rate'))

    def clear_title(self):
        self.filter_dd_title.clear_elements()
        
    def add_title(self, value):
        self.filter_dd_title.add_element(value, value)

    def select_title_by_text(self, text):
        self.filter_dd_title.select_element_by_text(text)
    
    # ---
    def clear_category(self):
        self.filter_dd_category.clear_elements()
        
    def add_category(self, value, id):
        self.filter_dd_category.add_element(value, id)
        
    def select_category_by_id(self, id):
        self.filter_dd_category.select_element_by_id(id)
        
    def select_category_by_text(self, text):
        self.filter_dd_category.select_element_by_text(text)    
            
    # ---    
    def clear_genre(self):
        self.filter_dd_genre.clear_elements()
        
    def add_genre(self, value, id):
        self.filter_dd_genre.add_element(value, id)
        
    def select_genre_by_id(self, id):
        self.filter_dd_genre.select_element_by_id(id)
        
    def select_genre_by_text(self, text):
        self.filter_dd_genre.select_element_by_text(text)        
    # ---
    def clear_theme(self):
        self.filter_dd_theme.clear_elements()

    def add_theme(self, value, id):
        self.filter_dd_theme.add_element(value, id)
        
    def select_theme_by_id(self, id):
        self.filter_dd_theme.select_element_by_id(id)        

    def select_theme_by_text(self, text):
        self.filter_dd_theme.select_element_by_text(text)        

    # ---
    def clear_director(self):
        self.filter_dd_director.clear_elements()
    
    def add_director(self, director):
        self.filter_dd_director.add_element(director, director)
    
    def select_director_by_text(self, text):
        self.filter_dd_director.select_element_by_text(text)
    # ---
    def clear_actor(self):
        self.filter_dd_actor.clear_elements()

    def add_actor(self, actor):
        self.filter_dd_actor.add_element(actor, actor)
        
    def select_actor_by_text(self, text):
        self.filter_dd_actor.select_element_by_text(text)

    # ---
    def add_rate_element(self, value, id):
        self.filter_section_rating.add_rate_element(value, id)
        
    def select_rate_element_by_text(self, text):
        self.filter_section_rating.select_rate_element_by_text(text)
        
    # ---
    def clear_rate(self):
        self.filter_section_rating.clear_rate()
    
    def clear_favorite(self):
        self.filter_section_rating.clear_favorite()
        
    def clear_new(self):
        self.filter_section_rating.clear_new()
        
        
    # ---
    def get_filter_selection(self):
        filter_selection = {
            "title":    ["title", self.filter_dd_title.get_selected_value(), None, "a"],
            "category": ["category", self.filter_dd_category.get_selected_value(), [self.filter_dd_category.get_selected_id()], "v"],
            "genre":    ["genre", self.filter_dd_genre.get_selected_value(), [self.filter_dd_genre.get_selected_id()], "a"],
            "theme":    ["theme", self.filter_dd_theme.get_selected_value(), [self.filter_dd_theme.get_selected_id()], "a"],
            "director": ["director", self.filter_dd_director.get_selected_value(), None, "a"],
            "actor":    ["actor", self.filter_dd_actor.get_selected_value(), None, "a"],
#            "best":     ["best", self.filter_cb_best.is_checked(), None, "c"],
            "new":      ["new", self.filter_section_rating.is_new_checked(), None, "c"],
            "favorite": ["favorite", self.filter_section_rating.is_favorite_checked(),None, "c"],
            "rate":     ["rate", self.filter_section_rating.get_rate_selected_value(),None, "a"],
        }
        return filter_selection
    
    def clear_button_clicked(self):
        self.clear_clicked.emit()
    
    def state_changed(self):
        self.changed.emit()

    def closeEvent(self, event):
        print('close filter holder')
        
    def clear_fields(self):
        self.clear_actor()
        self.clear_director()
        self.clear_category()
        self.clear_genre()
        self.clear_theme()
        self.clear_title()
        self.clear_favorite()
        self.clear_new()
        self.clear_rate()
#        self.filter_cb_best.setChecked(False)


# ================
#
# Dropdown HOLDER
#
# ================
class FilterDropDownHolder(QWidget):
    
    def __init__(self):
        super().__init__()

        self.self_layout = QVBoxLayout(self)
        self.setLayout( self.self_layout )
        self.self_layout.setContentsMargins(0, 0, 0, 0)
        self.self_layout.setSpacing(1)
        self.self_layout.setAlignment(Qt.AlignTop)

#        self.setStyleSheet( 'background: green')

    def add_dropdown(self, filter_dropdown):
        self.self_layout.addWidget(filter_dropdown)

# =============================
#
# Filter Drop-Down Simple
#
# =============================
#
class FilterDropDownSimple(QWidget):
    
    state_changed = pyqtSignal()
    
    def __init__(self, label):
        super().__init__()

        self_layout = QHBoxLayout(self)
        self_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout( self_layout )
#        self.setStyleSheet( 'background: green')
        
        self.label_widget = QLabel(label)
        self_layout.addWidget( self.label_widget )

        self.dropdown = QComboBox(self)
        self.dropdown.setFocusPolicy(Qt.NoFocus)
        #self.dropdown.setEditable(True)
        
        self.dropdown.currentIndexChanged.connect(self.current_index_changed)

        style_box = '''
            QComboBox { 
                max-width: 200px; min-width: 200px; border: 1px solid gray; border-radius: 5px;
            }
        '''
        style_drop_down ='''
            QComboBox QAbstractItemView::item { 
                color: red;
                max-height: 15px;
            }
        '''            
      
        self.dropdown.setStyleSheet(style_box)
        self.dropdown.addItem("")

        self_layout.addWidget( self.dropdown )
    
    def clear_elements(self):
        self.dropdown.clear()

    def add_element(self, value, id):
        self.dropdown.addItem(value, id)

    # -------------------------------------
    # get the index of the selected element
    # -------------------------------------
    def get_selected_id(self):
        return self.dropdown.itemData( self.dropdown.currentIndex() )

    # -------------------------------------
    # get the value of the selected element
    # -------------------------------------
    def get_selected_value(self):
        return self.dropdown.itemText( self.dropdown.currentIndex() )
    
    def select_element_by_id(self, id):
        self.dropdown.setCurrentIndex( self.dropdown.findData(id) )

    def select_element_by_text(self, text):
        self.dropdown.setCurrentIndex( self.dropdown.findText(text) )

    def current_index_changed(self):
        self.state_changed.emit()
        
    def refresh_label(self, new_label):
        self.label_widget.setText(new_label)










# ==========
#
# Rating
#
# ==========
class RatingSection(QWidget):
    def __init__(self, favorite_title, new_title, rate_title):
        super().__init__()

        style_checkbox = 'QCheckBox {min-height: 15px; max-height: 15px; border: 0px solid gray;}'
        style_combobox = 'QComboBox {max-width: 50px; min-width: 50px; border: 1px solid gray; border-radius: 5px;}'

        self.self_layout = QGridLayout(self)
        self.setLayout( self.self_layout )
        self.self_layout.setContentsMargins(0, 0, 0, 0)
        self.self_layout.setSpacing(0)    

        # favorite
        self.favorite_label = QLabel(favorite_title)
        self.self_layout.addWidget( self.favorite_label, 0, 0 )
        self.favorite_cb = QCheckBox(self)
        self.favorite_cb.setFocusPolicy(Qt.NoFocus)
        self.favorite_cb.setLayoutDirection( Qt.RightToLeft )
        self.favorite_cb.setStyleSheet( style_checkbox )
        self.self_layout.addWidget( self.favorite_cb, 0, 1 )        
        
        # new
        self.new_label = QLabel(new_title)
        self.self_layout.addWidget( self.new_label, 1, 0 )
        self.new_cb = QCheckBox(self)
        self.new_cb.setFocusPolicy(Qt.NoFocus)
        self.new_cb.setLayoutDirection( Qt.RightToLeft )
        self.new_cb.setStyleSheet( style_checkbox )
        self.self_layout.addWidget( self.new_cb, 1, 1 )
        
        # rate
        self.rate_label = QLabel(rate_title)
        self.self_layout.addWidget( self.rate_label, 2, 0 )
        self.rate_cb = QComboBox(self)
        self.rate_cb.setFocusPolicy(Qt.NoFocus)
#        self.rate_cb.setLayoutDirection( Qt.RightToLeft )
        self.rate_cb.setStyleSheet( style_combobox )
#        self.rate_cb.currentIndexChanged.connect(self.rate_index_changed)
        self.self_layout.addWidget( self.rate_cb, 2, 1 )
    
    # --- favorite ---    
    def is_favorite_checked(self):
        return 'y' if self.favorite_cb.isChecked() else None        
 
    def refresh_favorite_label(self, new_label):
        self.favorite_label.setText(new_label)

    # --- new ---
    def is_new_checked(self):
        return 'y' if self.new_cb.isChecked() else None        
 
    def refresh_new_label(self, new_label):
        self.new_label.setText(new_label)

    # --- rate ---
    def refresh_rate_label(self, new_label):
        self.rate_label.setText(new_label)
        
    def clear_rate_elements(self):
        self.rate_cb.clear()

    def add_rate_element(self, value, id):
        self.rate_cb.addItem(value, id)

    def get_rate_selected_id(self):
        return self.rate_cb.itemData( self.rate_cb.currentIndex() )

    def get_rate_selected_value(self):
        return self.rate_cb.itemText( self.rate_cb.currentIndex() )
    
    def select_rate_element_by_id(self, id):
        self.rate_cb.setCurrentIndex( self.rate_cb.findData(id) )

    def select_rate_element_by_text(self, text):
        self.rate_cb.setCurrentIndex( self.rate_cb.findText(text) )

    def clear_rate(self):
        self.rate_cb.clear()

    def clear_favorite(self):        
        self.favorite_cb.setChecked(False)        

    def clear_new(self):        
        self.new_cb.setChecked(False)        
   


