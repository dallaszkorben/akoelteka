from PyQt5.QtCore import QUrl 
from PyQt5.QtWidgets import QApplication 
from PyQt5.QtWebEngineWidgets import QWebEngineView 
import sys


app = QApplication(sys.argv) 
browser = QWebEngineView()
browser.load(QUrl("http://localhost:8000/index.html"))

browser.show()
sys.exit(app.exec_()) 

