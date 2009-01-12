from google.appengine.ext import db

################################################################################
# models
################################################################################
class Volunteer(db.Model):
  user = db.UserProperty()
  neighborhood = db.StringProperty()

class Event(db.Model):
  name = db.StringProperty()
  date = db.DateProperty()
  neighborhood = db.StringProperty()
  
class EventVolunteer(db.Model):
  event = db.ReferenceProperty(Event,
                               required = True,
                               collection_name = 'volunteers')
  volunteer = db.ReferenceProperty(Volunteer,
                                    required = True,
                                    collection_name = 'events')
  isowner = db.BooleanProperty(required = True)