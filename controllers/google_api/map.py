import os
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template
from google.appengine.api import users

from models.neighborhood import Neighborhood
from controllers.abstract_handler import AbstractHandler

class MapHandler(AbstractHandler):
    def get(self):
        
        params = self.parameterize() 
        
        template_values = {
            'lon' : params.get('lon'),
            'lat': params.get('lat')
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__), '..', '..', 'views', 'google', 'map.html')
        self.response.out.write(template.render(path, template_values))


class NeighborhoodMapHandler(AbstractHandler):
    LIMIT = 25 
    def get(self):
        
        params = self.parameterize() 
        neighborhood = Neighborhood.get_by_id(int(params.get('nid')))
        if neighborhood:
            events = neighborhood.events_future().fetch(self.LIMIT)
        else:
            events = []
            
        template_values = {
            'lon' : params.get('lon'),
            'lat': params.get('lat'),
            'events': events,
            'zoom': 12
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__), '..', '..', 'views', 'google', 'events_map.html')
        self.response.out.write(template.render(path, template_values))
    
class RegionMapHandler(AbstractHandler):
    LIMIT = 25 
    def get(self):
        app = self.get_application()
        lon = app.sw_coord.lon + (app.ne_coord.lon - app.sw_coord.lon) / 2.0
        lat = app.ne_coord.lat + (app.sw_coord.lat - app.ne_coord.lat) / 2.0
        
        events = app.upcoming_events().fetch(self.LIMIT)
            
        template_values = {
            'lon' : lon,
            'lat': lat,
            'events': events,
            'zoom': 10
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__), '..', '..', 'views', 'google', 'events_map.html')
        self.response.out.write(template.render(path, template_values))

class NeighborhoodsMapHandler(AbstractHandler):
    LIMIT = 25
    def get(self):
        app = self.get_application()
        lon = app.sw_coord.lon + (app.ne_coord.lon - app.sw_coord.lon) / 2.0
        lat = app.ne_coord.lat + (app.sw_coord.lat - app.ne_coord.lat) / 2.0
        
        events = app.upcoming_events().fetch(self.LIMIT)
            
        template_values = {
            'lon' : lon,
            'lat': lat,
            'neighborhoods': [n for n in app.neighborhoods.fetch(limit=250) if n.centroid],
            'zoom': 10
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__), '..', '..', 'views', 'google', 'neighborhoods_map.html')
        self.response.out.write(template.render(path, template_values))
    