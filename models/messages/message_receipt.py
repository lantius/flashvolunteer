import re, logging

from google.appengine.ext import db
from google.appengine.api import mail

from models.messages.message import Message

from models.messages.message_type import MessageType, MessagePropagationType

from components.time_zones import Pacific, utc

from google.appengine.ext import deferred
from google.appengine.runtime import apiproxy_errors 


class MessageReceipt(db.Model):
    
    message = db.ReferenceProperty(Message, collection_name = 'receipt', required = True)
    recipient = db.ReferenceProperty(reference_class = None, collection_name = 'incoming_messages')

    read = db.BooleanProperty(default = False)

    timestamp = db.DateTimeProperty(auto_now_add = True)
    
    emailed = db.BooleanProperty(default = False)
        
    #### state of message sending 
    sent = db.BooleanProperty(default = False)
    in_task_queue = db.BooleanProperty(default = False)
    ##############
    
    def get_timestamp(self):
        return self.timestamp.replace(tzinfo=utc).astimezone(Pacific)
    
    
    def send(self, domain, is_debugging = False):

        if self.message.flagged and not self.message.verified: return

        if not is_debugging:                 
            if not self.emailed:
                should_email = self.should_email()
                if should_email:                        
                    try:
                        self.email(domain = domain)
                    except Exception, e:
                        logging.error('could not send message receipt %i %s: %s'%(self.key().id(), self.message.subject, str(e)))           

        self.sent = self.emailed or not should_email 
        self.put()
    
    def should_email(self):
        prop = MessagePropagationType.all().filter('name =', 'email').get()        
        #don't email forum messages and don't email folks who chose not to be emailed...
        if self.recipient is None or \
           not isinstance(self.recipient, Volunteer) or \
           not self._get_message_pref(recipient = self.recipient, prop = prop): 
            return False
        else:
            return True
        
        
    def email(self, domain):
        
        domain = 'http://www.' + domain
        footer = self.message.get_email_footer(domain)
        body = self.message.body + footer

        try:
            self.emailed = True    
            
            self.put()
            #rate limiting for email sending. quota is 8 per minute free
            deferred.defer(send_email, 
                           subject = self.message.subject,
                           to = self.recipient.get_name() + "<" + self.recipient.get_email() + ">", 
                           body = body,
                           _queue="email")
            
        except Exception, e:
            self.emailed = False
            logging.info('could not send to %s'%self.recipient.key().id())
            raise

    def _get_message_pref(self, recipient, prop):
        prefs = recipient._get_message_pref(type = self.message.type)
        if not prefs: 
            prefs = self.message.type.default_propagation
        else:
            prefs = prefs.propagation
        
        return prop.key().id() in prefs        
    
    
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