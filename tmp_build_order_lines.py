import configparser
import logging
import logging.handlers
import sys
from pb_Woo_Order_Class import PbWooCommerce
from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from cls_web_order import webOrderUI

config = configparser.ConfigParser()
config.read('shireButchery.ini')

##############Logging Settings##############
# Added a logging routine so when
logging.basicConfig(level=logging.DEBUG)

# Configure logging to log to a file, making a new file at midnight and keeping the last 3 day's data
# Give the logger a unique name (good practice)
logger = logging.getLogger('')
logger.setLevel(logging.DEBUG)
# Change the above to .DEBUG for message infomation and .INFO for runtime minimal messages
handler = logging.handlers.TimedRotatingFileHandler(config['LOCAL']['logfile'], when="midnight", backupCount=3)
# Format each log message like this
formatter = logging.Formatter("%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s")
# Attach the formatter to the handler

handler.setFormatter(formatter)
# Attach the handler to the logger
logger.addHandler(handler)
#########################################

stylesheet = """
     webOrderUI {      
        background-color: #ebe5e4; 
     }
 """


if __name__ == '__main__':
    # Get list of Orders being packed from
    logger.info("Start Connection to Woo Commerce")
    #updated_order_lines = [{'id': 120, 'product_id' : 404, 'quantity': 5, }]
    #updated_order = {'line_items': []}
    #updated_order['line_items'] += updated_order_lines
    #result = wc.update_order(updated_order, myorder['id'])
    #print(result)
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(stylesheet)
    window = webOrderUI('1356')

    app.exec_()