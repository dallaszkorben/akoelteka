import sys
import os

from pkg_resources import resource_string, resource_filename

from akoteka.gui.card_holder_pane import CardHolder
    
from akoteka.gui.glob import *
from akoteka.gui.glob import _

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
                "key" : "all",       #all, best, new, favorite, director, actor, theme, genre
                "value" : "",
                "hierarchy" : "",
                "paths" : [
                    "/media/akoel/Movies/Final"
                ]                
            }
        )

        self.add_new_holder(previous_holder, card_holder)

    def set_back_button_listener(self, listener):
        self.control_panel.set_back_button_listener(listener)
        
    def get_filter(self):
        return self.control_panel.get_filter_holder()

# =========================================
#
# Control Panel on the TOP of the Window
#
# Contains:
#           Back Button
#           Filter
#
# =========================================
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

        # Back button on the left
        self_layout.addWidget( back_button )

        self_layout.addStretch(1)
        
        self.filter_holder = FilterHolder()
        
        # Filter on the right
        self_layout.addWidget(self.filter_holder)
        
        self.back_button_listener = None

    def set_back_button_listener(self, listener):
        self.back_button_listener = listener
        
    def back_button_on_click(self):
        if self.back_button_listener:
            self.back_button_listener.go_back()

    def get_filter_holder(self):
        return self.filter_holder

class FilterDropDownHolder(QWidget):
    
    def __init__(self):
        super().__init__()

        self.self_layout = QVBoxLayout(self)
        self.setLayout( self.self_layout )
        self.self_layout.setContentsMargins(0, 0, 0, 0)
        self.self_layout.setSpacing(1)

#        self.setStyleSheet( 'background: green')

    def add_dropdown(self, filter_dropdown):
        self.self_layout.addWidget(filter_dropdown)
        

class FilterDropDown(QWidget):
    
    def __init__(self, label):
        super().__init__()

        self_layout = QHBoxLayout(self)
        self_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout( self_layout )
#        self.setStyleSheet( 'background: green')
        
        self_layout.addWidget( QLabel(label))

        self.dropdown = QComboBox(self)

        # TODO does not work to set the properties of the dropdown list. find out and fix
        style =             '''
            QComboBox { max-width: 200px; min-width: 200px; min-height: 15px; max-height: 15px;}
            QComboBox QAbstractItemView::item { min-width:100px; max-width:100px; min-height: 150px;}
            QListView::item:selected { color: red; background-color: lightgray; min-width: 1000px;}"
            '''            

        style_down_arrow = '''
            QComboBox::down-arrow { 
                image: url( ''' + resource_filename(__name__,os.path.join("img", "back-button.jpg")) + ''');
                
            }
        '''
        style_box = '''
            QComboBox { 
                max-width: 200px; min-width: 200px; border: 1px solid gray; border-radius: 5px;
            }
        '''
#       max-width: 200px; min-width: 200px; min-height: 1em; max-height: 1em; border: 1px solid gray; border-radius: 5px;
        
        style_drop_down ='''
            QComboBox QAbstractItemView::item { 
                color: red;
                max-height: 15px;
            }
        '''            
      
        self.dropdown.setStyleSheet(style_box + style_drop_down)
        self.dropdown.addItem("")

        self_layout.addWidget( self.dropdown )

    def add_element(self, element):
        self.dropdown.addItem(element)
        

class FilterCheckBox(QWidget):
    def __init__(self, label):
        super().__init__()

        self_layout = QVBoxLayout(self)
        self_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout( self_layout )
#        self.setStyleSheet( 'background: green')
        
        checkbox = QCheckBox(label)
        checkbox.setLayoutDirection( Qt.RightToLeft )
        style_checkbox = '''
            QCheckBox { 
                min-height: 15px; max-height: 15px; border: 0px solid gray;
            }
        '''
        checkbox.setStyleSheet( style_checkbox )
        
        self_layout.addWidget( checkbox)

class FilterCheckBoxHolder(QWidget):
    
    def __init__(self):
        super().__init__()

        self.self_layout = QVBoxLayout(self)
        self.setLayout( self.self_layout )
        self.self_layout.setContentsMargins(0, 0, 0, 0)
        self.self_layout.setSpacing(1)

        #self.setStyleSheet( 'background: green')
        
    def add_checkbox(self, filter_checkbox):
        self.self_layout.addWidget(filter_checkbox)
        

class FilterHolder(QWidget):
    def __init__(self):
        super().__init__()

        self_layout = QHBoxLayout(self)
        self.setLayout( self_layout )
        self_layout.setContentsMargins(0, 0, 0, 0)
        self_layout.setSpacing(8)    
        
        #
        # Checkboxes
        #
        self.filter_cb_best = FilterCheckBox(_('title_best'))
        self.filter_cb_new = FilterCheckBox(_('title_new'))
        self.filter_cb_favorite = FilterCheckBox(_('title_favorite'))
        
        holder_checkbox = FilterCheckBoxHolder()
                
        holder_checkbox.add_checkbox(self.filter_cb_best)
        holder_checkbox.add_checkbox(self.filter_cb_new)
        holder_checkbox.add_checkbox(self.filter_cb_favorite)
                
        self_layout.addWidget(holder_checkbox)

        #
        # Dropdown - genre+theme
        #
        self.filter_dd_genre = FilterDropDown(_('title_genre'))
        self.filter_dd_theme = FilterDropDown(_('title_theme'))
        
        holder_dropdown_gt = FilterDropDownHolder()
        
        holder_dropdown_gt.add_dropdown(self.filter_dd_genre)
        holder_dropdown_gt.add_dropdown(self.filter_dd_theme)
        
        self_layout.addWidget(holder_dropdown_gt)

        #
        # Dropdown - director+actor
        #
        self.filter_dd_director = FilterDropDown(_('title_director'))
        self.filter_dd_actor = FilterDropDown(_('title_actor'))
        
        holder_dropdown_da = FilterDropDownHolder()
        
        holder_dropdown_da.add_dropdown(self.filter_dd_director)
        holder_dropdown_da.add_dropdown(self.filter_dd_actor)
        
        self_layout.addWidget(holder_dropdown_da)

    def add_genre(self, genre):
        self.filter_dd_genre.add_element(genre)

    def add_theme(self, theme):
        self.filter_dd_theme.add_element(theme)
    
    def add_director(self, director):
        self.filter_dd_director.add_element(director)
    
    def add_actor(self, actor):
        self.filter_dd_actor.add_element(actor)
    
    
    
        
def main():    
    app = QApplication(sys.argv)
    ex = GuiAkoTeka()
    ex.start_card_holder()
    sys.exit(app.exec_())
    
    
