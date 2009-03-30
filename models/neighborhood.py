from google.appengine.ext import db

################################################################################
# Neighborhood
class Neighborhood(db.Model):
  name = db.StringProperty()
  # implicitly has .events and .volunteers properties

  def url(self):
    return '/neighborhoods/' + str(self.key().id())