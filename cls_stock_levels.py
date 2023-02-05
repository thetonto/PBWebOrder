from PyQt5 import QtCore, QtWidgets, Qt, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import sys
from pb_Woo_Order_Class import PbWooCommerce

# Setup Logging
# logger.debug('My message with %s', 'variable data')
import logging
logger = logging.getLogger(__name__)

class stockUI(QtWidgets.QWidget):
    #Create signals for the communication with worker threads - Note to specify the params being sent
    update_order_requested = pyqtSignal(dict, str)
    load_order_requested = pyqtSignal(str)


    def __init__(self):
        super(stockUI, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('ui_stock.ui', self)  # Load the .ui file
        self.show()  # Show the GUI


        # Add connections to slots
        self.btnLookup.clicked.connect(self.get_stockLevel)
        self.pbOutOfStock.clicked.connect(self.setOutOfStock)
        self.pbAvailable.clicked.connect(self.setInStock)

    @QtCore.pyqtSlot()
    def get_stockLevel(self):
        #refresh the orders list
        print("Getting Stock Levels")
        plu = self.textPLU.toPlainText()
        wc = PbWooCommerce()
        if len(plu):
            stockData = wc.get_stock_level(plu)
            self.lblStockDescription.setText(stockData[0]['name'])
            self.lblStatus.setText('Status: ' + stockData[0]['stock_status'])
            self.ProductID = stockData[0]['id']

    @QtCore.pyqtSlot()
    def setOutOfStock(self):
        wc = PbWooCommerce()
        result = wc.update_stock_level(self.ProductID,'outofstock')
        self.lblStatus.setText('Status: ' + 'outofstock')


    @QtCore.pyqtSlot()
    def setInStock(self):
        wc = PbWooCommerce()
        result = wc.update_stock_level(self.ProductID, 'instock')
        self.lblStatus.setText('Status: ' + 'instock')