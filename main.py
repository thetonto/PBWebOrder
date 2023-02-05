import configparser
import logging.handlers
from PyQt5 import QtWidgets
from cls_Load_Orders import appUI
import sys

# Read the config file
config = configparser.ConfigParser()
config.read('shireButchery.ini')

# Have another crack at the logging.

logger = logging.getLogger('')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.handlers.TimedRotatingFileHandler(config['LOCAL']['logfile'], when="midnight", backupCount=3)
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

if __name__ == '__main__':
    # Initialise a global instance of the woocommerce class as we use it everywhere.
    logger.info("Starting application")
    # Set style to fusion to match between systems
    QtWidgets.QApplication.setStyle("fusion")
    app = QtWidgets.QApplication(sys.argv)

    window = appUI()
    app.exec_()
