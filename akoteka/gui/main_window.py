import sys
import os
import importlib

from threading import Thread

from pkg_resources import resource_string, resource_filename

from functools import cmp_to_key

import locale

from akoteka.setup.setup import getSetupIni
    
from akoteka.gui.pyqt_import import *

#from akoteka.gui.card_holder_pane import CardHolder
from cardholder.cardholder import CardHolder
from cardholder.cardholder import Card

from akoteka.gui.card_panel import CardPanel

from akoteka.gui.configuration_dialog import ConfigurationDialog

from akoteka.accessories import collect_cards
from akoteka.constants import *

from akoteka.handle_property import _
from akoteka.handle_property import re_read_config_ini
from akoteka.handle_property import config_ini
from akoteka.handle_property import get_config_ini

class GuiAkoTeka(QWidget):
    
    def __init__(self):
        super().__init__()     
        
        self.actual_card_holder = None
        self.card_holder_list = []
        
        # most outer container, just right in the Main Window
        box_layout = QVBoxLayout(self)
        self.setLayout(box_layout)
        # controls the distance between the MainWindow and the added container: scrollContent
        box_layout.setContentsMargins(0, 0, 0, 0)
        box_layout.setSpacing(0)
    
        # control line
        self.control_panel = ControlPanel(self)
        self.control_panel.set_back_button_method(self.restore_previous_holder)
        box_layout.addWidget( self.control_panel)
    
        # scroll_content where you can add your widgets - has scroll
        scroll = QScrollArea(self)
        box_layout.addWidget(scroll)
        scroll.setWidgetResizable(True)
        scroll_content = QWidget(scroll)
        scroll_content.setStyleSheet('background: ' + COLOR_MAIN_BACKGROUND)  

        # layout of the content with margins
        scroll_layout = QVBoxLayout(scroll_content)
        scroll.setWidget(scroll_content)
        # vertical distance between cards - Vertical
        scroll_layout.setSpacing(5)
        # spaces between the added Widget and this top, right, bottom, left side
        scroll_layout.setContentsMargins(15,15,15,15)
        scroll_content.setLayout(scroll_layout)

        # -------------------------------
        # Title
        # -------------------------------
        self.hierarchy_title = HierarchyTitle(scroll_content)
        self.hierarchy_title.set_background_color(QColor(COLOR_CARDHOLDER_BACKGROUND))
        self.hierarchy_title.set_border_radius(RADIUS_CARDHOLDER)

        # -------------------------------
        # Here comes later the CardHolder
        # -------------------------------
        self.card_holder_panel = QWidget(scroll_content)
        
        scroll_layout.addWidget(self.hierarchy_title)
        scroll_layout.addWidget(self.card_holder_panel)
        scroll_layout.addStretch(1)
        
        self.card_holder_panel_layout = QVBoxLayout(self.card_holder_panel)
        self.card_holder_panel_layout.setContentsMargins(0,0,0,0)
        self.card_holder_panel_layout.setSpacing(0)

        self.back_button_listener = None
        card_holder_list = []

        # --- Window ---
        sp=getSetupIni()
        self.setWindowTitle(sp['name'] + '-' + sp['version'])    
        #self.setGeometry(300, 300, 300, 200)
        self.resize(900,600)
        self.center()
        self.show()    

    def center(self):
        """Aligns the window to middle on the screen"""
        fg=self.frameGeometry()
        cp=QDesktopWidget().availableGeometry().center()
        fg.moveCenter(cp)
        self.move(fg.topLeft())

    # --------------------------
    #
    # Start Card Holder
    #
    # --------------------------
    def start_card_holder(self):

        # Create the first Card Holder
        self.go_down_in_hierarchy( [], "" ) 

        # Start to collect the Cards
        paths = [config_ini['media_path']]
        
        self.actual_card_holder.start_card_collection(paths)
        

    # ---------------------------
    #
    # Go deeper in the hierarchy
    #
    # ---------------------------
    def go_down_in_hierarchy( self, card_structure, title ):
        
        # if there is already a CardHolder
        if self.actual_card_holder:        
            
            # hide the old CardHolder it
            self.actual_card_holder.setHidden(True)
            
            # save the old CardHolder it in a list
            self.card_holder_list.append(self.actual_card_holder)
        
        self.actual_card_holder = CardHolder(            
            self, 
            card_structure,
            self.get_new_card,
            self.collect_cards
        )
        
        self.actual_card_holder.title = title
        self.actual_card_holder.set_max_overlapped_cards(4)
        self.actual_card_holder.set_y_coordinate_by_reverse_index_method(self.get_y_coordinate_by_reverse_index)
        self.actual_card_holder.set_x_offset_by_index_method(self.get_x_offset_by_index)
        self.actual_card_holder.set_background_color(QColor(COLOR_CARDHOLDER_BACKGROUND))
        self.actual_card_holder.set_border_radius(RADIUS_CARDHOLDER)
        self.actual_card_holder.set_border_width(15)        
        self.actual_card_holder.setAlignment(Qt.AlignBottom)

        self.hierarchy_title.set_title(self.card_holder_list, self.actual_card_holder)

        # add the new holder
        self.card_holder_panel_layout.addWidget(self.actual_card_holder)
        #self.scroll_layout.addStretch(1)
        
        # TODO get the filtered list !!!!!!!!!!!!!!!!!!!
        self.actual_card_holder.refresh_by_filtered_descriptor_list(card_structure)


    # -------------------------
    #
    # Come up in the hierarchy
    #
    # -------------------------
    def restore_previous_holder(self):
        
        size = len(self.card_holder_list)
        if  size >= 1:

            # get the previous CardHolder
            previous_card_holder = self.card_holder_list[size - 1]
            
            # remove the previous CardHolder from the history list
            self.card_holder_list.remove(previous_card_holder)
            
            # hide the old CardHolder
            self.actual_card_holder.setHidden(True)            
            
            # remove from the layout the old CardHolder
            self.card_holder_panel_layout.removeWidget(self.actual_card_holder)
        
            # the current card holder is the previous
            self.actual_card_holder = previous_card_holder
            
            # show the current card holder
            self.actual_card_holder.setHidden(False)

            self.hierarchy_title.set_title(self.card_holder_list, self.actual_card_holder)
            #self.hierarchy_title.set_title(self.card_holder_list + [[None,self.actual_title]])
            
            # TODO fill up with filtered list
            #self.actual_card_holder.fill_up_card_holder()
            card_structure = self.actual_card_holder.card_descriptor_list
            self.actual_card_holder.refresh_by_filtered_descriptor_list(card_structure)

    # ----------------------------------------------------------
    #
    # Calculates the Y coordinate of a Card using reverse index
    #
    # ----------------------------------------------------------
    def get_y_coordinate_by_reverse_index(self, reverse_index):
        return reverse_index * reverse_index * 8
    
    # -----------------------------------------------
    #
    # Calculates the X coordinate of a Card by index
    #
    # -----------------------------------------------
    def get_x_offset_by_index(self, index):
        return index * 4
       
       
    # TODO remove it
    def collect_cards(self, paths):
        cdl = collect_cards(paths)
        return cdl
    
    # --------------------
    #
    # Generates a new Card
    #
    # --------------------
    def get_new_card(self, card_data, local_index, index):

        card = Card(self.actual_card_holder, card_data, local_index, index)
        
        card.set_background_color(QColor(COLOR_CARD_BACKGROUND))
        card.set_border_normal_color(QColor(COLOR_CARD_BORDER_NORMAL_BACKGROUND))
        card.set_border_selected_color(QColor(COLOR_CARD_BORDER_SELECTED_BACKGROUND))
        
        card.set_not_selected()
        card.set_border_radius( RADIUS_CARD )
        card.set_border_width( WIDTH_BORDER_CARD )
 
        panel = card.get_panel()        
        layout = panel.get_layout()

        card_panel = CardPanel(card, card_data)
        layout.addWidget(card_panel)
        
        return card
    
    
    
       
       
            


  
    def set_filter_listener(self, listener):
        self.control_panel.set_filter_listener(listener)
        
    def get_filter_holder(self):
        return self.control_panel.get_filter_holder()
      
      
  

