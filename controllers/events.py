from components.geostring import Geostring
from components.time_zones import now
from controllers._helpers import NeighborhoodHelper, InterestCategoryHelper
from controllers.abstract_handler import AbstractHandler
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext.webapp import template
#from google.appengine.ext import deferred

from models.event import Event
from models.eventinterestcategory import EventInterestCategory
from models.eventphoto import EventPhoto
from models.eventvolunteer import EventVolunteer
from models.interestcategory import InterestCategory
from models.neighborhood import Neighborhood
from models.volunteer import Volunteer
import logging
import os, string, random
from datetime import datetime
                  
#this is a hack: google django does not have escapejs yet - this is from there
_base_js_escapes = (
  ('\\', r'\x5C'),
  ('\'', r'\x27'),
  ('"', r'\x22'),
  ('>', r'\x3E'),
  ('<', r'\x3C'),
  ('&', r'\x26'),
  ('=', r'\x3D'),
  ('-', r'\x2D'),
  (';', r'\x3B'),
  (u'\u2028', r'\u2028'),
  (u'\u2029', r'\u2029')
)

# Escape every ASCII character with a value less than 32.
_js_escapes = (_base_js_escapes +
               tuple([('%c' % z, '') for z in range(32)]))
               #tuple([('%c' % z, '\\x%02X' % z) for z in range(32)]))

def escapejs(value):
    """Hex encodes characters for use in JavaScript strings."""
    for bad, good in _js_escapes:
        value = value.replace(bad, good)
    return value
  

