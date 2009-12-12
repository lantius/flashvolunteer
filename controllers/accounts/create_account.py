from components.sessions import Session
from controllers._helpers import NeighborhoodHelper
from controllers._utils import is_debugging 
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
        dev_server = is_debugging() 
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
            'dev_server': dev_server,
            'volunteer': volunteer,
            'account': account,
            'home_neighborhoods': NeighborhoodHelper().selected(volunteer.home_neighborhood),
            'work_neighborhoods': NeighborhoodHelper().selected(volunteer.work_neighborhood),
            'fv_account': login_info is None,
          }
        self._add_base_template_values(vals = template_values)

        if dev_server:
            from google.appengine.api import users
            template_values['login_url'] = users.create_login_url(dest_url = '/dev_login') 
        else:
            template_values['token_url'] = self.request.host_url + '/login'

        
        path = os.path.join(os.path.dirname(__file__),'..', '..', 'views', 'accounts', 'new_account.html')
        self.response.out.write(template.render(path, template_values))    
        
    def post(self):
        
        params = self.parameterize()    
        session = Session()
        account = session.get('account')
        volunteer = session.get('volunteer')
        
        if params['session_id'] != session.sid:
            self.redirect('/timeout')
            return        
        
        #can't combine these two else risk not validating both...
        valid_entry = volunteer.validate(params) 
        valid_entry = account.validate(params) and valid_entry
        
        if not valid_entry:
            session['notification_message'] = ['<br>'.join(account.error.values())]
            self.redirect('/#/new')
            return False

        login_info = session.get('login_info', None)
        if not login_info:
            salt = session.sid
            login_info = {
                  'providerName': "fv",
                  'identifier': params['email'],
                  'digest': hashlib.sha224(params['password'] + salt).hexdigest(),
                  'digest2': hashlib.sha224(hashlib.sha224(params['password']).hexdigest() + salt).hexdigest(),
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
            self.redirect('/#/new')
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
            session['notification_message'].append('We\'re sorry, your account could not be created. Please try again.')
            self.redirect('/#/new')
            return False
        
        session['auth'] = auth
        session['login_info'] = login_info
        
        check_avatar(account = account)
                
        msg_params = {'name': volunteer.name} 
                
        from components.message_text import type3  
        from models.messages import MessageType
                  
        self.send_message(to = [account], 
                     subject = type3.subject%msg_params,
                     body = type3.body%msg_params,
                     type= MessageType.all().filter('name =', 'welcome').get(), 
                     immediate = True)
        
        del session['login_info']
        if 'login_redirect' in session:
            self.redirect(session['login_redirect'])
            del session['login_redirect']
        else:
            self.redirect('/#/settings')