# =========================================
# 
# This Class represents the title
#
# =========================================
#
class HierarchyTitle(QWidget):
    DEFAULT_BACKGROUND_COLOR = Qt.lightGray
    DEFAULT_BORDER_RADIUS = 10
    
    def __init__(self, parent):
        QWidget.__init__(self, parent)

        self_layout = QHBoxLayout(self)
        self_layout.setContentsMargins(5, 5, 5, 5)
        self_layout.setSpacing(1)
        self.setLayout( self_layout )
        
        self.label = QLabel("", self)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignHCenter)
        self.label.setFont(QFont( FONT_TYPE, HIERARCHY_TITLE_FONT_SIZE, weight=QFont.Bold))

        self_layout.addWidget(self.label)
        
        self.title = ""
        self.set_background_color(QColor(HierarchyTitle.DEFAULT_BACKGROUND_COLOR), False)
        self.set_border_radius(HierarchyTitle.DEFAULT_BORDER_RADIUS, False)
        
#        self.setHidden(True)

    def set_title(self, card_holder_list, actual_card_holder):
        
        title = " > ".join( [ ch.title for ch in card_holder_list + [actual_card_holder] if ch.title ]  )
        
        self.label.setText(title)
        self.title = title
        
#        if title:
#            self.setHidden(False)
#        else:
#            self.setHidden(True)

    def get_title(self):
        return self.title
        
    def set_background_color(self, color, update=False):
        self.background_color = color
        self.label.setStyleSheet('background: ' + color.name()) 
        if update:
            self.update()
            
    def set_border_radius(self, radius, update=True):
        self.border_radius = radius
        if update:
            self.update()            
        
    def paintEvent(self, event):
        s = self.size()
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing, True)
        qp.setBrush( self.background_color )

        qp.drawRoundedRect(0, 0, s.width(), s.height(), self.border_radius, self.border_radius)
        qp.end()  
        







