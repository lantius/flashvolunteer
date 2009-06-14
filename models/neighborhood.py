from google.appengine.ext import db

################################################################################
# Neighborhood
class Neighborhood(db.Model):
  name = db.StringProperty()
  # implicitly has .events and .volunteers properties

  def url(self):
    return '/neighborhoods/' + str(self.key().id())

  def volunteers_working_here(self):
    return (v for v in self.work_neighborhood)

  def volunteers_living_here(self):
    return (v for v in self.home_neighborhood)
