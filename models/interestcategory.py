from google.appengine.ext import db

################################################################################
# InterestCategory
class InterestCategory(db.Model):
  name = db.StringProperty()

  def events(self):
    return self.event_categories.filter('event_is_hidden =', False).order('event_date')

  def past_events(self):
    return self.event_categories.filter('event_is_upcoming =', False).filter('event_is_hidden =', False).order('event_date')

  def upcoming_events(self):
    return self.event_categories.filter('event_is_upcoming =', True).filter('event_is_hidden =', False).order('event_date')

  def volunteers_interested(self):
    return (vic.account.get_user() for vic in self.user_interests)

  def url(self):
    return '/category/' + str(self.key().id())