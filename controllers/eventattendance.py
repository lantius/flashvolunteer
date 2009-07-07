import os, string

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db

from models.volunteer import *
from models.event import *
from models.eventvolunteer import *

from controllers._auth import Authorize
from controllers._params import Parameters

################################################################################
# VerifyEventAttendance
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