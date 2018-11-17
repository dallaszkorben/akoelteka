import sys
import os

from pkg_resources import resource_string, resource_filename

from akoteka.gui.card_holder_pane import CardHolder
    
from akoteka.gui.glob import *

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

        card_holder = CardHolder()
        scroll_layout.addWidget(card_holder)
        
#        card_holder.remove_cards()
       
        
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