# =========================================
#
#          Control Panel 
#
# on the TOP of the Window
#
# Contains:
#           Back Button
#           Filter
#
# =========================================
class ControlPanel(QWidget):
    def __init__(self, gui):
        super().__init__()
       
        self.gui = gui
        
        self_layout = QHBoxLayout(self)
        self.setLayout(self_layout)
        
        # controls the distance between the MainWindow and the added container: scrollContent
        self_layout.setContentsMargins(3, 3, 3, 3)
        self_layout.setSpacing(5)

        # -------------
        #
        # Back Button
        #
        # -------------     
        self.back_button_method = None
        back_button = QPushButton()
        back_button.setFocusPolicy(Qt.NoFocus)
        back_button.clicked.connect(self.back_button_on_click)
        
        back_button.setIcon( QIcon( resource_filename(__name__,os.path.join("img", IMG_BACK_BUTTON)) ))
        back_button.setIconSize(QSize(32,32))
        back_button.setCursor(QCursor(Qt.PointingHandCursor))
        back_button.setStyleSheet("background:transparent; border:none") 

        # Back button on the left
        self_layout.addWidget( back_button )

        self_layout.addStretch(1)
        
        # -------------------
        #
        # Config Button
        #
        # -------------------
        self.config_button = QPushButton()
        self.config_button.setFocusPolicy(Qt.NoFocus)
        self.config_button.setCheckable(False)
        self.config_button.clicked.connect(self.config_button_on_click)
        
        config_icon = QIcon()
        config_icon.addPixmap(QPixmap( resource_filename(__name__,os.path.join("img", IMG_CONFIG_BUTTON)) ), QIcon.Normal, QIcon.On)
        self.config_button.setIcon( config_icon )
        self.config_button.setIconSize(QSize(25,25))
        self.config_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.config_button.setStyleSheet("background:transparent; border:none") 
        self_layout.addWidget( self.config_button )
        
        
        
        # -------------
        #
        # Filter Holder
        #
        # -------------
        self.filter_holder = FilterHolder()
        self.filter_holder.changed.connect(self.filter_on_change)
        
        # Filter on the right
        self_layout.addWidget(self.filter_holder)

        # Listeners
        self.back_button_listener = None
        self.filter_listener = None

    def refresh_label(self):
        self.filter_holder.refresh_label()

    def set_back_button_method(self, method):
        self.back_button_method = method
        
    def set_filter_listener(self, listener):
        self.filter_listener = listener
        
    def back_button_on_click(self):
        if self.back_button_method:
            self.back_button_method()


    # -----------------------
    #
    # Config Button Clicked
    #
    # -----------------------
    def config_button_on_click(self):

        dialog = ConfigurationDialog()
