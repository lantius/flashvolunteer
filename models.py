from google.appengine.ext import db

################################################################################
# models
################################################################################
class Neighborhood(db.Model):
  name = db.StringProperty()
  # implicitly has .events and .volunteers properties
      
class InterestCategory(db.Model):
  name = db.StringProperty()

  def events(self):
    return (eic.event for eic in self.eventinterestcategories)

class Volunteer(db.Model):
  user = db.UserProperty()
  neighborhood = db.ReferenceProperty(Neighborhood)
  session_id = db.StringProperty()

  def events(self):
    return (ev.event for ev in self.eventvolunteers)
  
  def interestcategories(self):
    return (vic.interestcategory for vic in self.volunteerinterestcategories)

  def following(self):
    return (f.volunteer for f in self.volunteerfollowing)

  def followers(self):
    return (f.follower for f in self.volunteerfollowers)
  
  # both following and follower
  def friends(self):
    fr = []
    for following in self.following():
      for follower in self.followers():
        if following.key().id == follower.key().id:
          fr.append(following)
    return (f for f in fr)
  
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
     return (ev.volunteer for ev in self.eventvolunteers)
  
  def interestcategories(self):
     return (eic.interestcategory for eic in self.eventinterestcategories)

################################################################################
# "join" models
################################################################################
class EventVolunteer(db.Model):
  event = db.ReferenceProperty(Event,
                               required = True,
                               collection_name = 'eventvolunteers')
  volunteer = db.ReferenceProperty(Volunteer,
                                    required = True,
                                    collection_name = 'eventvolunteers')
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


class VolunteerFollower(db.Model):
  volunteer = db.ReferenceProperty(Volunteer,
                                   required = True,
                                   collection_name = 'volunteerfollowers')
  follower = db.ReferenceProperty(Volunteer,
                                  required = True,
                                  collection_name = 'volunteerfollowing')
                                  
