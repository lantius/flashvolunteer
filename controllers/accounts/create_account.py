from components.sessions import Session
from controllers._auth import Authorize
from controllers._helpers import NeighborhoodHelper
from controllers._params import Parameters
from controllers._utils import is_debugging, send_message 
from controllers.abstract_handler import AbstractHandler
from controllers.accounts.login import check_avatar

from google.appengine.api.users import User
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template

from models.auth import Account, Auth
from models.volunteer import Volunteer

import os, logging, hashlib
import urllib

class CreateAccount(AbstractHandler):
    
    def get(self, account = None, volunteer = None):
        session = Session()

        login_info = session.get('login_info', None)
        
        if account is None:
            name = None
            if login_info:
                email = login_info['email']
                name = login_info.get('displayName', None)
            else:
                email = None
            
            
            account = Account(
                preferred_email = email,
                name = name
            )
            
        if volunteer is None:
            volunteer = Volunteer()
            
        session['account'] = account
        session['volunteer'] = volunteer
        
            
        template_values = {
            'volunteer': volunteer,
            'account': account,
            'home_neighborhoods': NeighborhoodHelper().selected(volunteer.home_neighborhood),
            'work_neighborhoods': NeighborhoodHelper().selected(volunteer.work_neighborhood),
            'fv_account': login_info is None,
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__),'..', '..', 'views', 'accounts', 'new_account.html')
        self.response.out.write(template.render(path, template_values))    
        
    def post(self):
        
        params = Parameters.parameterize(self.request)    
        session = Session()
        account = session.get('account')
        volunteer = session.get('volunteer')
        
        if params['session_id'] != session.sid:
            self.redirect('/timeout')
            return        
        
        #can't combine these two less risk short circuiting...
        valid_entry = volunteer.validate(params) 
        valid_entry = account.validate(params) and valid_entry
        
        if not valid_entry:
            self.get(account = account, volunteer = volunteer)
            return False

        login_info = session.get('login_info', None)
        if not login_info:
            salt = session.sid
            login_info = {
                  'providerName': "fv",
                  'identifier': params['email'],
                  'digest': hashlib.sha224(params['password'] + salt).hexdigest(),
                  'salt': salt
            }
            
        auth = Auth(
            strategy = login_info['providerName'],
            identifier = login_info['identifier']
        )
        if login_info['providerName'] == 'fv':
            auth.digest = login_info['digest']
            auth.salt = login_info['salt']


        if not account:
            self.redirect('/new')
            return False

        user = User(email = account.preferred_email)
        account.user = user
        
        try:
            try:
                account.put()
            except: 
                account.put()
            
            try:
                volunteer.account = account
                volunteer.user = user
                volunteer.put()
            except:
                volunteer.put()
                
            try:
                auth.account = account
                auth.put()
            except:
                auth.put()

        except:
            self.get(account = account, volunteer = volunteer)
            return False
        
        session['auth'] = auth
        session['login_info'] = login_info
        
        check_avatar(volunteer = volunteer)
                
        msg_params = {'name': volunteer.name} 
                
        from components.message_text import type3  
        from models.messages import MessageType
                  
        send_message(to = [volunteer], 
                     subject = type3.subject%msg_params,
                     body = type3.body%msg_params,
                     type= MessageType.all().filter('name =', 'welcome').get(), 
                     immediate = True)
        
        if 'login_redirect' in session:
            self.redirect(session['login_redirect'])
            del session['login_redirect']
        self.redirect('/settings')
