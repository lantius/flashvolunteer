import os, string

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db

from models.volunteer import Volunteer
from models.event import Event
from models.eventvolunteer import EventVolunteer

from controllers._auth import Authorize
from controllers._utils import send_message, get_domain

from controllers.abstract_handler import AbstractHandler

from components.message_text import type1_vol, type1_unvol
################################################################################
# VolunteerForEvent
################################################################################
class VolunteerForEvent(AbstractHandler):

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
              (to, subject, body) = self.get_message_text(event = event, 
                                                                  volunteer = volunteer, 
                                                                  sign_up = False)
              send_message(sender = volunteer, 
                            to = to, 
                            subject = subject, 
                            body = body, 
                            type = 1,
                            referral_url = event.url())
          else:
            if not eventvolunteer:
              eventvolunteer = EventVolunteer(volunteer=volunteer, event=event, isowner=False)
              eventvolunteer.put()
              (to, subject, body) = self.get_message_text(event = event, 
                                                                  volunteer = volunteer,
                                                                  sign_up = True)
        
              send_message(sender = volunteer, 
                            to = to, 
                            subject = subject, 
                            body = body, 
                            type = 1, 
                            referral_url = event.url())
              
        self.redirect('/events/' + url_data)
        return

    def get_message_text(self, event, volunteer, sign_up = True):
        #TODO email multiple owners
        owners = [ev.volunteer for ev in EventVolunteer.gql("WHERE isowner = true AND event = :event" ,
                          event=event).fetch(limit=10)]
                          
        to = owners
        
        if sign_up:
            msg = type1_vol
        else:
            msg = type1_unvol

        params = {
            'event_name': event.name.strip(),
            'owner_name': ', '.join([owner.get_name().strip() for owner in owners]),
            'event_url': 'http://%s%s'%(get_domain(), event.url()),
            'vol_count': EventVolunteer.gql("WHERE isowner = false AND event = :event" ,event=event).count(),
            'vol_name': volunteer.get_name()
        }
        body = msg.body%params
        subject = msg.subject%params
        
        return to, subject, body