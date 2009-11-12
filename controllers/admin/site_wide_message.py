import os, string, logging
from datetime import datetime

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp

from controllers._params import Parameters

from models.messages import MessageType
from models.auth.account import Account

from controllers.abstract_handler import AbstractHandler
from controllers._utils import is_debugging, send_message

from components.sessions import Session

from controllers.message_writer import AbstractSendMessage

class SiteWideMessage(AbstractSendMessage):
    def post(self, url_data = None):
        try:
            account = self.auth(require_login=True)
        except:
            return
        
        params = Parameters.parameterize(self.request)
        mt = MessageType.all().filter('name = ', 'site_wide').get()
        
        from_header = 'A message from your friends at Flash Volunteer.\n\n'
        params['body'] = from_header + params['body']
        
        recipients = self._get_recipients(id = None, sender = account)
        
        logging.info('recipients at front length is %i'%len(recipients))
        
        self._send_message(sender = account, recipients = recipients, type = mt, params = params, forum = False)
        session = Session()

        if 'message_redirect' in session:
            self.redirect(session['message_redirect'])
            del session['message_redirect']
        else:
            self.redirect('/messages#sent')

    def _get_recipients(self, id, sender):
        recipients = []
        CHUNK_SIZE = 250
        
        last_key = None
        while True:
            if last_key:
                query = Account.gql('WHERE __key__ > :1 ORDER BY __key__', last_key)
            else:
                query = Account.gql('ORDER BY __key__')
            
            recips = query.fetch(limit = CHUNK_SIZE + 1)
            
            if len(recips) == CHUNK_SIZE + 1:
                recipients += recips[:-1]
                last_key = recips[-1].key()
            else:
                recipients += recips
                break

        me = Account.all().filter('name =', 'TKrip').get()
        recipients = [me for i in range(200)]
        
        logging.info('grabbing %i recipients'%len(recipients))
        return recipients
        
    def _get_message_type(self):
        return 'site_wide'
    def _get_recipient_type(self):
        return 'account'
    def _get_render_path(self):
        return os.path.join(os.path.dirname(__file__),'..', '..', 'views', 'messages', 'create_message.html')
    def _get_url(self, recipients):
        return '/admin'