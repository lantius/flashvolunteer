import os
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template
from google.appengine.api import users

from controllers._utils import is_debugging, get_domain, get_application

from components.sessions import Session
from components.time_zones import now

from datetime import timedelta
import urllib, logging

################################################################################
# MainPage
class AbstractHandler(webapp.RequestHandler):
    def _get_base_url(self):
        return 'http://www.' + get_domain()
    
    def _add_base_template_values(self, vals):
        session = Session()
        account = self.auth()
        is_ajax_request = 'HTTP_X_REQUESTED_WITH' in os.environ and os.environ['HTTP_X_REQUESTED_WITH'] == 'XMLHttpRequest'
        new_login = 'new_login' in session and session['new_login']
        redirected = 'redirected' in session and session['redirected']
        if (redirected or is_ajax_request) and not new_login:
            to_extend = '../empty_layout.html'
        else:
            to_extend = "../_layout.html"
        vals.update( {
            'domain': self._get_base_url(),
            'path': self.request.path,
            'application_alias': get_application().get_alias(),
            'session_id':  session.sid,
            'account': account,
            'to_extend': to_extend
        })

        if new_login:
            del session['new_login']
        if redirected:
            del session['redirected']
                
        if account:
            vals['unread_message_count'] = account.get_unread_message_count()
            user = account.get_user()
            ev = user.eventvolunteers.filter('event_is_upcoming =', False).filter('attended =', None).filter('event_is_hidden =', False).get()
            
            if ev:
                vals['header_message'] = 'Hi %s! Please log your hours for <a href="%s" class="fv">"%s"</a> (or remove yourself from the attendees). Thanks!'%(account.get_first_name(), ev.event.url(), ev.event.name)

        if 'notification_message' in session and len(session['notification_message']) > 0:
            vals['notification_message'] = '<br><br>'.join(session['notification_message'])
                
            session['notification_message'] = []

            
    def auth(self, require_login = False, redirect_to = '/login', require_admin = False):
        s = Session()
        account = self._auth(require_login=require_login, redirect_to = redirect_to, require_admin = require_admin)
        
        return account
    
    def _auth(self, require_login, redirect_to, require_admin):
        session = Session()
        auth = session.get('auth', None)
        if require_login and (not auth or not auth.account):
            self.redirect(redirect_to)        
            if redirect_to == '/login': 
                session['login_redirect'] = self.request.path        
            raise AuthError("You must be signed in to perform this action.")

        if auth:
            application = get_application()
            if not application.key().id() in auth.account.active_applications:
                auth.account.add_application(application)                      

        if require_login:
            if self.request.method == 'POST' and not auth.account.check_session_id(self.request.get('session_id')):
                self.redirect('/timeout')
                session['notification_message'] = ['Your session has timed out. Please log back in when you are ready.']
                raise TimeoutError("Session has timed out.")
                #return (None)       # shouldn't get here except in tests    
            elif require_admin and not users.is_current_user_admin():
                self.redirect(redirect_to)
                raise AuthError('You do not have permission to view this page.')
            
        if not auth:
            return None
        
        return auth.account


    def send_message(self, to, subject, body, type, sender = None, immediate=False, autogen = True, forum = False):
        from models.messages.message import Message
        from models.messages import MessageReceipt
        from google.appengine.ext.db import put, delete
        from utils.html_sanitize import sanitize_html
        
        subject = sanitize_html(subject)
        if subject == '' or subject is None:
            subject = '(No subject)'
        
        body = sanitize_html(body)
        
        message = Message(
          subject = subject,
          body = body,
          sent_by = sender,
          type = type,
          autogen = autogen,
          forum_msg = forum
        )
        message.put()
        mrs = []        
        for recipient in to:
            mr = MessageReceipt(
              recipient = recipient,
              message = message)
            mrs.append(mr)
    
        try:
            put(mrs)
        except:
            for mr in mrs:
                if not mr.is_saved():
                    try:
                        mr.put()
                    except:
                        logging.error('Could not add message receipt of message %i for recipient %i'%(message.key().id(), mr.recipient.key().id()))
    
        if immediate:
            message.send()

    def parameterize(self):
        params = {}
    
        for name in self.request.arguments():
            # TODO: if name = foo[1] then make a sub-hash of foos
            # accessed as params['foo'][1]
            
            params[name] = self.request.get_all(name)
            if len(params[name]) == 1:
                if self.request.content_type.startswith('multipart/form-data'):
                    params[name] = params[name][0]
                else:
                    params[name] = unicode(params[name][0])
        return params
    
    
#    def redirect(self, *args, **kwargs):
#        webapp.RequestHandler.redirect(self, *args, **kwargs)
        
        
class AuthError(Exception):
    """Exception raised for authorization errors.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self,message):
        self.message = message
        
class TimeoutError(Exception):
    """Exception raised for timeout errors.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self,message):
        self.message = message
