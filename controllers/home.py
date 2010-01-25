import os, logging
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template
from google.appengine.api import users

from controllers.abstract_handler import AbstractHandler

################################################################################
# MainPage
class MainPage(AbstractHandler):
    LIMIT = 3 
    def get(self):
        if self.request.path.find('incentives') > -1:
            self.incentives()
        else:
            self.homepage()
      
    def homepage(self):
        try:
            account = self.auth()
        except:
            raise
            return  
        
        if account: user = account.get_user()
        else: user = None
          
        upcoming_events = self.get_application().upcoming_events().fetch(MainPage.LIMIT)
        
        template_values = {
            'volunteer' : user,
            'upcoming_events': upcoming_events,
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__), '..', 'views', 'home', 'index.html')
        self.response.out.write(template.render(path, template_values))

    def incentives(self):
        try:
            account = self.auth()
        except:
            return    
        
        if account: user = account.get_user()
        else: user = None
          
        template_values = {
            'volunteer' : user,
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__), '..', 'views', 'home', 'incentives.html')
        self.response.out.write(template.render(path, template_values))
