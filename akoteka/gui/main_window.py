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
        scroll_content.setStyleSheet('background: black')  

        # layout of the content with margins
        self.scroll_layout = QVBoxLayout(scroll_content)
        scroll.setWidget(scroll_content)
        # vertical distance between cards - Vertical
        self.scroll_layout.setSpacing(0)
        # spaces between the added Widget and this top, right, bottom, left side
        self.scroll_layout.setContentsMargins(0,0,0,0)
        scroll_content.setLayout(self.scroll_layout)

#        self.card_holder = CardHolder()
#        self.scroll_layout.addWidget(self.card_holder)
#        self.card_holder.setHidden(True)
##        self.card_holder.setHidden(False)
        
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
        
    def add_new_holder(self, previous_holder, new_holder):

        print(previous_holder)
        # if there was previous holder
        if previous_holder:

            # then hide it
            previous_holder.setHidden(True)

        # add the new holder
        self.scroll_layout.addWidget(new_holder)
        
    def restore_previous_holder(self, previous_holder, actual_holder):
        
        self.inner_layout.removeWidget(actual_holder)
        actual_holder.setParent(None)
        
        previous_holder.setHidden(False)
        
        
    def start_card_holder(self):

        previous_holder = None
        card_holder=CardHolder(
            self,
            previous_holder,
            {
                "key" : "all",
                "value" : "",
                "value-store-mode" : "*",
                "paths" : [
                    "/media/akoel/Movies/Final/Films"
                ]                
            }
        )

        self.add_new_holder(previous_holder, card_holder)


        
def main():    
    app = QApplication(sys.argv)
    ex = GuiAkoTeka()
    ex.start_card_holder()
    sys.exit(app.exec_())
    
    
