import datetime
import logging
import urllib
from components.geostring import *
from google.appengine.api import urlfetch

from google.appengine.ext import db
from models.neighborhood import *
from models.interestcategory import *

# flashvolunteer-dev.appspot.com
#GOOGLE_MAPS_API_KEY = 'ABQIAAAA5caWoMd1eNfUNui_l1ovGxRzNuM6YWShM3q9_tmx1xqncfIVVBR0Vl7Dzc-1cpY5wjaMPmq_fwpBYA'
# flashvolunteer.appspot.com
#GOOGLE_MAPS_API_KEY = 'ABQIAAAA5caWoMd1eNfUNui_l1ovGxQ_mWzt9DEjH1LJGfRCLKaKtSAdHRQXsI-fBQAVUzaYlblLSlzQ1ctnSQ'
# flashvolunteer.org
GOOGLE_MAPS_API_KEY = 'ABQIAAAApwXNBqL2vnoPPZzBT8fEFBT8o8BW0NprhG7ZQBw6sHycsndbhRS7hhGpRgOy2Kssletcr3BQkAy7jg'
#http://v01-1.latest.flashvolunteer.appspot.com
#GOOGLE_MAPS_API_KEY = 'ABQIAAAApwXNBqL2vnoPPZzBT8fEFBRKcpMVieIGuRjmcVoCEVomVUOSzxQXzU7Vr92SCk5CZf8Fq_G1wz5bIA'


