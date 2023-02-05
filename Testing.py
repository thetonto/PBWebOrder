import unittest
from pb_Woo_Order_Class import PbWooCommerce


class MyTestCase(unittest.TestCase):
    def test_woo_api_activation(self):
        self.wc = PbWooCommerce()
        #Check that the WCAPI has a true value which means is has initialised.
        self.assertTrue(self.wc.wcapi.wp_api,"Did not initialise")


if __name__ == '__main__':
    unittest.main()
