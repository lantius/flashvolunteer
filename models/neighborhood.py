from google.appengine.ext import db
from models.application import Application


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

  def events_past(self):
    return self.events.order('date').filter('in_past =', True).filter('hidden =', False)

  def events_future(self):
    return self.events.order('date').filter('in_past =', False).filter('hidden =', False)
