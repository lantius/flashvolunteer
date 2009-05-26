import os, string, datetime

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from models.volunteer import *
from models.event import *
from models.eventvolunteer import *
from models.neighborhood import *
from models.interestcategory import *
from models.eventinterestcategory import *

from controllers._auth import Authorize
from controllers._params import Parameters

from controllers._helpers import NeighborhoodHelper, InterestCategoryHelper

################################################################################
# Events page
################################################################################
class EventsPage(webapp.RequestHandler):
  ################################################################################
  # GET
  def get(self, url_data):    
    if url_data:
      if '/new' == url_data:
        self.new()
      elif '/search' == url_data:
        params = Parameters.parameterize(self.request)
        self.search(params)
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
    
    if 'is_delete' in params and params['is_delete'] == 'true':
      self.delete(url_data[1:], volunteer)
      self.redirect("/events")
      return
  
    id = self.create(params, volunteer)
    if id is None:
        self.redirect('/events')
        return
    
    
    self.redirect("/events/" + str(int(id)))
    return

  ################################################################################
  # LIST
  def list(self):
    try:
      volunteer = Authorize.login(self, requireVolunteer=True, redirectTo='/settings')
    except:
      return
    

    template_values = {
        'volunteer': volunteer,
        'eventvolunteer': volunteer.eventvolunteers,
        'neighborhoods': NeighborhoodHelper().selected(volunteer.home_neighborhood),
        'interestcategories' : InterestCategoryHelper().selected(volunteer),
        'session_id': volunteer.session_id,
      }
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'events', 'events.html')
    self.response.out.write(template.render(path, template_values))
    
  ################################################################################
  # SHOW A SINGLE EVENT
  def show(self, event_id):
    volunteer = Authorize.login(self)

    event = Event.get_by_id(int(event_id))
    owners = EventVolunteer.gql("where isowner=true AND event = :event", event=event).fetch(limit=100)
    
    eventvolunteer = ""
    session_id = ''
    
    if volunteer:
      eventvolunteer = EventVolunteer.gql("WHERE volunteer = :volunteer AND event = :event" ,
                         volunteer=volunteer, event=event).get()
      session_id = volunteer.session_id
                           
    friends = dict([(f.key().id(),1) for f in volunteer.friends()])
    followers = dict([(f.key().id(),1) for f in volunteer.followers()])
    following = dict([(f.key().id(),1) for f in volunteer.following()])
    
    attendees_anonymous = []
    attendees_friends = []
    attendees_followers = []
    attendees_following = []
    attendees_unknown = []
    
    for v in event.volunteers():
        id = v.key().id()
        if id == volunteer.key().id(): continue
        
        if v.event_access(volunteer = volunteer): 
            if id in friends:
                attendees_friends.append(v)
            elif id in followers:
                attendees_followers.append(v)
            elif id in following:
                attendees_following.append(v)
            else:
                attendees_unknown.append(v)
        else: 
            attendees_anonymous.append(v)

    template_values = { 'event' : event, 
                        'eventvolunteer': eventvolunteer, 
                        'owners': owners, 
                        'volunteer': volunteer, 
                        'session_id': session_id,
                        'attendees_friends': attendees_friends,
                        'attendees_followers': attendees_followers,
                        'attendees_following': attendees_following,
                        'attendees_anonymous': attendees_anonymous,
                        'attendees_unknown': attendees_unknown
                        }
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'events', 'event.html')
    self.response.out.write(template.render(path, template_values))
     
  ################################################################################
  # DELETE
  def delete(self, event_id, volunteer):
    event = Event.get_by_id(int(event_id))
    
    eventvolunteer = EventVolunteer.gql("WHERE volunteer = :volunteer AND isowner = true AND event = :event" ,
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
  def new(self):
    try:
      volunteer = Authorize.login(self, requireVolunteer=True, redirectTo='/settings')
    except:
      return

    if not volunteer.can_create_events():
      self.redirect("/events") #TODO REDIRECT to error page
      return

    template_values = {
        'volunteer': volunteer,
        'eventvolunteer': volunteer.eventvolunteers,
        'neighborhoods': NeighborhoodHelper().selected(volunteer.home_neighborhood),
        'interestcategories' : InterestCategoryHelper().selected(volunteer),
        'session_id': volunteer.session_id
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
      return None
      
    event.name = params['name']
    event.date = datetime.datetime.strptime(params['time'] + " " + params['date'], "%H:%M %m/%d/%Y")
    event.description = params['description']
    event.neighborhood = Neighborhood.get_by_id(int(params['neighborhood']))
    event.address = params['address']
    event.special_instructions = params['special_instructions']
    
    # TODO: Check to make sure values are present and valid
    # TODO: transaction such that if anything throws an exception we don't litter the database
    event.put()

    for interestcategory in InterestCategory.all():
      pic = 'interestcategory[' + str(interestcategory.key().id()) + ']'
      if params[pic] == ['1','1']: 
        eic = EventInterestCategory(event = event, interestcategory = interestcategory)
        eic.put()

    eventVolunteer = EventVolunteer(volunteer=volunteer, event=event, isowner=True)
    eventVolunteer.put()
    
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

    if params['neighborhood']:
      try:
        neighborhood = Neighborhood.get_by_id(int(params['neighborhood']))
        events_query.filter('neighborhood =', neighborhood)
      except:
        pass

    if params['fromdate']:
      try:
        fromdate = datetime.datetime.strptime(params['fromdate'], "%m/%d/%Y")
        events_query.filter('date >=', fromdate)
      except:
        pass

    if params['todate']:
      try:
        todate = datetime.datetime.strptime(params['todate'], "%m/%d/%Y")
        events_query.filter('date <=', todate)
      except:
        pass

    events = events_query.fetch(limit = 25)

    return (neighborhood, fromdate, todate, events)

################################################################################
# VolunteerForEvent
################################################################################
class VolunteerForEvent(webapp.RequestHandler):

  def post(self, url_data):
    try:
      volunteer = Authorize.login(self, requireVolunteer=True, redirectTo='/settings')
    except:
      return

    event = Event.get_by_id(int(url_data))
    
    if event:
      eventvolunteer = EventVolunteer.gql("WHERE volunteer = :volunteer AND isowner = false AND event = :event" ,
                          volunteer=volunteer, event=event).get()
      if self.request.get('delete') and self.request.get('delete') == "true":
        if eventvolunteer:
          eventvolunteer.delete()
      else:
        if not eventvolunteer:
          eventvolunteer = EventVolunteer(volunteer=volunteer, event=event, isowner=False)
          eventvolunteer.put()
    
    self.redirect('/events/' + url_data)
    return

################################################################################
# VolunteerForEvent
################################################################################
class VerifyEventAttendance(webapp.RequestHandler):
  
  ################################################################################
  # GET
  def get(self, url_data):
    try:
      volunteer = Authorize.login(self, requireVolunteer=True, redirectTo='/settings')
    except:
      return

    params = Parameters.parameterize(self.request)
    params['id'] = url_data

    self.show(params, volunteer)

  ################################################################################
  # POST
  def post(self, url_data):
    try:
      volunteer = Authorize.login(self, requireVolunteer=True, redirectTo='/settings')
    except:
      return

    params = Parameters.parameterize(self.request)
    params['id'] = url_data

    self.update(params, volunteer)

    self.redirect("/events/" + url_data)

  ################################################################################
  # SHOW
  def show(self, params, volunteer):
    event = Event.get_by_id(int(params['id']))    
    if not event:
      self.redirect("/events/" + url_data)
      return
    
    ev = EventVolunteer.gql("WHERE volunteer = :volunteer AND event = :event" ,
                        volunteer=volunteer, event=event).get()
    if not ev:
      self.redirect("/events/" + url_data)
      return
    
    template_values = {
        'eventvolunteer': ev,
        'volunteer' : ev.volunteer,
        'event' : ev.event,
        'now' : datetime.datetime.now().strftime("%A, %d %B %Y"),
      }
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'events', 'receipt.html')
    self.response.out.write(template.render(path, template_values))
    
    
  ################################################################################
  # UPDATE
  def update(self, params, volunteer):
    event = Event.get_by_id(int(params['id']))

    if not event:
      return
    
    owner = EventVolunteer.gql("WHERE volunteer = :volunteer AND isowner = true AND event = :event" ,
                        volunteer=volunteer, event=event).get()
    
    if not owner:
      return
      
    for key in params.keys():
      if key.startswith('event_volunteer_'):
        i = len('event_volunteer_')
        event_volunteer_id = key[i:]
        attended = params[key]
        hours = None
        if 'hours_' + event_volunteer_id in params.keys():
          hours = params['hours_' + event_volunteer_id]
        self.update_volunteer_attendance(event_volunteer_id, attended, hours)

  def update_volunteer_attendance(self, event_volunteer_id, attended, hours):
    eventvolunteer = EventVolunteer.get_by_id(int(event_volunteer_id))
    if not eventvolunteer:
      return
    
    if attended == 'True':
      eventvolunteer.attended = True
    elif attended == 'False':
      eventvolunteer.attended = False
    else:
      eventvolunteer.attended = False
      
    if hours:
      try:
        eventvolunteer.hours = int(hours)
      except exceptions.ValueError:
        eventvolunteer.hours = None
      
    eventvolunteer.put()

    
################################################################################
# EditEventPage
################################################################################
class EditEventPage(webapp.RequestHandler):
  
  ################################################################################
  # GET
  def get(self, url_data):
    try:
      volunteer = Authorize.login(self, requireVolunteer=True, redirectTo='/settings')
    except:
      return
    self.edit({ 'id' : url_data }, volunteer)

  ################################################################################
  # POST
  def post(self, url_data):
    try:
      volunteer = Authorize.login(self, requireVolunteer=True, redirectTo='/settings')
    except:
      return
      
    params = Parameters.parameterize(self.request)
    params['id'] = url_data
    
    self.update(params, volunteer)
    
    self.redirect("/events/" + url_data)
    
  ################################################################################
  # EDIT (is the get)
  def edit(self, params, volunteer):
    event = Event.get_by_id(int(params['id']))
    
    eventvolunteer = EventVolunteer.gql("WHERE volunteer = :volunteer AND event = :event AND isowner=true" ,
                           volunteer=volunteer, event=event).get()
    if not eventvolunteer:
      self.redirect("/events/" + params['id'])
      return
    
    owners = EventVolunteer.gql("where isowner=true AND event = :event", event=event).fetch(limit=100)
    

    template_values = { 
      'event' : event, 
      'eventvolunteer': eventvolunteer, 
      'owners': owners, 
      'volunteer': volunteer, 
      'neighborhoods': NeighborhoodHelper().selected(event.neighborhood),
      'interestcategories' : InterestCategoryHelper().selected(event),
      'session_id': volunteer.session_id,
    }
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'events', 'event_edit.html')
    self.response.out.write(template.render(path, template_values))
  
  ################################################################################
  # UPDATE
  def update(self, params, volunteer):
    event = Event.get_by_id(int(params['id']))
    
    if not event.validate(params):
      return None
    
    eventvolunteer = EventVolunteer.gql("WHERE volunteer = :volunteer AND event = :event AND isowner=true" ,
                           volunteer=volunteer, event=event).get()
    if eventvolunteer:
      event.name = params['name']
      event.date = datetime.datetime.strptime(params['time'] + " " + params['date'], "%H:%M %m/%d/%Y")
      event.neighborhood = Neighborhood.get_by_id(int(params['neighborhood']))
      event.description = params['description']
      event.address = params['address']
      event.special_instructions = params['special_instructions']
      
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

  