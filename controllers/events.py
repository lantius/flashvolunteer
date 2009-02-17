import os, string

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from models import Volunteer, Event, EventVolunteer, Neighborhood, InterestCategory, EventInterestCategory

from controllers._auth import Authorize
from controllers._params import Parameters

from controllers._helpers import NeighborhoodHelper, InterestCategoryHelper

################################################################################
# Events page
################################################################################
class EventsPage(webapp.RequestHandler):
  ################################################################################
  # GET
  ################################################################################    
  def get(self, url_data):    
    if url_data:
      self.show(url_data[1:])
    else:
      self.list()

  ################################################################################
  # POST
  ################################################################################
  def post(self, url_data):
    (user, volunteer) = Authorize.login(self, requireUser=True, requireVolunteer=True, redirectTo='settings')  
    params = Parameters.parameterize(self.request)
    
    if 'is_delete' in params and params['is_delete'] == 'true':
      self.delete(params, volunteer)
      self.redirect("/events")
      return

    self.create(params, volunteer)
    self.redirect("/events")
    return

  ################################################################################
  # LIST
  ################################################################################  
  def list(self):
    (user, volunteer) = Authorize.login(self, requireUser=True, requireVolunteer=True, redirectTo='/settings')

    message = "default message"
    logout_url = users.create_logout_url(self.request.uri)
    
    template_values = {
        'logout_url': logout_url,
        'message': message,
        'eventvolunteer': volunteer.eventvolunteers,
        'neighborhoods': NeighborhoodHelper().selected(volunteer),
        'interestcategories' : InterestCategoryHelper().selected(volunteer),
        'session_id': volunteer.session_id
      }
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'events.html')
    self.response.out.write(template.render(path, template_values))
    
  ################################################################################
  # SHOW A SINGLE EVENT
  ################################################################################
  def show(self, event_id):
    (user, volunteer) = Authorize.login(self)

    event = Event.get_by_id(int(event_id))
    owners = EventVolunteer.gql("where isowner=true AND event = :event", event=event).fetch(limit=100)
    
    eventvolunteer = ""
    logout_url = ''
    session_id = ''
    
    if user:    
      logout_url = users.create_logout_url(self.request.uri)
      
    if volunteer:
      eventvolunteer = EventVolunteer.gql("WHERE volunteer = :volunteer AND event = :event" ,
                         volunteer=volunteer, event=event).get()
      session_id = volunteer.session_id
                           
    template_values = { 'event' : event, 'eventvolunteer': eventvolunteer, 'owners': owners, 'logout_url': logout_url, 'session_id': session_id}
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'event.html')
    self.response.out.write(template.render(path, template_values))
     
  ################################################################################
  # DELETE
  ################################################################################
  def delete(self, params, volunteer):
    event = Event.get_by_id(int(params['id']))
    
    eventvolunteer = EventVolunteer.gql("WHERE volunteer = :volunteer AND isowner = true AND event = :event" ,
                        volunteer=volunteer, event=event).get()
    if eventvolunteer:
      for ev in event.eventvolunteers:
        ev.delete() 
      for ei in event.eventinterestcategories:
        ei.delete()
      event.delete()

  ################################################################################
  # CREATE
  ################################################################################
  def create(self, params, volunteer):
    event = Event()
    event.name = params['name']
    event.neighborhood = Neighborhood.get_by_id(int(params['neighborhood']))
    
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
# VolunteerForEvent
################################################################################
class VolunteerForEvent(webapp.RequestHandler):

  def post(self, url_data):
    (user, volunteer) = Authorize.login(self, requireUser=True, requireVolunteer=True, redirectTo='/settings')

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
# EditEventPage
################################################################################
class EditEventPage(webapp.RequestHandler):
  
  ################################################################################
  # GET
  ################################################################################
  def get(self, url_data):
    (user, volunteer) = Authorize.login(self, requireUser=True, requireVolunteer=True, redirectTo='settings')
    self.edit({ 'id' : url_data }, volunteer)

  ################################################################################
  # POST
  ################################################################################
  def post(self, url_data):
    (user, volunteer) = Authorize.login(self, requireUser=True, requireVolunteer=True, redirectTo='settings')
    params = { 'id' : url_data, 
               'name' : self.request.get('name'),
               'neighborhood' : int(self.request.get('neighborhood')),
             }
    for interestcategory in InterestCategory.all():
      icp = 'interestcategory[' + str(interestcategory.key().id()) + ']'
      params[icp] = self.request.get_all(icp)        
    
    self.update(params, volunteer)
    
    self.redirect("/events/" + url_data)
    
  ################################################################################
  # EDIT
  ################################################################################
  def edit(self, params, volunteer):
    event = Event.get_by_id(int(params['id']))
    
    eventvolunteer = EventVolunteer.gql("WHERE volunteer = :volunteer AND event = :event AND isowner=true" ,
                           volunteer=volunteer, event=event).get()
    if not eventvolunteer:
      self.redirect("/events/" + params['id'])
      return
    
    owners = EventVolunteer.gql("where isowner=true AND event = :event", event=event).fetch(limit=100)
    

    logout_url = users.create_logout_url(self.request.uri)
    template_values = { 
      'event' : event, 
      'eventvolunteer': eventvolunteer, 
      'owners': owners, 
      'logout_url': logout_url, 
      'neighborhoods': NeighborhoodHelper().selected(event),
      'interestcategories' : InterestCategoryHelper().selected(event),
      'session_id': volunteer.session_id,
    }
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'event_edit.html')
    self.response.out.write(template.render(path, template_values))
  
  ################################################################################
  # UPDATE
  ################################################################################
  def update(self, params, volunteer):
    event = Event.get_by_id(int(params['id']))
    
    eventvolunteer = EventVolunteer.gql("WHERE volunteer = :volunteer AND event = :event AND isowner=true" ,
                           volunteer=volunteer, event=event).get()
    if eventvolunteer:
      event.name = params['name']
      event.neighborhood = Neighborhood.get_by_id(params['neighborhood'])
      
      for interestcategory in InterestCategory.all():
        paramname = 'interestcategory[' + str(interestcategory.key().id()) + ']'
        eic = EventInterestCategory.gql("WHERE event = :event AND interestcategory = :interestcategory" ,
                            event = event, interestcategory = interestcategory).get()
        if params[paramname] == ['1','1'] and not eic:          
          eic = EventInterestCategory(event = event, interestcategory = interestcategory)
          eic.put()
        elif params[paramname] == ['1'] and eic:
          eic.delete()
          
      event.put()
    