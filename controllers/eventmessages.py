import os, string, datetime

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from models import Volunteer, Event, Message

from controllers._auth import Authorize
from controllers._params import Parameters
from controllers.messages import Message

################################################################################
################################################################################
class EventMessagesPage(webapp.RequestHandler):

  ################################################################################
  # GET
  def get(self, event_data, message_data):    
    event = Event.get_by_id(int(event_data[1:]))

    if message_data:
      if 'new' == message_data:
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
    
    event = Event.get_by_id(int(event_data[1:]))
    params = Parameters.parameterize(self.request)
    
    if 'is_delete' in params and params['is_delete'] == 'true':
      self.delete(params, volunteer)
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

    logout_url = users.create_logout_url(self.request.uri)

    template_values = {
        'logout_url': logout_url,
        'event' : event,
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
    
    m = MessagesPage()
    message_id = m.create(params, self.volunteer)
    message = Message.get_by_id(int(message_id))

    eventmessage = EventMessage(event = event, message = message)
    eventmessage.put()
    
    return eventmessage.key().id()
    
  ################################################################################
  # DELETE
  def delete(self, params, event, volunteer):
    message = Message.get_by_id(int(params['id']))
    
    eventmessage = EventMessage.gql("WHERE message = :message AND event = :event" ,
                        message=message, event=event).get()
      
      
      
      
      
      
    