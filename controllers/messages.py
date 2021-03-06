import os, string, logging
from datetime import datetime

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp

from models.messages import MessageType, Message
from models.event import Event
from models.neighborhood import Neighborhood
from controllers.abstract_handler import AbstractHandler


################################################################################
# Messages page
################################################################################
LIST_LIMIT = 10
class Mailbox(AbstractHandler):

    ################################################################################
    # GET
    def get(self, url_data):
        if not url_data:
            self.list()
        elif url_data == 'inbox':
            self.inbox()
        elif url_data == 'sent':
            self.sent()
        else:
            self.show(url_data[1:])
    
    def show(self, id):
        try:
            volunteer = self.auth(require_login=True)
        except:
            return
        
        message = Message.get_by_id(int(id))
        viewer_is_sender = message.sender and volunteer.key().id() == message.sender.key().id()
        if message:
            mr = message.sent_to.filter('recipient =', volunteer).get()
        if not message or not (mr or viewer_is_sender):
            if self.request.referrer:
                self.redirect(self.request.referrer)
            else:
                self.redirect('/')
            return
                
        template_values = {
            'volunteer': volunteer,
            'message': message,
            'sender_viewing': message.sender is not None and message.sender.key().id() == volunteer.key().id()
            
          }
        self._add_base_template_values(vals = template_values)
        
        if not viewer_is_sender and not mr.read: 
            mr.read = True
            mr.put()
        
        path = os.path.join(os.path.dirname(__file__),'..', 'views', 'messages', 'message.html')
        self.response.out.write(template.render(path, template_values, debug=self.is_debugging()))        
          
          
    def _get_next(self, lst):
        try:
            next = lst[-1].trigger
        except:
            next = lst[-1].timestamp
            
        if next.second != 59:
            #this is because the comparison operator is working against a 
            #reverse sorted list & datetime.isotime returns a microsecond
            #in its str rep which cannot be recreated through strftime
            next = next.replace(second=next.second+1)
        else:
            next = next.replace(minute=next.minute+1, second = 0)
            
        next = next.strftime('%Y-%m-%d%H:%M:%S')   
        return next
             
    def sent(self):
        try:
            volunteer = self.auth(require_login=True)
        except:
            raise
        
        sent_messages = volunteer.get_sent_messages()
        
        bookmark = self.request.get("bookmark", None)
        if bookmark:
            bookmark = datetime.strptime(bookmark, '%Y-%m-%d%H:%M:%S')            
            sent_messages = sent_messages.filter('trigger <=', bookmark).fetch(LIST_LIMIT+1)
        else:
            sent_messages = sent_messages.fetch(LIST_LIMIT+1)
            
        if len(sent_messages) == LIST_LIMIT+1:
            sent_next = self._get_next(lst = sent_messages)                
            sent_messages = sent_messages[:LIST_LIMIT]
        else:
            sent_next = None

        template_values = {
            'volunteer': volunteer,
            'sent_messages': sent_messages,
            'sent_next': sent_next,
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__),'..', 'views', 'messages', '_sent.html')
        self.response.out.write(template.render(path, template_values, debug=self.is_debugging()))    
                

    def inbox(self):
        try:
            volunteer = self.auth(require_login=True)
        except:
            raise
        
        messages = volunteer.get_messages()
        
        bookmark = self.request.get("bookmark", None)
        if bookmark:
            bookmark = datetime.strptime(bookmark, '%Y-%m-%d%H:%M:%S')            
            messages = messages.filter('timestamp <=', bookmark).fetch(LIST_LIMIT+1)
        else:
            messages = messages.fetch(LIST_LIMIT+1)
            
        if len(messages) == LIST_LIMIT+1:
            next = self._get_next(lst = messages)                
            messages = messages[:LIST_LIMIT]
        else:
            next = None

        template_values = {
            'volunteer': volunteer,
            'messages': messages,
            'next': next,
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__),'..', 'views', 'messages', '_inbox.html')
        self.response.out.write(template.render(path, template_values, debug=self.is_debugging()))   
    ################################################################################
    # LIST
    def list(self):
        try:
            volunteer = self.auth(require_login=True)
        except:
            raise

        template_values = {
            'volunteer': volunteer,
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__),'..', 'views', 'messages', 'mailbox.html')
        self.response.out.write(template.render(path, template_values, debug=self.is_debugging()))    
    
################################################################################
# Forum page
################################################################################
class Forum(Mailbox):

    ################################################################################
    # GET
    def get(self, url_data):
        try:
            volunteer = self.auth(require_login=False)
        except:
            return

        application = self.get_application()

        forum = {}
        if self.request.path.find('events') == 1:
            #event forum 
            event = Event.get_by_id(int(url_data))
            if not event or event.application.key().id() != application.key().id():
                self.error(404)
                return
            forum['name'] = event.name
            forum['path'] = '/events/' + str(event.key().id())
            forum['recipient_type'] = 'event'
            messages = event.incoming_messages.order('-timestamp')
        elif self.request.path.find('neighborhoods') == 1:
            #neighborhood forum 
            neighborhood = Neighborhood.get_by_id(int(url_data))
            forum['name'] = neighborhood.name
            forum['path'] = '/neighborhoods/' + str(neighborhood.key().id())
            forum['recipient_type'] = 'neighborhood'
            messages = neighborhood.incoming_messages.order('-timestamp')
        else:
            raise
      
        forum['messages'] = messages.fetch(1000)
            
        template_values = {
            'volunteer': volunteer,
            'forum': forum,
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__),'..', 'views', 'messages', 'forum.html')
        self.response.out.write(template.render(path, template_values, debug=self.is_debugging()))         
       
            
   