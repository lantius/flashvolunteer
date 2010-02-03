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
            account = self.auth()
        except:
            return
        
        if account: user = account.get_user()
        else: user = None
                
        template_values = {
            'volunteer': user,
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__),'..', 'views', 'static', urldata + '.html')
        self.response.out.write(template.render(path, template_values))
        return