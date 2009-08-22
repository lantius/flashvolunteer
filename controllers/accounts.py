import os
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template
from google.appengine.api import users

from controllers._auth import Authorize
from controllers._helpers import NeighborhoodHelper

from models.volunteer import *
from models.neighborhood import *
from models.event import *
from models.interestcategory import *

from components.sessions import Session

################################################################################
# MainPage
class AccountPage(webapp.RequestHandler):
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
    user = users.get_current_user()
    session = Session()
    session['user'] = user
    self.redirect('/settings')
      
  ################################################################################
  # splashpage
  def login(self):

    try:
      from google3.apphosting.runtime import _apphosting_runtime___python__apiproxy
    except ImportError:
      _apphosting_runtime___python__apiproxy = None

    dev_server = not _apphosting_runtime___python__apiproxy
    
    template_values = { 
      'new_account': self.request.path == '/create',
      'dev_server': dev_server
    }
    
    if dev_server:
        from google.appengine.api import users
        template_values['login_url'] = users.create_login_url(dest_url = '/dev_login') 
    else:
        template_values['token_url'] = self.request.host_url + '/rpx_response'
        
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

class RPXTokenHandler(webapp.RequestHandler):
      
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
          login_info['email'] = login_info['preferredUsername'] + '@' + login_info['providerName']
          
      session = Session()
      user = User(email = login_info['email'], _auth_domain = login_info['providerName'])
      session['user'] = user
      
      self.redirect('/settings')
    else:
      self.redirect('/error')  
    