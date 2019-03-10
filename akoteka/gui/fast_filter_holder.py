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
from akoteka.accessories import filter_key
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
        self.filter_dd_genre = FilterDropDownSimple(_('title_genre') + ": ")
        self.filter_dd_theme = FilterDropDownSimple(_('title_theme') + ": ")
        
        holder_dropdown_gt = FilterDropDownHolder()
        
        holder_dropdown_gt.add_dropdown(self.filter_dd_genre)
        holder_dropdown_gt.add_dropdown(self.filter_dd_theme)
        
        holder_layout.addWidget(holder_dropdown_gt) 
 
        # ----------
        #
        # Checkboxes
        #
        # ----------
        self.filter_cb_favorite = FilterCheckBox(_('title_favorite') + ": ")
        self.filter_cb_best = FilterCheckBox(_('title_best') + ": ")
        self.filter_cb_new = FilterCheckBox(_('title_new') + ": ")
                
        holder_checkbox = FilterCheckBoxHolder()
        
        holder_checkbox.add_checkbox(self.filter_cb_favorite)
        holder_checkbox.add_checkbox(self.filter_cb_best)
        holder_checkbox.add_checkbox(self.filter_cb_new)        
                
        # Listener
        self.filter_cb_favorite.stateChanged.connect(self.state_changed)
        self.filter_cb_best.stateChanged.connect(self.state_changed)
        self.filter_cb_new.stateChanged.connect(self.state_changed)
                        
        holder_layout.addWidget(holder_checkbox)
 
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
        self.filter_dd_genre.state_changed.connect(self.state_changed)
        self.filter_dd_theme.state_changed.connect(self.state_changed)
        self.filter_dd_director.state_changed.connect(self.state_changed)
        self.filter_dd_actor.state_changed.connect(self.state_changed)

    def refresh_label(self):
        self.filter_dd_title.refresh_label(_('title_title'))
        self.filter_dd_genre.refresh_label(_('title_genre'))
        self.filter_dd_theme.refresh_label(_('title_theme'))
        self.filter_dd_director.refresh_label(_('title_director'))
        self.filter_dd_actor.refresh_label(_('title_actor'))
        self.filter_cb_favorite.refresh_label(_('title_favorite'))
        self.filter_cb_new.refresh_label(_('title_new'))
        self.filter_cb_best.refresh_label(_('title_best'))

    def clear_title(self):
        self.filter_dd_title.clear_elements()
        
    def add_title(self, value):
        self.filter_dd_title.add_element(value, value)

    def select_title_by_text(self, text):
        self.filter_dd_title.select_element_by_text(text)
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
    def get_filter_selection(self):
        filter_selection = {
            "title":    ["title", self.filter_dd_title.get_selected_value(), None, "a"],
            "genre":    ["genre", self.filter_dd_genre.get_selected_value(), [self.filter_dd_genre.get_selected_id()], "a"],
            "theme":    ["theme", self.filter_dd_theme.get_selected_value(), [self.filter_dd_theme.get_selected_id()], "a"],
            "director": ["director", self.filter_dd_director.get_selected_value(), None, "a"],
            "actor":    ["actor", self.filter_dd_actor.get_selected_value(), None, "a"],
            "best":     ["best", self.filter_cb_best.is_checked(), None, "c"],
            "new":      ["new", self.filter_cb_new.is_checked(), None, "c"],
            "favorite": ["favorite", self.filter_cb_favorite.is_checked(),None, "c"],
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
        self.clear_genre()
        self.clear_theme()
        self.clear_title()
        self.filter_cb_favorite.setChecked(False)
        self.filter_cb_new.setChecked(False)
        self.filter_cb_best.setChecked(False)


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

        # TODO does not work to set the properties of the dropdown list. find out and fix
        style =             '''
            QComboBox { max-width: 200px; min-width: 200px; min-height: 15px; max-height: 15px;}
            QComboBox QAbstractItemView::item { min-width:100px; max-width:100px; min-height: 150px;}
            QListView::item:selected { color: red; background-color: lightgray; min-width: 1000px;}"
            '''            

        style_down_arrow = '''
            QComboBox::down-arrow { 
                image: url( ''' + resource_filename(__name__,os.path.join("img", "back-button.jpg")) + ''');
                
            }
        '''
        style_box = '''
            QComboBox { 
                max-width: 200px; min-width: 200px; border: 1px solid gray; border-radius: 5px;
            }
        '''
#       max-width: 200px; min-width: 200px; min-height: 1em; max-height: 1em; border: 1px solid gray; border-radius: 5px;
        
        style_drop_down ='''
            QComboBox QAbstractItemView::item { 
                color: red;
                max-height: 15px;
            }
        '''            
      
        self.dropdown.setStyleSheet(style_box + style_drop_down)
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
# CheckBox
#
# ==========
class FilterCheckBox(QCheckBox):
    def __init__(self, label):
        super().__init__(label)

        self.setLayoutDirection( Qt.RightToLeft )
        style_checkbox = '''
            QCheckBox { 
                min-height: 15px; max-height: 15px; border: 0px solid gray;
            }
        '''
        self.setStyleSheet( style_checkbox )
#        self.setFocusPolicy(Qt.NoFocus)

    def is_checked(self):
        return 'y' if self.isChecked() else None        
 
    def refresh_label(self, new_label):
        self.setText(new_label)


# ================
#
# Checkbox HOLDER
#
# ================
class FilterCheckBoxHolder(QWidget):
    
    def __init__(self):
        super().__init__()

        self.self_layout = QVBoxLayout(self)
        self.setLayout( self.self_layout )
        self.self_layout.setContentsMargins(0, 0, 0, 0)
        self.self_layout.setSpacing(1)

        #self.setStyleSheet( 'background: green')
        
    def add_checkbox(self, filter_checkbox):
        self.self_layout.addWidget(filter_checkbox)
        




