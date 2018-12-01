import sys
import os
import json
from subprocess import call
from threading import Thread
from pkg_resources import resource_string, resource_filename

from PyQt5.QtCore import pyqtSignal  

from akoteka.accessories import collect_cards
from akoteka.accessories import filter_key

from akoteka.gui.glob import *
from akoteka.gui.glob import _

#from akoteka.gui.glob import media_path_film
from akoteka.gui.glob import media_player_video
from akoteka.gui.glob import media_player_video_param

#from akoteka.gui.glob import language

PICTURE_WIDTH = 190
PICTURE_HEIGHT = 160

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
    
    def __init__(self, parent, previous_holder, hierarchy, paths):
        super().__init__()

        self.parent = parent
        self.previous_holder = previous_holder
        self.hierarchy = hierarchy
        self.paths = paths 

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
        
        self.title_hierarchy = self.hierarchy
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
        self.cc = CollectCardThread( self, self.paths, self.parent.get_filter_holder().get_filter_selection() )
        self.cc.trigger.connect(self.fill_up_card_holder)
        self.cc.start()
        
        self.parent.set_back_button_listener(self)
  
    def show_card_holder(self):
        self.card_holder_canvas.setHidden(False)
        
    def remove_cards(self):
        self.card_holder_layout.removeItem(self.stretchie)
        for i in reversed(range(self.card_holder_layout.count())): 
            widgetToRemove = self.card_holder_layout.itemAt(i).widget()
        
            # remove it from the layout list
            self.card_holder_layout.removeWidget(widgetToRemove)
            
            # remove it from the gui
            widgetToRemove.setParent(None)
            
    def go_deeper(self, child_paths, card_title):
        deeper_card_holder = CardHolder(
            self.parent, 
            self, 
            self.title_hierarchy + (" > " if self.title_hierarchy else "") + card_title, 
            child_paths 
        )
        self.parent.add_new_holder(self, deeper_card_holder)
        
    def go_back(self):
        self.parent.restore_previous_holder(self.previous_holder, self)
        self.parent.set_back_button_listener(self.previous_holder)

    # 
    # This method fills up the card_holder
    #
    # connected SIGNAL 
    def fill_up_card_holder(self, card_list):
        
        for crd in card_list:

            card = Card(self)
            card.set_image_path( crd["image-path"] )
            card.set_child_paths( crd["child-paths"] )
            card.set_media_path( crd["media-path"] )
            card.set_title( crd["title"][language] )

            if crd["media-path"]:
                    
                    card.add_info_line( _("title_director"), ", ".join( [ d for d in crd["director"] ] ) )
                    card.add_info_line( _("title_actor"), ", ".join( [ a for a in crd["actor"] ] ) )
                    card.add_info_line( _("title_genre"), ", ".join( [ _("genre_"+g) for g in crd["genre"] ] ) )
                    card.add_info_line( _("title_theme"), ", ".join( [ _("theme_"+a) for a in crd["theme"] ] ) )

                    card.add_element_to_collector_line( _("title_year"), crd["year"])
                    card.add_element_to_collector_line( _("title_length"), crd["length"])
                    card.add_element_to_collector_line( _("title_nationality"), ", ".join( [ dic._("nat_" + a) for a in crd["nationality"] ]) )

            self.card_holder_layout.addWidget( card )
        
        if card_list:
            self.show_card_holder()



class CollectCardThread(QtCore.QThread):
    trigger = pyqtSignal(list)

    def __init__(self, parent=None, paths=None, filter_selection=None):
        super().__init__()
        #self.start()
        
        self.parent = parent
        self.paths = paths
        self.filter_selection = filter_selection
        
    def run(self):

        #for path in self.paths:
        card_list = collect_cards( self.paths, self.filter_selection )

        #import time
        #time.sleep(10)
        self.trigger.emit(card_list)

    def __del__(self):
        self.exiting = True
        self.wait()
        
      
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

        self.card_image = CardImage()
        card_layout.addWidget( self.card_image )
        self.card_information = CardInformation()
        card_layout.addWidget( self.card_information )
 
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
            self.card_holder.go_deeper(self.get_child_paths(), self.card_information.get_title() )
       
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
    
    def set_child_paths( self, child_paths ):
        self.card_image.set_child_paths( child_paths )
        
    def get_child_paths( self ):
        return self.card_image.get_child_paths()
        
    def set_title(self, title):
        self.card_information.set_title(title)
        
    def add_info_line( self, label, value ):
        self.card_information.add_info_line( label, value )
        
    def add_element_to_collector_line( self, label, value ):
        self.card_information.add_element_to_collector_line( label, value )

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

        else:
#            self.setStyleSheet('background: ' + COLOR_CARD_BORDER_CONTAINER)        
            qp.setBrush( QColor(COLOR_CARD_BORDER_CONTAINER ))

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
        
        # Horizintal line under the "Year/Length/Nationality" line
        self.info_layout.addWidget( QHLine())


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
        self.child_paths = json.loads('[]')
        
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

    def set_child_paths( self, child_paths ):
        self.child_paths = child_paths

    def get_child_paths( self ):
        return self.child_paths
