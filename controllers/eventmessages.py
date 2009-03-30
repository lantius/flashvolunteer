import os, string, datetime

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from models import Volunteer, Event, Message, EventVolunteer

from controllers._auth import Authorize
from controllers._params import Parameters
from controllers.messages import MessagesPage

################################################################################
################################################################################
class EventMessagesPage(MessagesPage):

  ################################################################################
  # GET
  def get(self, event_data, message_data):    
    event = Event.get_by_id(int(event_data))

    if message_data:
      if '/new' == message_data:
        self.new(event)
      else:
        self.show(event, message_data[1:])
    else:
      self.list(event)
      
  ################################################################################
  # POST
  def post(self, event_data, message_data):
    try:
      (user, volunteer) = Authorize.login(self, requireUser=True, requireVolunteer=True, redirectTo='settings')
    except:
      return
    
    event = Event.get_by_id(int(event_data))
    params = Parameters.parameterize(self.request)
    
    if 'is_delete' in params and params['is_delete'] == 'true':
      self.delete(message_data[1:], volunteer)
      self.redirect(event.url() + '/messages')
      return

    self.create(params, event, volunteer)
    self.redirect(event.url() + '/messages')
    return
  
  ################################################################################
  # NEW
  def new(self, event):
    try:
      (user, volunteer) = Authorize.login(self, requireUser=True, requireVolunteer=True, redirectTo='settings')
    except:
      return

    eventvolunteer = EventVolunteer.gql("WHERE event = :event AND volunteer = :volunteer AND isowner = true",
                event = event, volunteer = volunteer).get()
                
    logout_url = users.create_logout_url(self.request.uri)
    
    message = Message()
    template_values = {
        'logout_url': logout_url,
        'event' : event,
        'eventvolunteer' : eventvolunteer,
        'message' : message,
        'session_id': volunteer.session_id
      }
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'messages', 'create_message.html')
    self.response.out.write(template.render(path, template_values))
  
  ################################################################################
  # CREATE
  def create(self, params, event, volunteer):
    ev = EventVolunteer.gql("WHERE event = :event AND volunteer = :volunteer AND isowner = true",
                event = event, volunteer = volunteer).get()
    if not ev:
      return None
    
    params['recipient'] = event
    message_id = MessagesPage.create(self, params, volunteer)
    message = Message.get_by_id(int(message_id))
    
  ################################################################################
  # LIST
  def list(self, event):
    try:
      (user, volunteer) = Authorize.login(self, requireUser=False, requireVolunteer=False, redirectTo='settings')
    except:
      return
    eventvolunteer = None  
    logout_url = None
    
    if user:
      logout_url = users.create_logout_url(self.request.uri)
    
      if volunteer:
        eventvolunteer = EventVolunteer.gql("WHERE event = :event AND volunteer = :volunteer AND isowner = true",
                event = event, volunteer = volunteer).get()
    
    template_values = {
        'eventvolunteer' : eventvolunteer,
        'logout_url': logout_url,
        'event' : event,
      }
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'events', 'event_messages.html')
    self.response.out.write(template.render(path, template_values))  
    
    
    
    
    