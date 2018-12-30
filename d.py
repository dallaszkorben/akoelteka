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
        self.actual_card_holder.show()
        
        
        self.scroll_layout.addWidget(self.actual_card_holder)

 
        next_button = QPushButton("next")
        next_button.clicked.connect(self.actual_card_holder.select_next_card)
        
        previous_button = QPushButton("prev")
        previous_button.clicked.connect(self.actual_card_holder.select_previous_card)
        
        self.scroll_layout.addWidget(previous_button)
        self.scroll_layout.addWidget(next_button)
        
        self.show()
 
    def get_new_card(self, card_data, local_index, index):
        return Card(card_data, self.actual_card_holder, local_index, index)

 
 
 
 
 
 
MAX_OVERLAPPED_CARDS = 4
 
# =========================
#
# Card Holder
#
# =========================
class CardHolder( QLabel ):
    
    resized = QtCore.pyqtSignal(int,int)
    moved_to_front = QtCore.pyqtSignal(int)
    
    MARGIN = 20    
    
    def __init__(self, parent, recent_card_structure, title_hierarchy, get_new_card):
        super().__init__()

        self.get_new_card = get_new_card
        self.parent = parent
        self.title_hierarchy = title_hierarchy
        self.recent_card_structure = recent_card_structure
        
        self.cards = []
        self.card_list = []
        #self.pool_card_list = cycle(self,card_list)

        # -------------
        #
        # Main Panel
        #
        # ------------
        self.self_layout = QVBoxLayout(self)
        self.setLayout(self.self_layout)
        self.setStyleSheet('background: ' + "#756789")  

        self.fill_up_card_holder()
        
        # start index
        self.actual_card_index = 0

    def show(self):
        self.select_actual_card()
        
   
    def resizeEvent(self, event):
        self.resized.emit(event.size().width(),event.size().height())
        return super(CardHolder, self).resizeEvent(event)
     
    def fill_up_card_holder(self, recent_card_structure = []):

        self.card_list.append("Elso")
        self.card_list.append("Masodik")
        self.card_list.append("Harmadik")
        self.card_list.append("Negyedik")
        self.card_list.append("Otodik")
        self.card_list.append("hatodik")
        self.card_list.append("hetedik")
        self.card_list.append("Nyolcadik")
        self.card_list.append("Kilencedik")
        self.card_list.append("Tizedik")
 
    def remove_cards(self):
        for card in self.cards:
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
        
        for i in range( index_corr + MAX_OVERLAPPED_CARDS, index_corr - 1, -1):
            i_corr = self.index_correction(i)
            
            if( i_corr < len(self.card_list)):

                #card = Card(self.card_list[i_corr], self, i-index_corr, i_corr )
                card = self.get_new_card(self.card_list[i_corr], i-index_corr, i_corr )
                
                self.cards.append(card)

    def index_correction(self, index):
        return (len(self.card_list) - abs(index) if index < 0 else index) % len(self.card_list)



# ==================
#
# Card
#
# ==================
class Card(QWidget):
    
    MARGIN = 4
    RATE_OF_WIDTH_DECLINE = 10
    
    def __init__(self, card_data, parent, local_index, index):
        super().__init__(parent)

        self.card_data = card_data
        self.index = index
        self.local_index = local_index
        self.parent = parent
        self.actual_position = 0
        self.self_layout = QVBoxLayout(self)
        self.setLayout(self.self_layout)
        self.self_layout.setContentsMargins(Card.MARGIN, Card.MARGIN, Card.MARGIN, Card.MARGIN)  
        self.self_layout.setSpacing(5)
        self.setStyleSheet('background: ' + "#ccaaaa")   
        
        self.borderRadius = 10
        
        label=QLabel(card_data + "\n\n\n\n\n\n\n\n\n\nHello")
        self.self_layout.addWidget(label)
        
        # Place the Card to the right position
        self.place(local_index)
        
        # Connect the widget to the Container's Resize-Event
        self.parent.resized.connect(self.resized)
        
        # Show the Card in the right position
        self.show()
        
        #self.setDragEnabled(True)
        self.setAcceptDrops(True)
 
    def paintEvent(self, event):
        s = self.size()
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing, True)
        qp.setBrush( QColor( "#00cc00" ))

        qp.drawRoundedRect(0, 0, s.width(), s.height(), self.borderRadius, self.borderRadius)
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
        return  self.local_index * self.RATE_OF_WIDTH_DECLINE
 
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
        standard_width = width - 2*CardHolder.MARGIN - 2*self.get_x_offset()
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
        #y_position = CardHolder.MARGIN + ( MAX_OVERLAPPED_CARDS - local_index ) * 30
        y_position = CardHolder.MARGIN + ( MAX_OVERLAPPED_CARDS - local_index ) * ( MAX_OVERLAPPED_CARDS - local_index ) * 6
        self.move( CardHolder.MARGIN + self.get_x_offset(), y_position )

class MyCard(Card):
   def __init__(self, card_daa, parent, local_index, index):
        super().__init__(card_data, parent, local_index, index)
    

  
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    #ex.start_card_holder()
    sys.exit(app.exec_())
