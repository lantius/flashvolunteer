import os, string

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from models import Volunteer, Event, EventVolunteer, Neighborhood


################################################################################
# Events page
################################################################################
class EventsPage(webapp.RequestHandler):


  ################################################################################
  # INDEX
  ################################################################################  
  def list(self):
    user = users.get_current_user()

    if not user:
      self.redirect(users.create_login_url(self.request.uri))
      return

    volunteer = Volunteer.gql("where user = :user", user=user).get();
    
    if not volunteer:
      self.redirect("/settings");

    message = "default message"
    logout_url = users.create_logout_url(self.request.uri)
    template_values = {
        'logout_url': logout_url,
        'message': message,
        'eventvolunteer' : volunteer.ev_set,
        'neighborhoods' : Neighborhood.all(),
      }
    path = os.path.join(os.path.dirname(__file__), 'events.html')
    self.response.out.write(template.render(path, template_values))
    
  ################################################################################
  # SHOW
  # A SINGLE EVENT
  ################################################################################
  def show(self, event_id):
    event = Event.get_by_id(int(event_id))
    owners = EventVolunteer.gql("where isowner=true AND event = :event", event=event).fetch(limit=100)
    
    eventvolunteer = ""
    user = users.get_current_user()
    logout_url = ''
    if user:    
      volunteer = Volunteer.gql("where user = :user", user=user).get();
      logout_url = users.create_logout_url(self.request.uri)
      
      if volunteer:
        eventvolunteer = EventVolunteer.gql("WHERE volunteer = :volunteer AND event = :event" ,
                           volunteer=volunteer, event=event).get()
                           
    template_values = { 'event' : event, 'eventvolunteer': eventvolunteer, 'owners': owners, 'logout_url': logout_url}
    path = os.path.join(os.path.dirname(__file__), 'event.html')
    self.response.out.write(template.render(path, template_values))
     
     
  ################################################################################
  # POST
  ################################################################################
  def post(self, url_data):
    user = users.get_current_user()

    if not user:
        self.redirect(users.create_login_url(self.request.uri))
        return
        
    volunteer = Volunteer.gql("where user = :user", user=user).get();
    if not volunteer:
      self.redirect("/settings");

    isDelete = self.request.get('delete')
    
    if isDelete and isDelete == 'true':
      EventsPage.delete(self)
      self.redirect("/events")
      return

    event = Event()
    event.name = self.request.get('name')
    event.neighborhood = Neighborhood.get_by_id(int(self.request.get('neighborhood')))
    # TODO
    # Check to make sure values are present and valid
    event.put()

    eventVolunteer = EventVolunteer(volunteer=volunteer, event=event, isowner=True)
    eventVolunteer.put()
    
    self.redirect("/events")
    
  ################################################################################
  # DELETE
  ################################################################################
  def delete(self):
    user = users.get_current_user()

    if not user:
        self.redirect(users.create_login_url(self.request.uri))
        return
        
    volunteer = Volunteer.gql("WHERE user = :user", user=user).get();
    if not volunteer:
      self.redirect("/settings");
    
    event = Event.get_by_id(int(self.request.get('id')))
    
    eventvolunteer = EventVolunteer.gql("WHERE volunteer = :volunteer AND isowner = true AND event = :event" ,
                        volunteer=volunteer, event=event).get()
    if eventvolunteer:
      event.delete()
      eventvolunteer.delete()
      # TODO: need to delete all other volunteers for this event as well, when we have them...


  ################################################################################
  # POST
  ################################################################################    


  ################################################################################
  # GET
  ################################################################################    
  def get(self, url_data):    
    if url_data:
      self.show(url_data[1:])
    else:
      self.list()

################################################################################
# VolunteerForEvent
################################################################################
class VolunteerForEvent(webapp.RequestHandler):

  def post(self, url_data):

    user = users.get_current_user()

    if not user:
      self.redirect(users.create_login_url(self.request.uri))
      return
    
    volunteer = Volunteer.gql("where user = :user", user=user).get();
    if not volunteer:
      self.redirect("/settings");
      
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


################################################################################
# EditEventPage
################################################################################
class EditEventPage(webapp.RequestHandler):
  
  ################################################################################
  def get(self, url_data):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.uri))
      return
    
    volunteer = Volunteer.gql("where user = :user", user=user).get();
    if not volunteer:
      self.redirect("/settings");    
    
    event = Event.get_by_id(int(url_data))
    
    eventvolunteer = EventVolunteer.gql("WHERE volunteer = :volunteer AND event = :event AND isowner=true" ,
                           volunteer=volunteer, event=event).get()
    if not eventvolunteer:
      self.redirect("/events/" + url_data)
      return
    
    owners = EventVolunteer.gql("where isowner=true AND event = :event", event=event).fetch(limit=100)
    
                           
    logout_url = users.create_logout_url(self.request.uri)
    template_values = { 'event' : event, 'eventvolunteer': eventvolunteer, 'owners': owners, 
    'logout_url': logout_url, 
    'neighborhoods' : Neighborhood.all(),
    }
    path = os.path.join(os.path.dirname(__file__), 'event_edit.html')
    self.response.out.write(template.render(path, template_values))
  
  ################################################################################
  def post(self, url_data):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.uri))
      return
    
    volunteer = Volunteer.gql("where user = :user", user=user).get();
    if not volunteer:
      self.redirect("/settings");    
    
    event = Event.get_by_id(int(url_data))
    
    eventvolunteer = EventVolunteer.gql("WHERE volunteer = :volunteer AND event = :event AND isowner=true" ,
                           volunteer=volunteer, event=event).get()
    if not eventvolunteer:
      self.redirect("/events/" + url_data)
      return
    
    event.name = self.request.get('name')
    event.neighborhood = Neighborhood.get_by_id(int(self.request.get('neighborhood')))
    event.put()
    
    self.redirect("/events/" + url_data)
    