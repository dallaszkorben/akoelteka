import sys
import os

from akoteka.gui.glob import *
from akoteka.gui.glob import _
from akoteka.gui import glob

from pkg_resources import resource_string, resource_filename


# ====================
#
# Configuration Dialog
#
# ====================
class ConfigurationDialog(QDialog):

    def __init__(self):
        super().__init__()    
    
        self.setWindowTitle(_('title_settings'))
        self.resize(400, 113)

        self.self_layout = QVBoxLayout(self)
        self.setLayout(self.self_layout)
        
        self.content_section = ContentSection()
        self.self_layout.addWidget(self.content_section)
        
        self.self_layout.addStretch(1)
        
        button_box_section = ButtonBoxSection(self)
        self.self_layout.addWidget(button_box_section)
        
        # language
        self.language_selector = LanguageSelector(glob.language)
        self.content_section.addWidget(self.language_selector)
        
        # media path
        self.media_path_selector = MediaPathSelector(glob.media_path)
        self.content_section.addWidget(self.media_path_selector)
        
        # video player
        
        # video player parameters        
    
    def get_media_path(self):
        return self.media_path_selector.get_media_path()
        
    def get_language(self):
        return self.language_selector.get_language()
    

class ContentSection(QWidget):
        def __init__(self):
            super().__init__()    
    
            self.self_layout = QVBoxLayout(self)
            self.setLayout(self.self_layout)
        
        def addWidget(self, widget):
            self.self_layout.addWidget(widget)

class ButtonBoxSection(QWidget):
        def __init__(self, parent):
            super().__init__()    
    
            self.self_layout = QHBoxLayout(self)
            self.setLayout(self.self_layout)
            
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            self.self_layout.addWidget( button_box )

            button_box.button(QDialogButtonBox.Ok).setText(_('button_ok'))
            button_box.button(QDialogButtonBox.Cancel).setText(_('button_cancel'))
            button_box.accepted.connect(parent.accept)
            button_box.rejected.connect(parent.reject)
            
        
# ====================
#
# Language Selector
#
# ====================
class LanguageSelector(QWidget):
    
    def __init__(self, default_language):
        super().__init__()    
    
        self_layout=QHBoxLayout(self)
        self.setLayout(self_layout)

        self_layout.addWidget(QLabel(_('title_language') + ':'))
        
        self.language_combo = QComboBox()
        self.language_combo.addItem(_('lang_hu'), 'hu')
        self.language_combo.addItem(_('lang_en'), 'en')
        self_layout.addWidget(self.language_combo)
        
        self.language_combo.setCurrentIndex( self.language_combo.findData(default_language) )

    def get_language(self):
        return self.language_combo.itemData( self.language_combo.currentIndex() )

# ====================
#
# Media Path Selector
#
# ====================
class MediaPathSelector(QWidget):
    
    def __init__(self, default_media_path):
        super().__init__()    
    
        self_layout=QHBoxLayout(self)
        self.setLayout(self_layout)

        # Title
        self_layout.addWidget(QLabel(_('title_media_path') + ':'))

        # Text Field
        self.folder_field = QLineEdit(self)
        self.folder_field.setText(default_media_path)
        self_layout.addWidget(self.folder_field)
        
        # Button
        self.folder_selector_button = QPushButton()
        self.folder_selector_button.setCheckable(False)
        selector_icon = QIcon()
        selector_icon.addPixmap(QPixmap( resource_filename(__name__,os.path.join("img", IMG_FOLDER_BUTTON)) ), QIcon.Normal, QIcon.On)
        self.folder_selector_button.setIcon( selector_icon )
        self.folder_selector_button.setIconSize(QSize(25,25))
        self.folder_selector_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.folder_selector_button.setStyleSheet("background:transparent; border:none") 
        self.folder_selector_button.clicked.connect(self.select_folder_button_on_click)

        self_layout.addWidget(self.folder_selector_button)


    def get_media_path(self):
        return self.folder_field.text()
    
    def select_folder_button_on_click(self):
        
        folder = QFileDialog.getExistingDirectory(self, _('title_select_media_directory'), glob.media_path, QFileDialog.ShowDirsOnly)
        
        if folder:
            self.folder_field.setText(folder)
        




