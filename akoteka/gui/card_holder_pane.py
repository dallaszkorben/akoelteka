import sys
import os
import json
from subprocess import call
from threading import Thread
from pkg_resources import resource_string, resource_filename

from akoteka.accessories import collect_cards

from akoteka.gui.glob import *
from akoteka.gui.glob import _

from akoteka.gui.glob import media_path_film
from akoteka.gui.glob import media_player_video
from akoteka.gui.glob import media_player_video_param

#from akoteka.gui.glob import language

PICTURE_WIDTH = 190
PICTURE_HEIGHT = 160

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
        
        card_layout = QHBoxLayout(self)
        # control the gap between the card, and its contents
        card_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout( card_layout )
        
        # border
        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Sunken)
        self.setLineWidth(1)
        
        # gap between the card, an the elements of the card - horizontal gap
        card_layout.setSpacing(10)

        self.card_image = CardImage()
        card_layout.addWidget( self.card_image )
        self.card_information = Card_Information()
        card_layout.addWidget( self.card_information )
        
        self.setStyleSheet('background: lightgray') 
        
        #self.setMinimumHeight(PICTURE_HEIGHT)
       
    def mousePressEvent(self, event):
        
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
            self.card_holder.go_deeper(self.get_child_paths() )
   
   
       
    def set_image_path( self, image_path ):
        self.card_image.set_image_path( image_path )
        
    def set_media_path( self, media_path ):
        self.card_image.set_media_path( media_path )

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


class CardHolder( QWidget ):
    def __init__(self, parent, previous_holder, target):
        super().__init__()

        self.parent = parent
        self.previous_holder = previous_holder

        self_layout = QVBoxLayout(self)
        self.setLayout(self_layout)
        # controls the distance between the MainWindow and the added container: scrollContent
        self_layout.setContentsMargins(12,12,12,12)     
        self_layout.setSpacing(0)
        
        card_holder_canvas = QWidget()
        self.card_holder_layout = QVBoxLayout(card_holder_canvas)
        card_holder_canvas.setLayout(self.card_holder_layout)
        self.card_holder_layout.setContentsMargins(12,12,12,12)  
        self.card_holder_layout.setSpacing(5)
        card_holder_canvas.setStyleSheet('background: gray')   

        self_layout.addWidget(card_holder_canvas)

        # -------------
        #
        # Header
        #
        # ------------
#        header = QLabel()
#        header.setFont(QFont( "Comic Sans MS", 23, weight=QFont.Bold))
#        header.setAlignment(Qt.AlignVCenter)
#        header.setText("Filter")
#        #scroll_layout.addWidget( header )
#        self.card_holder_layout.addWidget( header )        
        
        # -------------
        #
        # Cards
        #
        # ------------
        #self.remove_cards()

        self.key = target[ "key" ]
        self.value = target[ "value" ]
        self.value_store_mode = target[ "value-store-mode" ]
        
        for path in target["paths"]:
        
            card_list = collect_cards( path, key=self.key, value=self.value, value_store_mode=self.value_store_mode )
            for crd in card_list:
            
                #scrollLayout.addWidget( QPushButton(str(i)) )
                card = Card(self)
                card.set_image_path( crd["image-path"] )
                card.set_child_paths( crd["child-paths"] )
                card.set_media_path( crd["media-path"] )
                card.set_title( crd["title"][language] )
                card.add_info_line( _("title_director"), ", ".join( [ d for d in crd["director"] ] ) )
                card.add_info_line( _("title_actor"), ", ".join( [ a for a in crd["actor"] ] ) )
                card.add_info_line( _("title_genre"), ", ".join( [ _("genre_"+g) for g in crd["genre"] ] ) )
                card.add_info_line( _("title_theme"), ", ".join( [ _("theme_"+a) for a in crd["theme"] ] ) )

                card.add_element_to_collector_line( _("title_year"), crd["year"])
                card.add_element_to_collector_line( _("title_length"), crd["length"])
                card.add_element_to_collector_line( _("title_nationality"), ", ".join( [ dic._("nat_" + a) for a in crd["nationality"] ]) )
            
                #scroll_layout.addWidget( card )
                self.card_holder_layout.addWidget( card )
            
            # add after the last card
            #scroll_layout.addStretch(1)        

        self.stretchie = QSpacerItem(10,10,QSizePolicy.Minimum,QSizePolicy.Expanding)
        self.card_holder_layout.addItem(self.stretchie)
        
        self.parent.set_back_button_listener(self)
  
    def remove_cards(self):
        self.card_holder_layout.removeItem(self.stretchie)
        for i in reversed(range(self.card_holder_layout.count())): 
            widgetToRemove = self.card_holder_layout.itemAt(i).widget()
        
            # remove it from the layout list
            self.card_holder_layout.removeWidget(widgetToRemove)
            
            # remove it from the gui
            widgetToRemove.setParent(None)
            
    def go_deeper(self, child_paths):
        deeper_card_holder = CardHolder(self.parent, self, 
            {
                "key" : self.key,
                "value" : self.value,
                "value-store-mode" : self.value_store_mode,
                "paths" : child_paths        
            }                                        
        )
        self.parent.add_new_holder(self, deeper_card_holder)
        
    def go_back(self):
        self.parent.restore_previous_holder(self.previous_holder, self)
        self.parent.set_back_button_listener(self.previous_holder)
        

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
        
