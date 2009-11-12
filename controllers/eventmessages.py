import os, string

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp

from models.volunteer import Volunteer
from models.event import Event
from models.messages.message import Message
from models.eventvolunteer import EventVolunteer

from controllers.messages import MessagesPage

from components.sessions import Session

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
      account = self.auth(require_login=True, redirect_to='/settings')
    except:
      return
    
    event = Event.get_by_id(int(event_data))
    params = self.parameterize() 
    
    if 'is_delete' in params and params['is_delete'] == 'true':
      self.delete(message_data[1:], account)
      self.redirect(event.url() + '/messages')
      return

    self.create(params, event, account)
    session = Session()
    self.redirect('/')
    return
  
  ################################################################################
  # NEW
  def new(self, event):
    try:
      volunteer = self.auth(require_login=True, redirect_to='/settings')
    except:
      return

    eventvolunteer = event.eventvolunteers.filter('account =', volunteer.account).filter('isowner =', True).get()


    message = Message()
    template_values = {
        'volunteer': volunteer,
        'event' : event,
        'eventvolunteer' : eventvolunteer,
        'message' : message,
      }
    self._add_base_template_values(vals = template_values)
    
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'messages', 'create_message.html')
    self.response.out.write(template.render(path, template_values))
  
  ################################################################################
  # CREATE
  def create(self, params, event, volunteer):
    ev = event.eventvolunteers.filter('account =', volunteer.account).filter('isowner =', True).get()

    if not ev:
      return None
    
    params['recipient'] = event
    message_id = MessagesPage.create(self, params, volunteer)
    message = Message.get_by_id(int(message_id))
    
  ################################################################################
  # LIST
  def list(self, event):
    try:
      account = self.auth(redirect_to='/settings')
    except:
      return
    
    if account: user = account.get_user()
    else: user = None
    
    eventvolunteer = None  
    
    if account:
      eventvolunteer = event.eventvolunteers.filter('account =', account).filter('isowner =', True).get()

    
    
    template_values = {
        'eventvolunteer' : eventvolunteer,
        'volunteer': user,
        'event' : event,
      }
    self._add_base_template_values(vals = template_values)
    
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'events', 'event_messages.html')
    self.response.out.write(template.render(path, template_values))  
    
    