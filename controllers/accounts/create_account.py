import os, logging, hashlib
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template

from controllers._auth import Authorize
from controllers._helpers import NeighborhoodHelper
from controllers._utils import is_debugging

from models.auth import Account

from components.sessions import Session
from controllers._params import Parameters

import urllib

from controllers.abstract_handler import AbstractHandler

from google.appengine.api.users import User
from controllers.accounts.login import check_avatar

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
            volunteer = Volunteer(account = account)
            
        session['account'] = account
        session['volunteer'] = volunteer
        
            
        template_values = {
            'volunteer': volunteer,
            'home_neighborhoods': NeighborhoodHelper().selected(None),
            'work_neighborhoods': NeighborhoodHelper().selected(None),
            'fv_account': login_info is None
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__),'..', 'views', 'accounts', 'new_account.html')
        self.response.out.write(template.render(path, template_values))    
        
    def post(self):
        
        params = Parameters.parameterize(self.request)    
        session = Session()
        account = session.get('account', None)
        volunteer = session.get('volunteer', None)
        
        
        if params['session_id'] != session.sid:
            self.redirect('/error')
            return
        
        if 'password' in params and params['password'] != params['passwordcheck']:
            logging.info('PASSWORDS DO NOT MATCH')
            self.get(account = account, volunteer = volunteer)
        
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
            identifier = login_info['identifier'],
            account = account
        )
        if login_info['providerName'] == 'fv':
            auth.digest = login_info['digest'],
            auth.salt = login_info['salt'],


        if not account:
            self.redirect('/new')
            return False

        if not volunteer.validate(params) or not account.validate(params):
            self.get(account = account, volunteer = volunteer)
            return False
        
        user = User(email = account.email)
        account.user = user
        volunteer.account = account
        auth.account = account
        
        try:
            try:
                account.put()
            except: 
                account.put()
            
            try:
                volunteer.put()
            except:
                volunteer.put()
                
            try:
                auth.put()
            except:
                auth.put()

        except:
            self.get(account = account, volunteer = volunteer)
            return False
        
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
