from PyQt5 import QtCore, QtWidgets, Qt, uic, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from pb_Woo_Order_Class import PbWooCommerce
from delivery_note_printing import create_delivery
import dialog_functions
import sys

# Setup Logging
# logger.debug('My message with %s', 'variable data')
import logging
logger = logging.getLogger(__name__)

# set some column constants for ease of change later if needed
COL_ITEM_WEIGHT = 6
COL_TOTAL_WEIGHT = 7
COL_PACKED_WEIGHT = 8
COL_SUBTOTAL = 9
COL_DISCOUNT = 10
COL_TOTAL = 11


class worker_update_order(QObject):
    finished = pyqtSignal()

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        # Initialse connection to woo
        self.wc = PbWooCommerce()

    @pyqtSlot(dict, str)  # Wrap in slot for better communication etc and remember to declare the arguments
    def run_update_order(self, order, order_id):
        # Update the order on Woo
        result = self.wc.update_order(order, order_id)
        logger.debug('Order %s updated ', order_id)
        # we are not sending anything back as we don't need it, thou error handling could be better,  problem is dict vs string hand back, may bet both from the class?
        self.finished.emit()

class worker_load_order(QObject):
    finished = pyqtSignal(dict)

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        # Initialse connection to woo
        self.wc = PbWooCommerce()
        self.orderDiscount = 0

    @pyqtSlot(str) # Wrap slot in decorator and we are accepting a single string with the order id
    def get_order(self, order_id):
        # Get the order from Woocommerce
        logger.debug('In thread about to start order load')
        result = self.wc.get_single_order(order_id)
        logger.info('Successfully loaded order %s from Woocommerce', order_id)
        # sendback the result which contains the order.
        self.finished.emit(result)


