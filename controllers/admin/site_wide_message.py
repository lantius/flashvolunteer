import os, string, logging
from datetime import datetime

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp

from controllers._params import Parameters

from controllers._auth import Authorize

from models.messages import MessageType
from models.volunteer import Volunteer
from models.auth.account import Account

from controllers.abstract_handler import AbstractHandler
from controllers._utils import is_debugging, send_message

from components.sessions import Session

from controllers.message_writer import AbstractSendMessage

class SiteWideMessage(AbstractSendMessage):
    def post(self):
        try:
            volunteer = Authorize.login(self, requireVolunteer=True)
        except:
            return
        
        params = Parameters.parameterize(self.request)
        mt = MessageType.all().filter('name = ', 'site_wide').get()
        
        from_header = 'A message from your friends at Flash Volunteer.\n\n'
        params['body'] = from_header + params['body']
        
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

        self._send_message(sender = volunteer.account, recipients = recipients, type = mt, params = params)
        session = Session()
        self.redirect(session.get('message_redirect','/'))
        if 'message_redirect' in session:
            self.redirect(session['message_redirect'])
            del session['message_redirect']
        else:
            self.redirect('/messages#sent')

