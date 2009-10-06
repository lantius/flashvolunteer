from google.appengine.ext import db
from google.appengine.api import mail

class MessagePropagationType(db.Model):
    #####################################
    #MESSAGE PROPAGATION OPTIONS
    #####################################
    #
    # 1. FV MAILBOX
    # 2. EMAIL
    #
    name = db.StringProperty()
    prompt = db.StringProperty()