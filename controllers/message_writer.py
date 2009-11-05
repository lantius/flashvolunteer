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


class SendMessage_Personal(AbstractSendMessage):
    #enter message into database
    def post(self, url_data):
        try:
            account = self.auth(require_login=True)
        except:
            return
        
        id = url_data
        if self.request.path.find('volunteers') == 1: #found at pos 1
          #send to person
          recipients = [Volunteer.get_by_id(int(id))]
        elif self.request.path.find('events') == 1:
          #send to event forum 
          recipients = [Event.get_by_id(int(id))]
        elif self.request.path.find('neighborhoods') == 1:
          #send to neighborhood forum 
          recipients = [Neighborhood.get_by_id(int(id))]
         
        params = Parameters.parameterize(self.request)
        mt = MessageType.all().filter('name = ', 'person_to_person').get()
        
        #from_header = 'From: %s\n\n'%account.name
        #params['body'] = from_header + params['body']
        self._send_message(sender = account, recipients = recipients, type = mt, params = params)
        session = Session()
        self.redirect(session.get('message_redirect','/'))
        if 'message_redirect' in session:
            self.redirect(session['message_redirect'])
            del session['message_redirect']
        else:
            self.redirect('/messages')

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
        if self.request.path.find('volunteers') == 1: #found at pos 1
          #send to person
          recipient = Volunteer.get_by_id(int(id))
          template_values = {'recipient_type': 'volunteer'}
          render_path = os.path.join(os.path.dirname(__file__),'..', 'views', 'messages', 'create_message.html')
        elif self.request.path.find('events') == 1:
          #send to event forum 
          recipient = Event.get_by_id(int(id))
          template_values = {'recipient_type': 'event'}
          render_path = os.path.join(os.path.dirname(__file__),'..', 'views', 'messages', 'create_forumpost.html')
        elif self.request.path.find('neighborhoods') == 1:
          #send to neighborhood forum 
          recipient = Neighborhood.get_by_id(int(id))
          template_values = {'recipient_type': 'neighborhood'}
          render_path = os.path.join(os.path.dirname(__file__),'..', 'views', 'messages', 'create_forumpost.html')
        
        recipients = [recipient]
        url = recipient.url()
        
        if len(recipients) > 10: 
            recipients = ', '.join([r.name for r in recipients[:10]]) + '...'
        else:
            recipients = ', '.join([r.name for r in recipients])
            
        template_values.update({
          'volunteer': account.get_user(),
          'recipients': recipients,
          'url': url
          })
        self._add_base_template_values(vals = template_values)
      
        self.response.out.write(template.render(render_path, template_values))

