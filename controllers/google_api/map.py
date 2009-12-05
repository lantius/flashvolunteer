import os
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template
from google.appengine.api import users


from controllers.abstract_handler import AbstractHandler

class MapHandler(AbstractHandler):
  LIMIT = 100 
  def get(self):
      
    params = self.parameterize() 

    template_values = {
        'lon' : params.get('lon'),
        'lat': params.get('lat')
      }
    self._add_base_template_values(vals = template_values)
    
    path = os.path.join(os.path.dirname(__file__), '..', '..', 'views', 'google', 'map.html')
    self.response.out.write(template.render(path, template_values))
