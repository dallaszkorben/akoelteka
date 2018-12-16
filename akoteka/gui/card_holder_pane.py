import sys
import os
import json
from subprocess import call
from threading import Thread
from pkg_resources import resource_string, resource_filename
from functools import cmp_to_key
import locale

from PyQt5.QtCore import pyqtSignal  

from akoteka.accessories import filter_key

from akoteka.handle_property import Property

from akoteka.gui.glob import *
from akoteka.gui.glob import _
from akoteka.gui import glob

#from akoteka.gui.glob import media_path_film
from akoteka.gui.glob import media_player_video
from akoteka.gui.glob import media_player_video_param

PICTURE_WIDTH = 190
PICTURE_HEIGHT = 160
RATE_WIDTH = 30

COLOR_CARD = "#b3d4c9"
COLOR_CARD_BORDER_MEDIA = "#b3d4c9"
COLOR_CARD_BORDER_CONTAINER = "#0e997a"
COLOR_CARD_HOLDER_CARDS = "#3f6b61"
COLOR_CARD_HOLDER_MAIN = "#73948d"

# ================================================
# 
# This Class represents a Card Holder of the Cards
#
# ================================================
#
# The title_layer stores the Title and the card_holder_canvas
# The card_holder_layout stores the Cards
#
#            parent,
#            previous_holder,
#            hierarchy,
#            paths
#
class CardHolder( QLabel ):
    
    card_array = None
    
    def __init__(self, parent, recent_card_structure, title_hierarchy):
        super().__init__()

        self.parent = parent
        self.title_hierarchy = title_hierarchy
        self.recent_card_structure = recent_card_structure

        # -------------
        #
        # Main Panel
        #
        # ------------
        self.self_layout = QVBoxLayout(self)
        self.setLayout(self.self_layout)
        # controls the distance between the MainWindow and the added container: scrollContent
        # order: left, top, right, bottom
        self.self_layout.setContentsMargins(9,9,9,9)     
        self.self_layout.setSpacing(10)
        self.setStyleSheet('background: ' + COLOR_CARD_HOLDER_MAIN)   

        # -------------
        #
        # Title
        #
        # ------------
        title = QLabel()
        title.setFont(QFont( "Comic Sans MS", 23, weight=QFont.Bold))
        title.setAlignment(Qt.AlignHCenter)
        
        title.setText(self.title_hierarchy)
        self.self_layout.addWidget( title )        
        
        # -------------
        #
        # Card Holder Panel
        #
        # ------------
        self.card_holder_canvas = CardHolderPanel()
        self.card_holder_layout = self.card_holder_canvas.getLayout()
        
        # Basically the Canvas Holder is Hidden
        self.card_holder_canvas.setHidden(True)
        
        self.self_layout.addWidget(self.card_holder_canvas)
        self.self_layout.addStretch(1)
        
        # -------------
        #
        # Cards
        #
        # ------------
        self.fill_up_card_holder()
        
        # ----------------------
        #
        # Listeners registration
        #
        # ----------------------
        self.parent.set_back_button_listener(self)
  
    def show_card_holder(self):
        self.card_holder_canvas.setHidden(False)
        
    def hide_card_holder(self):
        self.card_holder_canvas.setHidden(True)
        
    def remove_cards(self):
        for i in reversed(range(self.card_holder_layout.count())): 
            widgetToRemove = self.card_holder_layout.itemAt(i).widget()
        
            # remove it from the layout list
            self.card_holder_layout.removeWidget(widgetToRemove)
            
            # remove it from the gui
            widgetToRemove.setParent(None)
            
        self.hide_card_holder()

    def get_title_hierarchy(self):
        return self.title_hierarchy

    # ----------------------------------
    #
    # Clicked on the Collector's picture
    #
    # Go down in the hierarchy
    #
    # ----------------------------------
    def go_deeper(self, card_structure, card_title):     
        self.parent.add_holder(card_structure, card_title)
        
    # ------------------------
    #
    # Back button pressed
    #
    # Come up in the hierarchy
    #
    # ------------------------
    def go_back(self):
        self.parent.restore_previous_holder()

    # -------------------------------------
    # 
    # This method fills up the card_holder
    # 
    # -------------------------------------
    def fill_up_card_holder(self, recent_card_structure = []):

        self.parent.set_filter_listener(None)

        # it happens in the first time called from main_window.py
        if recent_card_structure:
            self.recent_card_structure = recent_card_structure

        # produces the Filtered_Card_Structure out of recent_card_structure
        filtered_card_structure = json.loads('[]')
        filter_hit_list = {
            "genre": set(),
            "theme": set(),
            "director": set(),
            "actor": set(),
            "favorite": set(),
            "new": set(),
            "best": set()
        }
        self.generate_filtered_card_structure(self.recent_card_structure, filtered_card_structure, filter_hit_list)
     
        # ------------------------------------
        #
        # Save the recent state of the filters
        #
        # ------------------------------------
        filters = {
            "genre": "",
            "theme": "",
            "director": "",
            "actor": "",
            "favorite": "",
            "new": "",
            "best": ""
        }
        for category, value in self.parent.get_filter_holder().get_filter_selection().items():            
            if value != None and value != "":
                filters[category] = value
        
        # Remove all Cards and hide the CardHolder
        self.remove_cards()

        #
        # Show the MEDIA CARDs / COLLECTOR CARDs on the recent level        
        #
        is_card = False

        for crd in filtered_card_structure:
        #for crd in self.recent_card_structure:            
            #print(crd['recent-folder'])

            card = Card(self)
            card.set_image_path( crd["extra"]["image-path"] )
            
            #card.set_sub_cards( crd["sub-cards"] )
            card.set_sub_cards( crd["extra"]["orig-sub-cards"] )
            card.set_media_path( crd["extra"]["media-path"] )
            card.set_title( crd["title"][glob.language] )

            #fits = True
            
            # if MEDIA CARD
            if crd["extra"]["media-path"]:
                    
                card.add_info_line( _("title_director"), ", ".join( [ d for d in crd["general"]["director"] ] ) )
                card.add_info_line( _("title_actor"), ", ".join( [ a for a in crd["general"]["actor"] ] ) )
                card.add_info_line( _("title_genre"), ", ".join( [ _("genre_"+g) if g else "" for g in crd["general"]["genre"] ] ) )
                card.add_info_line( _("title_theme"), ", ".join( [ _("theme_"+a) if a else "" for a in crd["general"]["theme"] ] ) )

                card.add_element_to_collector_line( _("title_year"), crd["general"]["year"])
                card.add_element_to_collector_line( _("title_length"), crd["general"]["length"])
                card.add_element_to_collector_line( _("title_country"), ", ".join( [ dic._("country_" + a) for a in crd["general"]["country"] ]) )
                   
                # initialize the rating buttons
                card.set_rating(crd['rating'])
                card.set_folder(crd['extra']['recent-folder'])
            
            # Show the CARD on the CARD HOLDER
            self.card_holder_layout.addWidget( card )
            
            # There is at least ONE CARD (MEDIA/COLLECTOR)
            is_card = True
        
        # Change filter according to the Cards
        self.parent.get_filter_holder().clear_genre()
        self.parent.get_filter_holder().add_genre("", "")
        for element in sorted([(_("genre_" + e),e) for e in filter_hit_list['genre']], key=lambda t: locale.strxfrm(t[0]) ):            
            self.parent.get_filter_holder().add_genre(element[0], element[1])
        
        self.parent.get_filter_holder().clear_theme()
        self.parent.get_filter_holder().add_theme("", "")
        for element in sorted([(_("theme_" + e), e) for e in filter_hit_list['theme']], key=lambda t: locale.strxfrm(t[0]) ):            
            self.parent.get_filter_holder().add_theme(element[0], element[1])

        self.parent.get_filter_holder().clear_director()
        self.parent.get_filter_holder().add_director("")
        for element in sorted( filter_hit_list['director'], key=cmp_to_key(locale.strcoll) ):
            self.parent.get_filter_holder().add_director(element)

        self.parent.get_filter_holder().clear_actor()
        self.parent.get_filter_holder().add_actor("")
        for element in sorted( filter_hit_list['actor'], key=cmp_to_key(locale.strcoll) ):
            self.parent.get_filter_holder().add_actor(element)
        
        # If there was at least one Card
        if is_card:

            # then the CardHolder will be show
            self.show_card_holder()
            
        # --------------------
        #
        # Reselect the Filters
        #
        # --------------------
        self.parent.get_filter_holder().select_genre(filters["genre"])
        self.parent.get_filter_holder().select_theme(filters["theme"])
        self.parent.get_filter_holder().select_director(filters["director"])
        self.parent.get_filter_holder().select_actor(filters["actor"])
        
        self.parent.set_filter_listener(self)



    # ================================
    # 
    # Generates Filtered CardStructure
    #
    #
    # filter_hit_list = {
    #   "genre": set(),
    #   "theme": set(),
    #   "director": set(),
    #   "actor": set(),
    #   "favorite": set(),
    #   "new": set(),
    #   "best": set()
    # }
    # ================================   
    def generate_filtered_card_structure(self, card_structure, filtered_card_structure, filter_hit_list):

        mediaFits = False
        collectorFits = False
            
        for crd in card_structure:            
            
            card = {}
            card['title'] = crd['title']
            card['general'] = crd['general']
            card['rating'] = crd['rating']

            card['extra'] = {}            
            card['extra']['image-path'] = crd['extra']['image-path']
            card['extra']['media-path'] = crd['extra']['media-path']
            card['extra']['recent-folder'] = crd['extra']['recent-folder']            
            card['extra']['sub-cards'] = json.loads('[]')
            card['extra']['orig-sub-cards'] = crd['extra']['sub-cards']

            # in case of MEDIA CARD
            if crd['extra']['media-path']:

                fits = True
                
                # go through the filters
                for category, value in self.parent.get_filter_holder().get_filter_selection().items():
            
                    # if the specific filter is set
                    if value != None and value != "":

                        if filter_key[category]['store-mode'] == 'v':
                            if value != crd[filter_key[category]['section']][category]:
                                fits = False
                                
                        elif filter_key[category]['store-mode'] == 'a':
                            if value not in crd[filter_key[category]['section']][category]:
                                fits = False
                        else:
                            fits = False

                # let's keep this MEDIA CARD as it fits
                if fits:

                    # Collect the filters
                    for category, value in self.parent.get_filter_holder().get_filter_selection().items():
                        if filter_key[category]['store-mode'] == 'v':
                            if card[filter_key[category]['section']][category]:
                                filter_hit_list[category].add(card[filter_key[category]['section']][category])
                                
                        elif filter_key[category]['store-mode'] == 'a':
                            for cat in card[filter_key[category]['section']][category]:
                                if cat.strip():
                                    filter_hit_list[category].add(cat.strip())
                    
                    filtered_card_structure.append(card)                    
                    mediaFits = True
                    
            # in case of COLLECTOR CARD
            else:                     
                     
                # then it depends on the next level
                fits = self.generate_filtered_card_structure(crd['extra']['sub-cards'], card['extra']['sub-cards'], filter_hit_list)
                
                if fits:
                    filtered_card_structure.append(card)
                    collectorFits = True
        
        return (mediaFits or collectorFits)
                    
            
                
                

