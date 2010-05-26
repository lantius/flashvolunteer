import os, string, logging
from datetime import datetime

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp

from models.messages import MessageType

from controllers.message_writer import AbstractSendMessage

class SiteWideMessage(AbstractSendMessage):
    def post(self, url_data = None):
        try:
            volunteer = self.auth(require_login=True)
        except:
            return
        
        params = self.parameterize()
        mt = MessageType.all().filter('name = ', 'site_wide').get()
        
        from_header = 'A message from your friends at Flash Volunteer.\n\n'
        params['body'] = from_header + params['body']
        
        recipients = AbstractSendMessage.get_all_recipients()
        
        logging.info('Site wide message size: %i'%len(recipients))
        self._send_message(sender = volunteer, recipients = recipients, type = mt, params = params, forum = False)
        session = self._session()

        if 'message_redirect' in session:
            self.redirect(session['message_redirect'])
            del session['message_redirect']
        else:
            self.redirect('/#/messages')

        
    def _get_message_type(self):
        return 'site_wide'
    def _get_recipient_type(self):
        return 'volunteer'
    def _get_render_path(self):
        return os.path.join(os.path.dirname(__file__),'..', '..', 'views', 'messages', 'create_message.html')
    def _get_url(self, recipients):
        return '/admin'