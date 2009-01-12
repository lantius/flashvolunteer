from google.appengine.ext import db

################################################################################
# models
################################################################################
class Neighborhood(db.Model):
  name = db.StringProperty()

class Volunteer(db.Model):
  user = db.UserProperty()
  neighborhood = db.ReferenceProperty(Neighborhood)

  def events(self):
    return (ev.event for ev in self.events_set)
  
class Event(db.Model):
  name = db.StringProperty()
  neighborhood = db.ReferenceProperty(Neighborhood)
  date = db.DateProperty()
  
  def volunteers(self):
     return (ev.volunteer for ev in self.volunteers_set)
  
class EventVolunteer(db.Model):
  event = db.ReferenceProperty(Event,
                               required = True,
                               collection_name = 'volunteers_set')
  volunteer = db.ReferenceProperty(Volunteer,
                                    required = True,
                                    collection_name = 'events_set')
  isowner = db.BooleanProperty(required = True)