class CardHolderPanel( QLabel ):
    def __init__(self):
        super().__init__()

        # -------------
        #
        # Main Panel
        #
        # ------------
        #self_layout = QVBoxLayout(self)
        #self.setLayout(self_layout)
        ## controls the distance between the MainWindow and the added container: scrollContent
        ## order: left, top, right, bottom
        #self_layout.setContentsMargins(9,9,9,9)     
        #self_layout.setSpacing(10)
        #self.setStyleSheet('background: ' + COLOR_CARD_HOLDER_MAIN)   
      
        self.self_layout = QVBoxLayout(self)
        self.setLayout(self.self_layout)
        self.self_layout.setContentsMargins(12,12,12,12)  
        self.self_layout.setSpacing(5)
        #self.setStyleSheet('background: ' + COLOR_CARD_HOLDER_CARDS)   
        
        self.borderRadius = 10

    def getLayout(self):
        return self.self_layout

    def paintEvent(self, event):

        s = self.size()
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing, True)
        qp.setBrush( QColor( COLOR_CARD_HOLDER_CARDS ))

        qp.drawRoundedRect(0, 0, s.width(), s.height(), self.borderRadius, self.borderRadius)
        qp.end()

# =========================================
# 
# This Class represents a Card of a movie
#
# =========================================
#
# It contains an image and many characteristics of a movie on a card
#
class Card(QLabel):
    
    def __init__(self, card_holder):
        super().__init__()
        
        self.card_holder = card_holder

        self_layout = QHBoxLayout(self)
        self_layout.setContentsMargins(8, 8, 8, 8)
        self.setLayout( self_layout )
        self.setStyleSheet( 'background: ' +  COLOR_CARD_HOLDER_CARDS)
        
        card_panel = QLabel()
        self_layout.addWidget(card_panel)
        card_layout = QHBoxLayout(card_panel)
        card_layout.setContentsMargins(0, 0, 0, 0)
        # gap between the card, an the elements of the card - horizontal gap
        card_layout.setSpacing(10)
        card_panel.setLayout( card_layout )
        card_panel.setStyleSheet('background: ' + COLOR_CARD)

        #
        # Containers in the Card
        #
        self.card_image = CardImage()
        card_layout.addWidget( self.card_image )
        self.card_information = CardInformation()
        card_layout.addWidget( self.card_information )
        self.card_rating = CardRating()
        card_layout.addWidget( self.card_rating )
 
        self.borderRadius = 5
       
    def mousePressEvent(self, event):
        
        # Play media
        if self.get_media_path():
            
            switch_list = media_player_video_param.split(" ")
            param_list = []
            param_list.append(media_player_video)
            param_list += switch_list
            param_list.append(self.get_media_path())


            thread = Thread(target = call, args = (param_list, ))
            thread.start()
            #call( param_list )
            
        else:
            self.card_holder.go_deeper(self.get_sub_cards(), self.card_information.get_title() )
       
    def set_image_path( self, image_path ):
        self.card_image.set_image_path( image_path )
        
    def set_media_path( self, media_path ):
        self.card_image.set_media_path( media_path )
        
        # if it is a direct card to a media
