from google.appengine.ext import db
from models.application import Application
import math

################################################################################
# Neighborhood
class Neighborhood(db.Model):
    name = db.StringProperty()
    application = db.ReferenceProperty(Application,
                                       collection_name = 'neighborhoods',
                                       default = None)
    
    centroid = db.GeoPtProperty()
    
    # implicitly has .events and .volunteers properties
    
    def url(self):
        return '/neighborhoods/' + str(self.key().id())
    
    def volunteers_working_here(self):
        return self.work_neighborhood
    
    def volunteers_living_here(self):
        return self.home_neighborhood
    
    def ongoing_opportunities(self):
        return self.events.order('date').filter('in_past =', True).filter('hidden =', False).filter('is_ongoing =',True)
    
    def events_past(self):
        return self.events.order('date').filter('in_past =', True).filter('hidden =', False)
    
    def events_future(self):
        return self.events.order('date').filter('in_past =', False).filter('hidden =', False).filter('is_ongoing =',False)

    def distance_from_centroid(self, location):
        return math.sqrt( math.pow(self.centroid.lat - location.lat, 2) + math.pow(self.centroid.lon - location.lon, 2))