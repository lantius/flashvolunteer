import os, string, logging
from datetime import datetime

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp

from controllers._params import Parameters


from models.messages import MessageType
from models.volunteer import Volunteer
from models.event import Event
from models.neighborhood import Neighborhood

from controllers.abstract_handler import AbstractHandler
from controllers._utils import is_debugging, send_message

from components.sessions import Session

class AbstractSendMessage(AbstractHandler):
    ################################################################################
    # POST
    def _send_message(self, sender, recipients, type, params):            
        if len(recipients) == 0: return
        
        send_message(to = recipients, 
                     subject = params['subject'], 
                     body = params['body'], 
                     type = type, 
                     sender = sender,
                     autogen = False)
        
        return
    
    def _redirect_to(self):
        return '/messages'

    def _get_recipients(self, id):
        raise
    def _get_message_type(self):
        raise
    def _get_recipient_type(self):
        raise
    def _get_render_path(self):
        raise
    
    def post(self, url_data):
        try:
            account = self.auth(require_login=True)
        except:
            return
        
        id = url_data
        
        recipients = self._get_recipients(id)
         
        params = Parameters.parameterize(self.request)
        
        mt = MessageType.all().filter('name = ', self._get_message_type()).get()  
        
        self._send_message(sender = account, recipients = recipients, type = mt, params = params)
        session = Session()
        self.redirect(session.get('message_redirect','/'))
        if 'message_redirect' in session:
            self.redirect(session['message_redirect'])
            del session['message_redirect']
        else:
            self.redirect(self._redirect_to())
            
    #show message entry form
    def get(self, url_data):
        try:
            account = self.auth(require_login=True)
        except:
            return
        params = Parameters.parameterize(self.request)
        session = Session()
        if 'redirect' in params:
            session['message_redirect'] = params['redirect']
        id = url_data
 
        template_values = {}
        recipients = self._get_recipients(id)
        render_path = self._get_render_path()
        
        url = recipients[0].url()
        
        if len(recipients) > 10: 
            recipients = ', '.join([r.name for r in recipients[:10]]) + '...'
        else:
            recipients = ', '.join([r.name for r in recipients])
            
        template_values.update({
          'volunteer': account.get_user(),
          'recipients': recipients,
          'url': url,
          'recipient_type': self._get_recipient_type()
          })
        self._add_base_template_values(vals = template_values)
      
        self.response.out.write(template.render(render_path, template_values))        
            
class SendMessage_Personal(AbstractSendMessage):
    #enter message into database

    def _get_recipients(self, id):
        #send to person
        return [Volunteer.get_by_id(int(id)).account]

    def _get_message_type(self):
        return 'person_to_person'
    
    def _get_recipient_type(self):
        return 'account'
    
    def _get_render_path(self):
        return os.path.join(os.path.dirname(__file__),'..', 'views', 'messages', 'create_message.html')
    
class SendMessage_Event(AbstractSendMessage):
    def _get_recipients(self, id):
        #send to person
        return [Event.get_by_id(int(id))]

    def _get_message_type(self):
        return 'event_forum'

    def _get_recipient_type(self):
        return 'event'
    
    def _get_render_path(self):
        return os.path.join(os.path.dirname(__file__),'..', 'views', 'messages', 'create_forumpost.html')
    

class SendMessage_Neighborhood(AbstractSendMessage):
    def _get_recipients(self, id):
        #send to person
        return [Neighborhood.get_by_id(int(id))]

    def _get_message_type(self):
        return 'neighborhood_forum'

    def _get_recipient_type(self):
        return 'neighborhood'
    
    def _get_render_path(self):
        return os.path.join(os.path.dirname(__file__),'..', 'views', 'messages', 'create_forumpost.html')