#!!!!!        

        # if OK was clicked
        if dialog.exec_() == QDialog.Accepted:        

            # get the values from the DIALOG
            l = dialog.get_language()
            mp = dialog.get_media_path()
            vp = dialog.get_media_player_video()
            vpp = dialog.get_media_player_video_param()
            ap = dialog.get_media_player_audio()
            app = dialog.get_media_player_audio_param()

            # Update the config.ini file
            config_ini_function = get_config_ini()
            config_ini_function.set_media_path(mp) 
            config_ini_function.set_language(l)
            config_ini_function.set_media_player_video(vp)
            config_ini_function.set_media_player_video_param(vpp)
            config_ini_function.set_media_player_audio(ap)
            config_ini_function.set_media_player_audio_param(app)


#!!!!!!!!!!!!
            # Re-read the config.ini file
            re_read_config_ini()

            # Re-import card_holder_pane
            mod = importlib.import_module("akoteka.gui.card_panel")
            importlib.reload(mod)
#!!!!!!!!!!!!

            # remove history
            for card_holder in self.gui.card_holder_list:
                card_holder.setHidden(True)
                self.gui.scroll_layout.removeWidget(card_holder)
            self.gui.card_holder_list.clear()
                
            # Remove recent CardHolder as well
            self.gui.actual_card_holder.setHidden(True)
            self.gui.card_holder_panel_layout.removeWidget(self.gui.actual_card_holder)
            self.gui.actual_card_holder = None
            
            # reload the cards
            self.gui.start_card_holder()
            
            # refresh the Control Panel
            self.refresh_label()
            
        dialog.deleteLater()
 
    def filter_on_change(self):
        if self.filter_listener:
            self.filter_listener.fill_up_card_holder()
    
    def get_filter_holder(self):
        return self.filter_holder









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

    def get_selected(self):
        return self.dropdown.itemData( self.dropdown.currentIndex() )
    
    def select_element(self, id):
        self.dropdown.setCurrentIndex( self.dropdown.findData(id) )

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
        self.setFocusPolicy(Qt.NoFocus)

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
        

