import os, string, logging
from datetime import datetime

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp

from controllers._auth import Authorize

from models.messages import MessageType, Message
from controllers.abstract_handler import AbstractHandler
from controllers._utils import is_debugging, send_message

from components.sessions import Session



################################################################################
# Messages page
################################################################################
PAGELIMIT = 10
class Mailbox(AbstractHandler):

    ################################################################################
    # GET
    def get(self, url_data):
        if url_data:
            self.show(url_data[1:])
        else:
            self.list()
    
    def show(self, id):
        try:
            volunteer = Authorize.login(self, requireVolunteer=True)
        except:
            return
        
        message = Message.get_by_id(int(id))
        
        if not message or not (volunteer.is_recipient(message) or volunteer.key().id() == message.sent_by.key().id()):
            if self.request.referrer:
                self.redirect(self.request.referrer)
            else:
                self.redirect('/')
                
        template_values = {
            'volunteer': volunteer,
            'message': message,
            'sender_viewing': message.sent_by is not None and message.sent_by.key().id() == volunteer.key().id()
            
          }
        self._add_base_template_values(vals = template_values)
        
        if not message.read: 
            message.read = True
            message.put()
        
        path = os.path.join(os.path.dirname(__file__),'..', 'views', 'messages', 'message.html')
        self.response.out.write(template.render(path, template_values, debug=is_debugging()))        
          
          
    def _get_next(self, lst):
        try:
            next = lst[-1].trigger
        except:
            next = lst[-1].timestamp
            
        if next.second != 59:
            #this is because the comparison operator is working against a 
            #reverse sorted list & datetime.isotime returns a microsecond
            #in its str rep which cannot be recreated through strftime
            next.replace(second=next.second+1)
        else:
            next.replace(minute=next.minute+1, second = 0)
            
        next = next.strftime('%Y-%m-%d %H:%M:%S')   
        return next
             
    ################################################################################
    # LIST
    def list(self):
        try:
            volunteer = Authorize.login(self, requireVolunteer=True)
        except:
            return
        
        messages = volunteer.get_messages().filter('show_in_mail =', True)
        
        sent_messages = volunteer.get_sent_messages()
        
        bookmark = self.request.get("bookmark", None)
        if bookmark:
            bookmark = datetime.strptime(bookmark, '%Y-%m-%d %H:%M:%S')            
            messages = messages.filter('trigger <=', bookmark).fetch(PAGELIMIT+1)
            sent_messages = sent_messages.filter('trigger <=', bookmark).fetch(PAGELIMIT+1)
        else:
            messages = messages.fetch(PAGELIMIT+1)
            sent_messages = sent_messages.fetch(PAGELIMIT+1)
            
        if len(messages) == PAGELIMIT+1:
            next = self._get_next(lst = messages)                
            messages = messages[:PAGELIMIT]
        else:
            next = None

        if len(sent_messages) == PAGELIMIT+1:
            sent_next = self._get_next(lst = sent_messages)                
            sent_messages = sent_messages[:PAGELIMIT]
        else:
            sent_next = None

        template_values = {
            'volunteer': volunteer,
            'messages': messages,
            'next': next,
            'sent_messages': sent_messages,
            'sent_next': sent_next,
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__),'..', 'views', 'messages', 'mailbox.html')
        self.response.out.write(template.render(path, template_values, debug=is_debugging()))