#        if self.card_image.get_media_path():
#            self.setStyleSheet('background: ' + COLOR_CARD_BORDER_MEDIA)
#        else:
#            self.setStyleSheet('background: ' + COLOR_CARD_BORDER_CONTAINER)

    def get_media_path( self ):
        return self.card_image.get_media_path( )
    
    def set_sub_cards( self, sub_cards ):
        self.card_image.set_sub_cards( sub_cards )
        
    def get_sub_cards( self ):
        return self.card_image.get_sub_cards()
        
    def set_title(self, title):
        self.card_information.set_title(title)
        
    def add_info_line( self, label, value ):
        self.card_information.add_info_line( label, value )
        
    def add_element_to_collector_line( self, label, value ):
        self.card_information.add_element_to_collector_line( label, value )
        
    def set_rating( self, rating ):
        self.card_rating.set_rating(rating)
        
    def set_folder( self, folder ):
        self.card_rating.set_folder(folder)
        
    def paintEvent(self, event):
        # get current window size
        s = self.size()
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing, True)
        
        # if it is a direct card to a media
        if self.card_image.get_media_path():
            #self.setStyleSheet('background: ' + COLOR_CARD_BORDER_MEDIA)
            #qp.setPen(self.foregroundColor)
            qp.setBrush( QColor(COLOR_CARD_BORDER_MEDIA))
            
            # Show the RATING section
            self.card_rating.setHidden(False)

        else:
