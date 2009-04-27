import datetime
from google.appengine.ext import db
from models.neighborhood import *
from models.interestcategory import *

################################################################################
# Event
class Event(db.Model):
  name = db.StringProperty()
  neighborhood = db.ReferenceProperty(Neighborhood,
                                      collection_name = 'events')
  date_created = db.DateProperty(auto_now_add=True)
  date = db.DateTimeProperty()
  description = db.TextProperty()
  special_instructions = db.TextProperty()
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
  
  def inpast(self):
      return self.date < datetime.datetime.now()