################################################################################
# Events page
################################################################################
class EventsPage(AbstractHandler):
    LIMIT = 3
    ################################################################################
    # GET
    def get(self, url_data):    
        if url_data:
            if '/new' == url_data:
                self.new({})
            elif '/search' == url_data:
                params = self.parameterize() 
                self.search(params)
            elif '/edit' == url_data[-5:]:
                event = Event.get_by_id(int(url_data[1:-5]))
                self.edit(event)
            else:
                self.show(url_data[1:])
        else:
            self.list()
    
    ################################################################################
    # POST
    def post(self, url_data):
        try:
            volunteer = self.auth(require_login=True)
        except:
            return
        
        params = self.parameterize() 
        event_id = None
        
        if'/edit' == url_data[-5:]:
            params['id'] = url_data[1:-5]
            event_id = self.update(params, volunteer)
        elif 'is_delete' in params and params['is_delete'] == 'true':
            self.delete(url_data[1:], volunteer)
            self.redirect("/#/events")
            return
        elif 'action' in params: #add an event photo album
            self._handle_photos(params, volunteer)
            return
        else:
            event_id = self.create(params, volunteer)
            if event_id:
                event = Event.get_by_id(event_id)
                session = self._session()
                self.add_notification_message('Event "%s" has been created!'%event.name)
        
        if event_id is None:
            self.redirect('/#/events')
            return
        elif event_id:
            self.redirect("/#/events/" + str(int(event_id)))
        
        return
  
    ################################################################################
    # LIST
    def list(self):
        try:
            volunteer = self.auth()
        except:
            return
        
        upcoming_events = self.get_application().upcoming_events().fetch(EventsPage.LIMIT)
        ongoing_opportunities = self.get_application().ongoing_opportunities().fetch(EventsPage.LIMIT)
        
        if volunteer:
            recommended_events = None
            volunteer.recommended_events(application = self.get_application(),
                                         session = self._session())[:EventsPage.LIMIT]
            neighborhoods = NeighborhoodHelper().selected(self.get_application(),volunteer.home_neighborhood)
            #interest_categories = InterestCategoryHelper().selected(user)
            
            (future_events, my_past_events, events_coordinating, past_events_coordinated) = volunteer.get_activities(EventsPage.LIMIT)
            my_past_events.reverse()
            
        else: 
            application = self.get_application()
            recommended_events = None
            future_events = None
            my_past_events = None
            events_coordinating = None
            neighborhoods = application.neighborhoods
            #TODO: convert to application-specific data model
            #interest_categories = InterestCategory.all()
        
        
        template_values = {
            'volunteer': volunteer,
            'neighborhoods': neighborhoods,
            'recommended_events': recommended_events,
            'events_coordinating': events_coordinating,
            #'interestcategories' : interest_categories,
            'upcoming_events': upcoming_events,
            'future_events': future_events,
            'past_events': my_past_events,
            'ongoing_opportunities':ongoing_opportunities
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__),'..', 'views', 'events', 'events.html')
        self.response.out.write(template.render(path, template_values, debug=self.is_debugging()))

  
    ################################################################################
    # SHOW A SINGLE EVENT
    def show(self, event_id):
        
        #number of attendees to show in list
        
        offset = 0
        
        volunteer = self.auth()
        application = self.get_application()
        
        event = Event.get_by_id(int(event_id))
                
        if not event or event.application.key().id() != application.key().id():
            #logging.info('didnt match' + str(application.name))
            self.error(404)
            return
            
        owners = event.hosts()
        eventphotos = event.eventphotos.order('display_weight').fetch(limit=100)
        
        #logging.info(owners)
        for ep in eventphotos:
            if (ep.can_edit(volunteer)):
                ep.can_edit_now = True
            else:
                ep.can_edit_now = False
        
        eventvolunteer = None
        
        attendees_anonymous = []
        attendees = []

        #fill forum block
        forum = {}
        message_receipts = event.incoming_messages.order('timestamp').fetch(limit=6)
        messages = [mr.message for mr in message_receipts]
        
        if (len(messages) > 5): 
            messages = messages[0:4]
            forum['more_messages'] = True
            
        forum['messages'] = messages 
        forum['path'] = self.request.path
        #end fill forum block

        if volunteer:
            eventvolunteer = event.eventvolunteers.filter('volunteer = ', volunteer).get()
        
            if eventvolunteer and (eventvolunteer.isowner or event.in_past): 
                # TODO: randomize this...
                attendees = list(event.volunteers())[offset:offset+EventsPage.LIMIT]
            else:
                public_attendees = []
                for v in event.volunteers():
                    if v.key().id() == volunteer.key().id() or v.event_access(volunteer = volunteer):
                        public_attendees.append(v)
                    else:
                        attendees_anonymous.append(v)
                
                attendees = public_attendees[offset:offset+EventsPage.LIMIT]
        
        template_values = { 
                            'volunteer': volunteer,
                            'event' : event, 
                            'eventvolunteer': eventvolunteer, 
                            'eventphotos': eventphotos,
                            'event_categories': ', '.join([ic.name for ic in event.interestcategories()]),
                            'owners': owners, 
                            'attendees': attendees,
                            'attendees_anonymous': attendees_anonymous,
                            'num_anon': len(attendees_anonymous),
                            'forum': forum,
                            }
        self._add_base_template_values(vals = template_values)
        
        path = None
        if self.request.headers["Accept"] == "application/json":
            path = os.path.join(os.path.dirname(__file__),'..', 'views', 'events', 'event.json')
        else:
            path = os.path.join(os.path.dirname(__file__),'..', 'views', 'events', 'event.html')
        self.response.out.write(template.render(path, template_values, debug=self.is_debugging()))
   
    ################################################################################
    # DELETE
    def delete(self, event_id, volunteer):
        event = Event.get_by_id(int(event_id))
        
        eventvolunteer = event.eventvolunteers.filter('volunteer =', volunteer).filter('isowner =', True).get()
        if eventvolunteer:
            for ev in event.eventvolunteers:
                #TODO notify everyone who was going to attend that this was cancelled.
                ev.delete() 
            for ei in event.event_categories:
                ei.delete()
            event.delete()
  
    ################################################################################
    # NEW
    def new(self, event):
        try:
            volunteer = self.auth(require_login=True)
        except:
            return
        
        neighborhoods = NeighborhoodHelper().selected(self.get_application(),volunteer.home_neighborhood)
        if event:
            neighborhoods = NeighborhoodHelper().selected(self.get_application(),event.neighborhood)
        
        template_values = {
            'event' : event,
            'volunteer': volunteer,
            'neighborhoods': neighborhoods,
            'interestcategories' : InterestCategoryHelper().selected(volunteer),
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__),'..', 'views', 'events', 'create_event.html')
        self.response.out.write(template.render(path, template_values, debug=self.is_debugging()))

    ################################################################################
    # CREATE
    def create(self, params, volunteer):
        application = self.get_application()
        event = Event(application = application)
        session = self._session()
        
        if not event.validate(params):
            self.add_notification_message('Sorry, your event could not be created')
            self.redirect('/#/events')
            return False
        
        try:
            event.put()
        except:
            self.add_notification_message('Sorry, your event could not be created')
            self.redirect('/#/events')
            return False
        
        #TODO: convert interest category helper to application-specific data model
        for interestcategory in InterestCategory.all():
            pic = 'interestcategory[' + str(interestcategory.key().id()) + ']'
            if params[pic] == ['1','1']: 
                eic = EventInterestCategory(event = event, interestcategory = interestcategory)
                eic.put()
        
        eventVolunteer = EventVolunteer(
                                volunteer=volunteer, 
                                event=event, 
                                isowner=True,
                                event_is_upcoming = not event.in_past,
                                event_is_hidden = event.hidden,
                                event_date = event.date,
                                application = event.application)
        eventVolunteer.put()
        
        return event.key().id()
  
    ################################################################################
    # EDIT
    def edit(self, event): 
        try:
            volunteer = self.auth(require_login=True)
        except:
            return   
        
        eventvolunteer = event.eventvolunteers.filter('volunteer =', volunteer).filter('isowner =', True)
        
        if not eventvolunteer:
            self.redirect("/#/events/" + event.id)
            return
        
        owners = event.hosts()
    
        event.description = event.description.replace('\n<br>','\n')
        event.special_instructions = event.special_instructions.replace('\n<br>','\n')
    
        template_values = { 
            'event' : event, 
            'eventvolunteer': eventvolunteer, 
            'owners': owners, 
            'volunteer': volunteer, 
            'neighborhoods': NeighborhoodHelper().selected(self.get_application(),event.neighborhood),
            'interestcategories' : InterestCategoryHelper().selected(event),
        }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__),'..', 'views', 'events', 'event_edit.html')
        self.response.out.write(template.render(path, template_values, debug=self.is_debugging()))
      
    ################################################################################
    # UPDATE
    def update(self, params, volunteer):
        event = Event.get_by_id(int(params['id']))
        
        eventvolunteer = event.eventvolunteers.filter('volunteer =', volunteer).filter('isowner =', True).get()

        if not eventvolunteer:
            return None
        
        hidden = event.hidden
        date = event.date
        session = self._session()
        if not event.validate(params):
            self.add_notification_message('Sorry, your changes could not be saved.')
            self.redirect('/#' + event.url())
            return False
        
        if hidden != event.hidden:
            for ev in event.eventvolunteers:
                ev.event_is_hidden = event.hidden
                ev.put()
            for eic in event.event_categories:
                eic.event_is_hidden = event.hidden
                eic.put()

        if date != event.date:
            for ev in event.eventvolunteers:
                ev.event_date = event.date
                ev.put()
            for eic in event.event_categories:
                eic.event_date = event.date
                eic.put()
                        
        #TODO: convert interest category helper to application-specific data model
        for interestcategory in InterestCategory.all():
            param_name = 'interestcategory[' + str(interestcategory.key().id()) + ']'
            eic = event.event_categories.filter('interestcategory = ', interestcategory).get()
            if params[param_name] == ['1','1'] and not eic:          
                eic = EventInterestCategory(event = event, interestcategory = interestcategory)
                eic.put()
            elif params[param_name] == '1' and eic:
                eic.delete()    
        
        event.put()
        memcache.set('Event-interestcategories-%i'%event.key().id(), None)
        
        return event.key().id()
  
     
    ################################################################################
    # SEARCH
    def search(self, params):
        
        volunteer = self.auth()
        
        (neighborhood, events, interestcategory, next, prev)  = self.do_search(params)
        
        template_values = { 
          'neighborhood' : neighborhood,
          'events' : events,
          'interestcategory': interestcategory,
          'volunteer': volunteer,
          'searchterms': params['searchterms'],
          'next': next,
          'prev': prev,
          'url': '/events/search'
        }
        self._add_base_template_values(vals = template_values)
        
        is_json = self.is_json(params)
        if is_json:
            if (('jsoncallback' in params)):
                for event in events:
                    event.description = escapejs(event.description)
                    event.special_instructions = escapejs(event.special_instructions)
            
            path = os.path.join(os.path.dirname(__file__),'..', 'views', 'events', 'events_search.json')
            render_out = template.render(path, template_values, debug=self.is_debugging())
            if (('jsoncallback' in params)):
                render_out = params['jsoncallback'] + '(' + render_out + ');'
        else:
            path = os.path.join(os.path.dirname(__file__),'..', 'views', 'events', 'events_search.html')
            render_out = template.render(path, template_values, debug=self.is_debugging())
        
        self.response.out.write(render_out)

    def is_json(self, params):
        if ((self.request.headers["Accept"] == "application/json") or 
             ('format' in params and params['format'] == 'json')):
            return True
        else:
            return False
     
    
    def do_search(self, params):
        SEARCH_LIST = 10

        application = self.get_application()
        session = self._session()
        
        bookmark_loc = self.request.get("bookmark", None)
        events_filter_keys = []
        events_search_keys = []
        
        cursor_filter = None
        do_filter = True
        bookmark = None
        bookmark_key = None
        events_filter_result = []
        events_search_result = []
        local_now = now()

        searchterms = params['searchterms']

        #argh: need join between StemmedIndex entities from Event.search and results from Event
        #get all results for searchterms - since we can't ask for an order on these, we need to get all of them :-(
        if (len(searchterms) != 0):
            events_search_result = Event.search(phrase = searchterms, keys_only=True)
            events_search_keys += [tup[0] for tup in events_search_result]


        events_query = Event.all(keys_only=True)
        events_query = events_query.filter('hidden = ', False)
        events_query = events_query.filter('application = ', application)
        
        if bookmark_loc and bookmark_loc != '-':
            bookmark_key = db.Key(bookmark_loc)
            bookmark_event = db.get(bookmark_key)
            bookmark = bookmark_event.date
            trace = session.get('events_search_prev', None)
            if not trace or trace == []:
                session['events_search_prev'] = [bookmark_loc]
                prev = '-'
            else:                
                if 'back' in params and params['back'] == '1':
                    prev = trace.pop() 
                    prev_event = db.get(prev)
                    while prev_event.date >= bookmark_event.date:
                        try:
                            prev = trace.pop()                                                                    
                        except: 
                            prev = '-'
                            break
                else:
                    prev = trace[-1]
                    trace.append(bookmark_loc)
                    
                session['events_search_prev'] = trace
                
        else: #no bookmark requested
            if 'events_search_prev' in session:
                del session['events_search_prev']
                    
            prev = ''
            if 'past_events' in params and params['past_events']: #all requested
                session['past_events'] = str(params['past_events'])
                session['searchurl'] = True             
            else: #only current requested
                bookmark = local_now

        if (bookmark):                        
            events_query = events_query.filter('date >= ', bookmark)
        
              
        events_query = events_query.order('date') 
        
        memcache.delete('past_events')
        memcache.delete('searchurl')
        
        neighborhood = None
        interestcategory = None
        ur = None
        ll = None
        
        if ('ur' in params and params['ur']) and ('ll' in params and params['ll']):
        #      try:
            (lat,lon) = params['ur'].split(',')
            ur = db.GeoPt(lat,lon)
            (lat,lon) = params['ll'].split(',')
            ll = db.GeoPt(lat,lon)
            urstring = str(Geostring((ur.lat,ur.lon)) )
            llstring = str(Geostring((ll.lat,ll.lon)) )
            events_query.filter('geostring <= ', urstring).filter('geostring >= ', llstring).order('geostring')
            #events_query.filter('geostring >= ', bbstring).order('geostring')
        #      except:
        #        pass    
        
        if 'neighborhood' in params and params['neighborhood']:
            try:
                neighborhood = Neighborhood.get_by_id(int(params['neighborhood']))
                events_query.filter('neighborhood =', neighborhood)
            except:
                pass
        
        
        while (do_filter): 
            if cursor_filter:
                events_query.with_cursor(cursor_filter)
            events_filter_result = events_query.fetch(limit = SEARCH_LIST + 1)
            num_events_filter_result = len(events_filter_result)
            cursor_filter = events_query.cursor()
            
            if bookmark_key: 
                try:
                    ind = events_filter_result.index(bookmark_key)
                    events_filter_result = events_filter_result[ind:] #discard items before ind
                except:
                    pass
    
            events_filter_keys += events_filter_result
        
            if (len(searchterms) == 0): #no searchterms, use just filters
                events_search_keys = events_filter_keys
    
            #find events that are in both filter and search results
            events_keys = filter(lambda x:x in events_search_keys , events_filter_keys)    
            
            if (len(events_keys) >= SEARCH_LIST + 1):
                break #enough found: get out
            
            if (num_events_filter_result < SEARCH_LIST + 1): #must be last batch of events
                break
            
        #from keys to entities
        events = [Event.get(key) for key in events_keys]
        
        if len(events) >= SEARCH_LIST+1:
            next = events[SEARCH_LIST].key() 
            events = events[:SEARCH_LIST] #first SEARCH_LIST items
        else:
            next = None
            
        if ur and ll:
            events = [event for event in events if 
                             event.location.lon > ll.lon 
                         and event.location.lat > ll.lat 
                         and event.location.lon < ur.lon 
                         and event.location.lat < ur.lat]
        
        
        if 'interestcategory' in params and params['interestcategory'] and params['interestcategory'] != 'default':
            try:
                catid = int(params['interestcategory'])
                interestcategory = InterestCategory.get_by_id(catid)
                events = [event for event in events if 
                        catid in [ic.interestcategory.key().id() for ic in event.event_categories]]
            except:
                pass
                    
        return (neighborhood, events, interestcategory, next, prev)
  
    ################################################################################
    # all posts that deal with photo albums from the events page
    def _handle_photos(self, params, volunteer):
        event_id = params['event_id']
        event = Event.get_by_id(int(event_id))
        if params['action'] == 's_addexternalalbum':
            
            if not event:
                raise
            
            last_eventphoto = event.eventphotos.order('-display_weight').get()
            if last_eventphoto:
                display_weight = last_eventphoto.display_weight + 1
            else:
                display_weight = 0
            
            eventphoto = EventPhoto(event=Event.get_by_id(int(event_id)), 
                                             content=params['content'], 
                                             display_weight = display_weight,
                                             type=EventPhoto.RSS_ALBUM, 
                                             status=EventPhoto.PUBLISHED,
                                             user=volunteer
                                             )
            eventphoto.put()
        elif params['action'] == 'Remove':
            album_id = params['album_id']
            eventphoto = EventPhoto.get_by_id(int(album_id))
            eventphoto.delete()
        elif params['action'] == 'Up':
            album_id = params['album_id']
            eventphoto = EventPhoto.get_by_id(int(album_id))
            #look for photo with display_weight lower than curent, start with highest
            lowers = event.eventphotos.filter('display_weight <', eventphoto.display_weight).order('-display_weight')
        
            #swap weights
            for lower in lowers:
                temp = eventphoto.display_weight
                eventphoto.display_weight = lower.display_weight
                eventphoto.put()
                lower.display_weight = temp
                lower.put()
        elif params['action'] == 'Down':
            album_id = params['album_id']
            eventphoto = EventPhoto.get_by_id(int(album_id))
            #look for photo with display_weight higher than curent, start with lowest
            highers = event.eventphotos.filter('display_weight >', eventphoto.display_weight).order('display_weight')
        
            #swap weights
            for higher in highers:
                temp = eventphoto.display_weight
                eventphoto.display_weight = higher.display_weight
                eventphoto.put()
                higher.display_weight = temp
                higher.put()
        
        memcache.set('Event-get_numphotoalbums-%i'%event.key().id(), None)
        
        if event_id and event_id != None:
            self.redirect("/#/events/" + str(int(event_id)))
      
      