#            self.setStyleSheet('background: ' + COLOR_CARD_BORDER_CONTAINER)        
            qp.setBrush( QColor(COLOR_CARD_BORDER_CONTAINER ))
            
            # Hide the RATING section
            self.card_rating.setHidden(True)

        # Create ROUNDED corner to the CARD
        qp.drawRoundedRect(0, 0, s.width(), s.height(), self.borderRadius, self.borderRadius)
        qp.end()
        
        
        

        
class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)

class QVLine(QFrame):
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)
        
# ---------------------------------------------------
#
# CardInfoTitle
#
# ---------------------------------------------------
class CardInfoTitle(QLabel):
    def __init__(self):
        super().__init__()

        self.setWordWrap(True)
        
        # border
        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Sunken)
        self.setLineWidth(0)

        # font, colors
        self.setFont(QFont( "Comic Sans MS", 18, weight=QFont.Bold))
        self.text = None
    
    def set_title(self, title):
        self.setText(title)
        self.text = title
        
    def get_title(self):
        return self.text
        
class CardInfoLineLabel(QLabel):
    def __init__(self, label):
        super().__init__()
 
        self.setAlignment(Qt.AlignTop);
        self.setMinimumWidth(60)
        
        # font, colors
        self.setFont(QFont( "Comic Sans MS", 10, weight=QFont.Normal))

        self.setText(label)

class CardInfoLineValue(QLabel):
    def __init__(self, value):
        super().__init__()
        
        self.setWordWrap(True)
        
        # font, colors
        self.setFont(QFont( "Comic Sans MS", 10, weight=QFont.Normal))
    
        self.setText(value)

