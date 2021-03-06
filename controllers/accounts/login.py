import os, logging, hashlib
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template

from models.volunteer import Volunteer
from models.auth import Auth

import urllib

from controllers.abstract_handler import AbstractHandler
from google.appengine.api import urlfetch
from django.utils import simplejson
from google.appengine.ext import deferred
from google.appengine.api import memcache

################################################################################
# MainPage
class Login(AbstractHandler):
    LIMIT = 12 
    def get(self, errors = None):
        
        volunteer = self.auth()
        
        params = self.parameterize()
            
        if self.request.get('token', None):
            self.rpx_auth()
        elif self.request.path.find('dev_login') > -1:    
            self.dev_login()    
        elif not volunteer:
            redirect = None
            if 'redirect' in params:
                redirect = params['redirect']
            self.login(redirect = redirect)
        elif self.request.path.find('logout') > -1:    
            self.logout()
        else:
            self.redirect('/')

    def logout(self):
        session = self._session()
        session.flush()
        self.redirect('/')
        
    def dev_login(self):
        from google.appengine.api import users
        session = self._session()
        
        user = users.get_current_user()   
        v = None
        
        auth = Auth.all().filter('identifier =', user.email()).filter('strategy =', 'dev').get()
        if auth is None:
            volunteer = Volunteer(
                preferred_email = user.email(),
                name = user.email(),
                group_wheel = False
            )
            volunteer.put()

            auth = Auth(
                strategy = 'dev',
                identifier = user.email()
            )
            auth.user = volunteer
            auth.put()
        else:
            volunteer = auth.user
            
            
        session['auth'] = auth
        session['user'] = user
        session['volunteer'] = volunteer
        
        if 'login_redirect' in session:
            self.redirect(session['login_redirect'])
            del session['login_redirect']
        else:
            self.redirect('/#/settings')
        session['new_login'] = True
      
    def login(self, errors = None, email = None, redirect = None):
        dev_server = self.is_debugging() 
        session = self._session()

        if redirect:
            session['login_redirect'] = redirect
            #logging.info('got redirect: %s'%redirect)
            
        template_values = { 
          'dev_server': dev_server,
          'errors': errors,
          'email': email
        }
        
        if dev_server:
            from google.appengine.api import users
            template_values['login_url'] = users.create_login_url(dest_url = '/dev_login') 
        else:
            template_values['token_url'] = self.request.host_url + '/login'
            
        #logging.info('login referrer:'+self.request.referrer)

        self._add_base_template_values(vals = template_values)
        path = os.path.join(os.path.dirname(__file__), '..', '..', 'views', 'accounts', 'login.html')
        self.response.out.write(template.render(path, template_values))
            
    def post(self):
        session = self._session()
        
        if self.request.get('token', None):
            #logging.info('posting from rpx')
            self.rpx_auth()
        else:
            self.fv_auth()

        session['new_login'] = True
        if 'auth' in session:
            self.__login_cache()
            
    def fv_auth(self):
        params = self.parameterize() 
        
        session = self._session()
        
        if params['session_id'] != session.sid:
            self.redirect('/timeout')            

        email = params['email']
        password = params['password']
        
        auth = Auth.all().filter('identifier =', email).filter('strategy =', 'fv').get()
        if not auth:
            logging.info('could not log user in, no user by that name')
            self.add_notification_message('Sorry, we do not have an account with that email. If you are new to Flash Volunteer, please click the "Signup" button. If you\'ve previously used a third party to login, please select the relevant third party to the right. Thanks!')
            self.redirect('/#/login')
            return
        
        hash = hashlib.sha224(password + auth.salt).hexdigest()
        hash2 = hashlib.sha224(hashlib.sha224(password).hexdigest() + auth.salt).hexdigest() #for mobile clients that hash before sending password on...
        
        if not hash or (hash not in [auth.digest,auth.digest2] and hash2 not in [auth.digest,auth.digest2]):
            logging.info('could not log user in, wrong password')
            self.add_notification_message('Sorry, that is not the right password for this account.')
            self.redirect('/#/login')
            return
        
        if not auth.digest2: 
            auth.digest2 = hash2
            auth.put()
        
        session['auth'] = auth     
                                  
        if 'login_redirect' in session:
            self.redirect(session['login_redirect'])
            del session['login_redirect']
        else:
            self.redirect('/#/profile')
                
    def rpx_auth(self):
        token = self.request.get('token')
        url = 'https://rpxnow.com/api/v2/auth_info'
        args = {
          'format': 'json',
          'apiKey': 'b269b6356c17af69406026edb6b87d65df667b5e',
          'token': token
          }
        r = urlfetch.fetch(url=url,
                           payload=urllib.urlencode(args),
                           method=urlfetch.POST,
                           headers={'Content-Type':'application/x-www-form-urlencoded'}
                           )
        json = simplejson.loads(r.content)
        if json['stat'] == 'ok':  
            login_info = json['profile']  
            
            if 'email' in login_info and login_info['providerName'] != 'Facebook':
                login_info['identifier'] = login_info['email']
            elif 'preferredUsername' in login_info:
                login_info['identifier'] = login_info['preferredUsername'] + '@' + login_info['providerName']
                
            if 'email' not in login_info: 
                login_info['email'] = ''    
                
            session = self._session()
            session['login_info'] = login_info

            from models.auth import Auth
            auth = Auth.all().filter('identifier =', login_info['identifier']).filter('strategy =', login_info['providerName']).get()

            #logging.info(login_info)
            #logging.info(auth)
            #logging.info(login_info['identifier'])
            
            if auth:
                session['auth'] = auth
                volunteer = self.auth()
                check_avatar(volunteer = volunteer, session = session)

                if 'login_redirect' in session:
                    self.redirect(session['login_redirect'])
                    del session['login_redirect']
                else:
                    self.redirect('/#/profile')
            else:
                self.redirect('/#/new')
                
        else:
            self.redirect('/#/login')      

    def __login_cache(self):
        volunteer = self.auth()
        deferred.defer(cache_on_login, vol_id = volunteer.key().id(), _queue="login")
        
def cache_on_login(vol_id):
    volunteer = Volunteer.get_by_id(vol_id)
    logging.info('cache on login for vol %i'%vol_id)
    key = 'volunteer_teammates_%i'%vol_id
    
    memcache.set(key, dict( [(vf.followed.key().id(), 1) for vf in volunteer.following] ))
    
def check_avatar(volunteer, session):
    if not volunteer: return
    
    if volunteer.avatar is None and \
      'photo' in session['login_info']:

        try:
            import imghdr
        
            img = fetch(url = session['login_info']['photo']).content   
            content_type = imghdr.what(None, img)
            if not content_type:
                return
        
            volunteer.avatar_type = 'image/' + content_type
            volunteer.avatar = img
            volunteer.put()          
        except:
            pass
