from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os


from controllers.abstract_handler import AbstractHandler

################################################################################
# Help page
################################################################################
class StaticPage(AbstractHandler):
    def get(self, urldata):    
        try:
            volunteer = self.auth()
        except:
            return
        
        template_values = {
            'volunteer': volunteer,
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__),'..', 'views', 'static', urldata + '.html')
        self.response.out.write(template.render(path, template_values))
        return