from controllers.abstract_handler import AbstractHandler

from models.messages.message import Message

from google.appengine.api import memcache

import os, logging

from datetime import datetime
from google.appengine.ext import deferred

    
def check_messages():    
    messages_to_send = Message.all().filter('sent =', False).filter('in_task_queue =', False).filter('trigger <', datetime.now())

    for message in messages_to_send:
        try:
            message.in_task_queue = True
            message.put()
            message.send()    
        finally:
            message.in_task_queue = False
            message.put()
            
class MessageDispatcher(AbstractHandler):

    def get(self):
        if Message.all().filter('sent =', False).filter('in_task_queue =', False).filter('trigger <', datetime.now()).count() > 0:
            deferred.defer(check_messages)
            
            
        
    