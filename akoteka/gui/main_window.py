import sys
import os

from pkg_resources import resource_string, resource_filename

from akoteka.gui.card_holder_pane import CardHolder
    
from akoteka.gui.glob import *

class ControlPanel(QWidget):
    def __init__(self):
        super().__init__()        
        
        self_layout = QHBoxLayout(self)
        self.setLayout(self_layout)
        
        # controls the distance between the MainWindow and the added container: scrollContent
        self_layout.setContentsMargins(3, 3, 3, 3)
        self_layout.setSpacing(5)
        
        back_button = QPushButton()
        back_button.clicked.connect(self.back_button_on_click)
        
        back_button.setIcon( QIcon( resource_filename(__name__,os.path.join("img", "back-button.jpg")) ))
        back_button.setIconSize(QSize(32,32))
        back_button.setCursor(QCursor(Qt.PointingHandCursor))
        back_button.setStyleSheet("background:transparent; border:none") 

        self_layout.addWidget( back_button )

        self_layout.addStretch(1)
        
        self.back_button_listener = None

    def set_back_button_listener(self, listener):
        self.back_button_listener = listener
        
    def back_button_on_click(self):
        if self.back_button_listener:
            self.back_button_listener.go_back()

class GuiAkoTeka(QWidget):
    
    def __init__(self):
        super().__init__()        
        
        # most outer container, just right in the Main Window
        box_layout = QVBoxLayout(self)
        self.setLayout(box_layout)
        # controls the distance between the MainWindow and the added container: scrollContent
        box_layout.setContentsMargins(0, 0, 0, 0)
        box_layout.setSpacing(0)
    
        # control line
        self.control_panel = ControlPanel()
        box_layout.addWidget( self.control_panel)
    
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

        self.back_button_listener = None

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

        ## if there was previous holder
        if previous_holder:

            # then hide it
            previous_holder.setHidden(True)

        # add the new holder
        self.scroll_layout.addWidget(new_holder)
        
    def restore_previous_holder(self, previous_holder, actual_holder):
        
        if previous_holder:
            self.scroll_layout.removeWidget(actual_holder)
            actual_holder.setParent(None)
        
            previous_holder.setHidden(False)
        
        
    def start_card_holder(self):

        previous_holder = None
        card_holder=CardHolder(
            self,
            previous_holder,
            {
                "key" : "genre",
                "value" : "animation",
                "value-store-mode" : "a",
                "paths" : [
                    "/media/akoel/Movies/Final/Films"
                ]                
            }
        )

        self.add_new_holder(previous_holder, card_holder)

    def set_back_button_listener(self, listener):
        self.control_panel.set_back_button_listener(listener)
        
def main():    
    app = QApplication(sys.argv)
    ex = GuiAkoTeka()
    ex.start_card_holder()
    sys.exit(app.exec_())
    
    