# ---------------------------------------------------
#
# CardInfoLine 
#
# It contains a label and value horizontaly ordered
#
# ---------------------------------------------------
class CardInfoLine(QLabel):
    def __init__(self, label, value):
        super().__init__()
    
        line_layout = QHBoxLayout(self)
        line_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout( line_layout )
        line_layout.setSpacing(5)
        
        # border of the line
        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Sunken)
        self.setLineWidth(0)

        line_layout.addWidget(CardInfoLineLabel(label + ":"),)
        line_layout.addWidget(CardInfoLineValue(value), 1) 
        

#
# CardInfoLinesHolder
#
# It contains CardInfoLine objects vertically ordered
#
class CardInfoLinesHolder(QLabel):
    def __init__(self):
        super().__init__()
    
        self.line_layout = QHBoxLayout(self)
        self.line_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout( self.line_layout )
        self.line_layout.setSpacing(5)
        
        # border
        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Sunken)
        self.setLineWidth(0)
        
    def add_element(self, label, value ):
        self.line_layout.addWidget( CardInfoLine( label, value) )
        
        #line_layout.addStretch(1)

# ---------------------------------------------------
#
# CardInformation
#
# It contains two other containers vertically ordered:
# -CardInfoTitle
# -CardInfoLinesHolder
#
# ---------------------------------------------------
class CardInformation(QLabel):
    def __init__(self):
        super().__init__()
        
        self.info_layout = QVBoxLayout(self)
        self.setLayout(self.info_layout)
        self.info_layout.setContentsMargins(1,1,1,1)
        self.info_layout.setSpacing(0)
        
        self.card_info_title = CardInfoTitle()
        self.info_layout.addWidget( self.card_info_title )
        self.card_info_lines_holder = CardInfoLinesHolder()
        self.info_layout.addWidget( self.card_info_lines_holder )
        
        # Horizintal line under the "Year/Length/Country" line
        self.horizontal_line = QHLine()
        self.info_layout.addWidget( self.horizontal_line )


    def set_title(self, title ):
        self.card_info_title.set_title(title)
        
    def get_title(self):
        return self.card_info_title.get_title()

    def add_separator(self):
        self.info_layout.addWidget( QHLine() )
        
    def add_info_line( self, label, value ):
        self.info_layout.addWidget( CardInfoLine( label, value ) )
        
    def add_stretch( self ):
        self.info_layout.addStretch(1)

    def add_element_to_collector_line( self, label, value ):
        self.card_info_lines_holder.add_element( label, value )

class CardImage(QLabel):
    def __init__(self):
        super().__init__()
        
        image_layout = QHBoxLayout(self)
        image_layout.setContentsMargins(2,2,2,2)
        self.setLayout( image_layout )

        #p = self.palette()
        #p.setColor(self.backgroundRole(), Qt.red)
        #self.setPalette(p)
        self.setStyleSheet('background: black')
       
        self.media_path = None
        self.sub_cards = json.loads('[]')
        
        self.setMinimumWidth(PICTURE_WIDTH)
        self.setMaximumWidth(PICTURE_WIDTH)
        self.setMinimumHeight(PICTURE_HEIGHT)
      

    def enterEvent(self, event):
        self.update()
        QApplication.setOverrideCursor(Qt.PointingHandCursor)

    def leaveEvent(self, event):
        self.update()
        QApplication.restoreOverrideCursor()
    
    def paintEvent(self, event):
        if self.underMouse():                       
            self.setStyleSheet('background: gray')
        else:
            self.setStyleSheet('background: black')
        
        super().paintEvent(event)
        
    def set_image_path( self, image_path ):
        pixmap = QPixmap( image_path )
        smaller_pixmap = pixmap.scaledToWidth(PICTURE_WIDTH)
        #smaller_pixmap = pixmap.scaled(160, 160, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.setPixmap(smaller_pixmap)        

    def set_media_path( self, media_path ):
        self.media_path = media_path
     
    def get_media_path( self ):
        return self.media_path

    def set_sub_cards( self, sub_cards ):
        self.sub_cards = sub_cards

    def get_sub_cards( self ):
        
        return self.sub_cards      
        

