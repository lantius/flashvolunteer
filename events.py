import os

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from models import Volunteer, Event, EventVolunteer, Neighborhood


################################################################################
# Events page
################################################################################
class EventsPage(webapp.RequestHandler):

  ################################################################################
  # GET
  ################################################################################  
  def get(self):
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
        'events' : volunteer.events(),
        'neighborhoods' : Neighborhood.all(),
      }
    path = os.path.join(os.path.dirname(__file__), 'events.html')
    self.response.out.write(template.render(path, template_values))

  ################################################################################
  # POST
  ################################################################################
  def post(self):
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
      