from google.appengine.ext import db

################################################################################
# models
################################################################################
class Neighborhood(db.Model):
  name = db.StringProperty()
  # implicitly has .events and .volunteers properties

class InterestCategory(db.Model):
  name = db.StringProperty()

class Volunteer(db.Model):
  user = db.UserProperty()
  neighborhood = db.ReferenceProperty(Neighborhood)
  session_id = db.StringProperty()

  def events(self):
    return (ev.event for ev in self.ev_set)
    
  def check_session_id(self, form_session_id):
    if form_session_id == self.session_id:
      return True
    
    return False
  
class Event(db.Model):
  name = db.StringProperty()
  neighborhood = db.ReferenceProperty(Neighborhood,
                                      collection_name = 'events')
  date = db.DateProperty()
  
  def volunteers(self):
     return (ev.volunteer for ev in self.ev_set)
  
class EventVolunteer(db.Model):
  event = db.ReferenceProperty(Event,
                               required = True,
                               collection_name = 'ev_set')
  volunteer = db.ReferenceProperty(Volunteer,
                                    required = True,
                                    collection_name = 'ev_set')
  isowner = db.BooleanProperty(required = True)

class EventInterestCategory(db.Model):
  event = db.ReferenceProperty(Event,
                               required = True,
                               collection_name = 'eventinterestcategories')
  interestcategory = db.ReferenceProperty(InterestCategory,
                                required = True,
                                collection_name = 'eventinterestcategories')
                                
class VolunteerInterestCategory(db.Model):
  volunteer = db.ReferenceProperty(Volunteer,
                               required = True,
                               collection_name = 'volunteerinterestcategories')
  interestcategory = db.ReferenceProperty(InterestCategory,
                                required = True,
                                collection_name = 'volunteerinterestcategories')
