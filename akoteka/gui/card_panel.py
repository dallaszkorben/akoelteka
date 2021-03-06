import sys
import os
from subprocess import call
from pkg_resources import resource_string, resource_filename
from functools import cmp_to_key
import locale

from akoteka.accessories import get_pattern_video
from akoteka.accessories import get_pattern_audio
from akoteka.accessories import get_storyline_title
from akoteka.accessories import get_writer_title
from akoteka.accessories import get_director_title
from akoteka.accessories import get_actor_title
from akoteka.accessories import get_sound_title
from akoteka.accessories import play_media
from akoteka.accessories import FlowLayout

from akoteka.handle_property import _
from akoteka.handle_property import config_ini
from akoteka.handle_property import Property

from akoteka.gui.pyqt_import import QHLine
from akoteka.gui.pyqt_import import QSpinBox
from akoteka.gui.pyqt_import import *

from akoteka.constants import *

from cardholder.cardholder import Card
from PyQt5.Qt import QIcon
from asyncio.selector_events import ssl


# =========================================
# 
# Card Panel
#
# =========================================
class CardPanel(QWidget):
    """
    This class represents the Content of a Card.
    It is divided into three parts. Left to right:
        -Image
        -Information
        -Rating    
    """
    def __init__(self, card, card_data):
        """
        Constructor of the CardPanel
        card:       Card object, which should be used to present data
        card_data:  The descriptor of the Card
        """
        QWidget.__init__(self, card)
        
        self.card = card
        self.card_data = card_data
        self.card_holder = card.get_card_holder()
        self.card_path = None

        panel_layout = QHBoxLayout(self)
        panel_layout.setContentsMargins(WIDTH_PANEL_MARGIN_LEFT, WIDTH_PANEL_MARGIN_TOP, WIDTH_PANEL_MARGIN_RIGHT, WIDTH_PANEL_MARGIN_BOTTOM)
        panel_layout.setSpacing(10)
        self.setLayout( panel_layout )
        #self.setStyleSheet('background: ' + COLOR_CARD_BACKGROUND)
        #self.setStyleSheet('border:none')

        #
        # Containers in the Card
        #
        self.card_image = CardImage( self )
        panel_layout.addWidget( self.card_image )
        
        self.card_information = CardInformation()
        panel_layout.addWidget( self.card_information )
        self.card_rating = CardRating(self)
        panel_layout.addWidget( self.card_rating )
 
        self.set_image_path( card_data["extra"]["image-path"] )
        
        self.set_sub_cards( card_data['extra']['sub-cards'])
        
        self.set_media_path( card_data["extra"]["media-path"] )
        
        # -------------- TITLE -----------------------------
        
        title = card_data['title'][config_ini['language']].strip()
        orig_title = card_data['title']['orig'].strip()       
        self.set_title( title + (" (" + orig_title + ")" if config_ini['show_original_title']=='y' and orig_title and orig_title != title else "" ) )
 
        if card_data["extra"]["media-path"]:

            self.set_media( card_data["control"]["media"] )
            self.set_category( card_data["control"]["category"] )

            self.add_element_to_collector_line( _("title_year"), card_data["general"]["year"])
            self.add_element_to_collector_line( _("title_length"), card_data["general"]["length"])
            self.add_element_to_collector_line( _("title_country"), ", ".join( [ _("country_" + a) for a in card_data["general"]["country"] ]) )
            
            if ''.join(card_data["general"]["sound"]):
                self.add_element_to_collector_line(
                    get_sound_title(card_data["control"]["media"], card_data["control"]["category"]),
                    ", ".join( [ _("lang_" + a) for a in card_data["general"]["sound"] ]) if card_data["general"]["sound"] != [''] else "")

            if ''.join(card_data["general"]["sub"]):            
                self.add_element_to_collector_line( _("title_sub"), ", ".join( [ _("lang_" + a) for a in card_data["general"]["sub"] ]) if card_data["general"]["sub"] != [''] else "" )
 
            self.add_separator()

            # -------------- WRITER --------------------------
            
            if ''.join(card_data["general"]["writer"]):
                self.add_info_line( 
                    get_writer_title(card_data["control"]["media"], card_data["control"]["category"]),
                    ", ".join( [ d for d in card_data["general"]["writer"] ] ) )
            
            # -------------- DIRECTOR --------------------------
            
            if ''.join(card_data["general"]["director"]):
                    self.add_info_line( 
                        get_director_title(card_data["control"]["media"], card_data["control"]["category"]),
                        ", ".join( [ d for d in card_data["general"]["director"] ] ) )

            # -------------- ACTOR -----------------------------

            if ''.join(card_data["general"]["actor"]):
                self.add_info_line( 
                    get_actor_title(card_data["control"]["media"], card_data["control"]["category"]), 
                    ", ".join( [ a for a in card_data["general"]["actor"] ] ) )

            # -------------- GENRE -----------------------------

            if ''.join(card_data["general"]["genre"]):
                self.add_info_line( _("title_genre"), ", ".join( [ _("genre_" + g ) if g else "" for g in card_data["general"]["genre"] ] ) )


            # -------------- THEME -----------------------------

            #if card_data['control']['category'] == 'movie' or card_data['control']['category'] == 'talk':                    
            if ''.join(card_data["general"]["theme"]):
                    self.add_info_line( _("title_theme"), ", ".join( [ _("theme_" + a ) if a else "" for a in card_data["general"]["theme"] ] ) )

            # -------------- STORILINE -------------------------
                
            if card_data['storyline'][config_ini['language']]:
                self.add_separator()
                #title = _('title_storyline_movie') if card_data['control']['category'] == 'movie' else _('title_storyline_music') if card_data['control']['category'] == 'music' else _('title_storyline_talk') if card_data['control']['category'] == 'talk' else ''                
                self.add_info_line( 
                    get_storyline_title(card_data["control"]["media"], card_data["control"]["category"]), 
                    card_data['storyline'][config_ini['language']])
                   
            self.add_info_line_stretch()

            # -------------- RATING ----------------------------

            self.set_folder(card_data['extra']['recent-folder'])
            self.set_rating(card_data['rating'])
 
        # if it is a direct card to a media
        if self.card_image.get_media_path():
            
            # TODO
            #qp.setBrush( QColor(COLOR_CARD_BORDER_MEDIA))
            
            # Show the RATING section
            self.card_rating.setHidden(False)

        # if it is a Collector
        else:
            
            
            self.set_media( "" )

            # TODO
            #qp.setBrush( QColor(COLOR_CARD_BORDER_CONTAINER ))
            
            # Hide the RATING section
            self.card_rating.setHidden(True)
            
            self.add_info_line_stretch()

 
      
    def get_card_holder( self ):
        return self.card_holder

    def set_image_path( self, image_path ):
        self.card_image.set_image_path( image_path )
        
    def set_media_path( self, media_path ):
        self.card_image.set_media_path( media_path )

    def get_media_path( self ):
        return self.card_image.get_media_path( )

    def set_card_path( self, path ):
        self.card_path = path
        
    def get_card_path( self ):
        return self.card_path
    
    def set_sub_cards( self, sub_cards ):
        self.card_image.set_sub_cards( sub_cards )
        
    def get_sub_cards( self ):
        return self.card_image.get_sub_cards()
        
    def set_title(self, title):
        self.card_information.set_title(title)
        
    def set_media(self, media):
        self.card_information.set_media(media)
        
    def set_category(self, category):
        self.card_information.set_category(category)

    def get_title(self):
        return self.card_information.get_title()
        
    def add_separator(self):
        self.card_information.add_separator()
        
    def add_info_line( self, label, value ):
        self.card_information.add_info_line( label, value )
        
    def add_info_line_stretch(self):
        self.card_information.add_stretch()
        
    def add_element_to_collector_line( self, label, value ):
        self.card_information.add_element_to_collector_line( label, value )
        
    def set_rating( self, rating ):
        self.card_rating.set_rating(rating)
        
    def set_folder( self, folder ):
        self.card_rating.set_folder(folder)
        








   
        
        
        



        
        
        
        
