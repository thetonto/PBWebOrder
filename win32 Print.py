
#Code not used.  Keeping for reference

import os, sys
import win32print,  win32ui, win32api

import platform
if(platform.system())=='Linux':
    'We are on linux'
    print('Linux Detected')
else:
    logger.info("Windows Detected")


#p = win32print.OpenPrinter (printer_name)

printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL, None, 1)
print(printers)

#job = win32print.StartDocPrinter (p, 1, ("test of raw data", None, "RAW")) win32print.StartPagePrinter (p) win32print.WritePrinter (p, "data to print") win32print.EndPagePrinter (p)


#os.system("lpr -P printer_name file_name.txt")
cwd = os.getcwd()
#'BIXOLON SRP-E300'

name = win32print.GetDefaultPrinter() # verify that it matches with the name of your printer
printdefaults = {"DesiredAccess": win32print.PRINTER_ALL_ACCESS} # Doesn't work with PRINTER_ACCESS_USE
handle = win32print.OpenPrinter(name, printdefaults)
level = 2
attributes = win32print.GetPrinter(handle, level)
#attributes['pDevMode'].Duplex = 1  #no flip
#attributes['pDevMode'].Duplex = 2  #flip up
attributes['pDevMode'].Duplex = 3   #flip over
win32print.SetPrinter(handle, level, attributes, 0)
win32print.GetPrinter(handle, level)['pDevMode'].Duplex
win32api.ShellExecute(0,'print','pdf_1.pdf','.','/manualstoprint',0)