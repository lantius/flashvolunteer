import os, string

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db

from models.volunteer import Volunteer
from models.event import Event
from models.eventvolunteer import EventVolunteer

from components.time_zones import Pacific, now

from controllers.abstract_handler import AbstractHandler

################################################################################
# VerifyEventAttendance
################################################################################
class VerifyEventAttendance(AbstractHandler):
  
  ################################################################################
  # GET
  def get(self, url_data):
    try:
        account = self.auth(require_login=True)
    except:
        return
    
    params = self.parameterize() 
    params['id'] = url_data

    self.show(params, account)

  ################################################################################
  # POST
  def post(self, url_data):
    try:
        account = self.auth(require_login=True)
    except:
        return
    
    params = self.parameterize() 
    params['id'] = url_data

    self.update(params, account)

    self.redirect("/events/" + url_data)

  ################################################################################
  # SHOW
  def show(self, params, account):
    event = Event.get_by_id(int(params['id']))    
    if not event:
      self.redirect("/events/" + url_data)
      return
    
    if account: user = account.get_user()
    ev = event.eventvolunteers.filter('volunteer =', user).get()
                        
    if not ev:
      self.redirect("/events/" + url_data)
      return
    
    template_values = {
        'eventvolunteer': ev,
        'volunteer' : account.get_user(),
        'event' : event,
        'now' : now().strftime("%A, %d %B %Y"),
      }
    
    self._add_base_template_values(vals = template_values)
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'events', 'receipt.html')
    self.response.out.write(template.render(path, template_values))
    
  ################################################################################
  # UPDATE
  def update(self, params, account):
    event = Event.get_by_id(int(params['id']))

    if not event:
      return
    
    if account: user = account.get_user()
    owner = event.eventvolunteers.filter('volunteer =', user).filter('isowner =', True).get()

    
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

  ################################################################################
  # UPDATE VOLUNTEER ATTENDANCE
  def update_volunteer_attendance(self, event_volunteer_id, attended, hours):
    eventvolunteer = EventVolunteer.get_by_id(int(event_volunteer_id))
    if not eventvolunteer:
      return
    
    if attended == 'True':
      eventvolunteer.attended = True
    elif attended == 'False':
      eventvolunteer.attended = False
    else:
      eventvolunteer.attended = None
      
    if hours:
      try:
        eventvolunteer.hours = int(hours)
      except exceptions.ValueError:
        eventvolunteer.hours = None
      
    eventvolunteer.put()