class InitialDelegate(QtWidgets.QStyledItemDelegate):
    # align right and format to $
    def __init__(self, decimals, parent=None):
        super().__init__(parent)
        self.nDecimals = decimals

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = (QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        try:
            text = index.model().data(index, QtCore.Qt.DisplayRole)
            number = float(text)
            option.text = "${:,.{}f}".format(number, self.nDecimals)
        except:
            pass

class webOrderUI(QtWidgets.QWidget):
    #Create signals for the communication with worker threads - Note to specify the params being sent
    update_order_requested = pyqtSignal(dict, str)
    load_order_requested = pyqtSignal(str)


    def __init__(self, order_id):
        super(webOrderUI, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('ui_web_order.ui', self)  # Load the .ui file
        self.show()  # Show the GUI

        #Create Worker thread for Order Updates.
        self.worker = worker_update_order()
        self.thread = QThread()   #if we add more threads we will need to change the name of the thread
        self.worker.moveToThread(self.thread)

        self.worker.finished.connect(self.finished_update_order_lines)
        self.update_order_requested.connect(self.worker.run_update_order)
        #We are killing the thread here - vs I think it also possible to keep alive and trigger as well
        #self.worker.finished.connect(self.thread.quit)
        #self.worker.finished.connect(self.worker.deleteLater)
        #self.thread.finished.connect(self.thread.deleteLater)

        # Assign the worker to the thread and start the thread
        self.thread.start()

        #Create Worker thread for loading the order
        self.load_worker = worker_load_order()
        self.thread_load = QThread()
        self.load_worker.moveToThread(self.thread_load)
        # Connect signals & slots AFTER moving the object to the thread
        self.load_worker.finished.connect(self.process_loaded_order)
        self.load_order_requested.connect(self.load_worker.get_order)

        # Set the thread to delete itself as we only need once on the order load
        self.load_worker.finished.connect(self.thread_load.quit)
        self.load_worker.finished.connect(self.load_worker.deleteLater)
        self.load_worker.finished.connect(self.thread_load.deleteLater)
        self.thread_load.start()

        # Set Column Widths
        self.tableWidget.setColumnWidth(0, 0)
        self.tableWidget.setColumnWidth(1, 45)
        self.tableWidget.setColumnWidth(2, 450)
        self.tableWidget.setColumnWidth(4, 120)
        self.tableWidget.setColumnWidth(6, 60)
        self.tableWidget.setColumnWidth(8, 110)
        self.tableWidget.setColumnWidth(9, 110)
        self.tableWidget.setColumnWidth(10, 110)

        # Set Formatting on currency
        delegateFloat = InitialDelegate(2, self.tableWidget)  # <---
        self.tableWidget.setItemDelegateForColumn(3, delegateFloat)
        self.tableWidget.setItemDelegateForColumn(4, delegateFloat)
        self.tableWidget.setItemDelegateForColumn(9, delegateFloat)
        self.tableWidget.setItemDelegateForColumn(10, delegateFloat)
        self.tableWidget.setItemDelegateForColumn(11, delegateFloat)

        # Start setting General Field Values
        title = "Order Number: " + str(order_id)
        self.lblOrderNumber.setText(title)
        self.setWindowTitle("Process Order with Packing Weight")
        self.lblSystemStatus.setText("Ready")
        # set the order id into self so we can reference later
        self.order_id = order_id
        self.discountAmount = 0

        logger.info("Loading Order to Table")
        self.lblSystemStatus.setText("Loading order please wait")
        logger.debug("About to trigger thread")

        self.load_order_requested.emit(order_id)  #Trigger the thread to load the orders

        #Below allows bypassing of the Threads if needed for debugging.
        #self.wc = PbWooCommerce()
        #result = self.wc.get_single_order(order_id)
        #self.process_loaded_order(result)

    def process_loaded_order(self, myorder):
        #Process the loaded order after the thread signals it has finished
        order_line_items = myorder['line_items']
        self.lblCustomer.setText('Customer Name: ' + myorder['billing']['first_name'] + ' ' + myorder['billing']['last_name'])
        self.lblStatus.setText('Status: ' + myorder['status'].capitalize())
        discount = myorder['discount_total']
        self.lblDiscount.setText(str(discount))
        self.orderDiscount = discount

        #Sort out any discounts
        try:
            self.discountCode = self.discountCode = myorder['coupon_lines'][0]['code']
            self.discountAmount = myorder['coupon_lines'][0]['meta_data'][0]['value']['amount']
            self.discountType = myorder['coupon_lines'][0]['meta_data'][0]['value']['discount_type']
            self.lblDiscount.setText(str(self.discountAmount) + ' ' + str(self.discountType) + ' ' + str(self.discountCode))
        except:
            self.discountCode = ''

        self.lblStatus.setStyleSheet("color: #EE1C25")

        self.tableWidget.setRowCount(len(order_line_items))
        rowindex = 0
        for row in order_line_items:

            # process the line item metadata and extract the sell by weight data.
            packed_weight = 0
            sbw_total_weight = 0
            sbw_weight = 0
            actual_price = 0
            base_price = 0

            metadata = row['meta_data']
            if len(metadata):
                for metadata_row in metadata:
                    key = metadata_row['key']
                    if key == '_sbw_total_weight':
                        sbw_total_weight = metadata_row['value']
                    elif key == '_sbw_weight':
                        sbw_weight = metadata_row['value']
                    elif key == '_sbw_name':
                        sbw_name = metadata_row['value']
                    elif key == 'Base Price':
                        bps = metadata_row['value'].split('</span>')
                        # grab any discounts that may be present from the base price
                        if len(bps) == 5:
                            bps2 = bps[3].split('</bdi>')
                        else:
                            bps2 = bps[1].split('</bdi>')
                        base_price = bps2[0]
                    elif key == 'Retail Price':
                        bps = metadata_row['value'].split('</span>')
                        # grab any discounts that may be present from the base price
                        if len(bps) == 5:
                            bps2 = bps[3].split('</bdi>')
                        else:
                            bps2 = bps[1].split('</bdi>')
                        base_price = bps2[0]
                    elif key == 'Packed Weight':
                        packed_weight = metadata_row['value']

            # Get the actual item price from woo and check it exists.
            if not (base_price):
                logger.warning("Product ID %s needed a manual price lookup", row['product_id'])
                self.wc = PbWooCommerce()
                result = self.wc.get_product(row['product_id'])
                if result != 404:
                    base_price = result['price']

            # Setup the Font
            disabled_font = QtGui.QFont()
            disabled_font.setBold(True)
            #disabled_font.setWeight(75)

            # Get Line Item ID and lock it from editing
            order_id = QTableWidgetItem(str(row['id']))
            order_id.setFlags(Qt.ItemIsEditable | Qt.ItemIsSelectable)
            self.tableWidget.setItem(rowindex, 0, order_id)

            # Set the PLU and lock from editing
            plu = QTableWidgetItem(str(row['sku']))
            plu.setFont(disabled_font)
            plu.setFlags(Qt.ItemIsEditable | Qt.ItemIsSelectable)
            self.tableWidget.setItem(rowindex, 1, plu)

            # Set the Name and lock from editing
            name = QTableWidgetItem(str(row['name']))
            name.setFont(disabled_font)
            name.setFlags(Qt.ItemIsEditable | Qt.ItemIsSelectable)
            self.tableWidget.setItem(rowindex, 2, name)

            # Set the System Price and lock from editing
            sysprice = QTableWidgetItem(str(base_price))
            sysprice.setFont(disabled_font)
            sysprice.setFlags(Qt.ItemIsEditable | Qt.ItemIsSelectable)
            self.tableWidget.setItem(rowindex, 3, sysprice)

            # Set the sell Price and lock from editing
            sellprice = QTableWidgetItem(str(row['price']))
            sellprice.setFont(disabled_font)
            sellprice.setFlags(Qt.ItemIsEditable | Qt.ItemIsSelectable)
            self.tableWidget.setItem(rowindex, 4, sellprice)

            # Set the Item Weight and lock from editing
            item_weight = QTableWidgetItem(str(sbw_weight))
            item_weight.setFont(disabled_font)
            item_weight.setFlags(Qt.ItemIsEditable | Qt.ItemIsSelectable)
            self.tableWidget.setItem(rowindex, 5, item_weight)

            # Set the Total Weight and lock from editing
            total_weight = QTableWidgetItem(str(sbw_total_weight))
            total_weight.setFont(disabled_font)
            total_weight.setFlags(Qt.ItemIsEditable | Qt.ItemIsSelectable)
            self.tableWidget.setItem(rowindex, COL_TOTAL_WEIGHT, total_weight)

            # Set the sell Quantity and lock from editing
            quantity = QTableWidgetItem(str(row['quantity']))
            quantity.setFont(disabled_font)
            quantity.setFlags(Qt.ItemIsEditable | Qt.ItemIsSelectable)
            self.tableWidget.setItem(rowindex, COL_ITEM_WEIGHT, quantity)

            # We might want to include a meta look up here for previous weights entered

            # Set the packed weight if present and allow for editing
            self.tableWidget.setItem(rowindex, COL_PACKED_WEIGHT, QTableWidgetItem(str(packed_weight)))

            # Set the Sub total and lock for editing
            subtotal_cost = QTableWidgetItem(str(row['subtotal']))
            subtotal_cost.setFont(disabled_font)
            subtotal_cost.setFlags(Qt.ItemIsEditable | Qt.ItemIsSelectable)
            self.tableWidget.setItem(rowindex, COL_SUBTOTAL, subtotal_cost)

            discount = QTableWidgetItem(str(float(row['subtotal']) - float(str(row['total']))))
            discount.setFont(disabled_font)
            discount.setFlags(Qt.ItemIsEditable | Qt.ItemIsSelectable)
            self.tableWidget.setItem(rowindex, COL_DISCOUNT, discount)


            # Set the total and lock for editing
            total_cost = QTableWidgetItem(str(row['total']))
            total_cost.setFont(disabled_font)
            total_cost.setFlags(Qt.ItemIsEditable | Qt.ItemIsSelectable)
            self.tableWidget.setItem(rowindex, COL_TOTAL, total_cost)

            rowindex += 1

        # Now the order has loaded we can set the signals
        # Hide complete order button if not all the packed weights are there.


        if not (self.check_all_packed_weights()):
            self.btnCompleteOrder.hide()

        if myorder['status'] == 'processing':   #hide button is order is now out for delivery
            self.btnCompleteOrder.hide()

        # set the signal to track changes
        self.tableWidget.itemChanged.connect(self.changeWeight)
        # set the signal for update order items button press
        self.btnUpdateOrder.clicked.connect(self.update_order_lines)
        self.btnCompleteOrder.clicked.connect(self.update_orders)


        self.lblSystemStatus.setText("Ready")

    def changeWeight(self, index):
        # Calculate the new totals
        row = index.row()
        col = index.column()
        if col == COL_PACKED_WEIGHT:
            item = self.tableWidget.item(row, 2).text()
            try:
                weight = float(self.tableWidget.item(row, COL_PACKED_WEIGHT).text())
                actual_price = float(self.tableWidget.item(row, 3).text())
                new_subtotal_price = weight * actual_price
                set_new_subtotal_price = QTableWidgetItem(str(new_subtotal_price))
                set_new_subtotal_price.setFlags(Qt.ItemIsEditable | Qt.ItemIsSelectable)
                self.tableWidget.setItem(row, COL_SUBTOTAL, set_new_subtotal_price)

                if float(self.discountAmount) >0:
                    discount = new_subtotal_price * (float(self.discountAmount)/100)
                else:
                    discount = 0

                set_new_discount_price = QTableWidgetItem(str(discount))
                set_new_discount_price.setFlags(Qt.ItemIsEditable | Qt.ItemIsSelectable)
                self.tableWidget.setItem(row, COL_DISCOUNT, set_new_discount_price)

                newTotal = new_subtotal_price-discount
                set_new_total_price = QTableWidgetItem(str(newTotal))
                set_new_total_price.setFlags(Qt.ItemIsEditable | Qt.ItemIsSelectable)
                self.tableWidget.setItem(row, COL_TOTAL, set_new_total_price)


                logger.info("Packed weight {0} for total price ${1}".format(item, new_subtotal_price))
            except ValueError:
                dialog_functions.show_warning_dialog("You can only enter valid numbers for the packed weight/qty")
                self.tableWidget.setCurrentCell(row-1,COL_PACKED_WEIGHT)


        if self.check_all_packed_weights():
            print("All packing items are present")
            self.btnCompleteOrder.show()

    def update_order_lines(self, mode='button'):
        # Update the order lines
        updated_order = {'line_items': []}

        for row in range(self.tableWidget.rowCount()):
            # get the item ID, Packed Weight and Total Price from the line.
            item_id = self.tableWidget.item(row, 0).text()
            packed_weight = self.tableWidget.item(row, COL_PACKED_WEIGHT).text()
            subtotal_price = self.tableWidget.item(row, COL_SUBTOTAL).text()
            total_price = self.tableWidget.item(row, COL_TOTAL).text()

            updated_order_lines = [{
                'id': int(item_id),
                'subtotal': str(subtotal_price),
                'total': str(total_price),
                'meta_data': [
                    {
                        'key': 'Packed Weight',
                        'value': packed_weight
                    }
                ]
            }]
            # add the order lines to the main order
            updated_order['line_items'] += updated_order_lines

        # Emit the update order lines signal
        self.lblSystemStatus.setText("Updating Website")
        self.update_order_requested.emit(updated_order, self.order_id)

    def finished_update_order_lines(self):
        self.lblSystemStatus.setText("Ready")
        pass

    def update_orders(self):
        # Update the order to processing if all the items have been packed.
        # Check we have all the packed weights

        if not (self.check_all_packed_weights()):
            dd = dialog_functions.show_warning_dialog(
                "The order cannot be updated as there are still items with no packing weight")
        else:
            self.update_order_lines('Procedure')
            updated_order = {'status': 'processing'}
            self.wc = PbWooCommerce()
            result = self.wc.update_order(updated_order, self.order_id)

            #Create an update note on the system.
            notes = "Order changed from Packing to Processing"
            result = self.wc.update_note(notes, self.order_id)

            create_delivery(self.order_id)

            self.lblStatus.setText('Processing')
            dd = dialog_functions.show_information_dialog(
                "The order has been updated as processing and is ready for delivery")
            self.close

    def check_all_packed_weights(self):
        # Check if all the packed weights are present
        for row in range(self.tableWidget.rowCount()):
            packed_weight = self.tableWidget.item(row, COL_PACKED_WEIGHT).text()
            if packed_weight == '0':
                return False
        return True

    def closeEvent(self, event):
        # Must make sure we quit the threads we started and pooled
        try:
            if self.thread_load.isRunning():
                logger.debug('Load Order Thread was still running')
                self.thread_load.quit()
                self.thread_load.deleteLater()
        except Exception as e:
            print (e, e.args)
        try:
            if self.thread.isRunning():
                logger.debug('Update Order Thread was still running')
                self.thread.quit()
                self.thread.deleteLater()
        except Exception as e:
            print (e, e.args)
