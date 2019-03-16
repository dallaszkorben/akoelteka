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
from akoteka.gui.control_buttons_holder import ControlButtonsHolder
from akoteka.gui.fast_filter_holder import FastFilterHolder
from akoteka.gui.advanced_filter_holder import AdvancedFilterHolder

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
#from builtins import None

class GuiAkoTeka(QWidget, QObject):
    
    def __init__(self):
        #super().__init__()  
        QWidget.__init__(self)
        QObject.__init__(self)
        
        self.actual_card_holder = None
        self.card_holder_history = []
        
        # most outer container, just right in the Main Window
        box_layout = QVBoxLayout(self)
        self.setLayout(box_layout)
        # controls the distance between the MainWindow and the added container: scrollContent
        box_layout.setContentsMargins(0, 0, 0, 0)
        box_layout.setSpacing(0)
    
        # control panel
        self.control_panel = ControlPanel(self)
        self.control_panel.set_back_button_method(self.restore_previous_holder)
        box_layout.addWidget( self.control_panel)
    
        # scroll_content where you can add your widgets - has scroll
        scroll = QScrollArea(self)
        box_layout.addWidget(scroll)
        scroll.setWidgetResizable(True)
        scroll_content = QWidget(scroll)
        scroll_content.setStyleSheet('background: ' + COLOR_MAIN_BACKGROUND)
        scroll.setFocusPolicy(Qt.NoFocus)
    
#        scroll_content = QWidget(self)
#        scroll_content.setStyleSheet('background: ' + COLOR_MAIN_BACKGROUND)
#        box_layout.addWidget(scroll_content)
#        scroll_layout = QVBoxLayout(scroll_content)
#        scroll_content.setLayout(scroll_layout)

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
        self.hierarchy_title = HierarchyTitle(scroll_content, self)
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

    def startCardHolder(self):
        """
        --- Start Card Holder ---
        
        """
        # Create the first Card Holder - 
        #self.go_down_in_hierarchy( [], "" )
        self.go_down_in_hierarchy() 

        # Retreive the media path
        paths = [config_ini['media_path']]
        
        # Start to collect the Cards from the media path
        self.actual_card_holder.startCardCollection(paths)        

    def go_down_in_hierarchy( self, card_descriptor_structure=None, title=None, save=True ):
        """
        --- Go Down in Hierarchy
        
        Go deeper in the hierarchy

         card_descriptor_structure The NOT Filtered card hierarchy list
                                   on the recent level
         title                     The title what whould be shown above
                               the CardHolder
         save                      It controls to save the CardHolder
                                   into the history list
                                   collecting_finish uses it with False
        """
        # if it is called very first time
        if card_descriptor_structure is None:
            self.initialize = True
            card_descriptor_structure = []
            title = ""
            save = False
        else:
            self.initialize = False

        # if there is already a CardHolder
        if self.actual_card_holder:

            # hide the old CardHolder
            self.actual_card_holder.setHidden(True)

        # if it is said to Save the CardHolder to the history list
        if save:
            
            # save the old CardHolder it in a list
            self.card_holder_history.append(self.actual_card_holder)
                    
        self.actual_card_holder = CardHolder(            
            self, 
            self.get_new_card,
            self.collect_cards,
            self.collecting_start,
            self.collecting_finish
        )
        
        self.actual_card_holder.title = title
        self.actual_card_holder.set_max_overlapped_cards( MAX_OVERLAPPED_CARDS )
        self.actual_card_holder.set_y_coordinate_by_reverse_index_method(self.get_y_coordinate_by_reverse_index)
        self.actual_card_holder.set_x_offset_by_index_method(self.get_x_offset_by_index)
        self.actual_card_holder.set_background_color(QColor(COLOR_CARDHOLDER_BACKGROUND))
        self.actual_card_holder.set_border_radius(RADIUS_CARDHOLDER)
        self.actual_card_holder.set_border_width(15)        
                
        # Save the original card desctiptor structure into the CardHolder
        self.actual_card_holder.orig_card_descriptor_structure = card_descriptor_structure
        
        # Make the CardHolder to be in Focus
        self.actual_card_holder.setFocus()

        # Set the title of the CardHolder - The actual level of the hierarchy
        self.hierarchy_title.set_title(self.card_holder_history, self.actual_card_holder)

        # add the new holder to the panel
        self.card_holder_panel_layout.addWidget(self.actual_card_holder)
        #self.scroll_layout.addStretch(1)

        # filter the list by the filters + Fill-up the CardHolder with Cards using the parameter as list of descriptor
        self.filter_the_cards(card_descriptor_structure)

    def restore_previous_holder(self, steps=1):
        """
        --- Restore Previous Holder ---
        
        Come up in the hierarchy
        """        
        size = len(self.card_holder_history)
        if  size >= steps:

            for i in range(0, steps):
            
                previous_card_holder = self.card_holder_history.pop()
                # get the previous CardHolder
                #previous_card_holder = self.card_holder_history[size - 1]
            
                # remove the previous CardHolder from the history list
                #self.card_holder_history.remove(previous_card_holder)
            
            # hide the old CardHolder
            self.actual_card_holder.setHidden(True)            
            
            # remove from the layout the old CardHolder
            self.card_holder_panel_layout.removeWidget(self.actual_card_holder)
        
            # the current card holder is the previous
            self.actual_card_holder = previous_card_holder
            
            # show the current card holder
            self.actual_card_holder.setHidden(False)

            # set the title
            self.hierarchy_title.set_title(self.card_holder_history, self.actual_card_holder)
            
            # filter the list by the filters + Fill-up the CardHolder with Cards using the parameter as list of descriptor
            self.filter_the_cards(self.actual_card_holder.orig_card_descriptor_structure)
            #self.filter_the_cards(self.actual_card_holder.orig_card_descriptor_structure)
            
            # select the Card which was selected to enter
            self.actual_card_holder.select_actual_card()
            
            # Make the CardHolder to be in Focus
            self.actual_card_holder.setFocus()         

    def collecting_start(self):
        """
        --- Collecting Started ---
        Indicates that the CardCollection process started.
        The CardHolder calls this method
        Jobs to do:
            -Hide the title
        """
        self.hierarchy_title.setHidden(True)
        
        # close the Search panels and disable buttons to search
        self.control_panel.control_buttons_holder.enableSearchIcons(False)
        self.control_panel.control_buttons_holder.disablePlayStopContinously()

    def collecting_finish(self, card_holder, card_descriptor_structure):
        """
        --- Collecting Finished ---
        
        Indicates that the CardCollection process finished.
        The CardHolder calls this method
        Jobs to do:
            -Show the title
            -Set up the filters
        """        
        
        if card_descriptor_structure:
          
            # Show the title of the CardHolder (the certain level)        
            self.hierarchy_title.setHidden(False)       
        
        # Save the NOT Filtered list
        card_holder.orig_card_descriptor_structure = card_descriptor_structure
        
        # Set-up the Filters        
        self.set_up_filters(card_descriptor_structure)
        
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # This part is tricky
        # It prevents to show the 0. level of Cards
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        #
        # if there is only ONE Card and the status of the presentation is "initialize"
        if len(card_holder.card_descriptor_list) == 1 and self.initialize:
            # then I go down ONE level
