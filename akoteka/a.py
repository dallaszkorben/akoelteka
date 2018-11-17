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

from PyQt5.QtWidgets import QSizePolicy

from PyQt5.QtGui import QPixmap

from PyQt5.QtCore import Qt


class GuiAkoTeka(QWidget):
    
    def __init__(self):
        super().__init__()        
        

#        card_layout = QHBoxLayout(self)
        
        # control the gap between the card, and its contents
#        card_layout.setContentsMargins(0,0,0,0)
        # gap between the card, an the elements of the card - horizontal gap
#        card_layout.setSpacing(1)
#        self.setLayout( card_layout )
        
        
        image = QLabel(self)
        pixmap = QPixmap( "/media/akoel/Movies/Final/Films/A.Profi-1981/image.jpeg" )
        #image.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        smaller_pixmap = pixmap.scaled(160, 160, Qt.KeepAspectRatio, Qt.FastTransformation)
        image.setPixmap(smaller_pixmap)
        
        
        #pixmap.scaledToWidth(120)
        #pixmap.scaled(100,100)
        #pixmap.scaledToHeight(170)
        #image.resize(pixmap.width(), pixmap.height())
        print(smaller_pixmap.width(), smaller_pixmap.height())
        
        
        image.move(200,200)
        
        
        # --- Window ---
        self.setWindowTitle('akoTeka')    
        #self.setGeometry(300, 300, 300, 200)
        self.resize(600,600)
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


main()
