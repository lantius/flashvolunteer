from controllers._utils import check_messages
from controllers.abstract_handler import AbstractHandler

from google.appengine.api import memcache

import os, logging

class MessageDispatcher(AbstractHandler):

    def get(self):
        #potential race condition, but probably unlikely enough with minimal consequences...

        if not memcache.get('message_dispatcher_out'):
            memcache.set('message_dispatcher_out', True, 300)
            try:
                logging.info('message dispatcher is running')
                check_messages()
                
            finally:
                memcache.set('message_dispatcher_out', False)
        return
            
            
        
    