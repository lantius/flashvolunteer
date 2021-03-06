import os
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template
from google.appengine.api import users

from components.gaeutilities.sessions import Session
from components.time_zones import now

from datetime import timedelta
import urllib, logging

from models.application import Application
from models.applicationdomain import ApplicationDomain
from models.skin import Skin

from google.appengine.api import memcache
from google.appengine.ext.db import put, delete



from utils.misc_methods import get_google_maps_api_key
################################################################################
# MainPage
class AbstractHandler(webapp.RequestHandler):
    
    def _session(self):
        return Session()
    
    def _get_base_url(self):
        return 'http://www.' + self.get_domain()
    
    def _add_base_template_values(self, vals):
        session = self._session()
        #logging.info('_add_base_template_values: %s'%session.sid)
        volunteer = self.get_account()
        application = self.get_application()
            
        is_ajax_request = self.ajax_request()
        new_login = 'new_login' in session and session['new_login']
        redirected = 'redirected' in session and session['redirected']
        if (redirected or is_ajax_request) and not new_login:
            to_extend = '../empty_layout.html'
        else:
            to_extend = "../_layout.html"
        vals.update( {
            'domain': self._get_base_url(),
            'path': self.request.path,
            'application_alias': application.get_alias(),
            'session_id':  session.sid,
            'volunteer': volunteer,
            'to_extend': to_extend,
            'skin': application.skin.get(),
            'GOOGLEMAPSAPI': get_google_maps_api_key()
        })

        if new_login:
            del session['new_login']
        if redirected:
            del session['redirected']
                
        if volunteer:
            vals['unread_message_count'] = volunteer.get_unread_message_count()
            evs = volunteer.eventvolunteers.filter('event_is_upcoming =', False).filter('attended =', None).filter('event_is_hidden =', False).fetch(20)
            log_ev = None
            for ev in evs:
                if ev.application.key().id() == application.key().id():
                    log_ev = ev
                    break
                
            if log_ev:
                vals['header_message'] = 'Hi %s! Please log your hours for <a href="%s" class="fv">"%s"</a> (or remove yourself from the attendees). Thanks!'%(volunteer.get_first_name(), log_ev.event.url(), log_ev.event.name)

        if 'notification_message' in session and is_ajax_request and len(session['notification_message']) > 0:
            vals['notification_message'] = '<br><br>'.join(session['notification_message'])
                
            session['notification_message'] = []

            
    def get_account(self):
        session = self._session()
        auth = session.get('auth', None)   
        if auth is None: return None
        else:
            try:
                return auth.user
            except:
                session.flush()
                return None
            
    def auth(self, require_login = False, redirect_to = '/login', require_admin = False):
        session = self._session()
        #logging.info('auth: %s'%session.sid)
        #logging.error(whosdaddy() + '   ' + whoami() + 'login_redirect' in session)
        
        if require_admin: require_login = True
        
        volunteer = self._auth(require_login=require_login, redirect_to = redirect_to, require_admin = require_admin)
        
        return volunteer
    
    #def redirect(self, uri):
    #    logging.info('redirecting to %s'%uri)
    #    webapp.RequestHandler.redirect(self,uri)
        
    def _auth(self, require_login, redirect_to, require_admin):
        
        session = self._session()
        
        volunteer = self.get_account()
        
        if volunteer:
            application = self.get_application()
            if not application.key().id() in volunteer.applications:
                volunteer.add_application(application)                      

        if require_login:
            if not volunteer:
                self.redirect(redirect_to)        
                if redirect_to == '/login': 
                    session['login_redirect'] = self.request.path        
                raise AuthError("You must be signed in to perform this action.")
                        
            elif self.request.method == 'POST' and not volunteer.check_session_id(self.request.get('session_id'), session = session):
                self.redirect('/timeout')
                self.add_notification_message('Your session has timed out. Please log back in when you are ready.')
                raise TimeoutError("Session has timed out.")
                #return (None)       # shouldn't get here except in tests    
            elif require_admin and not volunteer.is_admin():
                self.redirect(redirect_to)
                raise AuthError('You do not have permission to view this page.')
        
        return volunteer

    def ajax_request(self):
        return 'HTTP_X_REQUESTED_WITH' in os.environ and os.environ['HTTP_X_REQUESTED_WITH'] == 'XMLHttpRequest'
    


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
    
    def add_notification_message(self, message):
        session = self._session()
        logging.info('writting %s to %s'%(session.sid, message))
        if 'notification_message' in session:
            session['notification_message'] = session['notification_message'] + [message]
        else:
            session['notification_message'] = [message]
            
    def get_server(self):
        """Determines which host requests are being served from. 
        
        0 == development server
        1 == flashvolunteer-dev.appspot.com or development.flashvolunteer.org
        2 == flashvolunteer.org etc.    
        """
        
        if 'SERVER_SOFTWARE' not in os.environ or os.environ['SERVER_SOFTWARE'].startswith('Development'): 
            return 0
        else:
            app_id = os.environ['APPLICATION_ID']
            if app_id == 'flashvolunteer-dev':
                return 1
            elif app_id == 'flashvolunteer': 
                return 2
            elif app_id == 'georgetown-fv':
                return 3
                
    def get_application(self, just_id = False):
        domain = self.get_domain()
        key = "app-%s"%domain
        
        application = memcache.get(key)
        if application is None:
            app_domain = ApplicationDomain.all().filter('domain = ',domain).get()
            if app_domain is None:
                #if Application.all().count() == 0:
                from utils.applications.operations import synchronize_apps
                logging.info('syncing apps')
                synchronize_apps(server = self.get_server())
                
        
                logging.error('got bad domain name: %s'%domain)
                #TODO: is it a good policy to return seattle app by default?
                return Application.all().filter('name = ', 'seattle').get()
            application = app_domain.application
            memcache.set(key, application)
        elif isinstance(application, ApplicationDomain):
            application = application.application
            memcache.set(key, application)
            
        if just_id: return application.key().id()
        else: return application
        
    def get_domain(self):
        
        session = self._session()
        if 'this_domain' not in session:
            domain = os.environ['HTTP_HOST']
            if domain.startswith('www.'):
                domain = domain[4:]
            
            if domain.endswith('flashvolunteer.appspot.com'):
                domain = domain.replace('flashvolunteer.appspot.com', 'flashvolunteer.org')
            elif domain.endswith('flashvolunteer-dev.appspot.com'): 
                domain = 'development.flashvolunteer.org'
            elif domain.endswith('georgetown-fv.appspot.com'):
                domain = 'georgetown.flashvolunteer.org'
    
    #        logging.info('************')
    #        logging.info('DOMAIN: '+ domain)
    #        logging.info('HTTP_HOST: '+ os.environ['HTTP_HOST'])
    #        logging.info('endswith: ' + str(domain.endswith('flashvolunteer-dev.appspot.com')))
    
    
            session['this_domain'] = domain
        return session['this_domain']
   
