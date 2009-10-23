from controllers._utils import check_messages
from controllers.abstract_handler import AbstractHandler

from google.appengine.api import memcache

import os, logging

class MessageDispatcher(AbstractHandler):

    def get(self):
        if not memcache.get('message_dispatcher_out'):
            memcache.add('message_dispatcher_out')
            try:
                check_messages()
            except:
                memcache.delete('message_dispatcher_out')
        return
            
            
        
    