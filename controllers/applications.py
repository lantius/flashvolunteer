from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os, random

from controllers.abstract_handler import AbstractHandler

from models.application import Application

class AllApplications(AbstractHandler):
  def get(self):    

    account = self.auth()
    
    params = self.parameterize() 
    
    applications = Application.all()
    
    template_values = {
        'applications': applications
    }
    self._add_base_template_values(vals = template_values)
    
    is_json = self.is_json(params)
    if is_json:
      path = os.path.join(os.path.dirname(__file__),'..', 'views', 'applications', 'applications.json')
      render_out = template.render(path, template_values)
      if (('jsoncallback' in params)):
        render_out = params['jsoncallback'] + '(' + render_out + ');'
    else:
        raise

    self.response.out.write(render_out)
    return

  def is_json(self, params):
    if ((self.request.headers["Accept"] == "application/json") or 
         ('format' in params and params['format'] == 'json')):
       return True
    else:
       return False
    
class ThisApplication(AbstractHandler):
  def get(self):    
    account = self.auth(redirect_to='/settings')
    if account: user = account.get_user()
    else: user = None
    
    params = self.parameterize() 
    
    application = self.get_application()
    
    template_values = {
        'volunteer': user,
        'applications': [application]
    }
    self._add_base_template_values(vals = template_values)
    
    is_json = self.is_json(params)
    if is_json:
      path = os.path.join(os.path.dirname(__file__),'..', 'views', 'applications', 'applications.json')
      render_out = template.render(path, template_values)
      if (('jsoncallback' in params)):
        render_out = params['jsoncallback'] + '(' + render_out + ');'
    else:
        raise

    self.response.out.write(render_out)
    return


  def is_json(self, params):
    if ((self.request.headers["Accept"] == "application/json") or 
         ('format' in params and params['format'] == 'json')):
       return True
    else:
       return False