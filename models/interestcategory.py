from google.appengine.ext import db

################################################################################
# InterestCategory
class InterestCategory(db.Model):
  name = db.StringProperty()

  def events(self):
    return (eic.event for eic in self.eventinterestcategories)

