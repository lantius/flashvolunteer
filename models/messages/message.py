import re, logging, time

from google.appengine.ext import db
from google.appengine.api import mail

from models.auth.account import Account

from models.messages.message_type import MessageType

from components.time_zones import Pacific, utc

    
def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

class Message(db.Model):
    subject = db.StringProperty()
    body = db.TextProperty()
    
    trigger = db.DateTimeProperty(auto_now_add = True)
    
    sent_by = db.ReferenceProperty(reference_class = Account, collection_name = 'sent_messages')
        
    flagged = db.BooleanProperty(default = False)
    verified = db.BooleanProperty(default = False)
        
    type = db.ReferenceProperty(MessageType)
    
    autogen = db.BooleanProperty(default = True)
    
    forum_msg = db.BooleanProperty(default = False)

            
    def get_mailbox_friendly_body(self):
        reg = r"(http://(www\.)?([-A-Za-z0-9+&@#/%?=~_|!:,.;]*[-A-Za-z0-9+&@#/%=~_|]))"
        msg = re.sub(reg,r'<a rel="nofollow" target="_blank" href="\1">\1</a>', self.body.replace('\n','<br>'))
        if self.autogen:
            msg += "<br><br>Thanks!<br>The Flash Volunteer team"
        return msg

    def url(self):
        return '/messages/' + str(self.key().id())
            
    def time_sent(self):
        return self.trigger.replace(tzinfo=utc).astimezone(Pacific).strftime("%m/%d/%Y %I:%M %p")
    
    def get_sender(self):
        return self.sent_by
    
    def get_recipient(self):
        return self.sent_to.get().recipient

    def get_email_footer(self, domain):

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
                    
        return footer