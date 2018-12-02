import sys
import os

from threading import Thread

from pkg_resources import resource_string, resource_filename

from akoteka.gui.card_holder_pane import CardHolder

from akoteka.accessories import collect_filters

from functools import cmp_to_key

import locale
    
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
        
        paths = [
                    media_path
                ]
        hierarchy = ""
        
        thread = Thread(target=self.fill_up_filters, args=(paths,))
        #thread.daemon = True                            
        thread.start()    
        
        card_holder=CardHolder(
            self,
            previous_holder,
            hierarchy,
            paths
        )

        self.add_new_holder(previous_holder, card_holder)

    def set_back_button_listener(self, listener):
        self.control_panel.set_back_button_listener(listener)
        
    def get_filter_holder(self):
        return self.control_panel.get_filter_holder()
    
    
    #
    # Fills up the Filters
    #
    def fill_up_filters(self, paths):
        
        hit_list = {
            "genre": set(),
            "theme": set(),
            "director": set(),
            "actor": set()        
        }

        for path in paths:
            collect_filters(path, hit_list)
        
        for element in sorted([(_("genre_" + e),e) for e in hit_list['genre']], key=lambda t: locale.strxfrm(t[0]) ):
            self.get_filter_holder().add_genre(element[0], element[1])        
        for element in sorted([(_("theme_" + e), e) for e in hit_list['theme']], key=lambda t: locale.strxfrm(t[0]) ):
            self.get_filter_holder().add_theme(element[0], element[1])
        for element in sorted( hit_list['director'], key=cmp_to_key(locale.strcoll) ):
            self.get_filter_holder().add_director(element)
        for element in sorted( hit_list['actor'], key=cmp_to_key(locale.strcoll) ):
            self.get_filter_holder().add_actor(element)
      

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

#        mylist = []
#        lm = ModelForTranslation(mylist, self)
#        cb = QComboBox(self)
#        cb.setModel(lm)
#        self_layout.addWidget(cb )
        
        
        # Read the actual element from the list
#        print( cb.itemData(cb.currentIndex()) )
        
        self.back_button_listener = None

    def set_back_button_listener(self, listener):
        self.back_button_listener = listener
        
    def back_button_on_click(self):
        if self.back_button_listener:
            self.back_button_listener.go_back()

    def get_filter_holder(self):
        return self.filter_holder

#
# Dropdown HOLDER
#
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
        

# =============================
#
# Filter Drop-Down Simple
#
# =============================
#
class FilterDropDownSimple(QWidget):
    
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

    def add_element(self, value, id):
        self.dropdown.addItem(value, id)

    def get_selected(self):
        return self.dropdown.itemData( self.dropdown.currentIndex() )


class ModelForTranslation(QAbstractTableModel):
    
    """
    datalist: a list where each item is a row
    """

    def __init__ (self, datalist=[], parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.datalist = datalist
    
    # Mandatory
    def rowCount(self, parent=QModelIndex()):
        return len(self.datalist)

    # Mandatory
    def columnCount(self, parent):
        return 2

    # Mandatory
    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        column = index.column()

        if index.isValid() and role == Qt.DisplayRole:
            elements_of_row = self.datalist[row]
            return QVariant(elements_of_row['name'])

        elif index.isValid() and role == Qt.UserRole:
            elements_of_row = self.datalist[row]
            return elements_of_row['id']
        else:
            return QVariant()

    def insertRows(self, position, rows=1, index=QModelIndex()):
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)
        for row in range(rows):
            self.datalist.insert(position + row,  {})
        self.endInsertRows()
        return True

    def setData(self, index, value, role):        
        row = index.row()
        column = index.column()

        # 256 value is for the second position
        if role == Qt.UserRole and column == 0:
            self.datalist[row]['id'] = value
        # 2 value is for the first position
        elif role == Qt.EditRole and column == 0:
            self.datalist[row]['name'] = value
   
        return True


# =================================
#
# Filter Drop-Down Translated 
#
# =================================
class FilterDropDownTranslated(QWidget):
    
    def __init__(self, label):
        super().__init__()

        self_layout = QHBoxLayout(self)
        self_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout( self_layout )
#        self.setStyleSheet( 'background: green')
        
        self_layout.addWidget( QLabel(label))

        self.dropdown = QComboBox(self)
        mylist = []
        tm = ModelForTranslation(mylist, self)
        self.dropdown.setModel(tm)

        style_box = '''
            QComboBox { 
                max-width: 200px; min-width: 200px; border: 1px solid gray; border-radius: 5px;
            }        '''
      
        self.dropdown.setStyleSheet(style_box)
        self.dropdown.addItem("","")

        self_layout.addWidget( self.dropdown )

    #
    # value:    Translated text
    # id:       translation code
    #
    def add_element(self, value, id):
        self.dropdown.addItem(value, id)
       

class FilterCheckBox(QWidget):
    def __init__(self, label):
        super().__init__()

        self_layout = QVBoxLayout(self)
        self_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout( self_layout )
#        self.setStyleSheet( 'background: green')
        
        self.checkbox = QCheckBox(label)
        self.checkbox.setLayoutDirection( Qt.RightToLeft )
        style_checkbox = '''
            QCheckBox { 
                min-height: 15px; max-height: 15px; border: 0px solid gray;
            }
        '''
        self.checkbox.setStyleSheet( style_checkbox )
        
        self_layout.addWidget( self.checkbox)

    def is_checked(self):
        return 'y' if self.checkbox.isChecked() else None

#
# Checkbox HOLDER
#
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
        

#
# Filter HOLDER
#
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
        #self.filter_dd_genre = FilterDropDownTranslated(_('title_genre'))
        #self.filter_dd_theme = FilterDropDownTranslated(_('title_theme'))
        self.filter_dd_genre = FilterDropDownSimple(_('title_genre'))
        self.filter_dd_theme = FilterDropDownSimple(_('title_theme'))
        
        holder_dropdown_gt = FilterDropDownHolder()
        
        holder_dropdown_gt.add_dropdown(self.filter_dd_genre)
        holder_dropdown_gt.add_dropdown(self.filter_dd_theme)
        
        self_layout.addWidget(holder_dropdown_gt)

        #
        # Dropdown - director+actor
        #
        self.filter_dd_director = FilterDropDownSimple(_('title_director'))
        self.filter_dd_actor = FilterDropDownSimple(_('title_actor'))
        
        holder_dropdown_da = FilterDropDownHolder()
        
        holder_dropdown_da.add_dropdown(self.filter_dd_director)
        holder_dropdown_da.add_dropdown(self.filter_dd_actor)
        
        self_layout.addWidget(holder_dropdown_da)

    def add_genre(self, value, id):
        self.filter_dd_genre.add_element(value, id)

    def add_theme(self, value, id):
        self.filter_dd_theme.add_element(value, id)
    
    def add_director(self, director):
        self.filter_dd_director.add_element(director, director)
    
    def add_actor(self, actor):
        self.filter_dd_actor.add_element(actor, actor)
    
    def get_filter_selection(self):
        filter_selection = {
            "best": self.filter_cb_best.is_checked(),
            "new": self.filter_cb_new.is_checked(),
            "favorite": self.filter_cb_favorite.is_checked(),
            "genre": self.filter_dd_genre.get_selected(),
            "theme": self.filter_dd_theme.get_selected(),
            "director": self.filter_dd_director.get_selected(),
            "actor": self.filter_dd_actor.get_selected()
        }
        return filter_selection
    
        
def main():   
    app = QApplication(sys.argv)
    ex = GuiAkoTeka()
    ex.start_card_holder()
    sys.exit(app.exec_())
    
    
