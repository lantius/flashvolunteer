import datetime
import logging
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
  duration = db.IntegerProperty()
  special_instructions = db.TextProperty()
  address = db.StringProperty(multiline=True)
  
  def __init__(self,
             parent=None,
             key_name=None,
             _app=None,
             _from_entity=False,
             **kwds):
    self.error = {} #instance object, not class object, or will be sticky
    db.Model.__init__(self, parent, key_name, _app, _from_entity, **kwds)
   
    
  def get_date(self):
    if not self.date:
      return "no date set"
  
    return self.date.strftime("%A, %d %B %Y")
  
  def get_time(self):
    if not self.date:
      return "no time set"
      
    return self.date.strftime("%I:%M%p")
  
  def url(self):
    if self.is_saved():
      return '/events/' + str(self.key().id())
    return '/events'
    
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
    self.error.clear()

    try:
      if not 'name' in params:
        raise Exception
      if not len(params['name']) > 0:
        raise Exception
      
      self.name = params['name']
    except:
      self.error['name'] = ('Name is required', params['name'])

    try:
      dateval = datetime.datetime.strptime(params['date'], "%m/%d/%Y")
    except ValueError:
      self.error['date'] = ('Invalid date format', params['date'])
    
    try:
      time = datetime.datetime.strptime(params['time'], "%H:%M")
    except ValueError:
      self.error['time'] = ('Invalid time', params['time'])

    if(not ('time' in self.error or 'date' in self.error)):
      self.date = datetime.datetime.strptime(params['time'] + ' ' + params['date'], "%H:%M %m/%d/%Y")
    
    try:
      self.duration = int(params['duration'])
    except:
      self.error['duration'] = ('Duration must be a number', params['duration'])
    
    try:
      if not 'description' in params:
        raise Exception
      if not len(params['description']) > 0:
        raise Exception
      self.description = params['description']
    except:
      self.error['description'] = ('Description is required', params['description'])
      
    try:
      self.neighborhood = Neighborhood.get_by_id(int(params['neighborhood']))
    except:
      self.error['neighborhood'] = ('Invalid neighborhood', params['neighborhood'])
    
    try:
      self.address = params['address']
    except:
      self.error['address'] = ('Invalid address', params['address'])
    
    try:
      self.special_instructions = params['special_instructions']
    except:
      self.error['special_instructions'] = ('Invalid special instructions', params['special_instructions'])
    
    return not self.error
  
  def inpast(self):
      return self.date < datetime.datetime.now()