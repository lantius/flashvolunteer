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


################################################################################
# Event Attendees 

class EventAttendeesPage(webapp.RequestHandler):

  def get(self, volunteer_id, page):
    if volunteer_id:
      self.show(volunteer_id, int(page))
    else:
      self.list() 

  def show(self, event_id, page):
    LIMIT = 12

    try:
      volunteer = Authorize.login(self, requireVolunteer=True, redirectTo='/settings')
    except:
      return

    event = Event.get_by_id(int(event_id))

    total = event.eventvolunteers.count()
    start = (page-1) * LIMIT + 1
    offset = start - 1
    
    eventvolunteer = EventVolunteer.gql("WHERE volunteer = :volunteer AND event = :event" ,
                         volunteer=volunteer, event=event).get() 
                         
    if eventvolunteer and (eventvolunteer.isowner or event.inpast()): 
        attendees = [ev.volunteer for ev in event.eventvolunteers.fetch(limit = LIMIT, offset = offset)]
    else:
        checked = 0
        has_access = 0
        non_anonymous_attendees = [v for v in event.volunteers() \
                                    if v.event_access(volunteer=volunteer) and v.key().id() != volunteer.key().id()]     
        
        attendees = non_anonymous_attendees[offset:offset+LIMIT]
                             
        total = len(non_anonymous_attendees)  
        
    end = start + len(attendees) - 1
                                            
    if end == total:
        next_page = -1
    else: 
        next_page = page + 1
    
    if page == 1:
        prev_page = -1
    else:
        prev_page = page -1
        
    template_values = { 'event': event,
                        'volunteer' : volunteer,
                        'team': attendees,
                        'session_id' : volunteer.session_id,
                        'total': total,
                        'start': start,
                        'end': end,
                        'next_page': next_page,
                        'prev_page': prev_page,
                        'title': '%s\'s Attendees'%event.name,
                        'url': '/events/%i/attendees/'%event.key().id()
                        }
    
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'volunteers', 'person_lists', '_paginated_volunteer_page.html')
    self.response.out.write(template.render(path, template_values))

