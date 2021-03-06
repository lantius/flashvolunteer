from components.time_zones import now
from utils.misc_methods import geocode
from google.appengine.ext import db
from models.application import Application
from models.neighborhood import Neighborhood
import datetime, logging, urllib
from utils.html_sanitize import sanitize_html
from models.afg_opportunity import AFGOpportunity
from django.utils.html import strip_tags

from controllers.search_katz import search
from google.appengine.api import memcache
from google.appengine.ext import deferred
from inspect import stack

################################################################################
# Event
class Event(search.SearchableEvent, db.Model):
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
    
    special_instructions = db.TextProperty()
    address = db.StringProperty(multiline=True)
    location = db.GeoPtProperty() # No default
    geostring = db.StringProperty()
    
    verified = db.BooleanProperty(default=False)
    hidden = db.BooleanProperty(default=False)
    coordinator = db.BooleanProperty(default=True)
    
    in_past = db.BooleanProperty(default=False)
    
    is_ongoing = db.BooleanProperty(default=False)
    
    ###message state
    reminder_message_sent = db.BooleanProperty(default=False)
    post_event_message_sent = db.BooleanProperty(default=False)
    
    event_url = db.LinkProperty(default = None)
    contact_email = db.StringProperty(default = None)
    
    #if this opportunity is published through FV, set this field to the Event
    source = db.ReferenceProperty(AFGOpportunity, default=None, collection_name='source')
    
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
          
    def is_ongoing_opportunity(self):
        td = self.enddate - self.date
        return td.days > 5
    
    def get_duration_hours(self):
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

        if not self.enddate:
            raise
        else:
            end = self.enddate
            
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
        method = stack()[0][3]
        key = '%s-%s-%i'%(self.__class__.__name__, method, self.key().id())
        result = memcache.get(key)
        if not result:
            result = [ev.volunteer for ev in self.eventvolunteers.filter('isowner = ', False)]
            memcache.set(key, result, 1000)
                    
        return result
    
    
    def volunteer_count(self):
        method = stack()[0][3]
        key = '%s-%s-%i'%(self.__class__.__name__, method, self.key().id())
        result = memcache.get(key)
        if not result:
            result = self.eventvolunteers.filter('isowner = ', False).count()
            memcache.set(key, result, 1000)
                    
        return result
    
    def hosts(self):
        method = stack()[0][3]
        key = '%s-%s-%i'%(self.__class__.__name__, method, self.key().id())
        result = memcache.get(key)
        if not result:
            result = [ev.volunteer for ev in self.eventvolunteers.filter('isowner = ', True)]
            memcache.set(key, result, 1000)
                    
        return result 
    
    def get_contact_email(self):
        if self.contact_email:
            return self.contact_email

        method = stack()[0][3]
        key = '%s-%s-%i'%(self.__class__.__name__, method, self.key().id())
        result = memcache.get(key)
        if not result:
            result = ','.join([ev.volunteer.get_email() for ev in self.eventvolunteers.filter('isowner = ', True)])
            memcache.set(key, result, 1000)
                    
        return result 
    
    def get_numphotoalbums(self):
        method = stack()[0][3]
        key = '%s-%s-%i'%(self.__class__.__name__, method, self.key().id())
        result = memcache.get(key)
        if not result:
            result = len(eventphotosphotos = [list(self.eventphotos)])
            memcache.set(key, result, 1000)
                    
        return result
    
    def interestcategories(self):
        method = stack()[0][3]
        key = key = '%s-%s-%i'%(self.__class__.__name__, method, self.key().id())
        result = memcache.get(key)
        if not result:
            result = [eic.interestcategory for eic in self.event_categories]
            memcache.set(key, result, 1000)
                    
        return result 
    
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
            params['name'] = sanitize_html(params['name'])
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
            params['description'] = sanitize_html(params['description'])
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
            params['address'] = sanitize_html(params['address'])
            self.address = params['address']
        except:
            self.error['address'] = ('Invalid address', params['address'])
        
        self.coordinator = 'coordinator' in params
        
        self.hidden = not 'show_event' in params
          
        # try our geocoding here
        if self.address:
            (self.location, self.geostring) = geocode(self.address)
        
        try:
            params['special_instructions'] = sanitize_html(params['special_instructions'])
            spi = params['special_instructions'].replace('\n', '\n<br>')
            if self.special_instructions != spi:
                self.special_instructions = spi
                self.verified = False
        except:
            self.error['special_instructions'] = ('Invalid special instructions',
                                                params['special_instructions'])
        
        if 'event_url' in params:
            try:
                self.event_url = params['event_url']
            except:
                pass
        
        if 'contact_email' in params:
            try:
                self.contact_email = params['contact_email']
            except:
                pass
            
        if 'afg_opp' in params:
            afg_opp = AFGOpportunity.get_by_id(int(params['afg_opp']))
            self.source = afg_opp
    
        self.is_ongoing = self.is_ongoing_opportunity()
        
        if self.error:
            raise Exception(self.error)
        return not self.error
    
    def inpast(self):
        return self.in_past or self.enddate is None or self.enddate < now()


        
    def put(self):
        db.Model.put(self)
        deferred.defer(self.index)
    
    #called from Searchable, provides data that should be indexed for full-text search
    def searchindex_getprop_func(self):
        props = []
        props.append(self.name)
        props.append(self.neighborhood.name)
        props.append(strip_tags(self.description))
        props.append(strip_tags(self.special_instructions))
        return props

    

from components.appengine_admin.model_register import register, ModelAdmin
## Admin views ##
class AdminEvent(ModelAdmin):
    model = Event
    listFields = ('name', 'neighborhood', 'description')
    editFields = ('name', 'neighborhood', 'description')
    readonlyFields = ()

register(AdminEvent)

