import os, logging, hashlib
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template

from controllers._helpers import NeighborhoodHelper
from controllers._utils import is_debugging

from models.volunteer import Volunteer
from models.neighborhood import Neighborhood
from models.event import Event
from models.interestcategory import InterestCategory
from models.auth import Account, Auth

from components.sessions import Session

import urllib

from controllers.abstract_handler import AbstractHandler
from google.appengine.api import urlfetch
from django.utils import simplejson
from google.appengine.api.users import User


################################################################################
# MainPage
class Login(AbstractHandler):
    LIMIT = 12 
    def get(self, errors = None):
        
        account = self.auth()
    
        if self.request.path.find('dev_login') > -1:    
            self.dev_login()    
        elif not account:
            self.login()
        elif self.request.path.find('logout') > -1:    
            self.logout()
        else:
            self.redirect('/')

    def logout(self):
        session = Session()
        session.delete()
        self.redirect('/')
        
    def dev_login(self):
        from google.appengine.api import users
        session = Session()
        user = users.get_current_user()   
        v = None
        
        auth = Auth.all().filter('identifier =', user.email()).filter('strategy =', 'dev').get()
        if auth is None:
            account = Account(
                preferred_email = user.email(),
                name = user.email(),
                group_wheel = False
            )
            account.put()

            auth = Auth(
                strategy = 'dev',
                identifier = user.email()
            )
            auth.account = account
            auth.put()
            v = Volunteer(account = account)
            v.put()
        else:
            account = auth.account
            
            
        session['auth'] = auth
        session['user'] = user
        session['account'] = account
        
        if 'login_redirect' in session:
            self.redirect(session['login_redirect'])
            del session['login_redirect']
        else:
            self.redirect('/#/settings')
        session['new_login'] = True
      
    def login(self, errors = None, email = None):
        logging.info('handling get')
        dev_server = is_debugging() 
        
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
            
            
        session = Session()
        logging.info('login referrer:'+self.request.referrer)

        self._add_base_template_values(vals = template_values)
        path = os.path.join(os.path.dirname(__file__), '..', '..', 'views', 'accounts', 'login.html')
        self.response.out.write(template.render(path, template_values))
    
    def post(self):
        logging.info('handling post .1')
        if self.request.get('token', None):
            self.rpx_auth()
        else:
            self.fv_auth()
        session = Session()
        session['new_login'] = True
            
    def fv_auth(self):
        from models.auth import Account, Auth
        errors = {}
        
        params = self.parameterize() 
        
        session = Session()
        
        if params['session_id'] != session.sid:
            self.redirect('/timeout')            

        email = params['email']
        password = params['password']
        
        auth = Auth.all().filter('identifier =', email).filter('strategy =', 'fv').get()
        if not auth:
            logging.info('could not log user in, no user by that name')
            errors['user_not_found'] = 1
            self.login(errors = errors, email = email)
            return
        
        hash = hashlib.sha224(password + auth.salt).hexdigest()
        if hash != auth.digest:
            logging.info('could not log user in, wrong password')
            errors['wrong_password'] = 1
            self.login(errors = errors, email = email)
            return
        
        session['auth'] = auth                               
        if 'login_redirect' in session:
            self.redirect(session['login_redirect'])
            del session['login_redirect']
        else:
            self.redirect('/#/profile')
                
    def rpx_auth(self):
        logging.info('handling post1')
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
        logging.info('handling post')
        if json['stat'] == 'ok':  
            login_info = json['profile']  

            if 'email' in login_info:
                login_info['identifier'] = login_info['email']
            elif 'preferredUsername' in login_info:
                login_info['identifier'] = login_info['preferredUsername'] + '@' + login_info['providerName']

            session = Session()
            session['login_info'] = login_info

            from models.auth import Auth
            auth = Auth.all().filter('identifier =', login_info['identifier']).filter('strategy =', login_info['providerName']).get()

            if auth:
                logging.info('got auth')
                session['auth'] = auth
                account = self.auth()
                check_avatar(account = account)
                if 'login_redirect' in session:
                    logging.info('redirecting to %s'%session['login_redirect'])
                    self.redirect(session['login_redirect'])
                    del session['login_redirect']
                else:
                    self.redirect('/#/profile')
            else:
                self.redirect('/#/new')
                
        else:
            self.redirect('/#/login')      

def check_avatar(account):
    if not account: return
    volunteer = account.get_user()
    
    session = Session()
    if volunteer and \
      volunteer.avatar is None and \
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
