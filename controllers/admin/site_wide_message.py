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

from controllers.message_writer import AbstractSendMessage

class SiteWideMessage(AbstractSendMessage):
    def post(self):
        try:
            volunteer = Authorize.login(self, requireVolunteer=True)
        except:
            return
        
        #todo: make this work for greater than 1000
        recipients = Volunteer.all().fetch(limit = 1000)
        params = Parameters.parameterize(self.request)
        mt = MessageType.all().filter('name = ', 'site_wide').get()
        
        from_header = 'A message from your friends at Flash Volunteer.\n\n'
        params['body'] = from_header + params['body']
        
        chunk_size = 250
        ranges = [(start * chunk_size, start * chunk_size +chunk_size) 
                  for start in range(0, len(recipients) / chunk_size + 1)]
        
        # send this in chunks because of app engine limitations on indexed properties 
        # (see http://groups.google.com/group/google-appengine/browse_thread/thread/d5f4dcb7d00ed4c6)
        for start, end in ranges:
            self._send_message(sender = volunteer, recipients = recipients[start:end], type = mt, params = params)
        session = Session()
        self.redirect(session.get('message_redirect','/'))
        if 'message_redirect' in session:
            self.redirect(session['message_redirect'])
            del session['message_redirect']
        else:
            self.redirect('/messages#sent')
        
    def get(self):
        try:
            volunteer = Authorize.login(self, requireVolunteer=True)
        except:
            return
        params = Parameters.parameterize(self.request)
        session = Session()
        if 'redirect' in params:
            session['message_redirect'] = params['redirect']
        
        recipients =  Volunteer.all().fetch(limit = 20) 
        url = '/admin'
        self._get_helper(recipients = recipients, url = url)

