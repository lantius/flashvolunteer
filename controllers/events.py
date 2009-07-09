import os, string, datetime
import exceptions
import logging

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db

from models.volunteer import *
from models.event import *
from models.eventvolunteer import *
from models.neighborhood import *
from models.interestcategory import *
from models.eventinterestcategory import *
from models.eventphoto import *
from models.interestcategory import InterestCategory

from controllers._auth import Authorize
from controllers._params import Parameters

from controllers._helpers import NeighborhoodHelper, InterestCategoryHelper

# flashvolunteer-dev.appspot.com
GOOGLE_MAPS_API_KEY = 'ABQIAAAA5caWoMd1eNfUNui_l1ovGxRzNuM6YWShM3q9_tmx1xqncfIVVBR0Vl7Dzc-1cpY5wjaMPmq_fwpBYA'
# flashvolunteer.appspot.com
# GOOGLE_MAPS_API_KEY = ABQIAAAA5caWoMd1eNfUNui_l1ovGxQ_mWzt9DEjH1LJGfRCLKaKtSAdHRQXsI-fBQAVUzaYlblLSlzQ1ctnSQ


def _get_upcoming_events():
    events = (e for e in Event.all() if 
            #recommend future events 
        not e.inpast())
    return sorted(events, lambda e,e2: cmp(e.date,e2.date))

def _get_recommended_events(volunteer):
    #TODO make more efficient
    vol_events = [v.key().id() for v in volunteer.events()]
    
    neighborhoods = []
    if(volunteer.work_neighborhood):
      neighborhoods.append(volunteer.work_neighborhood.name)
    if(volunteer.home_neighborhood):
      neighborhoods.append(volunteer.home_neighborhood.name)
    
    vol_interests = set([ic.name for ic in volunteer.interestcategories()])
    events = (e for e in _get_upcoming_events() if
            # recommend non rsvp'd events
            not e.key().id() in vol_events and  
            #recommend events in home or work neighborhood  
            (e.neighborhood.name in neighborhoods or  
             #recommend events in interest categories
            len(vol_interests.intersection(
                   set([ic.name for ic in e.interestcategories()]))
                ) > 0)
            )
    return events


