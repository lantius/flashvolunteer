from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os, random

from controllers._params import Parameters

from controllers._utils import get_application

from controllers.abstract_handler import AbstractHandler

from models.application import Application

class AllApplications(AbstractHandler):
  def get(self):    

    volunteer = self.auth()
    
    params = Parameters.parameterize(self.request)
    
    applications = Application.all()
    
    template_values = {
        'volunteer': volunteer,
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
    volunteer = self.auth(redirectTo='/settings')
    
    params = Parameters.parameterize(self.request)
    
    application = get_application()
    
    template_values = {
        'volunteer': volunteer,
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