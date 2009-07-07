import os, string

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db

from models.volunteer import *
from models.event import *
from models.eventvolunteer import *

from controllers._auth import Authorize

################################################################################
# VolunteerForEvent
################################################################################
class VolunteerForEvent(webapp.RequestHandler):

  ################################################################################
  # POST
  def post(self, url_data):
    try:
      volunteer = Authorize.login(self, requireVolunteer=True, redirectTo='/settings')
    except:
      return

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