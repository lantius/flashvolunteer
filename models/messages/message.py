import re

from google.appengine.ext import db
from google.appengine.api import mail

from models.volunteer import Volunteer

from controllers._utils import get_domain

from models.messages.message_type import MessageType, MessagePropagationType

from controllers._utils import is_debugging

def get_user(id):
    from models.organization import Organization

    recipient = Volunteer.get_by_id(id) 
    if not recipient:
        recipient = Organization.get_by_id(id)
    return recipient

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
    
    sent_by = db.ReferenceProperty(Volunteer, collection_name = 'sent_messages')
    recipients = db.ListProperty(int) #list of Users
    
    recipient = db.ReferenceProperty(Volunteer)
    
    flagged = db.BooleanProperty(default = False)
    verified = db.BooleanProperty(default = False)
        
    type = db.ReferenceProperty(MessageType)
    
    unread = db.ListProperty(int) #list of recipient ids that have yet to read the message
    
    read = db.BooleanProperty(default = False)
    autogen = db.BooleanProperty(default = True)
    
    show_in_mailbox = db.ListProperty(int)
    show_in_mail = db.BooleanProperty(default = False)
    
    def send(self):
        if self.flagged and not self.verified: return

        self.sent = True
        self.put()
                
        try:
            if not is_debugging(): 
                self.email()
            self.mailbox()
        except:
            self.sent = False
            self.put()

        
    def get_mailbox_friendly_body(self):
        reg = r"(http://(www\.)?([-A-Za-z0-9+&@#/%?=~_|!:,.;]*[-A-Za-z0-9+&@#/%=~_|]))"
        return re.sub(reg,r'<a rel="nofollow" target="_blank" href="\1">\1</a>', remove_html_tags(self.body).replace('\n','<br>'))

    def url(self):
        return '/messages/' + str(self.key().id())
            
    def time_sent(self):
        return self.trigger.strftime("%m/%d/%Y %H:%M")
    
    def get_sender(self):
        return self.sent_by
    
    def get_recipient(self):
        return self.sent_to.get().recipient

    def _get_message_pref(self, recipient, prop):
        prefs = recipient._get_message_pref(type = self.type)
        if not prefs: 
            prefs = self.type.default_propagation
        else:
            prefs = prefs.propagation
        
        return prop.key().id() in prefs        
        
    def email(self):
        footer = """\n
---
To view and reply to this message on Flash Volunteer, visit %(domain)s%(message_url)s.

If you have feedback for us at Flash Volunteer, please visit http://flashvolunteer.uservoice.com/. 

If you would prefer not to receive these types of messages, visit %(domain)s/settings and adjust your Message preferences.
"""  
        if self.autogen:
            footer = """
        
Thanks!
The Flash Volunteer team
""" + footer
 
        domain = 'http://www.' + get_domain()

        prop = MessagePropagationType.all().filter('name =', 'email').get()

        message = mail.EmailMessage(
            sender="noreply@flashvolunteer.org",
            subject=self.subject)   
        
        for mr in self.sent_to:    
            if mr.recipient is None or \
                not self._get_message_pref(recipient = mr.recipient, prop = prop): 
                continue
            message.to = mr.recipient.name + "<" + mr.recipient.get_email() + ">"
            message.body = self.body + footer%{'domain': domain, 'recipient_url': mr.recipient.url(), 'message_url': self.url()}  
            message.send()

    def mailbox(self):
        if self.autogen:
            footer = "\n\nThanks!\nThe Flash Volunteer team"
        else:
            footer = ''
        footer += "\n\n---\nIf you would prefer not to receive these types of messages, visit your <a href=\"/settings\">settings page</a> and adjust your Message preferences."
        self.body += footer
        self.put()
        prop = MessagePropagationType.all().filter('name =', 'mailbox').get()
        for mr in self.sent_to:
            if mr.recipient is None or \
               not self._get_message_pref(recipient = mr.recipient, prop = prop): 
                continue                  
            mr.show_in_mail = True
            mr.put()