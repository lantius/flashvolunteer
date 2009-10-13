import os, string, logging
from datetime import datetime

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from controllers._params import Parameters

from controllers._auth import Authorize

from models.messages import MessageType
from models.volunteer import Volunteer

from controllers.abstract_handler import AbstractHandler
from controllers._utils import is_debugging, send_message

from components.sessions import Session


class AbstractSendMessage(AbstractHandler):
    ################################################################################
    # POST
    def _send_message(self, sender, recipients, type_id, params):            
        mt = MessageType.all().filter('order = ', type_id).get()
        
        send_message(to = recipients, 
                     subject = params['subject'], 
                     body = params['body'], 
                     type = mt, 
                     sender = sender,
                     autogen = False)
        
        session = Session()
        self.redirect(session.get('redirect','/'))
        return

    def _get_helper(self, recipients, url):
        try:
            volunteer = Authorize.login(self, requireVolunteer=True, redirectTo='/settings')
        except:
            return
    
        params = Parameters.parameterize(self.request)
        
        template_values = {
          'volunteer': volunteer,
          'recipients': ', '.join([r.name for r in recipients]),
          'url': url
          }
        self._add_base_template_values(vals = template_values)
      
        path = os.path.join(os.path.dirname(__file__),'..', 'views', 'messages', 'create_message.html')
        self.response.out.write(template.render(path, template_values))

class SendMessage_Personal(AbstractSendMessage):
    def post(self, url_data):
        try:
            volunteer = Authorize.login(self, requireVolunteer=True, redirectTo='/settings')
        except:
            return
        
        id = url_data
        recipients = [Volunteer.get_by_id(int(id))]
        params = Parameters.parameterize(self.request)
        self._send_message(sender = volunteer, recipients = recipients, type_id = 4, params = params)
        
    def get(self, url_data):
        try:
            volunteer = Authorize.login(self, requireVolunteer=True, redirectTo='/settings')
        except:
            return
        
        id = url_data
        recipient = Volunteer.get_by_id(int(id))
        recipients = [recipient]
        url = recipient.url()
        self._get_helper(recipients = recipients, url = url)

