import logging
from datetime import datetime
import requests
import json
import configparser


# Setup Logging
# logger.debug('My message with %s', 'variable data')
import logging
logger = logging.getLogger(__name__)

#Read the config file
config = configparser.ConfigParser()
config.read('shireButchery.ini')

#Parse the order metadata to extra pickup time.  May extract more later
def parse_order_meta_data(ordermeta):
    delivery_type = delivery_date = delivery_time = pickup_date = pickup_time = ''
    if len(ordermeta['meta_data']):
        for metadata_row in ordermeta['meta_data']:
            key = metadata_row['key']
            if key == 'delivery_type':
                delivery_type = metadata_row['value']
            elif key == 'delivery_date':
                delivery_date = datetime.fromisoformat(metadata_row['value'])
            elif key == 'delivery_time':
                delivery_time = metadata_row['value']
            elif key == 'pickup_date':
                pickup_date = datetime.fromisoformat(metadata_row['value'])
            elif key == 'pickup_time':
                pickup_time = metadata_row['value']
    return delivery_type, delivery_date, delivery_time, pickup_date, pickup_time

def webhook_update_prices():
    #do a webhook call to the relay and onto Manticore to sync prices
    webhook_url = config['LOCAL']['web_hook']
    data = {'name': 'Pryde Butchery', 'cmd': 'Update Prices', 'key' :'6m&zD2aM8OaQ5tBeD4f'}
    headers = {'Content-Type': 'application/json', 'User-Agent': 'Miranda'}
    logger.info("Sending Request to Manticore to Sync Data")
    r = requests.post(webhook_url, data=json.dumps(data), headers=headers)
