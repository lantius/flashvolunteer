from google.appengine.ext import db
from google.appengine.api import mail

from google.appengine.api.users import User

################################################################################
# Message
class Message(db.Model):
  title = db.StringProperty()
  text = db.TextProperty()
  
  date = db.DateTimeProperty(auto_now_add=True)
  trigger = db.DateTimeProperty(required = True)
  
  
  sent = db.BooleanProperty(default = False)
  sender = db.ReferenceProperty(User,
                                collection_name = 'sent_messages')

  recipients = db.ListProperty(int) #list of Users
  sender = UserProperty()
  
  flagged = db.BooleanProperty(default = False)
  verified = db.BooleanProperty(default = False)
  
  referral_url = db.LinkProperty(default = None)

  def url(self):
    return self.recipient.url() + '/messages/' + str(self.key().id())
    
  def sendemail(self):
    mail.send_mail(sender="noreply@flashvolunteer.org",
                  to= self.recipient.name + "<" + self.recipient.user.email() + ">",
                  subject=self.title,
                  body=self.content)
    
  def get_sent_time(self):
    return self.sent.strftime("%d %B %Y %I:%M%p")