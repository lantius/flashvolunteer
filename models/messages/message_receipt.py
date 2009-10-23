import re

from google.appengine.ext import db

from models.volunteer import Volunteer
from models.messages.message import Message

from controllers._utils import is_debugging


class MessageReceipt(db.Model):
    
    message = db.ReferenceProperty(Message, collection_name = 'sent_to', required = True)
    recipient = db.ReferenceProperty(Volunteer, collection_name = 'incoming_messages')
        
    read = db.BooleanProperty(default = False)
    show_in_mail = db.BooleanProperty(default = False)

    timestamp = db.DateTimeProperty(required = True)
    