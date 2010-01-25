import os
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template
from google.appengine.api import users

from controllers.abstract_handler import AbstractHandler

################################################################################

#def get_unverified_events(region):
    #return events = region.events
    
# AdminPage
class AdminPage(AbstractHandler):
  LIMIT = 100 
  def get(self):
    try:
      account = self.auth()
    except:
      return    
    if account: user = account.get_user()
    else: user = None
      
    region = self.get_application()
    unverified_events = region.events.filter('verified = ',False)

    template_values = {
        'volunteer' : user,
        'unverified_events': unverified_events
      }
    self._add_base_template_values(vals = template_values)
    
    path = os.path.join(os.path.dirname(__file__), '..', '..', 'views', 'admin', 'index.html')
    self.response.out.write(template.render(path, template_values))