#            self.go_down_in_hierarchy(card_holder.card_descriptor_list[0]['extra']["orig-sub-cards"], card_holder.card_descriptor_list[0]['title'][config_ini['language']], save=False )
            self.go_down_in_hierarchy(card_holder.card_descriptor_list[0]['extra']["sub-cards"], card_holder.card_descriptor_list[0]['title'][config_ini['language']], save=False )

        # Enable the buttons to search
        self.control_panel.control_buttons_holder.enableSearchIcons(True)
        self.control_panel.control_buttons_holder.enablePlayContinously(True)
        
    def get_y_coordinate_by_reverse_index(self, reverse_index, diff_to_max):
        """
        --- Get Y coordinate by reverse index
      
        Calculates the Y coordinate of a Card using reverse index        
        """
        raw_pos = (reverse_index + diff_to_max) * (reverse_index + diff_to_max)
        offset = diff_to_max * diff_to_max
        return (raw_pos - offset) * 8
        #return reverse_index * 220
    
    def get_x_offset_by_index(self, index):
        """
        --- Get X offset by index ---
        
        Calculates the X coordinate of a Card by index        
        """
        return index * 4       

    def collect_cards(self, paths):
        """
        --- Collect Cards ---
        
        It will be executed only once
        in the CardHolder.CollectCardThread.run() what the 
        CardHOlder.startCardCollection() triggers in the startHolder() method
        """
        cdl = collect_cards(paths)
        filtered_card_structure = self.get_cards_by_advanced_filter(cdl)
        return filtered_card_structure
    
    def get_new_card(self, card_data, local_index, index):
        """
        --- Get New Card ---
        
        Generates a new Card
        """

        card = Card(self.actual_card_holder, card_data, local_index, index)
        
        if card_data["extra"]["media-path"]:
            card.set_background_color(QColor(COLOR_CARD_MOVIE_BACKGROUND))
        else:
            card.set_background_color(QColor(COLOR_CARD_COLLECTOR_BACKGROUND))
            
        card.set_border_normal_color(QColor(COLOR_CARD_BORDER_NORMAL_BACKGROUND))
        card.set_border_selected_color(QColor(COLOR_CARD_BORDER_SELECTED_BACKGROUND))
        
        card.set_not_selected()
        card.set_border_radius( RADIUS_CARD )
        card.set_border_width( WIDTH_BORDER_CARD )
 
        panel = card.get_panel()        
        layout = panel.get_layout()
        layout.setContentsMargins(0, 0, 0, 0)

        card_panel = CardPanel(card, card_data)
        layout.addWidget(card_panel)
        
        return card
  
    def set_fast_filter_listener(self, listener):
        self.control_panel.set_fast_filter_listener(listener)
        
    def set_advanced_filter_listener(self, listener):
        self.control_panel.set_advanced_filter_listener(listener)
        
    def get_fast_filter_holder(self):
        return self.control_panel.get_fast_filter_holder()
    
    def get_advanced_filter_holder(self):
        return self.control_panel.get_advanced_filter_holder()
      
    # --------------------------------
    #
    # Filter the Cards
    #
    # Filters the Cards and Show them
    #
    # --------------------------------
    def filter_the_cards(self, card_descriptor_structure=None):
        if card_descriptor_structure is None:
            card_descriptor_structure = self.actual_card_holder.orig_card_descriptor_structure
        
        filtered_card_structure = self.set_up_filters(card_descriptor_structure)
        
        # Fill up the CardHolder with Cards, alpabetically orderd by title 
        self.actual_card_holder.fillUpCardHolderByDescriptor(sorted(filtered_card_structure, key=lambda arg: locale.strxfrm(arg['title'][config_ini['language']]), reverse=False))
            
            
    # ----------------
    # Set-up Filters
    # ----------------
    def set_up_filters(self, card_descriptor_structure):
        # --- FILL UP ADVANCED FILTERS ---
        unconditional_list = self.get_unconditional_filter_list(card_descriptor_structure)        
        self.fill_up_advanced_filter_lists(unconditional_list)
        
        # --- FILL UP FAST FILTERS ---        
        fast_filter_list = self.get_fast_filter_list(card_descriptor_structure)
        self.fill_up_fast_filter_lists(fast_filter_list)

        # --- Filter the cards setting its ['extra']['visible'] attribute ---
        if not self.control_panel.fast_filter_holder.isHidden():
            filtered_cards = self.get_cards_by_fast_filter(card_descriptor_structure)
        else:    
            filtered_cards = self.get_cards_by_advanced_filter(card_descriptor_structure)
        
        # --- FILL UP PLAY CONTINOUSLY DROP-DOWN ---
        self.fill_up_play_continously_list(filtered_cards)
        
        return filtered_cards
    
        
    
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
    def get_fast_filter_list(self, card_structure):
        """ --------------------------------------------------------------------------------
        
        --- Get Fast Filter List ---
        
        Gives back the filter lists in the certain point of the card hierarchy                
        ------------------------------------------------------------------------------------""" 
        
        def generate_fast_filter_list(card_structure):
        
            # through the SORTED list
            #for crd in sorted(card_structure, key=lambda arg: arg['title'][config_ini['language']], reverse=False):
            for crd in card_structure:

                # in case of MEDIA CARD
                if crd['extra']['media-path']:              

                    # if the card fits to the filter
                    if self.isFitByFilterSelection(crd, self.get_fast_filter_holder().get_filter_selection().items()):

                        for c, v in self.get_fast_filter_holder().get_filter_selection().items():
                            category = v[0]
                        
                            if filter_key[category]['store-mode'] == 'v':
                                if crd[filter_key[category]['section']][category]:
                                    fast_filter_list[category].add(crd[filter_key[category]['section']][category])
                                
                            elif filter_key[category]['store-mode'] == 'a':
                                for cat in crd[filter_key[category]['section']][category]:
                                    if cat.strip():
                                        fast_filter_list[category].add(cat.strip())
                
                            elif filter_key[category]['store-mode'] == 't':
                                fast_filter_list['title'].add(crd[filter_key[category]['section']][config_ini['language']])
                    
                # in case of COLLECTOR CARD
                else:                     

                    # then it depends on the next level
                    generate_fast_filter_list(crd['extra']['sub-cards'])
        
            return fast_filter_list  
  
        fast_filter_list={
            "title": set(),
            "genre": set(),
            "theme": set(),
            "director": set(),
            "actor": set(),
#            "sound": set(),
#            "sub": set(),
#            "country": set(),
#            "year": set(),
#            "length": set(),
            "favorite": set(),
            "new": set(),
            "best": set() 
        }

        generate_fast_filter_list(card_structure)
        
        return fast_filter_list
    
    def fill_up_fast_filter_lists(self, fast_filter_list):
        """--------------------------------------------------------------
        
        Fill up the Fast Filter list by the fast_filter_list
        
        -----------------------------------------------------------------"""
        self.set_fast_filter_listener(None)
        
        fast_state_fields = {
                "title": "",
                "genre": "",
                "theme": "",
                "director": "",
                "actor": "",
#                "sound": "",
#                "sub": "",
#                "country": "",
#                "length-from": "",
#                "length-to": "",
#                "year-from": "",
#                "year-to": "",            
            }        

        # save the fields of the filters because the will be clear when the list is updated
        for category, value in self.get_fast_filter_holder().get_filter_selection().items():            
            if value[1] != None and value[1] != "":
                fast_state_fields[category] = value[1]

        # Fill up TITLE 
        self.get_fast_filter_holder().clear_title()
        self.get_fast_filter_holder().add_title("")
        for element in sorted( fast_filter_list['title'], key=cmp_to_key(locale.strcoll) ):
            self.get_fast_filter_holder().add_title(element)

        # Fill up GENRE 
        self.get_fast_filter_holder().clear_genre()
        self.get_fast_filter_holder().add_genre("", "")
        for element in sorted([(_("genre_" + e),e) for e in fast_filter_list['genre']], key=lambda t: locale.strxfrm(t[0]) ):            
            self.get_fast_filter_holder().add_genre(element[0], element[1])
        
        # Fill up THEME 
        self.get_fast_filter_holder().clear_theme()
        self.get_fast_filter_holder().add_theme("", "")
        for element in sorted([(_("theme_" + e), e) for e in fast_filter_list['theme']], key=lambda t: locale.strxfrm(t[0]) ):
            self.get_fast_filter_holder().add_theme(element[0], element[1])

        # Fill up DIRECTOR 
        self.get_fast_filter_holder().clear_director()
        self.get_fast_filter_holder().add_director("")
        for element in sorted( fast_filter_list['director'], key=cmp_to_key(locale.strcoll) ):
            self.get_fast_filter_holder().add_director(element)

        # Fill up ACTOR 
        self.get_fast_filter_holder().clear_actor()
        self.get_fast_filter_holder().add_actor("")
        for element in sorted( fast_filter_list['actor'], key=cmp_to_key(locale.strcoll) ):
            self.get_fast_filter_holder().add_actor(element)

        # Recover the contents of the fields
        self.get_fast_filter_holder().select_title_by_text(fast_state_fields["title"])
        self.get_fast_filter_holder().select_genre_by_text(fast_state_fields["genre"])
        self.get_fast_filter_holder().select_theme_by_text(fast_state_fields["theme"])
        self.get_fast_filter_holder().select_director_by_text(fast_state_fields["director"])
        self.get_fast_filter_holder().select_actor_by_text(fast_state_fields["actor"])        

        self.set_fast_filter_listener(self)
        
    def get_cards_by_fast_filter(self, card_structure):
        """
        parameters:
            card_structure:        the full structure on the recent level (not filtered)
        """  
        def generate_filtered_list(card_structure):

            mediaFits = False
            collectorFits = False
            
            # through the card structure
            for crd in card_structure:
            
                # in case of MEDIA CARD
                if crd['extra']['media-path']:

                    fits = True

                    if not self.control_panel.fast_filter_holder.isHidden():
    
                        fits = self.isFitByFilterSelection(crd, self.get_fast_filter_holder().get_filter_selection().items())
                 
                    if fits:

                        mediaFits = True
                 
                    crd['extra']['visible'] = fits
   
                # in case of COLLECTOR CARD
                else:                     

                    # then it depends on the next level
                    fits = generate_filtered_list(crd['extra']['sub-cards'])
                
                    if fits:
                        collectorFits = True        
            
                    crd['extra']['visible'] = fits
                
            return (mediaFits or collectorFits)
    
        generate_filtered_list(card_structure)
        return card_structure    
    







    
    def fill_up_play_continously_list(self, filtered_card_structure):
        """
        Gives back a list of media-cards which should be played
        
        Parameters:
            filtered_card_structure   ['extra']['sub-cards'] False - should not be played (filtered out) 
        
        Return:
            <list>[0] True/False - media/separator
            <list>[1] path to media
            <list>[2] title of the media
        """

        def generate_list(filtered_card_structure, playing_list):

            # through the SORTED list
            #for crd in sorted(filtered_card_structure, key=lambda arg: locale.strxfrm(arg['title'][config_ini['language']]), reverse=False):
            for crd in sorted(filtered_card_structure, key=lambda arg:  locale.strxfrm(arg['title'][config_ini['language']])    if arg['extra']['media-path'] and arg['extra']['visible'] else "_" + locale.strxfrm(arg['title'][config_ini['language']])            , reverse=False):
            
                # in case of MEDIA CARD
                if crd['extra']['media-path'] and crd['extra']['visible']:

                    playing_list.append((True, crd['extra']['media-path'], crd['title'][config_ini['language']]))
   
                # in case of COLLECTOR CARD
                elif crd['extra']['visible']:                     

                    playing_list.append((False, crd['extra']['media-path'], crd['title'][config_ini['language']]))
                    
                    # then it depends on the next level
                    generate_list(crd['extra']['sub-cards'], playing_list)
                
            return
    
        playing_list = []        
        generate_list(filtered_card_structure, playing_list)
        
        self.control_panel.control_buttons_holder.clear_play_continously_elements()
        self.control_panel.control_buttons_holder.add_play_continously_element("", "")
        for l in playing_list:
            if l[0]:
                self.control_panel.control_buttons_holder.add_play_continously_element(l[2], l[1])
            else:
                self.control_panel.control_buttons_holder.add_play_continously_separator()

    
    
    
    
    
    
    
      
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
    def get_unconditional_filter_list(self, card_structure):
        """ --------------------------------------------------------------------------------
        
        --- Get Advanced Filter List ---
        
        Gives back the unconditional filter lists in the certain point of the card hierarchy                
        ------------------------------------------------------------------------------------""" 
        
        def generate_unconditional_filter_list(card_structure):
        
            # through the SORTED list
            for crd in card_structure:
            #for crd in sorted(card_structure, key=lambda arg: arg['title'][config_ini['language']], reverse=False):

                # in case of MEDIA CARD
                if crd['extra']['media-path']:              

                    for c, v in self.get_advanced_filter_holder().get_filter_selection().items():
                        category = v[0]
                        
                        if filter_key[category]['store-mode'] == 'v':
                            if crd[filter_key[category]['section']][category]:
                                unconditional_filter_list[category].add(crd[filter_key[category]['section']][category])
                                
                        elif filter_key[category]['store-mode'] == 'a':
                            for cat in crd[filter_key[category]['section']][category]:
                                if cat.strip():
                                    unconditional_filter_list[category].add(cat.strip())
                
                        elif filter_key[category]['store-mode'] == 't':
                            unconditional_filter_list['title'].add(crd[filter_key[category]['section']][config_ini['language']])
                    
                # in case of COLLECTOR CARD
                else:                     

                    # then it depends on the next level
                    generate_unconditional_filter_list(crd['extra']['sub-cards'])
        
            return unconditional_filter_list  
  
        unconditional_filter_list={
            "title": set(),
            "genre": set(),
            "theme": set(),
            "director": set(),
            "actor": set(),
            "sound": set(),
            "sub": set(),
            "country": set(),
            "year": set(),
            "length": set(),
            "favorite": set(),
            "new": set(),
            "best": set() }

        # ADVANCED FILTER is visible
        #if not self.control_panel.advanced_filter_holder.isHidden():
        generate_unconditional_filter_list(card_structure)
        
        return unconditional_filter_list
  
    def fill_up_advanced_filter_lists(self, unconditional_filter_list):
        """--------------------------------------------------------------
        
        Fill up the Advanced Filter list by the unconditional_filter_list
        
        -----------------------------------------------------------------"""

        advanced_state_fields = {
                "title": "",
                "genre": "",
                "theme": "",
                "director": "",
                "actor": "",
                "sound": "",
                "sub": "",
                "country": "",
                "length-from": "",
                "length-to": "",
                "year-from": "",
                "year-to": "",            
            }        

        # save the fields of the filters because the will be clear when the list is updated
        for category, value in self.get_advanced_filter_holder().get_filter_selection().items():
            if value[1] != None and value[1] != "":
                advanced_state_fields[category] = value[1]

        # Fill up TITLE
        self.get_advanced_filter_holder().clear_title()            
        for element in sorted( unconditional_filter_list['title'], key=cmp_to_key(locale.strcoll) ):
            self.get_advanced_filter_holder().add_title(element)
        
        # Fill up GENRE 
        self.get_advanced_filter_holder().clear_genre()            
        for element in sorted([(_("genre_" + e),e) for e in unconditional_filter_list['genre']], key=lambda t: locale.strxfrm(t[0]) ):            
            self.get_advanced_filter_holder().add_genre(element[0], element[1])
        
        # Fill up THEME 
        self.get_advanced_filter_holder().clear_theme()
        for element in sorted([(_("theme_" + e), e) for e in unconditional_filter_list['theme']], key=lambda t: locale.strxfrm(t[0]) ):            
            self.get_advanced_filter_holder().add_theme(element[0], element[1])

        # Fill up DIRECTOR 
        self.get_advanced_filter_holder().clear_director()            
        for element in sorted( unconditional_filter_list['director'], key=cmp_to_key(locale.strcoll) ):
            self.get_advanced_filter_holder().add_director(element)

        # Fill up ACTOR 
        self.get_advanced_filter_holder().clear_actor()            
        for element in sorted( unconditional_filter_list['actor'], key=cmp_to_key(locale.strcoll) ):
            self.get_advanced_filter_holder().add_actor(element)
        
        # Fill up SOUND
        self.get_advanced_filter_holder().clear_sound()
        #self.get_advanced_filter_holder().add_sound("", "")
        for element in sorted([(_("lang_long_" + e), e) for e in unconditional_filter_list['sound']], key=lambda t: locale.strxfrm(t[0]) ):            
            self.get_advanced_filter_holder().add_sound(element[0], element[1])

        # Fill up SUBTITLE
        self.get_advanced_filter_holder().clear_sub()
        #self.get_advanced_filter_holder().add_sub("", "")
        for element in sorted([(_("lang_long_" + e), e) for e in unconditional_filter_list['sub']], key=lambda t: locale.strxfrm(t[0]) ):            
            self.get_advanced_filter_holder().add_sub(element[0], element[1])

        # Fill up COUNTRY
        self.get_advanced_filter_holder().clear_country()
        #self.get_advanced_filter_holder().add_country("", "")
        for element in sorted([(_("country_long_" + e), e) for e in unconditional_filter_list['country']], key=lambda t: locale.strxfrm(t[0]) ):            
            self.get_advanced_filter_holder().add_country(element[0], element[1])
       
        # Fill up YEAR from/to
        self.get_advanced_filter_holder().clear_year()
        #self.get_advanced_filter_holder().add_year("")
        for element in sorted( unconditional_filter_list['year'], key=cmp_to_key(locale.strcoll) ):
            self.get_advanced_filter_holder().add_year(element)

        # Fill up LENGTH from/to
        self.get_advanced_filter_holder().clear_length()
        #self.get_advanced_filter_holder().add_length("")
        for element in sorted( [str(int(spl[-2])).rjust(1) + ":" + str(int(spl[-1])).zfill(2) for spl in [l.split(":") for l in unconditional_filter_list['length'] if ':' in l ] if all(c.isdigit() for c in spl[-1] ) and all(c.isdigit() for c in spl[-2] )], key=cmp_to_key(locale.strcoll) ):
            self.get_advanced_filter_holder().add_length(element)
  
        # Recover the contents of the fields
        self.get_advanced_filter_holder().set_title(advanced_state_fields['title'])
        self.get_advanced_filter_holder().set_genre(advanced_state_fields['genre'])
        self.get_advanced_filter_holder().set_theme(advanced_state_fields['theme'])
        self.get_advanced_filter_holder().set_director(advanced_state_fields['director'])
        self.get_advanced_filter_holder().set_actor(advanced_state_fields['actor'])
        self.get_advanced_filter_holder().select_sound(advanced_state_fields['sound'])
        self.get_advanced_filter_holder().select_sub(advanced_state_fields['sub'])
        self.get_advanced_filter_holder().select_country(advanced_state_fields['country'])
        self.get_advanced_filter_holder().select_year_from(advanced_state_fields['year-from'])
        self.get_advanced_filter_holder().select_year_to(advanced_state_fields['year-to'])
        self.get_advanced_filter_holder().select_length_from(advanced_state_fields['length-from'])
        self.get_advanced_filter_holder().select_length_to(advanced_state_fields['length-to'])
        
    def get_cards_by_advanced_filter(self, card_structure):
        """
        parameters:
            card_structure:        the full structure on the recent level (not filtered)
        """  
        def generate_filtered_list(card_structure):

            mediaFits = False
            collectorFits = False
            
            # through the card structure
            for crd in card_structure:
            
                # in case of MEDIA CARD
                if crd['extra']['media-path']:

                    fits = True

                    if not self.control_panel.advanced_filter_holder.isHidden():
    
                        fits = self.isFitByFilterSelection(crd, self.get_advanced_filter_holder().get_filter_selection().items())
                 
                    if fits:

                        mediaFits = True

                    crd['extra']['visible'] = fits
   
                # in case of COLLECTOR CARD
                else:                     

                    # then it depends on the next level
                    fits = generate_filtered_list(crd['extra']['sub-cards'])
                
                    if fits:
                        collectorFits = True        
            
                    crd['extra']['visible'] = fits
                
            return (mediaFits or collectorFits)
    
        generate_filtered_list(card_structure)
        return card_structure

    def to_integer(self, value):         
        hours, minutes = map(int, (['0']+value.split(':'))[-2:])
        return hours * 60 + minutes
  
    def isFitByFilterSelection(self, card, filter_selection):
        """
        
        --- Is Fit By Filter Selection ---
        
        Say if the card fits to the Filter Selection        
        """
        fits = True            
        # go through the ADVANCED FILTERS by Categories and decide if the Card is filtered
        for c, v in filter_selection:
            category = v[0]
                        
            # do I want to check this Category match
            if v[1]:                            
                            
                fits = False
                operation = v[3]
                                
                if filter_key[category]['value-dict']:
                    mylist = v[2]
                else:
                    mylist = [v[1]]                                 
                
                for filter in mylist:
                    fits = False
                                    
                    # if multiple category values 
                    if filter_key[category]['store-mode'] == 'a':
                                      
                        # go through the category values in the card
                        # at least one category value should match to the filter
                        for e in card[filter_key[category]['section']][category]:

                            # is the filter a DICT
                            if filter_key[category]['value-dict']:

                                # then correct match needed
                                if filter.lower() == e.lower():
                                    fits = True
                                    break
                                        
                            # NOT dict
                            else:
                                                
                                #NOT correct mach needed
                                if filter.lower() in e.lower():
                                    fits = True
                                    break

                    elif filter_key[category]['store-mode'] == 'v':
                                    
                        # is the filter a DICT
                        if filter_key[category]['value-dict']:

                            # then correct match needed
                            if filter.lower() == card[filter_key[category]['section']][category].lower():
                                fits = True
                                break

                        # NOT dict
                        else:
                                                
                            if operation == 'gte':
 
                                # then >= needed
                                if self.to_integer(filter) <= self.to_integer(card[filter_key[category]['section']][category]):
                                    fits = True
                                    break                                                

                            elif operation == 'lte': 
                                                
                                # then <= needed
                                if self.to_integer(filter) >= self.to_integer(card[filter_key[category]['section']][category]):
                                    fits = True
                                    break                                                     
                                                
                            #NOT correct mach needed
                            elif filter.lower() in card[filter_key[category]['section']][category].lower():
                                fits = True
                                break
                                    
                    elif filter_key[category]['store-mode'] == 't':
                                        
                        # is the filter a DICT
                        if filter_key[category]['value-dict']:

                            # then correct match needed
                            if filter.lower() == card[filter_key[category]['section']][config_ini['language']].lower():
                                fits = True
                                break
                                        
                        # NOT dict
                        else:
                                            
                            if filter.lower() in card[filter_key[category]['section']][config_ini['language']].lower():
                                fits = True
                                break                                
                                
                    # if at least one filter matches to a category values in the card
                    if fits:
                        break

            if not fits:
                break                
        
        return fits
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
    # ----------------------------
    #
    # Key Press Event: Enter/Space
    #
    # ----------------------------
    def keyPressEvent(self, event):

        #
        # Enter / Return / Space
        #
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter or event.key() == Qt.Key_Space:

            # Simulate a Mouse Press / Release Event on the Image
            if self.actual_card_holder.shown_card_list and len(self.actual_card_holder.shown_card_list) > 0:
                card=self.actual_card_holder.shown_card_list[0]
                if card.is_selected():
                    
                    event_press = QMouseEvent(QEvent.MouseButtonPress, QPoint(10,10), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
                    event_release = QMouseEvent(QEvent.MouseButtonRelease, QPoint(10,10), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)

                    layout=card.get_panel().get_layout()                    
                    card_panel = layout.itemAt(0).widget()
                    card_panel.card_image.mousePressEvent(event_press)
                    card_panel.card_image.mouseReleaseEvent(event_release)            

        #
        # Escape
        #
        if event.key() == Qt.Key_Escape:
            self.restore_previous_holder()

        event.ignore()
  

class LinkLabel(QLabel):
    def __init__(self, text, parent, index):
        QLabel.__init__(self, text, parent)
        self.parent = parent
        self.index = index        
        self.setFont(QFont( FONT_TYPE, HIERARCHY_TITLE_FONT_SIZE, weight=QFont.Bold if index else QFont.Normal))

    # Mouse Hover in
    def enterEvent(self, event):
        if self.index:
            QApplication.setOverrideCursor(Qt.PointingHandCursor)
        event.ignore()

    # Mouse Hover out
    def leaveEvent(self, event):
        if self.index:
            QApplication.restoreOverrideCursor()
        event.ignore()

    # Mouse Press
    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.index:
            self.parent.panel.restore_previous_holder(self.index)
        event.ignore()
    

# =========================================
# 
# This Class represents the title
#
# =========================================
#
class HierarchyTitle(QWidget):
    DEFAULT_BACKGROUND_COLOR = Qt.lightGray
    DEFAULT_BORDER_RADIUS = 10
    
    def __init__(self, parent, panel):
        QWidget.__init__(self, parent)

        self.panel = panel
        
        self_layout = QHBoxLayout(self)
        self_layout.setContentsMargins(5, 5, 5, 5)
        self_layout.setSpacing(0)
        #self_layout.setAlignment(Qt.AlignHCenter)
        self.setLayout(self_layout)

        self.text = QWidget(self)
        #self.text.setWordWrap(True)
        #self.text.setAlignment(Qt.AlignHCenter)
        #self.text.setFont(QFont( FONT_TYPE, HIERARCHY_TITLE_FONT_SIZE, weight=QFont.Bold))
        self_layout.addWidget(self.text)
        
        #self.text_layout = FlowLayout(self.text)
        self.text_layout = QVBoxLayout(self.text)
        self.text_layout.setContentsMargins(0, 0, 0, 0)
        self.text_layout.setSpacing(0)
        self.text.setLayout(self.text_layout)

        self.set_background_color(QColor(HierarchyTitle.DEFAULT_BACKGROUND_COLOR), False)
        self.set_border_radius(HierarchyTitle.DEFAULT_BORDER_RADIUS, False)
        
        self.card_holder_history = None
        self.actual_card_holder = None
        self.no_refresh = False
        
#    def resizeEvent(self, event):
#        if not self.no_refresh:
#            self.refresh_title()
#        event.accept()
    
    def refresh_title(self):
        if self.card_holder_history and self.actual_card_holder:
            self.set_title(self.card_holder_history, self.actual_card_holder)
    
    def set_title(self, card_holder_history, actual_card_holder):
        #self.blockSignals(True)
        #self.no_refresh = True

        clearLayout(self.text_layout)
 
        self.card_holder_history = card_holder_history
        self.actual_card_holder = actual_card_holder
 
        history = []
        for index, card in enumerate(card_holder_history):
            if card.title:
                label = LinkLabel(card.title, self, len(card_holder_history)-index)
                history.append(label)
       
        minimumWidth = 0
        max_width = self.size().width() - 2 * 5        
        self.create_one_line_container()
        
        for cw in history:
            
            minimumWidth += self.get_width_in_pixels(cw)
            if minimumWidth <= max_width:            
                self.add_to_one_line_container(cw)
            else:
                self.push_new_line_container()
                self.create_one_line_container()
                minimumWidth = 0
                self.add_to_one_line_container(cw)
            
            separator = QLabel(' > ')
            separator.setFont(QFont( FONT_TYPE, HIERARCHY_TITLE_FONT_SIZE, weight=QFont.Normal ))
            minimumWidth += self.get_width_in_pixels(separator)
            if minimumWidth <= max_width:            
                self.add_to_one_line_container(separator)
            else:
                self.push_new_line_container()
                self.create_one_line_container()
                minimumWidth = 0
                self.add_to_one_line_container(separator)
                                       
        notLinkTitle = LinkLabel(actual_card_holder.title, self, 0)
        minimumWidth += self.get_width_in_pixels(notLinkTitle)
        if minimumWidth <= max_width:            
            self.add_to_one_line_container(notLinkTitle)
        else:
            self.push_new_line_container()
            self.create_one_line_container()
            minimumWidth = 0
            self.add_to_one_line_container(notLinkTitle)
        self.push_new_line_container()
       



    def create_one_line_container(self):
        self.one_line_container = QWidget(self)
        self.one_line_container_layout = QHBoxLayout(self.one_line_container)
        self.one_line_container_layout.setContentsMargins(0, 0, 0, 0)
        self.one_line_container_layout.setSpacing(0)
        self.one_line_container.setLayout(self.one_line_container_layout)
        self.one_line_container_layout.setAlignment(Qt.AlignHCenter)

    def add_to_one_line_container(self, cw):
        self.one_line_container_layout.addWidget(cw)
        
    def push_new_line_container(self):
        self.text_layout.addWidget(self.one_line_container)
        
    def get_width_in_pixels(self, cw):
        initialRect = cw.fontMetrics().boundingRect(cw.text());
        improvedRect = cw.fontMetrics().boundingRect(initialRect, 0, cw.text());   
        return improvedRect.width()
        
        
    def set_background_color(self, color, update=False):
        self.background_color = color
        self.text.setStyleSheet('background: ' + color.name()) 
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
#           Button Control
#           Fast Search Control
#           Advanced Search Control
#
# =========================================
class ControlPanel(QWidget):
    def __init__(self, gui):
        super().__init__(gui)
       
        self.gui = gui
        
        self_layout = QVBoxLayout(self)
        self.setLayout(self_layout)
        
        # controls the distance between the MainWindow and the added container: scrollContent
        self_layout.setContentsMargins(3, 3, 3, 3)
        self_layout.setSpacing(5)

        # ----------------------
        #
        # Control Buttons Holder
        #
        # ----------------------
        self.control_buttons_holder = ControlButtonsHolder(self)
        self_layout.addWidget(self.control_buttons_holder)
        
        # ------------------
        #
        # Fast Filter Holder
        #
        # ------------------
        self.fast_filter_holder = FastFilterHolder()
        self.fast_filter_holder.changed.connect(self.fast_filter_on_change)
        self.fast_filter_holder.clear_clicked.connect(self.fast_filter_clear_on_change)
        self.fast_filter_holder.setHidden(True)        
        self_layout.addWidget(self.fast_filter_holder)

        # ----------------------
        #
        # Advanced Filter Holder
        #
        # ----------------------
        self.advanced_filter_holder = AdvancedFilterHolder(self)
        self.advanced_filter_holder.filter_clicked.connect(self.advanced_filter_filter_on_click)
        self.advanced_filter_holder.clear_clicked.connect(self.advanced_filter_clear_on_click)
        self.advanced_filter_holder.setHidden(True)
        self_layout.addWidget(self.advanced_filter_holder)

        # Listeners
        self.back_button_listener = None
        self.fast_filter_listener = None
        self.advanced_filter_listener = None

    def refresh_label(self):
        self.fast_filter_holder.refresh_label()
        self.advanced_filter_holder.refresh_label()

    def set_back_button_method(self, method):
        self.control_buttons_holder.back_button_method = method
        
    def set_fast_filter_listener(self, listener):
        self.fast_filter_listener = listener
 
    # ----------------------------------
    #
    # a value changed in the fast filter
    # 
    # ----------------------------------
    def fast_filter_on_change(self):
        """
        --- Fast Filter on Change ---
        
        If there is no listener then Filters the Cards
        """
        if self.fast_filter_listener:
            self.gui.filter_the_cards()
            
    def fast_filter_clear_on_change(self):
        """
        --- Fast Filter Clear on Change ---
        
        -Clear all the fields
        -Filter the cards
        """
        self.fast_filter_listener = None
        self.fast_filter_holder.clear_fields()
        self.fast_filter_listener = self.gui
        self.fast_filter_on_change()
    
    def get_fast_filter_holder(self):
        return self.fast_filter_holder

    # ---------------------------------
    #
    # advanced filter clicked
    #
    # ---------------------------------
    def advanced_filter_filter_on_click(self):
        """
        --- Advanced Filter FILTER on Click
        
        The Filter button was clicked on the Advanced Filter panel
        -filter the cards
        """
        self.gui.filter_the_cards()
        
    def advanced_filter_clear_on_click(self):
        """
        --- Advanced Filter CLEAR on Click ---
        
        The CLEAR button was clicked on the Advanced Filter panel
        -clear the fields
        -filter the cards by cleared filter
        """
        self.advanced_filter_holder.clear_fields()
        self.gui.filter_the_cards()

    def get_advanced_filter_holder(self):
        return self.advanced_filter_holder

        
def main():    
    app = QApplication(sys.argv)
    
    ex = GuiAkoTeka()
    ex.startCardHolder()
    sys.exit(app.exec_())
    
    
