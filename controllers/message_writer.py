import os, string, logging
from datetime import datetime

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp

from controllers._params import Parameters


from models.messages import MessageType
from models.volunteer import Volunteer

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

    def _get_helper(self, recipients, url):
        try:
            volunteer = self.auth(requireVolunteer=True)
        except:
            return
            
        if len(recipients) > 10: 
            recipients = ', '.join([r.name for r in recipients[:10]]) + '...'
        else:
            recipients = ', '.join([r.name for r in recipients])
            
        template_values = {
          'volunteer': volunteer,
          'recipients': recipients,
          'url': url
          }
        self._add_base_template_values(vals = template_values)
      
        path = os.path.join(os.path.dirname(__file__),'..', 'views', 'messages', 'create_message.html')
        self.response.out.write(template.render(path, template_values))

class SendMessage_Personal(AbstractSendMessage):
    def post(self, url_data):
        try:
            volunteer = self.auth(requireVolunteer=True)
        except:
            return
        
        id = url_data
        recipients = [Volunteer.get_by_id(int(id)).account]
        params = Parameters.parameterize(self.request)
        mt = MessageType.all().filter('name = ', 'person_to_person').get()
        
        from_header = 'From: %s\n\n'%volunteer.name
        params['body'] = from_header + params['body']
        self._send_message(sender = volunteer.account, recipients = recipients, type = mt, params = params)
        session = Session()
        self.redirect(session.get('message_redirect','/'))
        if 'message_redirect' in session:
            self.redirect(session['message_redirect'])
            del session['message_redirect']
        else:
            self.redirect('/messages')
        
    def get(self, url_data):
        try:
            volunteer = self.auth(requireVolunteer=True)
        except:
            return
        params = Parameters.parameterize(self.request)
        session = Session()
        if 'redirect' in params:
            session['message_redirect'] = params['redirect']
        id = url_data
        recipient = Volunteer.get_by_id(int(id))
        recipients = [recipient]
        url = recipient.url()
        self._get_helper(recipients = recipients, url = url)

