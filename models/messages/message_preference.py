from google.appengine.ext import db
from google.appengine.api import mail

from models.volunteer import Volunteer
from models.auth.account import Account

from models.messages.message_type import MessageType
from models.messages.message_propagation_type import MessagePropagationType

class MessagePreference(db.Model):
    #####################################
    #MESSAGE PROPAGATION OPTIONS
    #####################################
    #
    # 1. FV MAILBOX
    # 2. EMAIL
    #
    type = db.ReferenceProperty(MessageType)
    propagation = db.ListProperty(int) #list of MessagePropagationType ids
    
    account = db.ReferenceProperty(Account, collection_name = 'message_preferences', required = True)    

    ##### DEPRECATED
    volunteer = db.ReferenceProperty(Volunteer, collection_name = 'message_preferences')    
