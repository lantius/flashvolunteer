from controllers.abstract_handler import AbstractHandler

from models.messages import MessageReceipt

from google.appengine.api import memcache

import os, logging

from datetime import datetime
from google.appengine.ext import deferred

    
def check_messages(domain, is_debugging):    
    messages_to_send = MessageReceipt.all().filter('sent =', False).filter('in_task_queue =', False).filter('timestamp <', datetime.now())

    for receipt in messages_to_send.fetch(limit=20):
        try:
            try:
                receipt.in_task_queue = True
                receipt.put()
                receipt.send(domain = domain,
                             is_debugging = is_debugging)    
            finally:
                receipt.in_task_queue = False
                receipt.put()
        except: 
            receipt.in_task_queue = False
            receipt.put()
            
class MessageDispatcher(AbstractHandler):

    def get(self):
        if MessageReceipt.all().filter('sent =', False).filter('in_task_queue =', False).filter('timestamp <', datetime.now()).count() > 0:
            deferred.defer(check_messages, self.get_domain(), self.is_debugging())
            
            
        
    