from google.appengine.ext import db
from google.appengine.api import mail

from models.messages.message_propagation_type import MessagePropagationType

class MessageType(db.Model):
    name = db.StringProperty()
    
    order = db.IntegerProperty(required = True) 
    prompt = db.StringProperty()
    
    default_propagation = db.ListProperty(int) #list of MessagePropagationType IDs
    
    in_settings = db.BooleanProperty(default = True)