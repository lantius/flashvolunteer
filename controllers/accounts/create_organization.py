from controllers._helpers import NeighborhoodHelper
from controllers.abstract_handler import AbstractHandler
from controllers.accounts.login import check_avatar

from google.appengine.api.users import User
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template

from models.auth import Account, Auth
from models.volunteer import Volunteer
from models.organization import Organization

import os, logging, hashlib, urllib

class CreateOrganization(AbstractHandler):

    def post(self):
        
        params = self.parameterize()    
        session = self._session()
        account = Account()  #session.get('account')
        volunteer = Volunteer() #session.get('volunteer')
        
        if params['session_id'] != session.sid:
            self.redirect('/timeout')
            return        
        
        #can't combine these two else risk not validating both...
        valid_entry = volunteer.validate(params) 
        valid_entry = account.validate(params) and valid_entry
        
        if not valid_entry:
            self.add_notification_message('<br>'.join(account.error.values()))
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
        org = Organization()
        
        try:
            account.put()
            
            volunteer.account = account
            volunteer.put()
                
            auth.account = account
            auth.put()
            
            org.name = volunteer.name
            org.email = volunteer.account.preferred_email
            org.admin = volunteer
            org.put()

        except:
            self.add_notification_message('We\'re sorry, your account could not be created. Please try again.')
            self.redirect('/#/new')
            return False
        
        session['auth'] = auth
        session['login_info'] = login_info
        
        check_avatar(account = account, session = session)
                
        msg_params = {'name': volunteer.name} 
        
        from utils.message_text import type3  
        from models.messages import MessageType
                  
        self.send_message(to = [account], 
                     subject = type3.subject%msg_params,
                     body = type3.body%msg_params,
                     type= MessageType.all().filter('name =', 'welcome').get(), 
                     immediate = True,
                     domain = self.get_domain())
        
        del session['login_info']
        if 'login_redirect' in session:
            self.redirect(session['login_redirect'])
            del session['login_redirect']
        else:
            self.redirect('/#/settings')