################################################################################
# EventAddCoordinatorPage page
################################################################################
class EventAddCoordinatorPage(AbstractHandler):
    LIMIT = 12
    ################################################################################
    # GET
    def get(self, event_id):   
        try:
            volunteer = self.auth(require_login=True)
        except:
            return
        
        event = Event.get_by_id(int(event_id))
        
        eventvolunteer = event.eventvolunteers.filter('volunteer =', volunteer).filter('isowner =', True).get()
        
        if not eventvolunteer:
            self.redirect("/#/events") #TODO REDIRECT to error page
            return
        
        template_values = {
            'event' : event,
            'volunteer': volunteer,
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__),'..', 'views', 'events', 'add_event_coordinator.html')
        self.response.out.write(template.render(path, template_values, debug=self.is_debugging()))
      
    def post(self, event_id):   
        try:
            volunteer = self.auth(require_login=True)
        except:
            return
        
        params = self.parameterize() 
        
        event = Event.get_by_id(int(event_id))
        
        eventvolunteer = event.eventvolunteers.filter('volunteer =', volunteer).filter('isowner =', True).get()
        
        if not eventvolunteer:
            self.redirect("/#/events") #TODO REDIRECT to error page
            return
        
        try:
            new_coord_id = int(params['coordinator'])
            new_coord_account = Volunteer.get_by_id(new_coord_id)
            if not new_coord_account: 
                raise
        
            new_coord = None
            for ev in new_coord_account.eventvolunteers:
                if ev.event.key().id() == event.key().id():
                    new_coord = ev
                    break
            
            if new_coord:
                new_coord.isowner = True
                new_coord.put()
        except:
            pass
        
        memcache.set('Event-hosts-%i'%event.key().id(), None)
        memcache.set('Event-get_contact_email-%i'%event.key().id(), None)
        
        self.redirect('/#/events/'+ event_id)
      