import os

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from models import Volunteer, Event, EventVolunteer


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
    ownedEvents = EventVolunteer.gql("where volunteer = :volunteer AND isowner=true", volunteer=volunteer).fetch(limit=100)
    if ownedEvents:
      events_html="Created Events:<BR><table border=\"1\">\n"
    
      for ownedEvent in ownedEvents:
        event = ownedEvent.event
        events_html += "\t<tr>\n"
        events_html += "\t\t<td>" + event.name + "</td>\n\t\t<td>" + event.neighborhood + "</td>\n"
        events_html += "\t\t<td><form action=\"/events\" method=\"post\">"
        events_html += "<input type=hidden name=\"delete\" value=\"true\">"
        events_html += "<input type=hidden name=\"event_name\" value=\""+ event.name + "\">"
        events_html += "<input type=hidden name=\"event_neighborhood\" value=\""+ event.neighborhood + "\">"
        events_html += "<input type=submit value=\"delete\">"
        events_html += "</form></td>\n"
        events_html += "\t</tr>\n"

      events_html += "</table>\n"
    else:
      events_html ="Create an Event<BR>"
      
      
    logout_url = users.create_logout_url(self.request.uri)
    template_values = {
        'logout_url': logout_url,
        'message': message,
        'events_html': events_html
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
    event.name = self.request.get('event_name')
    event.neighborhood = self.request.get('event_neighborhood')
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
        
    volunteer = Volunteer.gql("where user = :user", user=user).get();
    if not volunteer:
      self.redirect("/settings");
    
    name = self.request.get('event_name')
    neighborhood = self.request.get('event_neighborhood')
    
    #TODO
    # Make this more efficient with a join
    ownedEvents = EventVolunteer.gql("where volunteer = :volunteer AND isowner=true", volunteer=volunteer).fetch(limit=100)
    if ownedEvents:
      for ownedEvent in ownedEvents:
        event = ownedEvent.event
        if event.name == name and event.neighborhood == neighborhood:
          event.delete()
          ownedEvent.delete()
          return