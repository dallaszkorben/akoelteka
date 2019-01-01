import sys
from akoteka.gui.pyqt_import import *
from itertools import cycle

class App(QWidget):
 
    def __init__(self):
        super().__init__()
        self.title = 'Card selector'
        self.left = 10
        self.top = 10
        self.width = 420
        self.height = 300
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height) 
        self.setStyleSheet('background: gray')
 
        self.scroll_layout = QVBoxLayout(self)
        self.scroll_layout.setContentsMargins(15, 15, 15, 15)
        self.scroll_layout.setSpacing(0)
        self.setLayout(self.scroll_layout)

        self.actual_card_holder = CardHolder(            
            self, 
            [],
            "Kezdocim",
            self.get_new_card
        )
        
        self.actual_card_holder.set_background_color(QColor(Qt.yellow))
        self.actual_card_holder.set_border_width(5)
        self.scroll_layout.addWidget(self.actual_card_holder)
        
        cdl = []        
        cdl.append("Elso")
        cdl.append("Masodik")
        cdl.append("Harmadik")
        cdl.append("Negyedik")
        cdl.append("Otodik")
        self.actual_card_holder.refresh(cdl)
        
        
 
        next_button = QPushButton("next",self)
        next_button.clicked.connect(self.actual_card_holder.select_next_card)
        
        previous_button = QPushButton("prev",self)
        previous_button.clicked.connect(self.actual_card_holder.select_previous_card)
        
        #self.scroll_layout.addStretch(1)
        self.scroll_layout.addWidget(previous_button)
        self.scroll_layout.addWidget(next_button)
        
        self.show()
 
    def get_new_card(self, card_data, local_index, index):
        card = Card(card_data, self.actual_card_holder, local_index, index)
        #card.set_border_color(QColor(Qt.blue))
        #card.set_background_color(QColor(Qt.green))
        #card.set_border_radius( 15 )
        #card.set_border_width(8)
        
        panel = card.get_panel()
        layout = panel.get_layout()
        
        # Construct the Card
        label=QLabel(card_data + "\n\n\n\n\n\n\n\n\n\nHello")
        layout.addWidget(label)
        layout.addWidget(QPushButton("hello"))
        
        return card

 
 
 
 
 
 

 
# =========================
#
# Card Holder
#
# =========================
class CardHolder( QWidget ):
    
    resized = QtCore.pyqtSignal(int,int)
    moved_to_front = QtCore.pyqtSignal(int)

    DEFAULT_MAX_OVERLAPPED_CARDS = 4    
    DEFAULT_BORDER_WIDTH = 5
    DEFAULT_BACKGROUND_COLOR = QColor(Qt.red)
    DEFAULT_BORDER_RADIUS = 10
    
    def __init__(self, parent, recent_card_structure, title_hierarchy, get_new_card):
        super().__init__()

        self.get_new_card = get_new_card
        self.parent = parent
        self.title_hierarchy = title_hierarchy
        self.recent_card_structure = recent_card_structure
        
        self.shown_card_list = []
        self.card_descriptor_list = []

        self.set_max_overlapped_cards(CardHolder.DEFAULT_MAX_OVERLAPPED_CARDS, False)        
        self.set_border_width(CardHolder.DEFAULT_BORDER_WIDTH, False)
        self.set_border_radius(CardHolder.DEFAULT_BORDER_RADIUS, False)
        self.set_background_color(CardHolder.DEFAULT_BACKGROUND_COLOR, False)
        
        self.self_layout = QVBoxLayout(self)
        self.setLayout(self.self_layout)

        self.actual_card_index = 0
        self.show()

    def refresh(self, filtered_card_list): 
        self.fill_up_card_descriptor_list(filtered_card_list)
        self.select_actual_card()        

    def set_border_width(self, width, update=True):
        self.border_width = width
        if update:
            self.update()
        
    def get_border_width(self):
        return self.border_width

    def set_background_color(self, color, update=True):
        self.background_color = color
        ## without this line it wont paint the background, but the children get the background color info
        ## with this line, the rounded corners will be ruined
        #self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        #self.setStyleSheet('background-color: ' + self.background_color.name())
        if update:
            self.update()
        
    def set_max_overlapped_cards(self, number, update=True):
        self.max_overlapped_cards = number
        if update:
            self.select_index(self.actual_card_index)
        
    def set_border_radius(self, radius, update=True):
        self.border_radius = radius
        if update:
            self.update()
        
    def get_max_overlapped_cards(self):
        return self.max_overlapped_cards
  
    def resizeEvent(self, event):
        self.resized.emit(event.size().width(),event.size().height())
        return super(CardHolder, self).resizeEvent(event)
     
    def fill_up_card_descriptor_list(self, filtered_card_list = []):
        
        self.card_descriptor_list = []
        for c in filtered_card_list:
            self.card_descriptor_list.append(c)
 
    def remove_cards(self):
        for card in self.shown_card_list:
            card.setParent(None)
            card = None

    def select_next_card(self):
        self.select_index(self.actual_card_index + 1)

    def select_previous_card(self):
        self.select_index(self.actual_card_index - 1)
        
    def select_actual_card(self):
        self.select_index(self.actual_card_index)
    
    def select_index(self, index):
        index_corr = self.index_correction(index)
        
        self.actual_card_index = index_corr
        self.remove_cards()
        
        for i in range( index_corr + min(self.max_overlapped_cards, len(self.card_descriptor_list)-1), index_corr - 1, -1):
            i_corr = self.index_correction(i)
            
            if( i_corr < len(self.card_descriptor_list)):

                local_index = i-index_corr
                card = self.get_new_card(self.card_descriptor_list[i_corr], local_index, i_corr )                                
                card.place(local_index)
                
                self.shown_card_list.append(card)

    def index_correction(self, index):
        return (len(self.card_descriptor_list) - abs(index) if index < 0 else index) % len(self.card_descriptor_list)

    def paintEvent(self, event):
        s = self.size()
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing, True)
        qp.setBrush( self.background_color )

        qp.drawRoundedRect(0, 0, s.width(), s.height(), self.border_radius, self.border_radius)
        qp.end()  

    def wheelEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        value = event.angleDelta().y()/8/15
        if value > 0:
            self.select_next_card()
        else:
            self.select_previous_card()
        
