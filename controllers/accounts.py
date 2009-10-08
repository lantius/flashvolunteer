import os, logging
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template
from google.appengine.api import users

from controllers._auth import Authorize
from controllers._helpers import NeighborhoodHelper
from controllers._utils import is_debugging

from models.volunteer import Volunteer
from models.neighborhood import Neighborhood
from models.event import Event
from models.interestcategory import InterestCategory

from components.sessions import Session

import urllib

from controllers.abstract_handler import AbstractHandler

################################################################################
# MainPage
class AccountPage(AbstractHandler):
  LIMIT = 12 
  def get(self):
      
    volunteer = Authorize.login(self, requireVolunteer=False)

    # if volunteer is logged in, then they get their login page
    # otherwise, they get the splash page

    if self.request.path.find('dev_login') > -1:    
      self.dev_login()    
    elif not volunteer:
      self.login()
    elif self.request.path.find('logout') > -1:    
      self.logout(volunteer)
    else:
        self.redirect('/')

  def dev_login(self):
    from google.appengine.api import users
    session = Session()
    
    user = users.get_current_user()    
    session['user'] = user
    self.redirect('/settings')
    
  ################################################################################
  # splashpage
  def login(self):
                
    dev_server = is_debugging() 
    
    template_values = { 
      'new_account': self.request.path == '/create',
      'dev_server': dev_server,
    }
    
    if dev_server:
        from google.appengine.api import users
        template_values['login_url'] = users.create_login_url(dest_url = '/dev_login') 
    else:
        template_values['token_url'] = self.request.host_url + '/rpx_response'
        
    session = Session()
    session['redirect'] = self.request.GET.get('redirect', '/')
        
    self._add_base_template_values(vals = template_values)
    path = os.path.join(os.path.dirname(__file__), '..', 'views', 'home', 'login.html')
    self.response.out.write(template.render(path, template_values))

  ################################################################################
  # homepage
  def logout(self, volunteer):
    session = Session()
    session.delete()
    self.redirect('/')

    
from google.appengine.api import urlfetch
from django.utils import simplejson
from google.appengine.api.users import User

class RPXTokenHandler(AbstractHandler):
      
  def post(self):
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
      if not 'email' in login_info:
          if 'preferredUsername' in login_info:
              login_info['email'] = login_info['preferredUsername'] + '@' + login_info['providerName']
          elif 'identifier' in login_info:
              login_info['email'] = login_info['identifier']
          
      session = Session()
      user = User(email = login_info['email'], _auth_domain = login_info['providerName'])
      session['user'] = user
      logging.info('RPX post')

      self.redirect('/settings')
    else:
      self.redirect('/error')  
    