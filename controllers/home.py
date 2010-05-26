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
            volunteer = self.auth()
        except:
            return  
        
        upcoming_events = self.get_application().upcoming_events().fetch(MainPage.LIMIT)
        
        template_values = {
            'volunteer' : volunteer,
            'upcoming_events': upcoming_events,
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__), '..', 'views', 'home', 'index.html')
        self.response.out.write(template.render(path, template_values))

    def incentives(self):
        try:
            volunteer = self.auth()
        except:
            return    
        
        template_values = {
            'volunteer' : volunteer,
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__), '..', 'views', 'home', 'incentives.html')
        self.response.out.write(template.render(path, template_values))
