import re

from google.appengine.ext import db

from models.volunteer import Volunteer
from models.auth.account import Account

from models.messages.message import Message

from controllers._utils import is_debugging
from components.time_zones import Pacific, utc

class MessageReceipt(db.Model):
    
    message = db.ReferenceProperty(Message, collection_name = 'sent_to', required = True)
    #recipient = db.ReferenceProperty(Volunteer, collection_name = 'incoming_messages')

    recipient2 = db.ReferenceProperty(reference_class = None, collection_name = 'incoming_messages')

    read = db.BooleanProperty(default = False)

    timestamp = db.DateTimeProperty(auto_now_add = True)
    
    emailed = db.BooleanProperty(default = False)
    
    def get_timestamp(self):
        return timestamp.replace(tzinfo=utc).astimezone(Pacific)