class Card_Info_Title(QLabel):
    def __init__(self):
        super().__init__()
        
        # font, colors
        self.setFont(QFont( "Comic Sans MS", 18, weight=QFont.Bold))
    
    def set_title(self, title):
        self.setText(title)
        
class Card_Info_Line_Title(QLabel):
    def __init__(self, label):
        super().__init__()
        
        self.setAlignment(Qt.AlignTop);
        self.setMinimumWidth(60)
        
        # font, colors
        self.setFont(QFont( "Comic Sans MS", 10, weight=QFont.Normal))

        self.setText(label)

class Card_Info_Line_Value(QLabel):
    def __init__(self, value):
        super().__init__()
        
        self.setWordWrap(True)
        
        # font, colors
        self.setFont(QFont( "Comic Sans MS", 10, weight=QFont.Normal))
    
        self.setText(value)

class Card_Info_Line(QLabel):
    def __init__(self, label, value):
        super().__init__()
    
        line_layout = QHBoxLayout(self)
        line_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout( line_layout )
        line_layout.setSpacing(5)
        
        # border
        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Sunken)
        self.setLineWidth(2)

        line_layout.addWidget(Card_Info_Line_Title(label + ":"),)
        line_layout.addWidget(Card_Info_Line_Value(value), 1) 
        
        
class Card_Info_Collector_Line(QLabel):
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
        self.line_layout.addWidget( Card_Info_Line( label, value) )
        
        #line_layout.addStretch(1)



class Card_Information(QWidget):
    def __init__(self):
        super().__init__()
        
        self.info_layout = QVBoxLayout(self)
        self.setLayout(self.info_layout)
        self.info_layout.setContentsMargins(1,1,1,1)
        self.info_layout.setSpacing(0)
        
        self.card_info_title = Card_Info_Title()
        self.info_layout.addWidget( self.card_info_title )
        self.card_info_collector_line = Card_Info_Collector_Line()
        self.info_layout.addWidget( self.card_info_collector_line )        

    def set_title(self, title ):
        self.card_info_title.set_title(title)

    def add_separator(self):
        self.info_layout.addWidget( QHLine() )
        
    def add_info_line( self, label, value ):
        self.info_layout.addWidget( Card_Info_Line( label, value ) )
        
    def add_stretch( self ):
        self.info_layout.addStretch(1)

    def add_element_to_collector_line( self, label, value ):
        self.card_info_collector_line.add_element( label, value )

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
