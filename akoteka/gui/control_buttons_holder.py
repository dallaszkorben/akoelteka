import sys
import os
import signal
import importlib
import psutil

from threading import Thread
from pkg_resources import resource_string, resource_filename
from functools import cmp_to_key
import locale
from PyQt5.QtCore import QThread

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
from akoteka.accessories import play_media



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
        
        
        # ================================================
        # ================================================        
        
        # -------------------
        #
        # Play Sequentially Button
        #
        # -------------------

        self.play_continously_button = QPushButton()
        self.play_continously_button.setFocusPolicy(Qt.NoFocus)
        self.play_continously_button.clicked.connect(self.play_continously_button_on_click)
        
        play_continously_icon = QIcon()
        play_continously_icon.addPixmap(QPixmap( resource_filename(__name__,os.path.join("img", IMG_PLAY_CONTINOUSLY_BUTTON_ON)) ), QIcon.Normal, QIcon.On)
#        play_continously_icon.addPixmap(QPixmap( resource_filename(__name__,os.path.join("img", IMG_PLAY_CONTINOUSLY_BUTTON_OFF)) ), QIcon.Normal, QIcon.Off)
        self.play_continously_button.setIcon( play_continously_icon )
        self.play_continously_button.setIconSize(QSize(25,25))
        self.play_continously_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.play_continously_button.setStyleSheet("background:transparent; border:none") 
        self_layout.addWidget( self.play_continously_button )

        # -------------------
        #
        # Stop Button
        #
        # -------------------
        self.stop_continously_button = QPushButton()
        self.stop_continously_button.setFocusPolicy(Qt.NoFocus)
        self.stop_continously_button.clicked.connect(self.stop_continously_button_on_click)
        
        stop_continously_icon = QIcon()
        stop_continously_icon.addPixmap(QPixmap( resource_filename(__name__,os.path.join("img", IMG_STOP_CONTINOUSLY_BUTTON_ON)) ), QIcon.Normal, QIcon.On)
#        stop_continously_icon.addPixmap(QPixmap( resource_filename(__name__,os.path.join("img", IMG_STOP_CONTINOUSLY_BUTTON_OFF)) ), QIcon.Normal, QIcon.Off)
        self.stop_continously_button.setIcon( stop_continously_icon )
        self.stop_continously_button.setIconSize(QSize(25,25))
        self.stop_continously_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.stop_continously_button.setStyleSheet("background:transparent; border:none") 
        self_layout.addWidget( self.stop_continously_button )
        
        # ----------------------------------
        #
        # Playing Continously list drop-down
        #
        # ----------------------------------

        self.dropdown_play_continously = QComboBox(self)
        self.dropdown_play_continously.setFocusPolicy(Qt.NoFocus)
        self.dropdown_play_continously.setEditable(True)
        
