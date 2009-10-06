from google.appengine.ext import db
from google.appengine.api import mail

from models.volunteer import Volunteer
from models.organization import Organization

from controllers._utils import get_domain

from models.messages.message_type import MessageType, MessagePropagationType

def get_user(id):
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
    
    type = db.ReferenceProperty(MessageType)
    
    read = db.BooleanProperty(default = False)
    autogen = db.BooleanProperty(default = True)
    
    show_in_mailbox = db.ListProperty(int)
    
    def send(self):
        if self.flagged and not self.verified: return
        
        self.email()
        self.mailbox()
    
        self.sent = True
        self.put()
    
    def url(self):
        return '/messages/' + str(self.key().id())
            
    def time_sent(self):
        return self.trigger.strftime("%m/%d/%Y %H:%M")
    
    def get_sender(self):
        #TODO: maybe memcache this
        sender = get_user(self.sender) 
        return sender

    def _get_message_pref(self, recipient, prop):
        prefs = recipient._get_message_pref(type = self.type)
        if not prefs: 
            prefs = self.type.default_propagation
        else:
            prefs = prefs.propagation
        
        return prop.key().id() in prefs        
        
    def email(self):
        footer = """
        
Thanks!,
The Flash Volunteer team

---
If you would prefer not to receive these types of messages, visit %(domain)s%(recipient_url)s/settings and adjust your Message preferences.
"""   
        domain = 'http://' + get_domain(keep_www = True)

        prop = MessagePropagationType.all().filter('name =', 'email').get()
        for id in self.recipients:
            recipient = get_user(id = id)
            if recipient is None or not self._get_message_pref(recipient = recipient, prop = prop): continue
                                    
            mail.send_mail(sender="noreply@flashvolunteer.org",
                            to= recipient.name + "<" + recipient.get_email() + ">",
                            subject=self.subject,
                            body=self.body + footer%{'domain': domain, 'recipient_url': recipient.url})   
            
    def mailbox(self):
        footer = """
        
Thanks!,
The Flash Volunteer team

---
If you would prefer not to receive these types of messages, visit %(domain)s%(recipient_url)s/settings and adjust your Message preferences.
"""   

        prop = MessagePropagationType.all().filter('name =', 'mailbox').get()
        for id in self.recipients:
            recipient = get_user(id = id)
            if recipient is None or not self._get_message_pref(recipient = recipient, prop = prop): continue
                                    
            self.show_in_mailbox.append(recipient.key().id())
        self.put()
               

        

