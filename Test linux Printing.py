import cups
conn = cups.Connection()
printers = conn.getPrinters()
print(printers)
conn.printFile('BIXOLON_SRP-E300','pdf_1.pdf', "",{})