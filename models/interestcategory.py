from google.appengine.ext import db

################################################################################
# InterestCategory
class InterestCategory(db.Model):
  name = db.StringProperty()

  def events(self):
    return (eic.event for eic in self.event_categories if not eic.event.hidden)

  def past_events(self):
    return (eic.event for eic in self.event_categories if eic.event.inpast() and not eic.event.hidden)

  def upcoming_events(self):
    return (eic.event for eic in self.event_categories if not eic.event.inpast() and not eic.event.hidden)

  def volunteers_interested(self):
    return (vic.account.get_user() for vic in self.user_interests)

  def volunteers_living_here(self):
    return (v for v in self.home_neighborhood)

  def url(self):
    return '/category/' + str(self.key().id())