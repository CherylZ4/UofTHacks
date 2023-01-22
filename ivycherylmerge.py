from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6 import QtCore, QtGui
from pathlib import Path
import cloudvision
import cohereapi
import photoshoot
from PyQt6.QtGui import QIcon 
import sys

global objCoord

def grabAllDef(initialdict: dict):
    print('Run grabAllDef')
    finaldict = {}
    for keys in initialdict:
        finaldict[keys] = cohereapi.grabDefinition(keys)
        print(keys)
    print(finaldict)
    return finaldict


global current_obj

global defDict

class ImageWindow(QMainWindow):
    def __init__(self, file_name):
        super().__init__()
        self.setMouseTracking(True)
        self.w = None
        self.size = self.screen().size()
        self.setWindowTitle("Retina")
        self.setGeometry(100, 100, 800, 600)
        self.showMaximized()
        label = QLabel(self)
        self.pixmap = QPixmap(file_name)
        label.setPixmap(self.pixmap)
        # x = pixmap.width()
        # y = pixmap.height()
        self.setCentralWidget(label)
        self.resize(self.pixmap.width(), self.pixmap.height())
    
    def objClicked(self, event):
        global objCoord
        global current_obj
        pos = event.pos()
        for obj in objCoord:
            print(pos.x(), pos.y())
            if objCoord[obj][0][0] * self.pixmap.width() <= pos.x() <= objCoord[obj][2][0] * self.pixmap.width():
                if objCoord[obj][0][1] * self.pixmap.height() <= pos.y() <= objCoord[obj][2][1] * self.pixmap.height():
                    current_obj = obj
                    return True

        

    def mousePressEvent(self, event):
        pos = event.pos()
        if self.objClicked(event): 
            self.show_new_window(pos.x(), pos.y())

    def show_new_window(self, x, y):
        if self.w is None:
            self.w = Definition(x, y)
            self.w.show()
        else:
            self.w.close()
            self.w = None
    
    def closeEvent(self, event):
        if self.w:
            self.w.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Retina")
        self.setAutoFillBackground(True)
        self.setStyleSheet('background-color: #DBF0FF')
        button = QPushButton("+ Upload image", self)
        button.setFont(QFont('italic', 25))
        button.setGeometry(self.height()-200, self.width() - 430, 1050, 600)
        button.clicked.connect(self.open_image)
        button.setStyleSheet("border-style: outset; border-radius: 15px; margin: auto; background-color: #8BC3EB; font-weight:bold; font-size:40px; padding: 15px; width: 75%; font-style:italic")
        header = QLineEdit("Find Image Object Name and Definition", self)
        header.resize(800, 200)
        header.move(self.height()-200, self.width()-625)
        header.setFont(QFont('italic', 30))
        header.setStyleSheet("background-color: #73A4C8; margin:auto; font-weight: bold; font-size:35px; font-style:italic; border: 2px solid; border-radius:10px; padding: 15px")
        subheader = QLineEdit("Click on the object for definition", self)
        subheader.setGeometry(self.height()+350, self.width()-525, 450, 130)
        subheader.setStyleSheet("border-radius: 15px; margin:auto; background-color: #8DEDF9; opacity: 40%; padding: 15px; font-weight: bold; font-style:italic; font-size: 20px")
        
        abutton2 = QPushButton("Take photo", self)
        abutton2.setGeometry(self.height()+190, self.width()+160, 200, 50)
        abutton2.setStyleSheet("font-size: 20px; background-color: #4BB3FF;")
        abutton2.clicked.connect(self.take_photo)

        self.showMaximized()
        self.size = self.screen().size()

    def take_photo(self):
        global objCoord
        global defDict
        path = photoshoot.openCam()
        objCoord = cloudvision.grabobjects(path)
        defDict = grabAllDef(objCoord)
        print(objCoord)
        print(self.size.width(), self.size.height())
        if path:
            self.hide()
            self.image_window = ImageWindow(path)
            self.image_window.show()

    def open_image(self):
        global objCoord
        global defDict
        options = QFileDialog.Option.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","Images (*.png *.xpm *.jpg *.bmp);;All Files (*)", options=options)
        print(file_name)
        objCoord = cloudvision.grabobjects(file_name)
        defDict = grabAllDef(objCoord)
        print(objCoord)
        print(self.size.width(), self.size.height())

        if file_name:
            self.hide()
            self.image_window = ImageWindow(file_name)
            self.image_window.show()

class Color(QWidget):

    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)
        self.setStyleSheet('background-color: #DBF0FF')

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor)
        self.setPalette(palette)


class Definition(QWidget):
    
    def __init__(self, x, y):
        super().__init__()
        self.setFixedSize(500,400)
        layout = QVBoxLayout()
        self.setWindowTitle('Definition')

        global current_obj
        global defDict

        self.label = QLabel()
        self.label.setWordWrap(True)

        worddef = defDict[current_obj]
        print(worddef)
        self.label.setText(current_obj + '\n__________\n\n' + worddef)
        self.label.setStyleSheet(
            "background-color: #DBF0FF;"
            "font-family: times; "
            "font-size: 20px;"
            "color: #0D2333;"
        )
        
        self.label.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.label)

        self.setLayout(layout)



        self.move(x, y)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = MainWindow()
    #with open("style.qss", "r") as file:
       # app.setStyleSheet(file.read())
    window.show()
    sys.exit(app.exec())
