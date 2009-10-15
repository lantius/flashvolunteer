import re

from google.appengine.ext import db
from google.appengine.api import mail

from models.volunteer import Volunteer
from models.organization import Organization

from controllers._utils import get_domain

from models.messages.message_type import MessageType, MessagePropagationType

from controllers._utils import is_debugging

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


def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

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
        
    type = db.ReferenceProperty(MessageType)
    
    unread = db.ListProperty(int) #list of recipient ids that have yet to read the message
    autogen = db.BooleanProperty(default = True)
    
    show_in_mailbox = db.ListProperty(int)
    
    def send(self):
        if self.flagged and not self.verified: return
        
        if not is_debugging(): 
            self.email()
        self.mailbox()
    
        self.unread = self.recipients
        self.sent = True
        self.put()
        
    def get_mailbox_friendly_body(self):
        reg = r"(http://(www\.)?([-A-Za-z0-9+&@#/%?=~_|!:,.;]*[-A-Za-z0-9+&@#/%=~_|]))"
        return re.sub(reg,r'<a rel="nofollow" target="_blank" href="\1">\1</a>', remove_html_tags(self.body).replace('\n','<br>'))

    def url(self):
        return '/messages/' + str(self.key().id())
            
    def time_sent(self):
        return self.trigger.strftime("%m/%d/%Y %H:%M")
    
    def get_sender(self):
        #TODO: maybe memcache this
        if self.sender:
            sender = get_user(self.sender) 
        else:
            sender = None
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
To view this message on Flash Volunteer, visit %(domain)s%(message_url)s. There you may reply to the message or flag it as inappropriate.  

If you have feedback for the Flash Volunteer service, please visit http://flashvolunteer.uservoice.com/. 

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
                            body=self.body + footer%{'domain': domain, 'recipient_url': recipient.url(), 'message_url': self.url()})   
            
    def mailbox(self):
        footer = """
<br><br>
Thanks!,
The Flash Volunteer team
<br>
---
If you would prefer not to receive these types of messages, visit %(domain)s%(recipient_url)s/settings and adjust your Message preferences.
"""   

        prop = MessagePropagationType.all().filter('name =', 'mailbox').get()
        for id in self.recipients:
            recipient = get_user(id = id)
            if recipient is None or not self._get_message_pref(recipient = recipient, prop = prop): continue
                                    
            self.show_in_mailbox.append(recipient.key().id())
        self.put()
               

        

