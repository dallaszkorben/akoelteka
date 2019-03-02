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

from akoteka.gui.pyqt_import import *
from akoteka.gui.card_panel import CardPanel
from akoteka.gui.configuration_dialog import ConfigurationDialog

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

# ================================
#
# Control Buttons Holder
#
# Contains:
#           Back Button
#           Fast Search Button
#           Advanced Search Button
# ================================
class ControlButtonsHolder(QWidget):
    def __init__(self, control_panel):
        super().__init__()
       
        self.control_panel = control_panel
        
        self_layout = QHBoxLayout(self)
        self.setLayout(self_layout)
        
        self_layout.setContentsMargins(0, 0, 0, 0)
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
        # Fast Search Button
        #
        # -------------------
        self.fast_search_button = QPushButton()
        self.fast_search_button.setFocusPolicy(Qt.NoFocus)
        self.fast_search_button.setCheckable(True)
        self.fast_search_button.setAutoExclusive(False)
        self.fast_search_button.toggled.connect(self.fast_search_button_on_click)
        
        fast_search_icon = QIcon()
        fast_search_icon.addPixmap(QPixmap( resource_filename(__name__,os.path.join("img", IMG_FAST_SEARCH_BUTTON_ON)) ), QIcon.Normal, QIcon.On)
        fast_search_icon.addPixmap(QPixmap( resource_filename(__name__,os.path.join("img", IMG_FAST_SEARCH_BUTTON_OFF)) ), QIcon.Normal, QIcon.Off)
        self.fast_search_button.setIcon( fast_search_icon )
        self.fast_search_button.setIconSize(QSize(25,25))
        self.fast_search_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.fast_search_button.setStyleSheet("background:transparent; border:none") 
        self_layout.addWidget( self.fast_search_button )
        
        # -------------------
        #
        # Advanced Search Button
        #
        # -------------------
        self.advanced_search_button = QPushButton()
        self.advanced_search_button.setFocusPolicy(Qt.NoFocus)
        self.advanced_search_button.setCheckable(True)
        self.advanced_search_button.setAutoExclusive(False)
        self.advanced_search_button.toggled.connect(self.advanced_search_button_on_click)
        
        advanced_search_icon = QIcon()
        advanced_search_icon.addPixmap(QPixmap( resource_filename(__name__,os.path.join("img", IMG_ADVANCED_SEARCH_BUTTON_ON)) ), QIcon.Normal, QIcon.On)
        advanced_search_icon.addPixmap(QPixmap( resource_filename(__name__,os.path.join("img", IMG_ADVANCED_SEARCH_BUTTON_OFF)) ), QIcon.Normal, QIcon.Off)
        self.advanced_search_button.setIcon( advanced_search_icon )
        self.advanced_search_button.setIconSize(QSize(25,25))
        self.advanced_search_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.advanced_search_button.setStyleSheet("background:transparent; border:none") 
        self_layout.addWidget( self.advanced_search_button )
        
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
        
        self.enableSearchIcons(False)
        
         
    def enableSearchIcons(self, enabled):
        if self.advanced_search_button.isChecked():
            self.advanced_search_button.setChecked(False)

        if self.fast_search_button.isChecked():
            self.fast_search_button.setChecked(False)
        
        self.advanced_search_button.setEnabled(enabled)
        self.fast_search_button.setEnabled(enabled)

    # --------------------------
    #
    # Fast Search Button Clicked
    #
    # --------------------------
    def fast_search_button_on_click(self, checked):
        if checked:
            self.advanced_search_button.setChecked(False)
        # hide/show fast filter
        self.control_panel.fast_filter_holder.setHidden(not checked)
        # filter the list
        self.control_panel.fast_filter_on_change()
    
    # ------------------------------
    #
    # Advanced Search Button Clicked
    #
    # ------------------------------
    def advanced_search_button_on_click(self, checked):
        if checked:
            self.fast_search_button.setChecked(False)
        # hide/show advanced filter
        self.control_panel.advanced_filter_holder.setHidden(not checked)
        # filter the list
        self.control_panel.advanced_filter_on_click()
        
    # -------------------
    #
    # Back Button Clicked
    #
    # -------------------
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
            for card_holder in self.control_panel.gui.card_holder_history:
                card_holder.setHidden(True)
                self.control_panel.gui.card_holder_panel_layout.removeWidget(card_holder)
                #self.gui.scroll_layout.removeWidget(card_holder)
            self.control_panel.gui.card_holder_history.clear()
                
            # Remove recent CardHolder as well
            self.control_panel.gui.actual_card_holder.setHidden(True)
            self.control_panel.gui.card_holder_panel_layout.removeWidget(self.control_panel.gui.actual_card_holder)
            self.control_panel.gui.actual_card_holder = None
            
            # reload the cards
            self.control_panel.gui.startCardHolder()
            
            # refresh the Control Panel
            self.control_panel.refresh_label()
            
        dialog.deleteLater()