#    def redirect(self, *args, **kwargs):
#        webapp.RequestHandler.redirect(self, *args, **kwargs)
        
    def is_debugging(self):
        """Detects if app is running in production or not.
    
        Returns a boolean.
        """
        return self.get_server() == 0

    @classmethod
    def send_message(cls, to, subject, body, type, domain, sender = None, immediate=False, autogen = True, forum = False):
        from models.messages.message import Message
        from utils.html_sanitize import sanitize_html
        from google.appengine.ext import deferred
        
        CHUNKSIZE = 50
        
        subject = sanitize_html(subject)
        if subject == '' or subject is None:
            subject = '(No subject)'
        
        body = sanitize_html(body)
        
        message = Message(
          subject = subject,
          body = body,
          sender = sender,
          type = type,
          autogen = autogen,
          forum_msg = forum
        )
        message.put()

        num_recipients = len(list(to))
        if num_recipients > CHUNKSIZE: 
            for i in range(0, num_recipients/CHUNKSIZE + 1):
                deferred.defer(put_message_receipts, to[i*CHUNKSIZE:(i+1)*CHUNKSIZE], message.key().id(), domain, immediate)
        else:
            deferred.defer(put_message_receipts, to, message.key().id(), domain, immediate)

def put_message_receipts(to, message_key, domain, immediate):
    from models.messages import Message, MessageReceipt
    
    message = Message.get_by_id(message_key)
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
                    logging.error('Could not add message receipt of message %i for recipient %i'%(mr.message.key().id(), mr.recipient.key().id()))            
                    
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
