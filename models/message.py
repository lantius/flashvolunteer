from google.appengine.ext import db

from models.volunteer import *

################################################################################
# Message
class Message(db.Model):
  title = db.StringProperty()
  sent = db.DateTimeProperty(auto_now_add=True)
  sender = db.ReferenceProperty(Volunteer,
                                collection_name = 'sent_messages')
  recipient = db.ReferenceProperty(None,
                                   collection_name = 'messages')
  content = db.TextProperty()

  def url(self):
    return self.recipient.url() + '/messages/' + str(self.key().id())