#        self.dropdown.currentIndexChanged.connect(self.current_index_changed)

        style_box = '''
            QComboBox { 
                max-width: 200px; min-width: 300px; border: 1px solid gray; border-radius: 5px;
            }
        '''
        style_drop_down ='''
            QComboBox QAbstractItemView::item { 
                color: red;
                max-height: 15px;
            }
        '''            
      
        self.dropdown_play_continously.setStyleSheet(style_box + style_drop_down)
        #self.dropdown_play_continously.addItem("")
        self_layout.addWidget( self.dropdown_play_continously )

               
        self_layout.addStretch(1) 
        
        # ================================================
        # ================================================        
                
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
        
        # ================================================
        # ================================================
                        
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
        self.disablePlayStopContinously()
        
    # ======================================================
    
    def clear_play_continously_elements(self):
        self.dropdown_play_continously.clear()
        
    def add_play_continously_separator(self):
        self.dropdown_play_continously.insertSeparator(self.dropdown_play_continously.__len__())        
        
    def add_play_continously_element(self, title, path):
        self.dropdown_play_continously.addItem(title, path)        
        
    def get_play_continously_selected_path(self):
        return self.dropdown_play_continously.itemData( self.dropdown_play_continously.currentIndex() )

    def get_play_continously_path_by_index(self, index):
        return self.dropdown_play_continously.itemData( index )

    def get_play_continously_selected_title(self):
        return self.dropdown_play_continously.itemText( self.dropdown_play_continously.currentIndex() )    
    
    def get_play_continously_title_by_index(self, index):
        return self.dropdown_play_continously.itemText( index )
    
    def get_play_continously_selected_index(self):
        return self.dropdown_play_continously.currentIndex()

    def get_play_continously_last_index(self):
        return self.dropdown_play_continously.count() - 1
    
    def select_play_continously_element_by_index(self, index):
        self.dropdown_play_continously.setCurrentIndex(index)
        
    # ======================================================
            
    def disablePlayStopContinously(self):
        self.play_continously_button.setEnabled(False)
        self.stop_continously_button.setEnabled(False)
        self.dropdown_play_continously.setEnabled(False)
        
    def enablePlayContinously(self, enabled):
        self.play_continously_button.setEnabled(enabled)
        self.stop_continously_button.setEnabled(not enabled)
        self.dropdown_play_continously.setEnabled(enabled)
    
    # =====================================================
         
    def enableSearchIcons(self, enabled):
        if self.advanced_search_button.isChecked():
            self.advanced_search_button.setChecked(False)

        if self.fast_search_button.isChecked():
            self.fast_search_button.setChecked(False)
        
        self.advanced_search_button.setEnabled(enabled)
        self.fast_search_button.setEnabled(enabled)

    def play_continously_button_on_click(self):

        # Start to play the media collection
        inst = PlayContinouslyThread.play(self)
       
        # connect the "selected" event to a method which will select the media in the drop-down list
        inst.selected.connect(self.select_play_continously_element_by_index)

    def stop_continously_button_on_click(self):
        PlayContinouslyThread.stop()

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
        self.control_panel.advanced_filter_filter_on_click()
        
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
        



class PlayContinouslyThread(QThread):
    
    selected = pyqtSignal(int)
    
    __instance = None
    __run = False
    __wait_for_stop = False
    
    @classmethod
    def play(cls, parent):
        
        if cls.__instance is None:
            cls.__new__(cls)
        
        cls.__init__(cls.__instance, parent)
            
        if not cls.__run:
            cls.__instance.start()
            
        return cls.__instance

    @classmethod
    def stop(cls):
        PlayContinouslyThread.__wait_for_stop = True
        
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance    

    def __init__(self, parent):
        QThread.__init__(self)        
        self.parent = parent
         
    def run(self):

        PlayContinouslyThread.__run = True
        PlayContinouslyThread.__wait_for_stop = False
        self.parent.enablePlayContinously(False)

        start_index = self.parent.get_play_continously_selected_index()
        end_index = self.parent.get_play_continously_last_index()

        stop_all = False
        for index in range(start_index, end_index + 1):
            
            pid = None
            media = self.parent.get_play_continously_path_by_index(index)
            if media is not None:
            
                # play the next media
                pid = play_media(media)               
            
                # emit an media selection event
                self.selected.emit(index)                

            # checking if it stopped
            while pid is not None:

                # if the Play Continously is stopped
                if PlayContinouslyThread.__wait_for_stop:
                    
                    # then kill the process
                    stop_all = True
                    os.kill(pid, signal.SIGKILL)
                    break
                    
                    # --- Id does not work. root needed ---
                    #p = psutil.Process(pid)
                    #p.terminate()

                # I suppose the pid does not exist anymore
                still_exist_pid = False
                
                # I check the running processes
                for p in psutil.process_iter():
                    if p.pid == pid:
                        still_exist_pid = True
                        break
                    
                if not still_exist_pid:
                    break
                
                # at this point the pid is still exists so the media is playing
                # I wait a second
                QThread.sleep(1)

            # If the Play Continously is stopped
            if stop_all:
                
                # Break the loop on the files
                break

        # Indicates that the Thread is ready to start again
        self.parent.enablePlayContinously(True)
        PlayContinouslyThread.__run = False

    def __del__(self):
        self.exiting = True
        self.wait()
