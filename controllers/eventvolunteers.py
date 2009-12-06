import os, string

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db

from models.event import Event
from models.eventvolunteer import EventVolunteer
from models.messages import MessageType

from controllers.abstract_handler import AbstractHandler

from components.message_text import type1_vol, type1_unvol
from components.sessions import Session
################################################################################
# VolunteerForEvent
################################################################################
class VolunteerForEvent(AbstractHandler):

  ################################################################################
  # POST
    def post(self, url_data):
        try:
            account = self.auth(require_login=True)
        except:
            return
        
        event = Event.get_by_id(int(url_data))
        user = account.get_user()
        
        if event:
            eventvolunteer = event.eventvolunteers.filter('volunteer =', user).get()
            if self.request.get('delete') and self.request.get('delete') == "true":
                if eventvolunteer:
                    eventvolunteer.delete()
                    (to, subject, body) = self.get_message_text(event = event, 
                                                                  account = account, 
                                                                  sign_up = False)
                    self.send_message( to = to, 
                                subject = subject, 
                                body = body, 
                                type = MessageType.all().filter('name =', 'event_coord').get())
            else:
                if not eventvolunteer:
                    eventvolunteer = EventVolunteer(
                                        volunteer=user, 
                                        event=event, 
                                        isowner=False,
                                        event_is_upcoming = not event.in_past,
                                        event_is_hidden = event.hidden,
                                        event_date = event.date,
                                        application = event.application)
                    eventvolunteer.put()
                    (to, subject, body) = self.get_message_text(event = event, 
                                                                  account = account,
                                                                  sign_up = True)
        
                    self.send_message( to = to, 
                            subject = subject, 
                            body = body, 
                            type = MessageType.all().filter('name =', 'event_coord').get())
              
                    session = Session()
                    if event.in_past:
                        session['notification_message'] = ['Thanks for attending!']
                    else:
                        session['notification_message'] = ['You are now signed up for "%s"!'%event.name]
                    
        self.redirect('/#/events/' + url_data)
        return

    def get_message_text(self, event, account, sign_up = True):
        to = (ev.volunteer.account for ev in event.eventvolunteers.filter('isowner =', True).fetch(limit=10))
                          
        if sign_up:
            msg = type1_vol
        else:
            msg = type1_unvol

        params = {
            'event_name': event.name.strip(),
            'owner_name': ', '.join([owner.get_name().strip() for owner in to]),
            'event_url': '%s%s'%(self._get_base_url(), event.url()),
            'vol_count': event.volunteer_count(),
            'vol_name': account.get_name()
        }
        body = msg.body%params
        subject = msg.subject%params
        
        return to, subject, body