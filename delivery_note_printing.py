from fpdf import FPDF

import configparser
import os, sys, platform
from PyQt5.QtCore import *
from pb_Woo_Order_Class import PbWooCommerce
from fnc_meta_processing import parse_order_meta_data

import logging
import cups

logger = logging.getLogger(__name__)

if (platform.system()) == 'Windows':
    import win32print,  win32ui, win32api


#Read the config file
config = configparser.ConfigParser()
config.read('shireButchery.ini')

def create_delivery_note(order):
    #get the delivery meta data by handing over the order
    delivery_data = parse_order_meta_data(order)
    pdf = FPDF('P', 'mm', (72,150))

    # Add a page
    pdf.add_page()
    pdf.set_margin(5)

    pdf.image('PB_Horizonal_Textured_85h.png', 5, 8, 60)
    pdf.set_font('helvetica', 'B', 16)
    pdf.cell(0, 30, 'Delivery Docket', new_x="LMARGIN", new_y="NEXT", align = 'C')
    pdf.set_font('helvetica', '', size=12)
    pdf.cell(0,0,'Order Number: ' + str(order['id']), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(7)
    pdf.cell(0,7, order['shipping']['first_name'] +' ' + order['shipping']['last_name'], new_x="LMARGIN", new_y="NEXT")
    if order['billing']['phone']:
        pdf.cell(0, 7, 'Ph: ' + order['billing']['phone'], new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    if order['shipping']['company']:
        pdf.cell(0,7, order['shipping']['company'], new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0,7, order['shipping']['address_1'], new_x="LMARGIN", new_y="NEXT")
    if order['shipping']['address_2']:
        pdf.cell(0,10, order['shipping']['address_2'], new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0,7, order['shipping']['city'], new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0,7, order['shipping']['state']+ ' ' + order['shipping']['postcode'], new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    if order['customer_note']:
        pdf.cell(0, 7, "Customer Note:", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 7, order['customer_note'], new_x="LMARGIN", new_y="NEXT")
    pdf.ln(7)

    if delivery_data[0] == 'pickup':
        pdf.cell(0, 7, 'Pickup from Store', new_x="LMARGIN", new_y="NEXT")
        if delivery_data[3]:  # Check in case no date was in the order
            ready_by_date = delivery_data[3].strftime("%d/%m/%Y")
            pdf.cell(0, 7, ready_by_date, new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.cell(0, 7, delivery_data[0].capitalize(), new_x="LMARGIN", new_y="NEXT")
        if delivery_data[1]:
            ready_by_date = delivery_data[1].strftime("%d/%m/%Y")
            pdf.cell(0, 7, ready_by_date, new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 7, delivery_data[2], new_x="LMARGIN", new_y="NEXT")

    # Process the order meta here using the meta processor for delivery information.
    pdf.output('pdf_1.pdf')

    if (platform.system()) == 'Linux':
        try:
            logger.info("Printing on Linux")
            conn = cups.Connection()
            printers = conn.getPrinters()
            print(printers)
            conn.printFile('BIXOLON_SRP-E300','pdf_1.pdf', "",{})


        except Exception as e:
            logger.error("Oops!", e.__class__, "occurred.")

    else:
        try:
            logger.info("Windows Detected")
            # 'BIXOLON SRP-E300'

            name = win32print.GetDefaultPrinter()  # verify that it matches with the name of your printer
            name = 'BIXOLON SRP-E300'
            printdefaults = {"DesiredAccess": win32print.PRINTER_ALL_ACCESS}  # Doesn't work with PRINTER_ACCESS_USE
            handle = win32print.OpenPrinter(name, printdefaults)
            level = 2
            attributes = win32print.GetPrinter(handle, level)
            # attributes['pDevMode'].Duplex = 1  #no flip
            # attributes['pDevMode'].Duplex = 2  #flip up
            attributes['pDevMode'].Duplex = 3  # flip over
            win32print.SetPrinter(handle, level, attributes, 0)
            win32print.GetPrinter(handle, level)['pDevMode'].Duplex
            win32api.ShellExecute(0, 'print', 'pdf_1.pdf', '.', '/manualstoprint', 0)
        except Exception as e:
            logger.error("Oops!", e.__class__, "occurred.")

def create_delivery(order_id):
    wc = PbWooCommerce()
    order = wc.get_single_order(order_id)
    result = create_delivery_note(order)


if __name__ == '__main__':
    create_delivery('1510')