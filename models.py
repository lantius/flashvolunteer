import datetime
from google.appengine.ext import db
from types import *

################################################################################
# models
################################################################################

################################################################################
# Neighborhood
class Neighborhood(db.Model):
  name = db.StringProperty()
  # implicitly has .events and .volunteers properties

  def url(self):
    return '/neighborhoods/' + str(self.key().id())

################################################################################
# InterestCategory
class InterestCategory(db.Model):
  name = db.StringProperty()

  def events(self):
    return (eic.event for eic in self.eventinterestcategories)

################################################################################
# Volunteer
class Volunteer(db.Model):
  user = db.UserProperty()
  name = db.StringProperty()
  avatar = db.BlobProperty()
  quote = db.StringProperty()
  joinedon = db.DateProperty(auto_now_add=True)
  home_neighborhood = db.ReferenceProperty(Neighborhood, collection_name = 'home_neighborhood')
  work_neighborhood = db.ReferenceProperty(Neighborhood, collection_name = 'work_neighborhood')
  session_id = db.StringProperty()

  def get_name(self):
    if self.name:
      return self.name

    return self.user.nickname
    
  def url(self):
    return '/volunteers/' + str(self.key().id())

  def events(self):
    return (ev.event for ev in self.eventvolunteers)
  
  def interestcategories(self):
    return (vic.interestcategory for vic in self.volunteerinterestcategories)

  def following(self):
    return (f.volunteer for f in self.volunteerfollowing)

  def followers(self):
    return (f.follower for f in self.volunteerfollowers)

  def events_past_count(self):
    return len(self.events_past())

  def events_past(self):
    future_filter = lambda x: x.date < datetime.datetime.today()
    return filter(future_filter, self.events())
  
  def events_future_count(self):
    return len(self.events_future())

  def events_future(self):
    future_filter = lambda x: x.date >= datetime.datetime.today()
    return filter(future_filter, self.events())
        
  # both following and follower
  def friends(self):
    fr = []
    for following in self.following():
      for follower in self.followers():
        if following.key().id() == follower.key().id():
          fr.append(following)
    return (f for f in fr)
  
  def check_session_id(self, form_session_id):
    if form_session_id == self.session_id:
      return True
    
    return False


################################################################################
# Event
class Event(db.Model):
  name = db.StringProperty()
  neighborhood = db.ReferenceProperty(Neighborhood,
                                      collection_name = 'events')
  date_created = db.DateProperty(auto_now_add=True)
  date = db.DateTimeProperty()
  description = db.TextProperty()
  address = db.StringProperty(multiline=True)
  
  def get_date(self):
    if not self.date:
      return "no date set"
  
    return self.date.strftime("%A, %d %B %Y")
  
  def get_time(self):
    if not self.date:
      return "no time set"
      
    return self.date.strftime("%I:%M%p")
  
  def url(self):
    return '/events/' + str(self.key().id())
    
  def volunteers(self):
     return (ev.volunteer for ev in self.eventvolunteers)
     
  def hosts(self):
    hosts = ""
    for ev in self.eventvolunteers:
      if ev.isowner:
        hosts += "<a href='" + ev.volunteer.url() + "'>" + ev.volunteer.get_name() + "</a> "
    
    return hosts

  def interestcategories(self):
     return (eic.interestcategory for eic in self.eventinterestcategories)
     
  def validate(self, params):
    try:
      datetime.datetime.strptime(params['time'] + " " + params['date'], "%H:%M %m/%d/%Y")
      return True
    except:
      return False

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
                                  