# ===================================================
#
# CardRating
#
# It contains three elments in vertically ordered:
# -Favorite
# -Best
# -New
#
# ===================================================
class CardRating(QLabel):
    def __init__(self):
        super().__init__()
        
        self.rating_layout = QVBoxLayout(self)
        self.setLayout(self.rating_layout)
        self.rating_layout.setContentsMargins(1,1,1,1)
        self.rating_layout.setSpacing(0)
        #self.setStyleSheet('background: green')
        self.setMinimumWidth(RATE_WIDTH)


        # FAVORITE button
        self.rating_favorite_button = QPushButton()
        self.rating_favorite_button.setCheckable(True)        
        rating_favorite_icon = QIcon()
        rating_favorite_icon.addPixmap(QPixmap( resource_filename(__name__,os.path.join("img", IMG_FAVORITE_ON)) ), QIcon.Normal, QIcon.On)
        rating_favorite_icon.addPixmap(QPixmap( resource_filename(__name__,os.path.join("img", IMG_FAVORITE_OFF)) ), QIcon.Normal, QIcon.Off)
        self.rating_favorite_button.clicked.connect(self.rating_favorite_button_on_click)        
        self.rating_favorite_button.setIcon( rating_favorite_icon )
        self.rating_favorite_button.setIconSize(QSize(25,25))
        self.rating_favorite_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.rating_favorite_button.setStyleSheet("background:transparent; border:none") 
        self.rating_layout.addWidget( self.rating_favorite_button )

        # BEST button
        self.rating_best_button = QPushButton()
        self.rating_best_button.setCheckable(True)        
        rating_best_icon = QIcon()
        rating_best_icon.addPixmap(QPixmap( resource_filename(__name__,os.path.join("img", IMG_BEST_ON)) ), QIcon.Normal, QIcon.On)
        rating_best_icon.addPixmap(QPixmap( resource_filename(__name__,os.path.join("img", IMG_BEST_OFF)) ), QIcon.Normal, QIcon.Off)
        self.rating_best_button.clicked.connect(self.rating_best_button_on_click)        
        self.rating_best_button.setIcon( rating_best_icon )
        self.rating_best_button.setIconSize(QSize(25,25))
        self.rating_best_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.rating_best_button.setStyleSheet("background:transparent; border:none") 
        self.rating_layout.addWidget( self.rating_best_button )

        # NEW button
        self.rating_new_button = QPushButton()
        self.rating_new_button.setCheckable(True)        
        rating_new_icon = QIcon()
        rating_new_icon.addPixmap(QPixmap( resource_filename(__name__,os.path.join("img", IMG_NEW_ON)) ), QIcon.Normal, QIcon.On)
        rating_new_icon.addPixmap(QPixmap( resource_filename(__name__,os.path.join("img", IMG_BEST_OFF)) ), QIcon.Normal, QIcon.Off)
        self.rating_new_button.clicked.connect(self.rating_new_button_on_click)        
        self.rating_new_button.setIcon( rating_new_icon )
        self.rating_new_button.setIconSize(QSize(25,25))
        self.rating_new_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.rating_new_button.setStyleSheet("background:transparent; border:none") 
        self.rating_layout.addWidget( self.rating_new_button )

    def set_folder(self, folder):
        self.folder = folder

    def set_rating(self, rating):
        self.rating = rating
        self.rating_favorite_button.setChecked(rating[ RATING_KEY_FAVORITE ] == 'y')
        self.rating_best_button.setChecked(rating[ RATING_KEY_BEST ] == 'y')
        self.rating_new_button.setChecked(rating[ RATING_KEY_NEW ] == 'y')

    # -----------------------
    #
    # FAVORITE icon clicked
    #
    # -----------------------
    def rating_favorite_button_on_click(self):
        self.rating[ RATING_KEY_FAVORITE ] = 'y' if self.rating_favorite_button.isChecked() else 'n'
        card_ini = Property( os.path.join(self.folder, FILE_CARD_INI), True )
        card_ini.update(SECTION_RATING, RATING_KEY_FAVORITE, self.rating[RATING_KEY_FAVORITE])

    # -----------------------
    #
    # BEST icon clicked
    #
    # -----------------------       
    def rating_best_button_on_click(self):
        self.rating[RATING_KEY_BEST] = 'y' if self.rating_best_button.isChecked() else 'n'
        card_ini = Property( os.path.join(self.folder, FILE_CARD_INI), True )
        card_ini.update(SECTION_RATING, RATING_KEY_BEST, self.rating[RATING_KEY_BEST])

    # -----------------------
    #
    # NEW icon clicked
    #
    # -----------------------            
    def rating_new_button_on_click(self):
        self.rating[RATING_KEY_NEW] = 'y' if self.rating_new_button.isChecked() else 'n'
        card_ini = Property( os.path.join(self.folder, FILE_CARD_INI), True )
        card_ini.update(SECTION_RATING, RATING_KEY_NEW, self.rating[RATING_KEY_NEW])

