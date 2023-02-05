from woocommerce import API
import configparser


# Setup Logging
# logger.debug('My message with %s', 'variable data')
import logging
logger = logging.getLogger(__name__)

# get Configuration items
config = configparser.ConfigParser()
config.read('shireButchery.ini')

class PbWooCommerce(object):
    # Pryde Butchery Class to connect to woo commerce

    def __init__(self):
        self.wcapi = API(
            url=config['WOO']['woo_url'],
            consumer_key=config['WOO']['consumer_key'],
            consumer_secret=config['WOO']['consumer_secret'],
            timeout=20
        )
        logger.debug('Woocommerce API has initialised')

    def get_api(self):
        return self.wcapi

    def get_orders(self, status):
        # dd - Get all the products from the website
        result = self.wcapi.get('orders', params={"status": status})
        if result.status_code == 200:
            return result.json()
        else:
            return result.status_code

    def get_single_order(self, orderno):
        # dd - Get an order from the website
        logger.debug("Connecting for order %s", orderno)
        result = self.wcapi.get('orders/' + str(orderno))
        if result.status_code == 200:
            return result.json()
        else:
            return result.status_code

    def get_product(self, product_id):
        # dd - Get the productid from the website
        result = self.wcapi.get('products/' + str(product_id))
        if result.status_code == 200:
            return result.json()
        else:
            return result.status_code


    def update_order(self, order, order_id):
        # dd - Update order - Note we can hand WCAPI raw python object and it will do the conversion to JSON
        result = self.wcapi.put("orders/" + str(order_id), data=order)
        if result.status_code == 200:
            return result.json()
        else:
            return result.status_code

    def update_note(self, notes, order_id):
        # dd - Create order note
        data = {
            "note": notes
        }
        result = self.wcapi.post("orders/" + str(order_id) + "/notes", data=data)
        #/wp-json/wc/v3/orders/<id>/notes
        if result.status_code == 201:
            return result.json()
        else:
            return result.status_code

    def get_stock_level(self, sku):
        result = self.wcapi.get('products/', params={"sku": str(sku)})
        if result.status_code == 200:
            return result.json()
        else:
            return result.status_code

    def update_stock_level(self, productID, stockUpdate):
        data = {
            "stock_status" : stockUpdate
        }
        result = self.wcapi.put("products/" + str(productID), data)
        if result.status_code == 200:
            return result.json()
        else:
            return result.status_code
