from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os


from controllers.abstract_handler import AbstractHandler

################################################################################
# Help page
################################################################################
class CauseCrowdPage(AbstractHandler):
    def get(self, lang):
        try:
            volunteer = self.auth()
        except:
            return
        
        if not lang:
            lang = 'en'
            
        lang = lang.replace('/','')

        if (lang != 'en' and lang != 'es' and lang != 'cn' and lang != 'tw'):
            lang = 'en'
            
        template_values = {
            'volunteer': volunteer,
            'language' : lang,
          }
        self._add_base_template_values(vals = template_values)
        path = os.path.join(os.path.dirname(__file__),'..', 'views', 'static', 'causecrowd.html')
        self.response.out.write(template.render(path, template_values))
        return

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
