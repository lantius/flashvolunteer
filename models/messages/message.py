import re, logging, time

from google.appengine.ext import db
from google.appengine.api import mail

from models.volunteer import Volunteer
from models.auth.account import Account

from controllers._utils import get_domain

from models.messages.message_type import MessageType, MessagePropagationType

from controllers._utils import is_debugging

from components.time_zones import Pacific, utc

from google.appengine.ext import deferred
from google.appengine.runtime import apiproxy_errors 
    
def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

class Message(db.Model):
    subject = db.StringProperty()
    body = db.TextProperty()
    
    trigger = db.DateTimeProperty(auto_now_add = True)
    
    ##### DEPRECATED; user sender
    sent_by = db.ReferenceProperty(reference_class = None, collection_name = 'sent_messages')
    ###############
        
    flagged = db.BooleanProperty(default = False)
    verified = db.BooleanProperty(default = False)
        
    type = db.ReferenceProperty(MessageType)
    
    autogen = db.BooleanProperty(default = True)
    
    forum_msg = db.BooleanProperty(default = False)

    #### state of message sending 
    sent = db.BooleanProperty(default = False)
    in_task_queue = db.BooleanProperty(default = False)
    ##############
    
    def send(self):
        if self.flagged and not self.verified: return

        self.sent = True
        self.put()

        if not is_debugging():                 
            try:
                self.email()
            except Exception, e:
                logging.error('could not send message %i %s: %s'%(self.key().id(), self.subject, str(e)))
                self.sent = False            
                self.put()
            
    def get_mailbox_friendly_body(self):
        reg = r"(http://(www\.)?([-A-Za-z0-9+&@#/%?=~_|!:,.;]*[-A-Za-z0-9+&@#/%=~_|]))"
        msg = re.sub(reg,r'<a rel="nofollow" target="_blank" href="\1">\1</a>', remove_html_tags(self.body).replace('\n','<br>'))
        if self.autogen:
            msg += "<br><br>Thanks!\nThe Flash Volunteer team"
        return msg

    def url(self):
        return '/messages/' + str(self.key().id())
            
    def time_sent(self):
        return self.trigger.replace(tzinfo=utc).astimezone(Pacific).strftime("%m/%d/%Y %H:%M")
    
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
        domain = 'http://www.' + get_domain()

        if self.forum_msg:
            footer = """\n
---
If you have feedback for us at Flash Volunteer, please visit http://flashvolunteer.uservoice.com/. 

If you would prefer not to receive these types of messages, visit %(domain)s/settings and adjust your Message preferences.
"""%{'domain': domain, 'message_url': self.url()}  

        else:
            footer = """\n
---
To view and reply to this message on Flash Volunteer, visit %(domain)s%(message_url)s.

If you have feedback for us at Flash Volunteer, please visit http://flashvolunteer.uservoice.com/. 

If you would prefer not to receive these types of messages, visit %(domain)s/settings and adjust your Message preferences.
"""%{'domain': domain, 'message_url': self.url()}  
        
        if self.autogen:
            footer = "\n\nThanks!\nThe Flash Volunteer team%s"%footer 
        
        prop = MessagePropagationType.all().filter('name =', 'email').get()
           
        body = self.body + footer
        
        for mr in self.sent_to.filter('emailed =', False):    
            if mr.recipient is None or \
                not isinstance(mr.recipient, Account) or \
                not self._get_message_pref(recipient = mr.recipient, prop = prop): 
                continue
            
            try:
                mr.emailed = True    
                mr.put()
                #rate limiting for email sending. quota is 8 per minute free
                deferred.defer(send_email, 
                               subject = self.subject,
                               to = mr.recipient.name + "<" + mr.recipient.get_email() + ">", 
                               body = body,
                               _queue="email")
                
            except Exception, e:
                mr.emailed = False
                mr.put()
                raise
                
def send_email(subject, to, body):
    message = mail.EmailMessage(
            sender="Flash Volunteer <noreply@flashvolunteer.org>",
            subject=subject,
            to = to,
            body = body
            )
    try: 
        message.send()
    except apiproxy_errors.DeadlineExceededError, e:
        logging.warning('got deadline exceeded error on send mail; assuming that mail was delivered successfully')