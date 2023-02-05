
import sys
from PyQt5 import QtCore, QtGui, QtWidgets, Qt, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import *

def window():
   app = QApplication(sys.argv)
   w = QWidget()
   b = QPushButton(w)
   b.setText("Show message!")

   b.move(50 ,50)
   b.clicked.connect(show_information_dialog)
   w.setWindowTitle("PyQt Dialog demo")
   w.show()
   sys.exit(app.exec_())

def showdialog():
   #Sample Dialog with various options.  Keep for the reference.
   msg = QMessageBox()
   msg.setIcon(QMessageBox.Information)

   msg.setText("Order Items have been saved")
   msg.setInformativeText("This is additional information")
   msg.setWindowTitle("PB - Order Packing")
   msg.setDetailedText("The details are as follows:")
   msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
   msg.buttonClicked.connect(msgbtn)

   retval = msg.exec_()
   print ("value of pressed message box button:", retval)

def msgbtn(i):
   print ("Button pressed is:" ,i.text())


def show_information_dialog(message_text):
   msg = QMessageBox()
   msg.setIcon(QMessageBox.Information)
   msg.setText(message_text)
   msg.setWindowTitle("PB - Order Packing")
   msg.setStandardButtons(QMessageBox.Ok)
   retval = msg.exec_()
   return retval

def show_warning_dialog(message_text):
   msg = QMessageBox()
   msg.setIcon(QMessageBox.Warning)
   msg.setText(message_text)
   msg.setWindowTitle("PB - Order Packing")
   msg.setStandardButtons(QMessageBox.Ok)
   retval = msg.exec_()
   return retval

if __name__ == '__main__':
   window()