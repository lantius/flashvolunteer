from google.appengine.ext import db
from google.appengine.api import mail

from models.volunteer import Volunteer
from models.organization import Organization

def get_recipient(id):
    recipient = Volunteer.get_by_id(id) 
    if not recipient:
        recipient = Organization.get_by_id(id)
    return recipient

################################################################################
# Message
########################
#TYPE is a way to index what kind of message it is, for accounting purposes
#
# 1: message to event host when volunteer signs up
# 2: Message to volunteer when they are added to team#
#
#

class Message(db.Model):
    subject = db.StringProperty()
    body = db.TextProperty()
    
    date = db.DateTimeProperty(auto_now_add=True)
    trigger = db.DateTimeProperty(required = True)
    
    sent = db.BooleanProperty(default = False)
    sender = db.IntegerProperty()
    
    recipients = db.ListProperty(int) #list of Users
    
    flagged = db.BooleanProperty(default = False)
    verified = db.BooleanProperty(default = False)
    
    referral_url = db.LinkProperty(default = None)
    
    type = db.IntegerProperty(default = None)

    def send(self):
        if self.flagged and not self.verified: return
        
        for id in self.recipients:
            recipient = get_recipient(id = id)
            if recipient is None: continue
            
            mail.send_mail(sender="noreply@flashvolunteer.org",
                            to= recipient.name + "<" + recipient.get_email() + ">",
                            subject=self.subject,
                            body=self.body)
    
        self.sent = True
        self.put()
    
    def url(self):
        return self.recipient.url() + '/messages/' + str(self.key().id())
            
    def time_sent(self):
        return self.trigger.strftime("%m/%d/%Y %I:%M %p")


