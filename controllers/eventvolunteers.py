import os, string

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db

from models.volunteer import Volunteer
from models.event import Event
from models.eventvolunteer import EventVolunteer
from models.messages import MessageType

from controllers._utils import send_message

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
            volunteer = self.auth(requireVolunteer=True)
        except:
            return
        
        event = Event.get_by_id(int(url_data))
        
        if event:
            eventvolunteer = event.eventvolunteers.filter('account =', volunteer.account).get()
            if self.request.get('delete') and self.request.get('delete') == "true":
                if eventvolunteer:
                    eventvolunteer.delete()
                    (to, subject, body) = self.get_message_text(event = event, 
                                                                      volunteer = volunteer, 
                                                                      sign_up = False)
                    send_message( to = to, 
                                subject = subject, 
                                body = body, 
                                type = MessageType.all().filter('name =', 'event_coord').get())
            else:
                if not eventvolunteer:
                    eventvolunteer = EventVolunteer(account=volunteer.account, event=event, isowner=False)
                    eventvolunteer.put()
                    (to, subject, body) = self.get_message_text(event = event, 
                                                                      volunteer = volunteer,
                                                                      sign_up = True)
        
                    send_message( to = to, 
                            subject = subject, 
                            body = body, 
                            type = MessageType.all().filter('name =', 'event_coord').get())
              
        self.redirect('/events/' + url_data)
        return

    def get_message_text(self, event, volunteer, sign_up = True):
        to = (ev.account for ev in event.eventvolunteers.filter('isowner =', True).fetch(limit=10))
                          
        if sign_up:
            msg = type1_vol
        else:
            msg = type1_unvol

        params = {
            'event_name': event.name.strip(),
            'owner_name': ', '.join([owner.get_name().strip() for owner in to]),
            'event_url': '%s%s'%(self._get_base_url(), event.url()),
            'vol_count': event.volunteer_count(),
            'vol_name': volunteer.account.get_name()
        }
        body = msg.body%params
        subject = msg.subject%params
        
        return to, subject, body