# ---------------------------------------------------
#
# CardInfoTitle
#
# ---------------------------------------------------
class CardInfoTitle(QWidget):
#class CardInfoTitle(QLabel):
    def __init__(self):
        super().__init__()

        self.card_info_title_layout = QGridLayout(self)
        self.card_info_title_layout.setContentsMargins(0,0,0,0)
        self.card_info_title_layout.setSpacing(0)
        self.card_info_title_layout.setColumnStretch(1, 2)
        self.setLayout(self.card_info_title_layout)

        # --- Icons ---
        self.media_label = QLabel()
        self.media_label.setAlignment(Qt.AlignTop)

        media_pixmap = QPixmap( resource_filename(__name__,os.path.join("img", IMG_EMPTY_BUTTON)) )
        media_pixmap = media_pixmap.scaled(0, 0, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.media_label.setPixmap(media_pixmap)
        self.media_label.setStyleSheet("background:transparent; border:none") 
        
        # --- Title ---
        self.title = QLabel()
        self.title.setWordWrap(True)
        
        # border
        self.title.setFrameShape(QFrame.Panel)
        self.title.setFrameShadow(QFrame.Sunken)
        self.title.setLineWidth(0)

        # font, colors
        self.title.setFont(QFont( FONT_TYPE, INFO_TITLE_FONT_SIZE, weight=QFont.Bold))
        self.title.text = None
                
        self.card_info_title_layout.addWidget(self.media_label, 0, 0)
        self.card_info_title_layout.addWidget(self.title, 0, 1)


 
        
        
        
#        self.setWordWrap(True)
#        
#        # border
#        self.setFrameShape(QFrame.Panel)
#        self.setFrameShadow(QFrame.Sunken)
#        self.setLineWidth(0)
#
#        # font, colors
#        self.setFont(QFont( FONT_TYPE, INFO_TITLE_FONT_SIZE, weight=QFont.Bold))
#        self.text = None
                
    def set_media(self, media):
        if media == 'video':
            media_pixmap = QPixmap( resource_filename(__name__,os.path.join("img", IMG_MEDIA_VIDEO)) )
        elif media == 'audio':
            media_pixmap = QPixmap( resource_filename(__name__,os.path.join("img", IMG_MEDIA_AUDIO)) )
        elif media == 'image':
            media_pixmap = QPixmap( resource_filename(__name__,os.path.join("img", IMG_MEDIA_IMAGE)) )
        elif media == 'book':
            media_pixmap = QPixmap( resource_filename(__name__,os.path.join("img", IMG_MEDIA_BOOK)) )
        elif media == 'doc':
            media_pixmap = QPixmap( resource_filename(__name__,os.path.join("img", IMG_MEDIA_DOC)) )
        else:
            media_pixmap = QPixmap( resource_filename(__name__,os.path.join("img", IMG_MEDIA_FOLDER)) )
            
        self.card_info_title_layout.setSpacing(20)
        media_pixmap = media_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.media_label.setPixmap(media_pixmap)

    def set_category(self, category):
        pass
    
    def set_title(self, title):
        self.title.setText(title)
        self.title.text = title
#        self.setText(title)
#        self.text = title
        
    def get_title(self):
        return self.title.text
#        return self.text        


class CardInfoLineLabel(QLabel):
    def __init__(self, label):
        super().__init__()
 
        #self.setAlignment(Qt.AlignTop);
        self.setMinimumWidth( INFO_LABEL_WIDTH )
        
        # font, colors
        self.setFont(QFont( FONT_TYPE, INFO_FONT_SIZE, weight=QFont.Normal))

        self.setText(label)

class CardInfoLineValue(QLabel):
    def __init__(self, value):
        super().__init__()
        
        #self.setWordWrap(True)
        self.setWordWrap(False)
        #self.setMaximumHeight( ONE_LINE_HEIGHT )
        
        #line_layout = QHBoxLayout(self)        
        #line_layout.setContentsMargins(15, 15, 15, 15)
        #self.setLayout( line_layout )
        
        
        # font, colors
        self.setFont(QFont( FONT_TYPE, INFO_FONT_SIZE, weight=QFont.Normal))
    
        self.setText(value)

# ---------------------------------------------------
#
# CardInfoLine 
#
# It contains a label and value horizontaly ordered
#
# ---------------------------------------------------
class CardInfoLine(QWidget):
    def __init__(self, label, value):
        super().__init__()
    
        line_layout = QHBoxLayout(self)
        line_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout( line_layout )
        line_layout.setSpacing(0)

        line_layout.addWidget(CardInfoLineLabel(label + ":"),0)
        line_layout.addWidget(CardInfoLineValue(value), 1) 
        

#
# CardInfoLinesHolder
#
# It contains CardInfoLine objects vertically ordered
#
class CardInfoLinesHolder(QWidget):
    def __init__(self):
        super().__init__()
    
        self.line_layout = QHBoxLayout(self)
        self.line_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout( self.line_layout )
        self.line_layout.setSpacing(1)
        
    def add_element(self, label, value ):
        self.line_layout.addWidget( CardInfoLine( label, value) )

#
# CardCollectorLine
#
class CardCollectorLine(QWidget):
    def __init__(self):
        super().__init__()
    
        self.line_layout = QHBoxLayout(self)
        self.line_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout( self.line_layout )
        self.line_layout.setSpacing(1)
        
    def add_element(self, label, value ):

        label_l = QLabel(label + ": ")
        label_l.setFont(QFont( FONT_TYPE, INFO_FONT_SIZE, weight=QFont.Normal))
        self.line_layout.addWidget(label_l)
        
        value_l = QLabel(value)
        value_l.setFont(QFont( FONT_TYPE, INFO_FONT_SIZE, weight=QFont.Bold))
        self.line_layout.addWidget(value_l)

        self.line_layout.addStretch(1)

        

# ---------------------------------------------------
#
# CardInformation
#
# It contains two other containers vertically ordered:
# -CardInfoTitle
# -CardInfoLinesHolder
#
# ---------------------------------------------------
class CardInformation(QWidget):
    def __init__(self):
        super().__init__()
        
        self.info_layout = QVBoxLayout(self)
        self.setLayout(self.info_layout)
        self.info_layout.setContentsMargins(0,0,0,0)
        self.info_layout.setSpacing(0)
        
        self.card_info_title = CardInfoTitle()
        
        self.info_layout.addWidget( self.card_info_title )
        #self.card_info_lines_holder = CardInfoLinesHolder()
        self.card_info_lines_holder = CardCollectorLine()
        self.info_layout.addWidget( self.card_info_lines_holder )

    def set_title(self, title):
        self.card_info_title.set_title(title)

    def set_media(self, media):
        self.card_info_title.set_media(media)
        
    def set_category(self, category):
        self.card_info_title.set_category(category)
        
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


# ================
#
# Card Image
#
# ================
class CardImage(QWidget):
    def __init__(self, panel):
        super().__init__()
        
        self.panel = panel
        
        self_layout = QHBoxLayout(self)
        self_layout.setContentsMargins(2,2,2,2)
        self.setLayout( self_layout )

        self.image_panel = QLabel(self)
        self.image_panel.setAlignment(Qt.AlignCenter)
        panel_layout = QHBoxLayout(self.image_panel)
        panel_layout.setContentsMargins(0,0,0,0)
        self_layout.addWidget(self.image_panel)

        self.setStyleSheet('background: black')

        self.media_path = None
        self.sub_cards = []
        
        self.setMinimumWidth(PICTURE_WIDTH)
        self.setMaximumWidth(PICTURE_WIDTH)
        self.setMinimumHeight(PICTURE_HEIGHT)
        self.setMaximumHeight(PICTURE_HEIGHT)
        
        self.mouse_pressed_for_click = False

    # Mouse Hover in
    def enterEvent(self, event):
        self.update()
        QApplication.setOverrideCursor(Qt.PointingHandCursor)

        self.setStyleSheet('background: gray')

        event.ignore()

    # Mouse Hover out
    def leaveEvent(self, event):
        self.update()
        QApplication.restoreOverrideCursor()

        self.setStyleSheet('background: black')
        
        event.ignore()

# !!!! Do not use paintEvent to change color !!!!!
# !!!! If you use it, it will be an infinite loop and almost 100% CPU usage !!!!    
#    def paintEvent(self, event):
#        s = self.size()
#        qp = QPainter()
#        qp.begin(self)
#        qp.setRenderHint(QPainter.Antialiasing, True)
#        qp.setBrush( QColor(Qt.red) )
#
#        qp.drawRect(0, 0, s.width(), s.height())
#        qp.end()
        
        #if self.underMouse():                       
        #    self.setStyleSheet('background: gray')
        #else:
        #    self.setStyleSheet('background: black')
        
        #super().paintEvent(event)
        
    def set_image_path( self, image_path ):
        if image_path is not None:
            pixmap = QPixmap( image_path )
            if pixmap.width() >= pixmap.height():
                smaller_pixmap = pixmap.scaledToWidth(PICTURE_WIDTH)
            else:
                smaller_pixmap = pixmap.scaledToHeight(PICTURE_WIDTH)
            self.image_panel.setPixmap(smaller_pixmap)        

    def set_media_path( self, media_path ):
        self.media_path = media_path
     
    def get_media_path( self ):
        return self.media_path

    def set_sub_cards( self, sub_cards ):
        self.sub_cards = sub_cards

    def get_sub_cards( self ):        
        return self.sub_cards      
     

    # --------------------
    #
    # Mouse Press on Image
    #
    # --------------------
    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.panel.card.get_status() == Card.STATUS_SELECTED:
            self.mouse_pressed_for_click = True
            event.accept()
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.mouse_pressed_for_click = False
            event.accept()
        else:
            event.ignore()
     
    def mouseReleaseEvent(self, event):
        if event.button() != Qt.LeftButton or not self.mouse_pressed_for_click:
            self.mouse_pressed_for_click = False
            event.ignore()
            return
        
        self.mouse_already_pressed = False
        
        media_path = self.get_media_path()
            
        # Play media
        if media_path:
#            if get_pattern_audio().match(media_path):            
#                self.panel.card.get_card_holder().parent.player
            
            play_media(self.media_path)
            
        else:
            # go deeper
            self.panel.card_holder.parent.go_down_in_hierarchy(self.get_sub_cards(), self.panel.get_title() )
            
        event.accept()

# ===================================================
#
# CardRating
#
# It contains three elments in vertically ordered:
# -Rate
# -Favorite
# -New
#
# ===================================================
class CardRating(QLabel):
    def __init__(self, card_panel):
        super().__init__()
        
        self.card_panel = card_panel
        
        self.rating_layout = QVBoxLayout(self)
        self.setLayout(self.rating_layout)
        self.rating_layout.setContentsMargins(1,1,1,1)
        self.rating_layout.setSpacing(0)
        #self.setStyleSheet('background: green')
        self.setMinimumWidth(RATE_WIDTH)

        # RATING QSpinBox
        self.rating_rate_spinbox = MySpinBox(self.card_panel)
        self.rating_rate_spinbox.valueChanged.connect(self.rating_rate_spinbox_on_click)
        self.rating_layout.addWidget(self.rating_rate_spinbox)
        
        self.rating_layout.addStretch(2)


        # FAVORITE button
        self.rating_favorite_button = QPushButton()
        self.rating_favorite_button.setFocusPolicy(Qt.NoFocus)
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

        self.rating_layout.addStretch(2)

#        # BEST button
#        self.rating_best_button = QPushButton()
#        self.rating_best_button.setFocusPolicy(Qt.NoFocus)
#        self.rating_best_button.setCheckable(True)        
#        rating_best_icon = QIcon()
#        rating_best_icon.addPixmap(QPixmap( resource_filename(__name__,os.path.join("img", IMG_BEST_ON)) ), QIcon.Normal, QIcon.On)
#        rating_best_icon.addPixmap(QPixmap( resource_filename(__name__,os.path.join("img", IMG_BEST_OFF)) ), QIcon.Normal, QIcon.Off)
#        self.rating_best_button.clicked.connect(self.rating_best_button_on_click)        
#        self.rating_best_button.setIcon( rating_best_icon )
#        self.rating_best_button.setIconSize(QSize(25,25))
#        self.rating_best_button.setCursor(QCursor(Qt.PointingHandCursor))
#        self.rating_best_button.setStyleSheet("background:transparent; border:none") 
#        self.rating_layout.addWidget( self.rating_best_button )

        # NEW button
        self.rating_new_button = QPushButton()
        self.rating_new_button.setFocusPolicy(Qt.NoFocus)
        self.rating_new_button.setCheckable(True)        
        rating_new_icon = QIcon()
        rating_new_icon.addPixmap(QPixmap( resource_filename(__name__,os.path.join("img", IMG_NEW_ON)) ), QIcon.Normal, QIcon.On)
        rating_new_icon.addPixmap(QPixmap( resource_filename(__name__,os.path.join("img", IMG_NEW_OFF)) ), QIcon.Normal, QIcon.Off)
        self.rating_new_button.clicked.connect(self.rating_new_button_on_click)        
        self.rating_new_button.setIcon( rating_new_icon )
        self.rating_new_button.setIconSize(QSize(25,25))
        self.rating_new_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.rating_new_button.setStyleSheet("background:transparent; border:none") 
        self.rating_layout.addWidget( self.rating_new_button )
        
        self.rating_layout.addStretch(2)

    def set_folder(self, folder):
        self.folder = folder

    def set_rating(self, rating):
        self.rating = rating
        self.rating_rate_spinbox.setValue(int(rating[RATING_KEY_RATE]))
        self.rating_favorite_button.setChecked(rating[ RATING_KEY_FAVORITE ] == 'y')
#        self.rating_best_button.setChecked(rating[ RATING_KEY_BEST ] == 'y')
        self.rating_new_button.setChecked(rating[ RATING_KEY_NEW ] == 'y')

    # -----------------------
    #
    # RATE button clicked
    #
    # -----------------------
    def rating_rate_spinbox_on_click(self):
        self.rating[ RATING_KEY_RATE ] = str(self.rating_rate_spinbox.value())
        card_ini = Property( os.path.join(self.folder, FILE_CARD_INI), True )
        card_ini.update(SECTION_RATING, RATING_KEY_RATE, self.rating[RATING_KEY_RATE])

    # -----------------------
    #
    # FAVORITE icon clicked
    #
    # -----------------------
    def rating_favorite_button_on_click(self):
        self.rating[ RATING_KEY_FAVORITE ] = 'y' if self.rating_favorite_button.isChecked() else 'n'
        card_ini = Property( os.path.join(self.folder, FILE_CARD_INI), True )
        card_ini.update(SECTION_RATING, RATING_KEY_FAVORITE, self.rating[RATING_KEY_FAVORITE])

#    # -----------------------
#    #
#    # BEST icon clicked
#    #
#    # -----------------------       
#    def rating_best_button_on_click(self):
#        self.rating[RATING_KEY_BEST] = 'y' if self.rating_best_button.isChecked() else 'n'
#        card_ini = Property( os.path.join(self.folder, FILE_CARD_INI), True )
#        card_ini.update(SECTION_RATING, RATING_KEY_BEST, self.rating[RATING_KEY_BEST])

    # -----------------------
    #
    # NEW icon clicked
    #
    # -----------------------            
    def rating_new_button_on_click(self):
        self.rating[RATING_KEY_NEW] = 'y' if self.rating_new_button.isChecked() else 'n'
        card_ini = Property( os.path.join(self.folder, FILE_CARD_INI), True )
        card_ini.update(SECTION_RATING, RATING_KEY_NEW, self.rating[RATING_KEY_NEW])

class MySpinBox(QSpinBox):
    def __init__(self, card_panel):
        super().__init__()
        
        self.card_panel = card_panel
        
        self.setButtonSymbols(QAbstractSpinBox.NoButtons) #PlusMinus / NoButtons / UpDownArrows        
        self.setMaximum(10)
        self.setFocusPolicy(Qt.NoFocus)
        self.lineEdit().setReadOnly(True)
        self.setFont(QFont( FONT_TYPE, RATE_FONT_SIZE, weight=QFont.Bold))
#        self.lineEdit().setEnabled(False)
        self.lineEdit().setStyleSheet( "QLineEdit{color:black}")
        self.setStyleSheet( "QSpinBox{background:'" + COLOR_RAITING_RATE_BACKGROUND + "'}")

    def stepBy(self, steps):
        """
        It needs to be override to make deselection after the step.
        If it it not there, the selection color (blue) will be appear on the field
        """
        super().stepBy(steps)
        self.lineEdit().deselect()

    # Mouse Hover in
    def enterEvent(self, event):
        self.update()
        QApplication.setOverrideCursor(Qt.PointingHandCursor)

        self.setButtonSymbols(QAbstractSpinBox.PlusMinus) #PlusMinus / NoButtons / UpDownArrows        

        self.card_panel.get_card_holder().setFocus()
        event.ignore()

    # Mouse Hover out
    def leaveEvent(self, event):
        self.update()
        QApplication.restoreOverrideCursor()

        self.setButtonSymbols(QAbstractSpinBox.NoButtons) #PlusMinus / NoButtons / UpDownArrows        
        
        self.card_panel.get_card_holder().setFocus()
        event.ignore()