# ==================
#
# Panel
#
# ==================
class Panel(QWidget):
    DEFAULT_BORDER_WIDTH = 5
    DEFAULT_BACKGROUND_COLOR = QColor(Qt.lightGray)
    
    def __init__(self):
        super().__init__()
        
        self.self_layout = QVBoxLayout()
        self.self_layout.setSpacing(1)
        self.setLayout(self.self_layout)

        self.set_background_color(Panel.DEFAULT_BACKGROUND_COLOR, False)        
        self.set_border_width(Panel.DEFAULT_BORDER_WIDTH, False)
        #self.set_border_radius(border_radius, False)


    def get_layout(self):
        return self.self_layout
    
    def set_border_radius(self, radius, update=True):
        self.border_radius = radius
        if update:
            self.update()
        
    def set_border_width(self, width, update=True):
        self.border_width = width
        self.self_layout.setContentsMargins( self.border_width, self.border_width, self.border_width, self.border_width )
        if update:
            self.update()

    def set_background_color(self, color, update=True):
        self.background_color = color
        
        ## without this line it wont paint the background, but the children get the background color info
        ## with this line, the rounded corners will be ruined
        #self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet('background-color: ' + self.background_color.name())
        
        if update:            
            self.update()
    
    def paintEvent(self, event):
        s = self.size()
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing, True)
        qp.setBrush( self.background_color )

        qp.drawRoundedRect(0, 0, s.width(), s.height(), self.border_radius, self.border_radius)
        qp.end()    
    

# ==================
#
# Card
#
# ==================
class Card(QWidget):
    
    DEFAULT_RATE_OF_WIDTH_DECLINE = 10
    DEFAULT_BORDER_WIDTH = 2
    DEFAULT_BORDER_RADIUS = 10    
    DEFAULT_BORDER_COLOR = QColor(Qt.green)
    
    def __init__(self, card_data, parent, local_index, index):
        super().__init__(parent)

        self.card_data = card_data
        self.index = index
        self.local_index = local_index
        self.parent = parent
        self.actual_position = 0

        
        self.self_layout = QVBoxLayout(self)
        self.setLayout(self.self_layout)
        #self.self_layout.setContentsMargins(self.border_width,self.border_width,self.border_width,self.border_width)
        self.self_layout.setSpacing(0)
        
        ## without this line it wont paint the background, but the children get the background color info
        ## with this line, the rounded corners will be ruined
        #self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        #self.setStyleSheet('background-color: ' + "yellow")  





        # Panel where the content could be placed
        self.panel = Panel()
        self.panel_layout = self.panel.get_layout()
        self.self_layout.addWidget(self.panel)
        
        self.border_radius = Card.DEFAULT_BORDER_RADIUS
        self.set_border_width(Card.DEFAULT_BORDER_WIDTH, False)
        self.set_border_radius(Card.DEFAULT_BORDER_RADIUS, False)        
        self.set_rate_of_width_decline(Card.DEFAULT_RATE_OF_WIDTH_DECLINE, False)
        self.set_border_color(Card.DEFAULT_BORDER_COLOR, False)
        
        
        
        
        
        
        # Connect the widget to the Container's Resize-Event
        self.parent.resized.connect(self.resized)
        
        #self.setDragEnabled(True)
