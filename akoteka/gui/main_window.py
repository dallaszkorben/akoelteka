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

    # --------------------------
    #
    # Start CardHolder
    #
    # --------------------------
    def startCardHolder(self):

        # Create the first Card Holder - 
        #self.go_down_in_hierarchy( [], "" )
        self.go_down_in_hierarchy() 

        # Retreive the media path
        paths = [config_ini['media_path']]
        
        # Start to collect the Cards from the media path
        self.actual_card_holder.startCardCollection(paths)        

    # --------------------------------------------------------------
    #
    # Go deeper in the hierarchy
    #
    # card_descriptor_structure The NOT Filtered card hierarchy list
    #                           on the recent level
    # title                     The title what whould be shown above
    #                           the CardHolder
    # save                      It controls to save the CardHolder
    #                           into the history list
    #                           collecting_finish uses it with False
    # --------------------------------------------------------------
    def go_down_in_hierarchy( self, card_descriptor_structure=None, title=None, save=True ):

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

    # -------------------------
    #
    # Come up in the hierarchy
    #
    # -------------------------
    def restore_previous_holder(self, steps=1):
        
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
            
            # select the Card which was selected to enter
            self.actual_card_holder.select_actual_card()
            
            # Make the CardHolder to be in Focus
            self.actual_card_holder.setFocus()
         

    # ------------------
    # Collecting Started
    # ------------------
    def collecting_start(self):
        """
        Indicates that the CardCollection process started.
        The CardHolder calls this method
        Jobs to do:
            -Hide the title
        """
        self.hierarchy_title.setHidden(True)

    # -------------------
    # Collecting Finished
    # -------------------
    def collecting_finish(self, card_holder, card_descriptor_structure):
        """
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
            self.go_down_in_hierarchy(card_holder.card_descriptor_list[0]['extra']["orig-sub-cards"], card_holder.card_descriptor_list[0]['title'][config_ini['language']], save=False )

    # ----------------------------------------------------------
    #
    # Calculates the Y coordinate of a Card using reverse index
    #
    # ----------------------------------------------------------
    def get_y_coordinate_by_reverse_index(self, reverse_index, diff_to_max):
        raw_pos = (reverse_index + diff_to_max) * (reverse_index + diff_to_max)
        offset = diff_to_max * diff_to_max
        return (raw_pos - offset) * 8
        #return reverse_index * 220
    
    # -----------------------------------------------
    #
    # Calculates the X coordinate of a Card by index
    #
    # -----------------------------------------------
    def get_x_offset_by_index(self, index):
        return index * 4       

    def collect_cards(self, paths):
        cdl = collect_cards(paths)
        
        # Preparation for collecting the filtered_card_structure and filters
        filtered_card_structure = []
        filter_hit_list = {
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
            "best": set(),
        }
        filter_unconditional_list = {
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
            "best": set(),
        }
        self.generate_filtered_card_structure(cdl, filtered_card_structure, filter_hit_list, filter_unconditional_list)
        
        return filtered_card_structure
    
    # --------------------
    #
    # Generates a new Card
    #
    # --------------------
    def get_new_card(self, card_data, local_index, index):

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
        self.actual_card_holder.fillUpCardHolderByDescriptor(filtered_card_structure)

    # ----------------
    # Set-up Filters
    # ----------------
    def set_up_filters(self, card_descriptor_structure):
        
        #self.get_advanced_filter_holder().set_title('12')
        title = self.get_advanced_filter_holder().title_filter.getValue()
        
        """
        Based on the list that received as parameter, 
        it selects the possible filter elements
        """
        
        # ###################################
        # Turn OFF the listener to the Filter
        # ###################################
        self.set_fast_filter_listener(None)
        
        # ####################################
        # Save the recent state of the filters
        # ####################################
        fast_filters = {
            "title": "",
            "genre": "",
            "theme": "",
            "director": "",
            "actor": "",
            "favorite": "",
            "new": "",
            "best": ""
        }
        advanced_filters = {
            "title": "",
            "genre": "",
            "theme": "",
            "director": "",
            "actor": "",
            "sound": "",
            "sub": "",
            "country": "",
            "length_from": "",
            "length_to": "",
            "year_from": "",
            "year_to": "",            
        }        
        for category, value in self.get_fast_filter_holder().get_filter_selection().items():            
            if value != None and value != "":
                fast_filters[category] = value

        for category, value in self.get_advanced_filter_holder().get_filter_selection().items():            
            if value[0] != None and value[0] != "":
                advanced_filters[category] = value[0]
        
        # #############
        # Setup Filters
        # #############

        # Preparation for collecting the filtered_card_structure and filters
        filtered_card_structure = []
        filter_hit_list = {
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
            "best": set(),
        }
        filter_unconditional_list = {
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
            "best": set(),
            "year": set(),
        }
        
        self.generate_filtered_card_structure(card_descriptor_structure, filtered_card_structure, filter_hit_list, filter_unconditional_list)

        # Fill up TITLE
        # fast filter - dropdown
        self.get_fast_filter_holder().clear_title()
        self.get_fast_filter_holder().add_title("")
        for element in sorted( filter_hit_list['title'], key=cmp_to_key(locale.strcoll) ):
            self.get_fast_filter_holder().add_title(element)
        # advanced filter
        self.get_advanced_filter_holder().clear_title()            
        for element in sorted( filter_unconditional_list['title'], key=cmp_to_key(locale.strcoll) ):
            self.get_advanced_filter_holder().add_title(element)
        
        # Fill up GENRE 
        # fast filter - dropdown
        self.get_fast_filter_holder().clear_genre()
        self.get_fast_filter_holder().add_genre("", "")
        for element in sorted([(_("genre_" + e),e) for e in filter_hit_list['genre']], key=lambda t: locale.strxfrm(t[0]) ):            
            self.get_fast_filter_holder().add_genre(element[0], element[1])
        # advanced filter
        self.get_advanced_filter_holder().clear_genre()            
        for element in sorted([(_("genre_" + e),e) for e in filter_unconditional_list['genre']], key=lambda t: locale.strxfrm(t[0]) ):            
            self.get_advanced_filter_holder().add_genre(element[0], element[1])        
        
        # Fill up THEME 
        # fast filter - dropdown
        self.get_fast_filter_holder().clear_theme()
        self.get_fast_filter_holder().add_theme("", "")
        for element in sorted([(_("theme_" + e), e) for e in filter_hit_list['theme']], key=lambda t: locale.strxfrm(t[0]) ):            
            self.get_fast_filter_holder().add_theme(element[0], element[1])
        # advanced filter
        self.get_advanced_filter_holder().clear_theme()
        for element in sorted([(_("theme_" + e), e) for e in filter_unconditional_list['theme']], key=lambda t: locale.strxfrm(t[0]) ):            
            self.get_advanced_filter_holder().add_theme(element[0], element[1])

        # Fill up DIRECTOR 
        # fast filter - dropdown
        self.get_fast_filter_holder().clear_director()
        self.get_fast_filter_holder().add_director("")
        for element in sorted( filter_hit_list['director'], key=cmp_to_key(locale.strcoll) ):
            self.get_fast_filter_holder().add_director(element)
        # advanced filter
        self.get_advanced_filter_holder().clear_director()            
        for element in sorted( filter_unconditional_list['director'], key=cmp_to_key(locale.strcoll) ):
            self.get_advanced_filter_holder().add_director(element)

        # Fill up ACTOR 
        # falst filter - dropdown
        self.get_fast_filter_holder().clear_actor()
        self.get_fast_filter_holder().add_actor("")
        for element in sorted( filter_hit_list['actor'], key=cmp_to_key(locale.strcoll) ):
            self.get_fast_filter_holder().add_actor(element)
        # advanced filter
        self.get_advanced_filter_holder().clear_actor()            
        for element in sorted( filter_unconditional_list['actor'], key=cmp_to_key(locale.strcoll) ):
            self.get_advanced_filter_holder().add_actor(element)
        
        # Fill up SOUND
        self.get_advanced_filter_holder().clear_sound()
        #self.get_advanced_filter_holder().add_sound("", "")
        for element in sorted([(_("lang_long_" + e), e) for e in filter_unconditional_list['sound']], key=lambda t: locale.strxfrm(t[0]) ):            
            self.get_advanced_filter_holder().add_sound(element[0], element[1])

        # Fill up SUBTITLE
        self.get_advanced_filter_holder().clear_sub()
        #self.get_advanced_filter_holder().add_sub("", "")
        for element in sorted([(_("lang_long_" + e), e) for e in filter_unconditional_list['sub']], key=lambda t: locale.strxfrm(t[0]) ):            
            self.get_advanced_filter_holder().add_sub(element[0], element[1])

        # Fill up COUNTRY
        self.get_advanced_filter_holder().clear_country()
        #self.get_advanced_filter_holder().add_country("", "")
        for element in sorted([(_("country_long_" + e), e) for e in filter_unconditional_list['country']], key=lambda t: locale.strxfrm(t[0]) ):            
            self.get_advanced_filter_holder().add_country(element[0], element[1])
       
        # Fill up YEAR from/to
        self.get_advanced_filter_holder().clear_year()
        #self.get_advanced_filter_holder().add_year("")
        for element in sorted( filter_unconditional_list['year'], key=cmp_to_key(locale.strcoll) ):
            self.get_advanced_filter_holder().add_year(element)
        
        # Fill up LENGTH from/to
        self.get_advanced_filter_holder().clear_length()
        #self.get_advanced_filter_holder().add_length("")
        for element in sorted( [str(int(spl[-2])).rjust(1) + ":" + str(int(spl[-1])).zfill(2) for spl in [l.split(":") for l in filter_unconditional_list['length'] if ':' in l ] if all(c.isdigit() for c in spl[-1] ) and all(c.isdigit() for c in spl[-2] )], key=cmp_to_key(locale.strcoll) ):
            self.get_advanced_filter_holder().add_length(element)

        # ####################
        # Reselect the Filters
        # ####################
        self.get_fast_filter_holder().select_title(fast_filters["title"])
        self.get_fast_filter_holder().select_genre(fast_filters["genre"])
        self.get_fast_filter_holder().select_theme(fast_filters["theme"])
        self.get_fast_filter_holder().select_director(fast_filters["director"])
        self.get_fast_filter_holder().select_actor(fast_filters["actor"])
        
        self.get_advanced_filter_holder().set_title(advanced_filters['title'])
        self.get_advanced_filter_holder().set_genre(advanced_filters['genre'])
        self.get_advanced_filter_holder().set_theme(advanced_filters['theme'])
        self.get_advanced_filter_holder().set_director(advanced_filters['director'])
        self.get_advanced_filter_holder().set_actor(advanced_filters['actor'])
        self.get_advanced_filter_holder().select_sound(advanced_filters['sound'])
        self.get_advanced_filter_holder().select_sub(advanced_filters['sub'])
        self.get_advanced_filter_holder().select_country(advanced_filters['country'])
        
        # #######################################
        # Turn back ON the listener to the Filter
        # #######################################
        self.set_fast_filter_listener(self)

        return filtered_card_structure
    
    
    # ================================
    # 
    # Generates Filtered CardStructure
    #
    # ================================   
    def generate_filtered_card_structure(self, card_structure, filtered_card_structure, filter_hit_list, filter_unconditional_list):
        """
        This method serves a dual task:
            -Based on the Filter it generates a new, filtered list: filtered_card_structure
            -Collects the new Filter, based on the filtered list:   filter_hit_list
        """
        mediaFits = False
        collectorFits = False
            
        # through the SORTED list
        for crd in sorted(card_structure, key=lambda arg: arg['title'][config_ini['language']], reverse=False):
            
            card = {}
            card['title'] = crd['title']
            card['storyline'] = crd['storyline']
            card['general'] = crd['general']
            card['rating'] = crd['rating']
            card['links'] = crd['links']

            card['extra'] = {}            
            card['extra']['image-path'] = crd['extra']['image-path']
            card['extra']['media-path'] = crd['extra']['media-path']
            card['extra']['recent-folder'] = crd['extra']['recent-folder']            
            card['extra']['sub-cards'] = []
            card['extra']['orig-sub-cards'] = crd['extra']['sub-cards']

            # in case of MEDIA CARD
            if crd['extra']['media-path']:

#                print('title: ', card['title']['hu'])

                fits = True

                # FAST FILTER is visible
                if not self.control_panel.fast_filter_holder.isHidden():                 
                
                    # go through the FAST FILTERS and decide if the Card is filtered
                    for category, value in self.get_fast_filter_holder().get_filter_selection().items():
                 
                        # if the specific filter is set
                        if value != None and value != "":

                            if filter_key[category]['store-mode'] == 'v':
                                if value != crd[filter_key[category]['section']][category]:
                                    fits = False
                                    break
                                
                            elif filter_key[category]['store-mode'] == 'a':
                                if value not in crd[filter_key[category]['section']][category]:
                                    fits = False
                                    break
                                
                            elif filter_key[category]['store-mode'] == 't':
                                if value != card[filter_key[category]['section']][config_ini['language']]:
                                    fits = False
                                    break
                                
                            else:
                                fits = False
                                break

                # ADVANCED FILTER is visible
                elif not self.control_panel.advanced_filter_holder.isHidden(): 

                    # go through the ADVANCED FILTERS by Categories and decide if the Card is filtered
                    for category, v in self.get_advanced_filter_holder().get_filter_selection().items():
                        
#                        print('  category: ', category, 'typed: ', v[0], ', index: ', v[1], ', get: ', self.get_advanced_filter_holder().theme_filter.getValue() )
                        
                        # do I want to check this Category match
                        if v[0]:                            
                            
                            fits = False
                            
                            # go throug all filters in the category
                            for filter in v[1] if filter_key[category]['value-dict'] else [v[0]]:
                            
#                                print('    filter: ', filter)
                            
                                fits = False
                                    
                                # if multiple category values 
                                if filter_key[category]['store-mode'] == 'a':
                                      
#                                    print('    values in the card: ', crd[filter_key[category]['section']][category]) 
                                    # go through the category values in the card
                                    # at least one category value should match to the filter
                                    for e in crd[filter_key[category]['section']][category]:

                                        #print('    value in the card: ', e,  ', filter:', filter )

                                        # is the filter a DICT
                                        if filter_key[category]['value-dict']:

                                            # then correct match needed
                                            if filter.lower() == e.lower():
                                                fits = True
#                                                print('    break')
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
                                        if filter.lower() == crd[filter_key[category]['section']][category].lower():
                                            fits = True
                                            break

                                    # NOT dict
                                    else:
                                                
                                        #NOT correct mach needed
                                        if filter.lower() in crd[filter_key[category]['section']][category].lower():
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

#                        print('    all filter in category fits:', fits) 
#                        print()
                        if not fits:
                            #print('not fits, break', value, crd[filter_key[category]['section']][category])
                            break

#--                

                # Fill up the filter lists: unconditional/hit
                for category, value in self.get_fast_filter_holder().get_filter_selection().items():
                    if filter_key[category]['store-mode'] == 'v':
                        if card[filter_key[category]['section']][category]:
                            filter_unconditional_list[category].add(card[filter_key[category]['section']][category])
                            if fits:
                                filter_hit_list[category].add(card[filter_key[category]['section']][category])
                                
                    elif filter_key[category]['store-mode'] == 'a':
                        for cat in card[filter_key[category]['section']][category]:
                            if cat.strip():
                                filter_unconditional_list[category].add(cat.strip())
                                if fits:
                                    filter_hit_list[category].add(cat.strip())
                
                    elif filter_key[category]['store-mode'] == 't':
                        filter_unconditional_list['title'].add(card[filter_key[category]['section']][config_ini['language']])
                        if fits:
                            filter_hit_list['title'].add(card[filter_key[category]['section']][config_ini['language']])
                
                if fits:
                    filtered_card_structure.append(card)                    
                    mediaFits = True
   
#--
                    
            # in case of COLLECTOR CARD
            else:                     

 #               print('--')
                     
                # then it depends on the next level
                fits = self.generate_filtered_card_structure(crd['extra']['sub-cards'], card['extra']['sub-cards'], filter_hit_list, filter_unconditional_list)
                
                if fits:
                    filtered_card_structure.append(card)
                    collectorFits = True
        
        
        return (mediaFits or collectorFits)
  
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
        self.fast_filter_holder.setHidden(True)        
        self_layout.addWidget(self.fast_filter_holder)

        # ----------------------
        #
        # Advanced Filter Holder
        #
        # ----------------------
        self.advanced_filter_holder = AdvancedFilterHolder(self)
        self.advanced_filter_holder.clicked.connect(self.advanced_filter_on_click)
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
        if self.fast_filter_listener:
            self.gui.filter_the_cards()
    
    def get_fast_filter_holder(self):
        return self.fast_filter_holder

    # ---------------------------------
    #
    # advanced filter clicked
    #
    # ---------------------------------
    def advanced_filter_on_click(self):
        self.gui.filter_the_cards()

    def get_advanced_filter_holder(self):
        return self.advanced_filter_holder

        
def main():   
    
    app = QApplication(sys.argv)
    ex = GuiAkoTeka()
    ex.startCardHolder()
    sys.exit(app.exec_())
    
    
