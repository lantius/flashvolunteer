from components.geostring import *
from components.time_zones import Pacific, now
from controllers._utils import get_google_maps_api_key, get_application
from google.appengine.api import urlfetch
from google.appengine.ext import db
from models.application import Application
from models.interestcategory import InterestCategory
from models.neighborhood import Neighborhood
import datetime, logging, urllib


################################################################################
# Event
class Event(db.Model):
    name = db.StringProperty()
  
    neighborhood = db.ReferenceProperty(Neighborhood,
                                      collection_name='events')
  
    application = db.ReferenceProperty(Application,
                                     collection_name='events',
                                     default=None)

    description = db.TextProperty()
  
    date_created = db.DateProperty(auto_now_add=True)
    
    date = db.DateTimeProperty() #start date
    enddate = db.DateTimeProperty()
    
    duration = db.IntegerProperty() #OBSOLETE; in hours, use enddate-startdate
    duration_minutes = db.IntegerProperty() #OBSOLETE; full number of minutes e.g. 253 = 4 hours, 13 min, for now, total = duration * 60 + duration_minutes
    
    special_instructions = db.TextProperty()
    address = db.StringProperty(multiline=True)
    location = db.GeoPtProperty() # No default
    geostring = db.StringProperty()
    
    verified = db.BooleanProperty(default=False)
    hidden = db.BooleanProperty(default=False)
    coordinator = db.BooleanProperty(default=False)
    
    ###message state
    reminder_message_sent = db.BooleanProperty(default=False)
    post_event_message_sent = db.BooleanProperty(default=False)
    
    def __init__(self,
               parent=None,
               key_name=None,
               _app=None,
               _from_entity=False,
               **kwds):
        self.error = {} #instance object, not class object, or will be sticky
        self.save = {}
        db.Model.__init__(self, parent=parent,
                          key_name=key_name,
                          _app=_app,
                          _from_entity=_from_entity, **kwds)
          
    def get_duration_hours(self):
        if not self.enddate:
            min = 0
            if self.duration:
                min = 60 * self.duration
            if self.duration_minutes:
                min += self.duration_minutes
            return((min + 59) / 60) #round up
        else:
            diff = self.enddate - self.date
            return (diff.seconds / 60 + 59) / 60 #round up
    
    def get_start_repr(self, strftime):
        if (self.save.has_key('eventstart')):
            return self.save['eventstart']['date']
        if not self.date:
            return "no date set"
        return self.date.strftime(strftime)
    
    def get_start_time(self):
        return self.get_start_repr("%I:%M %p")

    def get_start_time_full(self):
        return self.get_start_repr("%m/%d %I:%M %p")
        
    def get_startdate_long(self):
        return self.get_start_repr("%A, %d %B %Y")
    
    def get_startdatetime(self):
        return self.get_start_repr("%Y-%m-%d %H:%M")
        
    def get_startdate_short(self):
      return self.get_start_repr("%m/%d")
    
    def get_startdate(self):
      return self.get_start_repr("%m/%d/%Y")
    
    def get_starthour(self):
      return self.get_start_repr("%H")
    
    def get_startminute(self):
      return self.get_start_repr("%M")
    
    def get_end_repr(self, strftime):
        if (self.save.has_key('eventend')):
            return self.save['eventend']['date']
        if not self.date:
            return "no date set"
        
        if self.enddate:
            end = self.enddate
        else: 
            end = self.date + self.get_duration()
        return end.strftime(strftime)  
    
    def get_enddate_long(self):
        return self.get_end_repr("%A, %d %B %Y")
    
    def get_enddatetime(self):
        return self.get_end_repr("%Y-%m-%d %H:%M")
    
    def get_enddate(self):
        return self.get_end_repr("%m/%d/%Y")

    def get_end_time_full(self):
        return self.get_end_repr("%m/%d %I:%M %p")
    
    def get_end_time(self):
        return self.get_end_repr("%I:%M %p")
    
    def get_endhour(self):
        return self.get_end_repr("%H")
    
    def get_endminute(self):
        return self.get_end_repr("%M")
    
    def get_address(self):
        return self.address
    
    def get_google_calendar_date(self):
        start = self.get_start_repr('%Y%m%dT%H%M00Z')
        str = '%s/%s' % (start, self.get_end_repr('%Y%m%dT%H%M00Z'))
        return str
    
    def url(self):
        if self.is_saved():
            return '/events/' + str(self.key().id())
        return '/events'
      
    def volunteers(self):
        return (ev.account.get_user() for ev in self.eventvolunteers.filter('isowner = ', False))
    
    def volunteer_count(self):
        return self.eventvolunteers.filter('isowner = ', False).count()
    
    def hosts(self):
        return (ev.account.get_user() for ev in self.eventvolunteers.filter('isowner = ', True))
    
    def contact_email(self):
        return ','.join([ev.account.get_email() for ev in self.eventvolunteers.filter('isowner = ', True)])
    
    def get_numphotoalbums(self):
        eventphotosphotos = [photo for photo in self.eventphotos]
        return len(eventphotosphotos)
    
    def interestcategories(self):
        return (eic.interestcategory for eic in self.event_categories)
    
    def geocode(self):
        response = urlfetch.fetch('http://maps.google.com/maps/geo?q=' + urllib.quote_plus(self.address) + '&output=csv&oe=utf8&sensor=false&key=' + get_google_maps_api_key())
        (httpcode) = response.content.split(',')[0]
        if '200' == httpcode:
            (httpcode, accuracy, lat, lon) = response.content.split(',')
            self.location = db.GeoPt(lat, lon)
            self.geostring = str(Geostring((self.location.lat, self.location.lon)))
      
    def validate_time(self, date, time):
        save = {
            'date' : date,
            'time' : time
        }
        error_string = []
        try:
            date_str = datetime.datetime.strptime(date, "%m/%d/%Y")
        except ValueError:
            error_string.append('Invalid date')
          
        try:
            time_str = datetime.datetime.strptime(time, "%I:%M %p")
        except ValueError:
            error_string.append('Invalid time')
                
        return (error_string, save)    
        
      
    def validate(self, params):
        self.error.clear()
        self.save.clear()
        
        try:
            if not 'name' in params:
                raise
            if not len(params['name']) > 0:
                raise
            if self.name != params['name']:
                self.name = params['name']
                self.verified = False
        except:
            self.error['name'] = ('Name is required', params['name'])
        
        
        #event start time
        params['starttime'] = params['starttime'].upper()
        (eventstart_error, save) = self.validate_time(params['startdate'], params['starttime'])
        self.save['eventstart'] = save
        if(len(eventstart_error) == 0):
            self.date = datetime.datetime.strptime(
              params['starttime'] + ' ' + params['startdate'], "%I:%M %p %m/%d/%Y"
            )
        else: 
            self.error['eventstart'] = eventstart_error
        
        #event end time
        params['endtime'] = params['endtime'].upper()
        (eventend_error, save) = self.validate_time(params['enddate'], params['endtime'])
        self.save['eventend'] = save
        if(len(eventend_error) == 0):
            enddatetime = datetime.datetime.strptime(
              params['endtime'] + ' ' + params['enddate'], "%I:%M %p %m/%d/%Y"
            )
            
            if(len(eventstart_error) == 0):
                
                delta = enddatetime - self.date 
                self.enddate = enddatetime
                
                if (delta < datetime.timedelta(0)): 
                  self.error['enddate_early'] = ('Event start (%s) cannot be later than' % self.date.strftime("%m/%d/%Y, %I:%M %p"),
                                                 'event end (%s)' % enddatetime.strftime("%m/%d/%Y, %I:%M %p"))
        else: 
            self.error['eventend'] = eventend_error
        
        
        try:
            if not 'description' in params or not len(params['description']) > 0:
                raise
            
            desc = params['description'].replace('\n', '\n<br>')
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
        
        self.coordinator = 'coordinator' in params
        
        self.hidden = not 'show_event' in params
          
        # try our geocoding here
        if self.address:
            self.geocode()
        
        try:
            spi = params['special_instructions'].replace('\n', '\n<br>')
            if self.special_instructions != spi:
                self.special_instructions = spi
                self.verified = False
        except:
            self.error['special_instructions'] = ('Invalid special instructions',
                                                params['special_instructions'])
        
        return not self.error
    
    def inpast(self):
        return self.date < now()
    
    #########################################
    ## DEPRECATED
      
    def get_duration(self):
        min = 0
        if self.duration:
            min = 60 * self.duration
        if self.duration_minutes:
            min += self.duration_minutes
        dur = datetime.timedelta(minutes=min)
        return dur