# ===============
#
# Filter HOLDER
#
# ===============
class FilterHolder(QWidget):
    
    changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        self_layout = QHBoxLayout(self)
        self.setLayout( self_layout )
        self_layout.setContentsMargins(0, 0, 0, 0)
        self_layout.setSpacing(8)    
        
        # ----------
        #
        # Checkboxes
        #
        # ----------
        self.filter_cb_favorite = FilterCheckBox(_('title_favorite'))
        self.filter_cb_best = FilterCheckBox(_('title_best'))
        self.filter_cb_new = FilterCheckBox(_('title_new'))
                
        holder_checkbox = FilterCheckBoxHolder()
        
        holder_checkbox.add_checkbox(self.filter_cb_favorite)
        holder_checkbox.add_checkbox(self.filter_cb_best)
        holder_checkbox.add_checkbox(self.filter_cb_new)        
                
        # Listener
        self.filter_cb_favorite.stateChanged.connect(self.state_changed)
        self.filter_cb_best.stateChanged.connect(self.state_changed)
        self.filter_cb_new.stateChanged.connect(self.state_changed)
                        
        self_layout.addWidget(holder_checkbox)

        # ----------
        #
        # Dropdowns 
        #
        # ----------

        #
        # Dropdown - genre+theme
        #
        self.filter_dd_genre = FilterDropDownSimple(_('title_genre'))
        self.filter_dd_theme = FilterDropDownSimple(_('title_theme'))
        
        holder_dropdown_gt = FilterDropDownHolder()
        
        holder_dropdown_gt.add_dropdown(self.filter_dd_genre)
        holder_dropdown_gt.add_dropdown(self.filter_dd_theme)
        
        self_layout.addWidget(holder_dropdown_gt)

        #
        # Dropdown - director+actor
        #
        self.filter_dd_director = FilterDropDownSimple(_('title_director'))
        self.filter_dd_actor = FilterDropDownSimple(_('title_actor'))
        
        holder_dropdown_da = FilterDropDownHolder()
        
        holder_dropdown_da.add_dropdown(self.filter_dd_director)
        holder_dropdown_da.add_dropdown(self.filter_dd_actor)
        
        self_layout.addWidget(holder_dropdown_da)

        # Listeners
        self.filter_dd_genre.state_changed.connect(self.state_changed)
        self.filter_dd_theme.state_changed.connect(self.state_changed)
        self.filter_dd_director.state_changed.connect(self.state_changed)
        self.filter_dd_actor.state_changed.connect(self.state_changed)

    def refresh_label(self):
        self.filter_dd_genre.refresh_label(_('title_genre'))
        self.filter_dd_theme.refresh_label(_('title_theme'))
        self.filter_dd_director.refresh_label(_('title_director'))
        self.filter_dd_actor.refresh_label(_('title_actor'))
        self.filter_cb_favorite.refresh_label(_('title_favorite'))
        self.filter_cb_new.refresh_label(_('title_new'))
        self.filter_cb_best.refresh_label(_('title_best'))
        
        
    def clear_genre(self):
        self.filter_dd_genre.clear_elements()
        
    def add_genre(self, value, id):
        self.filter_dd_genre.add_element(value, id)
        
    def select_genre(self, id):
        self.filter_dd_genre.select_element(id)

    def clear_theme(self):
        self.filter_dd_theme.clear_elements()

    def add_theme(self, value, id):
        self.filter_dd_theme.add_element(value, id)
        
    def select_theme(self, id):
        self.filter_dd_theme.select_element(id)        

    def clear_director(self):
        self.filter_dd_director.clear_elements()
    
    def add_director(self, director):
        self.filter_dd_director.add_element(director, director)
    
    def select_director(self, id):
        self.filter_dd_director.select_element(id)
        
    def clear_actor(self):
        self.filter_dd_actor.clear_elements()

    def add_actor(self, actor):
        self.filter_dd_actor.add_element(actor, actor)
        
    def select_actor(self, id):
        self.filter_dd_actor.select_element(id)        
    
    def get_filter_selection(self):
        filter_selection = {
            "best": self.filter_cb_best.is_checked(),
            "new": self.filter_cb_new.is_checked(),
            "favorite": self.filter_cb_favorite.is_checked(),
            "genre": self.filter_dd_genre.get_selected(),
            "theme": self.filter_dd_theme.get_selected(),
            "director": self.filter_dd_director.get_selected(),
            "actor": self.filter_dd_actor.get_selected()
        }
        return filter_selection
    
    def state_changed(self):
        self.changed.emit()
















        
def main():   
    
    app = QApplication(sys.argv)
    ex = GuiAkoTeka()
    ex.start_card_holder()
    sys.exit(app.exec_())
    
    
