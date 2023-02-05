
from PyQt5 import QtCore, QtWidgets, Qt, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import sys
from pb_Woo_Order_Class import PbWooCommerce
from cls_web_order import webOrderUI
from cls_stock_levels import stockUI
import fnc_meta_processing
import dialog_functions
import delivery_note_printing

# Setup Logging
# logger.debug('My message with %s', 'variable data')
import logging
logger = logging.getLogger(__name__)



#Set some column constants
COL_READY_DATE = 4
COL_COMPLETE = 7

class worker_load_orders(QObject):
        finished = pyqtSignal(list)

        @pyqtSlot()  #Wrap in slot for better communication etc
        def run(self):
            #Get the Orders from Woocommerce
            wc = PbWooCommerce()
            myorders = wc.get_orders('packing, processing')
            logger.debug('Orders Loaded')
            self.finished.emit(myorders)



class appUI(QtWidgets.QMainWindow):
    load_orders_requested = pyqtSignal()

    def __init__(self):
        super(appUI, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('ui_main_window.ui', self) # Load the .ui file
        self.logger = logging.getLogger(__name__)
        self.logger.info('Loading Orders window')
        self.lblStatus.setStyleSheet('color:#EE1C25')

        # Set Column Widths
        self.orderstableWidget.setColumnWidth(0,150)
        self.orderstableWidget.setColumnWidth(1, 320)
        self.orderstableWidget.setColumnWidth(2,150)
        self.orderstableWidget.setColumnWidth(5,122)
        self.orderstableWidget.setColumnWidth(6,145)
        self.orderstableWidget.setColumnWidth(7,145)
        

        self.show()  # Show the GUI

        self.load_orders()

        #Add connections to slots
        self.btnRefreshOrders.clicked.connect(self.refresh_orders)
        self.actionRefresh_Pricing.triggered.connect(self.refreshPricesOffsite)
        self.actionCheck_Stock.triggered.connect(self.checkStock)

    def load_orders(self):
        # Create a worker object and a thread
        self.btnRefreshOrders.hide()
        logger.debug("Getting Orders from the Website")
        self.lblStatus.setText("Getting Orders from Website")
        self.statusBar().showMessage("Getting Orders from Website")
        self.worker = worker_load_orders()
        self.thread = QThread()
        self.worker.moveToThread(self.thread)

        self.worker.finished.connect(self.process_orders)
        self.load_orders_requested.connect(self.worker.run)
        #We are killing the thread here - vs I think it also possible to keep alive and trigger as well
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Assign the worker to the thread and start the thread

        self.thread.start()

        # Start the load by emitting a signal
        self.load_orders_requested.emit()


    def process_orders(self, myorders):
        #Process the orders once the thread completes
        self.orderstableWidget.setRowCount(len(myorders))
        rowindex=0
        for row in myorders:
            order_id = QTableWidgetItem(str(row['id']))
            logger.debug("Loading order {0}".format(row['id']))
            order_id.setFlags(order_id.flags() & ~ Qt.ItemIsEditable)
            self.orderstableWidget.setItem(rowindex,0, order_id)

            delivery_data = fnc_meta_processing.parse_order_meta_data(row)
            if delivery_data[0] == 'pickup':
                if delivery_data[3]: #Check in case no date was in the order
                    ready_by_date = delivery_data[3].strftime("%d/%m/%Y")
            else:
                if delivery_data[1]:
                    ready_by_date = delivery_data[1].strftime("%d/%m/%Y")

            self.orderstableWidget.setItem(rowindex,1, QTableWidgetItem(str(row['billing']['first_name'] + ' ' + row['billing']['last_name'])))
            if row['status'] == 'processing':
                self.orderstableWidget.setItem(rowindex, 2, QTableWidgetItem('Ready for Delivery'))
                delivery_button = QtWidgets.QPushButton('Print Delivery Slip')
                delivery_button.setStyleSheet("background-color : #89CFF0")
                delivery_button.clicked.connect(self.print_delivery_note)
                self.orderstableWidget.setCellWidget(rowindex, 6, delivery_button)
                complete_button = QtWidgets.QPushButton('Finalise Order')
                complete_button.setStyleSheet("background-color : #8d6852")
                complete_button.clicked.connect(self.complete_order)
                self.orderstableWidget.setCellWidget(rowindex, 7, complete_button)

            else:
                self.orderstableWidget.setItem(rowindex, 2, QTableWidgetItem(row['status'].capitalize()))

            self.orderstableWidget.setItem(rowindex,3, QTableWidgetItem(delivery_data[0].capitalize()))
            self.orderstableWidget.setItem(rowindex, COL_READY_DATE, QTableWidgetItem(ready_by_date))


            #Add Edit Button
            # create an cell widget
            if row['status'] == 'packing':
                btn = QtWidgets.QPushButton('Edit Order')
                btn.setStyleSheet("background-color : #27ee1c")
            else:
                btn = QtWidgets.QPushButton('View Order')
                btn.setStyleSheet("background-color : #EE1C25 ;"
                                  "color: white")

            #https://stackoverflow.com/questions/47621172/applying-styles-to-pyqt-widgets-from-external-stylesheet
            btn.clicked.connect(self.orderClicked)
            self.orderstableWidget.setCellWidget(rowindex, 5, btn)
            rowindex +=1

        #Sort the table to oldest orders are first.
        self.orderstableWidget.sortItems(COL_READY_DATE, QtCore.Qt.AscendingOrder)

        self.btnRefreshOrders.show()
        self.statusBar().showMessage("Ready")
        self.lblStatus.setText("Ready")

    @QtCore.pyqtSlot()
    def orderClicked(self):
        button = self.sender()
        if button:
            row = self.orderstableWidget.indexAt(button.pos()).row()
            orderNumber = self.orderstableWidget.item(row, 0).text()
            self.dialog = webOrderUI(orderNumber)
            self.dialog.show()

    @QtCore.pyqtSlot()
    def checkStock(self):
        #Open the Stock Window
        self.dialog = stockUI()
        self.dialog.show()

    @QtCore.pyqtSlot()
    def refresh_orders(self):
        #refresh the orders list
        print("Refreshing Orders")
        self.statusBar().showMessage("Getting Orders from Website")
        self.orderstableWidget.setRowCount(0)
        self.load_orders()

    def refreshPricesOffsite(self):
        print('Call to refresh prices of site to Manticore')
        fnc_meta_processing.webhook_update_prices()
        dialog_functions.show_information_dialog("Request has been sent.")

    def print_delivery_note(self):
        #Print a delivery note to PrintNode
        button = self.sender()
        if button:
            row = self.orderstableWidget.indexAt(button.pos()).row()
            orderNumber = self.orderstableWidget.item(row, 0).text()
            delivery_note_printing.create_delivery(orderNumber)

    def complete_order(self):
        #Update the order to have status of completed
        button = self.sender()
        if button:
            row = self.orderstableWidget.indexAt(button.pos()).row()
            orderNumber = self.orderstableWidget.item(row, 0).text()
            logger.info('Completing Order %s', orderNumber)
            updated_order = {'status': 'completed'}
            self.wc = PbWooCommerce()
            result = self.wc.update_order(updated_order, orderNumber)
            dd = dialog_functions.show_information_dialog("The order has been finalised and customer will be charged")
            self.refresh_orders

if __name__ == '__main__':
    # Get list of Orders being packed from
    #logger.info("Start Connection to Woo Commerce")
    #This is make the class a global so we clean up the others where is a defined in the class for final integration
    wc = PbWooCommerce()
    app = QtWidgets.QApplication(sys.argv)
    window = appUI()
    app.exec_()