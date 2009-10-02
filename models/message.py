from google.appengine.ext import db
from google.appengine.api import mail

from models.volunteer import *

################################################################################
# Message
class Message(db.Model):
  title = db.StringProperty()
  sent = db.DateTimeProperty(auto_now_add=True)
  sender = db.ReferenceProperty(Volunteer,
                                collection_name = 'sent_messages')
  recipients = db.ListProperty(int)
  content = db.TextProperty()

  def url(self):
    return self.recipient.url() + '/messages/' + str(self.key().id())
    
  def sendemail(self):
    mail.send_mail(sender="noreply@flashvolunteer.org",
                  to= self.recipient.name + "<" + self.recipient.user.email() + ">",
                  subject=self.title,
                  body=self.content)
    
  def get_sent_time(self):
    return self.sent.strftime("%d %B %Y %I:%M%p")