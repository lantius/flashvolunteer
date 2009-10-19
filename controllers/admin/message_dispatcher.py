from controllers._utils import check_messages
from controllers.abstract_handler import AbstractHandler

import os, logging

class MessageDispatcher(AbstractHandler):

    def get(self):
        check_messages()
        return
            
            
        
    