################################################################################
# Event
class Event(db.Model):
  name = db.StringProperty()
  neighborhood = db.ReferenceProperty(Neighborhood,
                                      collection_name = 'events')
  date_created = db.DateProperty(auto_now_add=True)
  date = db.DateTimeProperty()
  description = db.TextProperty()
  duration = db.IntegerProperty() #in hours, obsolete, use duration_minutes
  duration_minutes = db.IntegerProperty() #full number of minutes e.g. 253 = 4 hours, 13 min, for now, total = duration * 60 + duration_minutes
  special_instructions = db.TextProperty()
  address = db.StringProperty(multiline=True)
  location = db.GeoPtProperty() # No default
  geostring = db.StringProperty()
  
  verified = db.BooleanProperty(default = False)
  hidden = db.BooleanProperty(default = False)
  
  def __init__(self,
             parent=None,
             key_name=None,
             _app=None,
             _from_entity=False,
             **kwds):
    self.error = {} #instance object, not class object, or will be sticky
    self.save = {}
    db.Model.__init__(self, parent, key_name, _app, _from_entity, **kwds)
   
    
  def get_duration(self):
    min = 0
    if self.duration:
      min = 60*self.duration
    if self.duration_minutes:
      min += self.duration_minutes
    dur = datetime.timedelta(minutes=min)
    return dur
  
  def get_duration_hours(self):
    min = 0
    if self.duration:
      min = 60*self.duration
    if self.duration_minutes:
      min += self.duration_minutes
    return((min+59)/60) #round up
    
    
  def get_time(self):
    if not self.date:
      return "no time set"
    return self.date.strftime("%I:%M %p")
  
  def get_startdate_long(self):
    if not self.date:
      return "no date set"
    return self.date.strftime("%A, %d %B %Y")
  
  def get_startdate(self):
    if (self.save.has_key('eventstart')):
      return self.save['eventstart']['date']
    if not self.date:
      return "no date set"
    return self.date.strftime("%m/%d/%Y")  
  
  def get_starthour(self):
    if (self.save.has_key('eventstart')):
      return self.save['eventstart']['hour']
    if not self.date:
        return "no time set"
    return self.date.strftime("%H")
  
  def get_startminute(self):
    if (self.save.has_key('eventstart')):
      return self.save['eventstart']['minute']
    if not self.date:
      return "no time set"
    return self.date.strftime("%M")
  
  def get_enddate(self):
    if (self.save.has_key('eventend')):
      return self.save['eventend']['date']
    if not self.date:
      return ""
    end = self.date + self.get_duration()
    return end.strftime("%m/%d/%Y")  
  
  def get_endhour(self):
    if (self.save.has_key('eventend')):
      return self.save['eventend']['hour']
    if not self.date:
      return "no time set"
    end = self.date + self.get_duration()
    return end.strftime("%H")
  
  def get_endminute(self):
    if (self.save.has_key('eventend')):
      return self.save['eventend']['minute']
    if not self.date:
      return "no time set"
    end = self.date + self.get_duration()
    return end.strftime("%M")
  
  def get_duration_string(self):
    dur = self.get_duration()
    weeks, days = divmod(dur.days, 7)
    minutes, seconds = divmod(dur.seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if (hours > 1):
      ret = "%02d:%02d hours" % (hours, minutes)
    else:
      ret = "%02d:%02d hour" % (hours, minutes)
    if (days):
      if (days > 1):
        ret = ("%d days, " % days) + ret
      else:
        ret = ("%d day, " % days) + ret
        
    if (weeks):
      if (weeks > 1):
        ret = ("%d weeks, " % weeks) + ret
      else:
        ret = ("%d week, " % weeks) + ret
        
    return ret
    
  def message_body(self):
      lines = ['You are invited to the event %s.'%self.name]
      lines.append('To sign up for the event, please visit http://www.flashvolunteer.org/events/%i.'%self.key().id())
      lines.append('Thanks!')
      return "%0A%0A".join(lines)
  
  def url(self):
    if self.is_saved():
      return '/events/' + str(self.key().id())
    return '/events'
    
  def volunteers(self):
    return (ev.volunteer for ev in self.eventvolunteers)
  
  def hosts(self):
    hosts = [ev for ev in self.eventvolunteers if ev.isowner]

    return hosts

  def interestcategories(self):
    return (eic.interestcategory for eic in self.eventinterestcategories)
  
  def geocode(self):
    response = urlfetch.fetch('http://maps.google.com/maps/geo?q=' + urllib.quote_plus(self.address) + '&output=csv&oe=utf8&sensor=false&key=' + GOOGLE_MAPS_API_KEY)
    (httpcode) = response.content.split(',')[0]
    if '200' == httpcode:
      (httpcode,accuracy,lat,lon) = response.content.split(',')
      self.location = db.GeoPt(lat,lon)
      self.geostring = str(Geostring((self.location.lat,self.location.lon)) )
    
  def validate_time(self, date, hour, minute):
    save = {}
    save['date'] = date
    save['hour'] = hour
    save['minute'] = minute
    
    error_string = []
    try:
      startdate = datetime.datetime.strptime(date, "%m/%d/%Y")
    except ValueError:
      error_string.append('Invalid date')

    
    if (minute == 'none'):
      error_string.append('Minutes not set')
      
    if (hour == 'none'):
      error_string.append('Hours not set')

    if (len(error_string)==0):
      try:
        time = datetime.datetime.strptime(hour + ":" + minute, "%H:%M")
      except ValueError:
        error_string.append('Invalid time')
        
    return (error_string, save)    
      
    
  def validate(self, params):
    self.error.clear()
    self.save.clear()

    try:
      if not 'name' in params:
        raise Exception
      if not len(params['name']) > 0:
        raise Exception
      if self.name != params['name']:
          self.name = params['name']
          self.verified = False
    except:
      self.error['name'] = ('Name is required', params['name'])

    #event start time
    (eventstart_error, save) = self.validate_time(params['startdate'], params['starthour'], params['startminute'])
    self.save['eventstart'] = save
    if(len(eventstart_error) == 0):
      self.date = datetime.datetime.strptime(
        params['starthour'] + ":" + params['startminute'] + ' ' + params['startdate'], "%H:%M %m/%d/%Y"
      )
    else: 
      self.error['eventstart'] = eventstart_error
    
    #event end time
    (eventend_error, save) = self.validate_time(params['enddate'], params['endhour'], params['endminute'])
    self.save['eventend'] = save
    if(len(eventend_error) == 0):
      enddatetime = datetime.datetime.strptime(
        params['endhour'] + ":" + params['endminute'] + ' ' + params['enddate'], "%H:%M %m/%d/%Y"
      )

      if(len(eventstart_error) == 0):
        delta = enddatetime - self.date 
        if (delta < datetime.timedelta(0)): 
          self.error['enddate_early'] = ('Event start (%s) cannot be later than' % self.date.strftime("%m/%d/%Y, %I:%M %p"),  
                                         'event end (%s)' % enddatetime.strftime("%m/%d/%Y, %I:%M %p") )
          self.duration_minutes = 0
        else:
          self.duration_minutes = delta.days*1440 + delta.seconds/60
          if (self.duration):
            self.duration_minutes += self.duration*60 #convert legacy hour based duration
            self.duration = 0
    else: 
      self.error['eventend'] = eventend_error

    
    try:
      if not 'description' in params:
        raise Exception
      if not len(params['description']) > 0:
        raise Exception
    
      desc = params['description'].replace('\n','\n<br>')
      if self.description != desc:
          self.description = desc
          self.verified = False
    except:
      self.error['description'] = ('Description is required',
                                   params['description'])
      
    try:
      self.neighborhood = Neighborhood.get_by_id(int(params['neighborhood']))
    except:
      self.error['neighborhood'] = ('Invalid neighborhood',
                                    params['neighborhood'])
    
    try:
      self.address = params['address']
    except:
      self.error['address'] = ('Invalid address', params['address'])
    
    self.hidden = not 'coordinator' in params
      
    # try our geocoding here
    if self.address:
      self.geocode()
    
    try:
      spi = params['special_instructions'].replace('\n','\n<br>')
      if self.special_instructions != spi:
          self.special_instructions = spi
          self.verified = False
    except:
      self.error['special_instructions'] = ('Invalid special instructions', 
                                            params['special_instructions'])
    
    return not self.error
  
  def inpast(self):
    return self.date < datetime.datetime.now()