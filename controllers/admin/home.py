import os, logging
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template

from controllers.abstract_handler import AbstractHandler

################################################################################

#def get_unverified_events(region):
    #return events = region.events
    
# AdminPage
class AdminPage(AbstractHandler):
    LIMIT = 100 
    def get(self):
        try:
            account = self.auth(require_login=True, require_admin = True)
        except:
            return   
          
        region = self.get_application()
        #unverified_events = region.events.filter('verified = ',False)
        
        for name in os.environ.keys():
            logging.info("%s = %s<br />\n" % (name, os.environ[name]))
            
        template_values = {
            'volunteer' : account.get_user()
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__), '..', '..', 'views', 'admin', 'index.html')
        self.response.out.write(template.render(path, template_values))