#        self.setAcceptDrops(True)
 
 
    def set_background_color(self, color):
        #self.background_color = color
        #self.setStyleSheet('background-color: ' + self.background_color.name())
        #self.update()
        self.panel.set_background_color(color)

    def set_border_color(self,color, update=True):
        self.border_color = color
        if update:
            self.update()      

    def set_border_width(self, width, update=True):
        self.border_width = width
        self.self_layout.setContentsMargins(self.border_width,self.border_width,self.border_width,self.border_width)
        self.panel.set_border_radius(self.border_radius - self.border_width, update)
        if update:
            self.update()

    def set_border_radius(self, radius, update=True):
        self.border_radius = radius
        self.panel.set_border_radius(self.border_radius - self.border_width, update)
        if update:
            self.update()

    def set_rate_of_width_decline(self, rate, update=True):
        self.rate_of_width_decline = rate
    
    
    def get_panel(self):
        return self.panel
 
    # -----------------------------------------------------
    # Overwrite the rate of the width's decline if you will
    # -----------------------------------------------------
    def get_rate_of_width_decline(self):
        return self.RATE_OF_WIDTH_DECLINE
 
    def paintEvent(self, event):
        s = self.size()
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing, True)
        qp.setBrush( self.border_color)

        qp.drawRoundedRect(0, 0, s.width(), s.height(), self.border_radius, self.border_radius)
        qp.end()
 
    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return
        drag = QDrag(self)
        mimedata = QMimeData()
        
        #mimedata.setText(self.text())
        mimedata.setText(str(self.index))
        
        drag.setMimeData(mimedata)
        pixmap = QPixmap(self.size())
        painter = QPainter(pixmap)
        painter.drawPixmap(self.rect(), self.grab())
        painter.end()
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())
        drag.exec_(Qt.CopyAction | Qt.MoveAction)
 
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()
        print("pressed:", self.card_data, self.index)
        #self.parent.resized.connect(self.resized)
        #self.parent.moved_to_front.emit(self.index)
        
        if self.local_index != 0:
            self.parent.select_index(self.index)
        
    def dragEnterEvent(self, e):
        print( "entered:", self.index, e.mimeData().text() )
           
   
    # ---------------------------------------------
    # The offset of the Card from the left side as 
    # 'The farther the card is the narrower it is'
    # ---------------------------------------------
    def get_x_offset(self):
        return  self.local_index * self.rate_of_width_decline
 
    # ----------------------------------------
    #
    # Resize the width of the Card
    #
    # It is called when:
    # 1. CardHolder emits a resize event
    # 2. The Card is created and Placed
    #
    # ----------------------------------------
    def resized(self, width, height):
        # The farther the card is the narrower it is
        standard_width = width - 2*self.parent.get_border_width() - 2*self.get_x_offset()
        self.resize( standard_width, self.sizeHint().height() )

    # ---------------------------------------
    #
    # Place the Card into the given position
    #
    # 0. position means the card is in front
    # 1. position is behind the 0. position
    # and so on
    # ---------------------------------------
    def place(self, local_index):
        
        # Need to resize and reposition the Car as 'The farther the card is the narrower it is'
        self.resized(self.parent.width(), self.parent.height())
        y_position = self.parent.get_border_width() + ( self.parent.get_max_overlapped_cards() - local_index ) * ( self.parent.get_max_overlapped_cards() - local_index ) * 6
        self.move( self.parent.get_border_width() + self.get_x_offset(), y_position )
        
        self.show()









        

  
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    #ex.start_card_holder()
    sys.exit(app.exec_())
