from controllers.abstract_handler import AbstractHandler

from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template

from models.auth import Account, Auth
from models.messages import MessageType

import os, logging, hashlib, urllib

class HelpLogin(AbstractHandler):


    def get(self):
        session = self._session()
        
        account = self.auth()
        if account: 
            self.redirect('/')
            return
        
        template_values = {
            'account': account,
          }
        self._add_base_template_values(vals = template_values)
    
        path = os.path.join(os.path.dirname(__file__),'..', '..', 'views', 'accounts', 'find_account.html')
        self.response.out.write(template.render(path, template_values))    
        
    def post(self):
        
        params = self.parameterize()    
        session = self._session()

        account = Account.all().filter('preferred_email = ', params['email']).get()
        
        if account:
            from utils.message_text import login_info_text
            
            try: 
                auth = account.auth_methods.get()
                
                pars = {'provider': auth.strategy, 'hint':''}
                if auth.strategy == 'fv':
                    #self.send_message(  to = [account], 
                    #                    subject = login_info_text.subject, 
                    #                    body = login_info_text.body%pars, 
                    #                    type = MessageType.all().filter('name =', 'account_reminder').get(),
                    # domain = self.get_domain())
                    self.add_notification_message('We found your account. You logged in using a Flash Volunteer account. Please use the form on the left of the page. If you have forgotten your password, please send us an email at info@flashvolunteer.org.')
                
                else:
                    logging.info('We found your account. You logged in using %s. Please select %s from the third-party provider list on the right side of the login page to proceed. Send us an email at info@flashvolunteer.org if you have problems.'%(auth.strategy,auth.strategy))
                    self.add_notification_message('We found your account. You logged in using %s. Please select %s from the third-party provider list on the right side of the login page to proceed. Send us an email at info@flashvolunteer.org if you have problems.'%(auth.strategy,auth.strategy))
            except:
                raise Exception('Error sending message')        
        else:
            self.add_notification_message('Sorry, we could not find your account. Did you by any chance sign in using Facebook?')
        self.redirect('/#/login')
