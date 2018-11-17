import sys
import os

from pkg_resources import resource_string, resource_filename

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtWidgets import QDesktopWidget
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QFrame

from PyQt5.QtGui import QFont
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QPalette
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QPainter

from PyQt5 import QtCore

from PyQt5.QtCore import Qt

from akoteka.accessories import collect_cards
from akoteka.handle_property import Config_Ini
from akoteka.handle_property import Dict

# Handle CONFIG.INI
config_ini = Config_Ini.get_instance()
language = config_ini.get_language()
media_path_film = config_ini.get_media_path_film()
media_player_video = config_ini.get_media_player_video()
media_player_video_param = config_ini.get_media_player_video_param()

dic = Dict.get_instance( language )

PICTURE_WIDTH = 190
PICTURE_HEIGHT = 160

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

class Card_Image(QLabel):
    def __init__(self):
        super().__init__()
        
        image_layout = QHBoxLayout(self)
        image_layout.setContentsMargins(2,2,2,2)
        self.setLayout( image_layout )

        #p = self.palette()
        #p.setColor(self.backgroundRole(), Qt.red)
        #self.setPalette(p)
        self.setStyleSheet('background: black')
       
        #pixmap = QPixmap( "/media/akoel/Movies/Final/Films/A.Profi-1981/image.jpeg" )
        #smaller_pixmap = pixmap.scaledToWidth(PICTURE_WIDTH)
        ##smaller_pixmap = pixmap.scaled(160, 160, Qt.KeepAspectRatio, Qt.FastTransformation)
        #self.setPixmap(smaller_pixmap)
        
        self.setMinimumWidth(PICTURE_WIDTH)
        self.setMaximumWidth(PICTURE_WIDTH)

    def enterEvent(self, event):
        self.update()

    def leaveEvent(self, event):
        self.update()
    
    def paintEvent(self, event):
        #pix = self.pixmap_hover if self.underMouse() else self.pixmap
        #pix = self.pixmap_hover if self.hasFocus() else self.pixmap
        #pix = self.pixmap_hover if self.underMouse() else self.pixmap_focus if self.hasFocus() else self.pixmap
        #if self.isDown():
        #    pix = self.pixmap_pressed
        #painter = QPainter(self)
        #painter.drawPixmap(event.rect(), self.pixmap)    
        
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
        
# =========================================
# 
# This Class represents a Card of a movie
#
# =========================================
#
# It contains an image and many characteristics of a movie on a card
#
class Card(QLabel):
    
    def __init__(self):
        super().__init__()
        
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

        self.card_image = Card_Image()
        card_layout.addWidget( self.card_image )
        self.card_information = Card_Information()
        card_layout.addWidget( self.card_information )
        
        self.setStyleSheet('background: lightgray') 
        
        #self.setMinimumHeight(PICTURE_HEIGHT)
        
    def set_image_path( self, image_path ):
        self.card_image.set_image_path( image_path )
        
    def set_title(self, title):
        self.card_information.set_title(title)
        
    def add_info_line( self, label, value ):
        self.card_information.add_info_line( label, value )
        
    def add_element_to_collector_line( self, label, value ):
        self.card_information.add_element_to_collector_line( label, value )


class Card_Holder( QWidget ):
    def __init__(self):
        super().__init__()

        holder_layout = QVBoxLayout(self)
        self.setLayout(holder_layout)
        # controls the distance between the MainWindow and the added container: scrollContent
        holder_layout.setContentsMargins(12,12,12,12)     
        holder_layout.setSpacing(0)
        
        inner_canvas = QWidget()
        self.inner_layout = QVBoxLayout(inner_canvas)
        inner_canvas.setLayout(self.inner_layout)
        self.inner_layout.setContentsMargins(12,12,12,12)  
        self.inner_layout.setSpacing(5)
        inner_canvas.setStyleSheet('background: gray')   

        holder_layout.addWidget(inner_canvas)
         
    
         

        # -------------
        #
        # Header
        #
        # ------------
        header = QLabel()
        header.setFont(QFont( "Comic Sans MS", 23, weight=QFont.Bold))
        header.setAlignment(Qt.AlignVCenter)
        header.setText("Filter")
        #scroll_layout.addWidget( header )
        self.inner_layout.addWidget( header )
        
        # -------------
        #
        # Cards
        #
        # ------------

 
        ret = collect_cards( "/media/akoel/Movies/Final/Films", key="all", value="", search="*" )
        for crd in ret:
            
            #scrollLayout.addWidget( QPushButton(str(i)) )
            card = Card()
            card.set_image_path( crd["image"] )
            card.set_title( crd["title"][language] )
            card.add_info_line( dic._("title_director"), ", ".join( [ d for d in crd["director"] ] ) )
            card.add_info_line( dic._("title_actor"), ", ".join( [ a for a in crd["actor"] ] ) )
            card.add_info_line( dic._("title_genre"), ", ".join( [ g for g in crd["genre"] ] ) )
            card.add_info_line( dic._("title_theme"), ", ".join( [ a for a in crd["theme"] ] ) )
            
            card.add_element_to_collector_line( dic._("title_year"), crd["year"])
            card.add_element_to_collector_line( dic._("title_length"), crd["length"])
            card.add_element_to_collector_line( dic._("title_nationality"), ", ".join( [ dic._("nat_" + a) for a in crd["nationality"] ]) )
            
            #scroll_layout.addWidget( card )
            self.inner_layout.addWidget( card )
        # add after the last card
        #scroll_layout.addStretch(1)
        self.inner_layout.addStretch(1)
        #scroll.setWidget(scroll_content)
  
    def remove_cards(self):
        for i in reversed(range(self.inner_layout.count())): 
            widgetToRemove = self.inner_layout.itemAt(i).widget()
            widgetToRemove.setParent(None)
        
            # remove it from the layout list
            self.inner_layout.removeWidget(widgetToRemove)
            # remove it from the gui
            
        

class GuiAkoTeka(QWidget):
    
    def __init__(self):
        super().__init__()        
        
        # most outer container, just right in the Main Window
        box_layout = QVBoxLayout(self)
        self.setLayout(box_layout)
        # controls the distance between the MainWindow and the added container: scrollContent
        box_layout.setContentsMargins(0, 0, 0, 0)
    
        # scroll_content where you can add your widgets - has scroll
        scroll = QScrollArea(self)
        box_layout.addWidget(scroll)
        scroll.setWidgetResizable(True)
        scroll_content = QWidget(scroll)
#        scroll_content.setStyleSheet('background: black')  

        # layout of the content with margins
        scroll_layout = QVBoxLayout(scroll_content)
        scroll.setWidget(scroll_content)
        # vertical distance between cards - Vertical
        scroll_layout.setSpacing(0)
        # spaces between the added Widget and this top, right, bottom, left side
        scroll_layout.setContentsMargins(0,0,0,0)
        scroll_content.setLayout(scroll_layout)

        card_holder = Card_Holder()
        scroll_layout.addWidget(card_holder)
        
        card_holder.remove_cards()

        
        
        # --- Window ---
        self.setWindowTitle('akoTeka')    
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

        
def main():    
    app = QApplication(sys.argv)
    ex = GuiAkoTeka()
    sys.exit(app.exec_())