################################################################################
# Events page
################################################################################
class EventsPage(webapp.RequestHandler):
  ################################################################################
  # GET
  def get(self, url_data):    
    if url_data:
      if '/new' == url_data:
        self.new({})
      elif '/search' == url_data:
        params = Parameters.parameterize(self.request)
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
      volunteer = Authorize.login(self, requireVolunteer=True, redirectTo='/settings')
    except:
      return
    
    params = Parameters.parameterize(self.request)
    event_id = None
    
    if'/edit' == url_data[-5:]:
      params['id'] = url_data[1:-5]
      event_id = self.update(params, volunteer)
    elif 'is_delete' in params and params['is_delete'] == 'true':
      self.delete(url_data[1:], volunteer)
      self.redirect("/events")
      return
    elif 'action' in params: #add an event photo album
      self._handle_photos(params, volunteer)
      return
    else:
      event_id = self.create(params, volunteer)
    
    if event_id is None:
      self.redirect('/events')
      return
    elif not event_id:
      return
      
    self.redirect("/events/" + str(int(event_id)))
    return
  
  ################################################################################
  # LIST
  def list(self):
    try:
      volunteer = Authorize.login(self, requireVolunteer=True, redirectTo='/settings')
    except:
      return
    
    recommended_events = _get_recommended_events(volunteer = volunteer)
    template_values = {
        'volunteer': volunteer,
        'eventvolunteer': volunteer.eventvolunteers,
        'neighborhoods': NeighborhoodHelper().selected(volunteer.home_neighborhood),
        'recommended_events': recommended_events,
        'interestcategories' : InterestCategoryHelper().selected(volunteer),
        'session_id': volunteer.session_id,
        'upcoming_events': _get_upcoming_events()
      }
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'events', 'events.html')
    self.response.out.write(template.render(path, template_values))
  

  

  
  ################################################################################
  # SHOW A SINGLE EVENT
  def show(self, event_id):

    #number of attendees to show in list
    LIMIT = 12
    offset = 0
    
    volunteer = Authorize.login(self)
    
    event = Event.get_by_id(int(event_id))
    owners = EventVolunteer.gql("where isowner=true AND event = :event", event=event).fetch(limit=100)
    eventphotos = EventPhoto.gql("WHERE event = :event ORDER BY display_weight ASC", event=event).fetch(limit=100)
    if len(owners) > 0:
        event_contact = owners[0].volunteer
    else:
        event_contact = None
    
    eventvolunteer = ""
    session_id = ''
    
    attendees_anonymous = []
    attendees = []
    
    if volunteer:

      session_id = volunteer.session_id
      eventvolunteer = EventVolunteer.gql("WHERE volunteer = :volunteer AND event = :event" ,
                         volunteer=volunteer, event=event).get() 
                         
      if eventvolunteer and (eventvolunteer.isowner or event.inpast()): 
        # TODO: randomize this...
        attendees = [ev.volunteer for ev in event.eventvolunteers.fetch(limit = LIMIT)]
      else:
          public_attendees = []
          for v in event.volunteers():
              if v.key().id() == volunteer.key().id(): continue
              if v.event_access(volunteer=volunteer):
                  public_attendees.append(v)
              else:
                  attendees_anonymous.append(v)
          
          attendees = public_attendees[offset:offset+LIMIT]

          
    template_values = { 'event' : event, 
                        'eventvolunteer': eventvolunteer, 
                        'eventphotos': eventphotos,
                        'event_categories': ', '.join([ic.name for ic in event.interestcategories()]),
                        'owners': owners, 
                        'contact': event_contact,
                        'volunteer': volunteer, 
                        'session_id': session_id,
                        'attendees': attendees,
                        'attendees_anonymous': attendees_anonymous,
                        'num_anon': len(attendees_anonymous),
                        'GOOGLE_MAPS_API_KEY' : GOOGLE_MAPS_API_KEY,
                        }
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'events', 'event.html')
    self.response.out.write(template.render(path, template_values))
     
  ################################################################################
  # DELETE
  def delete(self, event_id, volunteer):
    event = Event.get_by_id(int(event_id))
    
    eventvolunteer = EventVolunteer.gql("WHERE volunteer = :volunteer AND event = :event AND isowner = true" ,
                        volunteer=volunteer, event=event).get()
    if eventvolunteer:
      for ev in event.eventvolunteers:
        #TODO notify everyone who was going to attend that this was cancelled.
        ev.delete() 
      for ei in event.eventinterestcategories:
        ei.delete()
      event.delete()
  
  ################################################################################
  # NEW
  def new(self, event):
    try:
      volunteer = Authorize.login(self, requireVolunteer=True, redirectTo='/settings')
    except:
      return
    
    if not volunteer.can_create_events():
      self.redirect("/events") #TODO REDIRECT to error page
      return
    
    template_values = {
        'event' : event,
        'volunteer': volunteer,
        'neighborhoods': NeighborhoodHelper().selected(volunteer.home_neighborhood),
        'interestcategories' : InterestCategoryHelper().selected(volunteer),
      }
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'events', 'create_event.html')
    self.response.out.write(template.render(path, template_values))
  
  ################################################################################
  # CREATE
  def create(self, params, volunteer):
    event = Event()
    
    if not volunteer.can_create_events():
      self.redirect("/events") #TODO REDIRECT to error page
      return None
    
    if not event.validate(params):
      self.new(event)
      return False
    
    try:
      event.put()
    except:
      self.new(event)
      return
    
    for interestcategory in InterestCategory.all():
      pic = 'interestcategory[' + str(interestcategory.key().id()) + ']'
      if params[pic] == ['1','1']: 
        eic = EventInterestCategory(event = event, interestcategory = interestcategory)
        eic.put()
    
    eventVolunteer = EventVolunteer(volunteer=volunteer, event=event, isowner=True)
    eventVolunteer.put()
    
    return event.key().id()
  
  ################################################################################
  # EDIT
  def edit(self, event): 
    try:
      volunteer = Authorize.login(self, requireVolunteer=True, redirectTo='/settings')
    except:
      return   
    
    eventvolunteer = EventVolunteer.gql("WHERE volunteer = :volunteer AND event = :event AND isowner=true" ,
                           volunteer=volunteer, event=event).get()
    if not eventvolunteer:
      self.redirect("/events/" + event.id)
      return
    
    owners = EventVolunteer.gql("where isowner=true AND event = :event", event=event).fetch(limit=100)
    
    template_values = { 
      'event' : event, 
      'eventvolunteer': eventvolunteer, 
      'owners': owners, 
      'volunteer': volunteer, 
      'neighborhoods': NeighborhoodHelper().selected(event.neighborhood),
      'interestcategories' : InterestCategoryHelper().selected(event),
    }
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'events', 'event_edit.html')
    self.response.out.write(template.render(path, template_values))
  
  ################################################################################
  # UPDATE
  def update(self, params, volunteer):
    event = Event.get_by_id(int(params['id']))
    
    eventvolunteer = EventVolunteer.gql("WHERE volunteer = :volunteer AND event = :event AND isowner=true" ,
                           volunteer=volunteer, event=event).get()
    if not eventvolunteer:
      return None
    
    if not event.validate(params):
      self.edit(event)
      return False
    
    for interestcategory in InterestCategory.all():
      param_name = 'interestcategory[' + str(interestcategory.key().id()) + ']'
      eic = EventInterestCategory.gql("WHERE event = :event AND interestcategory = :interestcategory" ,
                          event = event, interestcategory = interestcategory).get()
      if params[param_name] == ['1','1'] and not eic:          
        eic = EventInterestCategory(event = event, interestcategory = interestcategory)
        eic.put()
      elif params[param_name] == '1' and eic:
        eic.delete()
    
    event.put()
    return event.key().id()
  
  ################################################################################
  # SEARCH
  def search(self, params):
    (neighborhood, fromdate, todate, events)  = self.do_search(params)
    template_values = { 
      'neighborhood' : neighborhood,
      'fromdate' : fromdate,
      'todate' : todate,
      'events' : events
    }
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'events', 'events_search.html')
    self.response.out.write(template.render(path, template_values))
  
  def do_search(self, params):
    events_query = Event.all()
    neighborhood = None
    todate = None
    fromdate = None
    
    if 'neighborhood' in params and params['neighborhood']:
      try:
        neighborhood = Neighborhood.get_by_id(int(params['neighborhood']))
        events_query.filter('neighborhood =', neighborhood)
      except:
        pass
    
    if 'fromdate' in params and params['fromdate']:
      try:
        fromdate = datetime.datetime.strptime(params['fromdate'], "%m/%d/%Y")
        events_query.filter('date >=', fromdate)
      except:
        pass
    
    if 'todate' in params and params['todate']:
      try:
        todate = datetime.datetime.strptime(params['todate'], "%m/%d/%Y")
        events_query.filter('date <=', todate)
      except:
        pass
    
    events = events_query.fetch(limit = 25)
    
    return (neighborhood, fromdate, todate, events)
  
  ################################################################################
  # all posts that deal with photo albums from the events page
  def _handle_photos(self, params, volunteer):
    event_id = params['event_id']
    if params['action'] == 's_addexternalalbum':
      last_eventphotos = EventPhoto.gql("WHERE event = :event ORDER BY display_weight DESC", event=Event.get_by_id(int(event_id))).fetch(limit=1)
      display_weight = 0
      for last_eventphoto in last_eventphotos: 
        display_weight = last_eventphoto.display_weight + 1
      eventphoto = EventPhoto(event=Event.get_by_id(int(event_id)), 
                                       volunteer=volunteer,
                                       content=params['content'], 
                                       display_weight = display_weight,
                                       type=EventPhoto.RSS_ALBUM, 
                                       status=EventPhoto.PUBLISHED
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
      lowers = EventPhoto.gql("WHERE event = :event AND display_weight < :cur_display_weight ORDER BY display_weight DESC", 
                                        event=Event.get_by_id(int(event_id)), 
                                        cur_display_weight=eventphoto.display_weight
                                        ).fetch(limit=1)
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
      highers = EventPhoto.gql("WHERE event = :event AND display_weight > :cur_display_weight ORDER BY display_weight ASC", 
                                        event=Event.get_by_id(int(event_id)), 
                                        cur_display_weight=eventphoto.display_weight
                                        ).fetch(limit=1)
      #swap weights
      for higher in highers:
        temp = eventphoto.display_weight
        eventphoto.display_weight = higher.display_weight
        eventphoto.put()
        higher.display_weight = temp
        higher.put()
    
    if event_id and event_id != None:
      self.redirect("/events/" + str(int(event_id)))