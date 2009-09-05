from google.appengine.ext import db

################################################################################
# InterestCategory
class InterestCategory(db.Model):
  name = db.StringProperty()

  def events(self):
    return (eic.event for eic in self.eventinterestcategories if not eic.event.hidden)

  def past_events(self):
    return (eic.event for eic in self.eventinterestcategories if eic.event.inpast and not eic.event.hidden)

  def upcoming_events(self):
    return (eic.event for eic in self.eventinterestcategories if not eic.event.inpast and not eic.event.hidden)

  def volunteers_interested(self):
    return (vic.volunteer for vic in self.volunteerinterestcategories)

  def volunteers_living_here(self):
    return (v for v in self.home_neighborhood)

  def url(self):
    return '/category/' + str(self.key().id())