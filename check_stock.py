

import sys
from pb_Woo_Order_Class import PbWooCommerce

wc = PbWooCommerce()
stocklevel = wc.get_stock_level('611')
print(stocklevel[0]['stock_status'])
productID = stocklevel[0]['id']

dd = wc.update_stock_level(productID, 'instock')