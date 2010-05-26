import os, string

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db

from models.event import Event
from models.eventvolunteer import EventVolunteer
from models.messages import MessageType

from controllers.abstract_handler import AbstractHandler

from utils.message_text import type1_vol, type1_unvol
################################################################################
# VolunteerForEvent
################################################################################
class VolunteerForEvent(AbstractHandler):

    def get(self, id):
        try:
            volunteer = self.auth(require_login=True)
        except:
            return
        
        event = Event.get_by_id(int(id))

        ev = event.eventvolunteers.filter('volunteer = ', volunteer).get()
        
        template_values = {
            'volunteer' : volunteer,
            'event' : event,
            'eventvolunteer': ev
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__), '..', 'views', 'events', 'event_page', 'volunteer_interest.html')
        self.response.out.write(template.render(path, template_values))
                
        
  ################################################################################
  # POST
    def post(self, url_data):
        try:
            volunteer = self.auth(require_login=True)
        except:
            return
        
        event = Event.get_by_id(int(url_data))
        
        if event and self.request.get('interested'):
            eventvolunteer = event.eventvolunteers.filter('volunteer =', volunteer).get()
            interest_level = int(self.request.get('interested'))
            
            if interest_level == 0:
                if eventvolunteer:
                    eventvolunteer.delete()
                    (to, subject, body) = self.get_message_text(event = event, 
                                                                  volunteer = volunteer, 
                                                                  sign_up = False)
                    if not event.inpast():
                        self.send_message( to = to, 
                                    subject = subject, 
                                    body = body, 
                                    type = MessageType.all().filter('name =', 'event_coord').get(),
                                    domain = self.get_domain())
            else:
                if not eventvolunteer:
                    eventvolunteer = EventVolunteer(
                                        volunteer=volunteer, 
                                        event=event, 
                                        isowner=False,
                                        event_is_upcoming = not event.in_past,
                                        event_is_hidden = event.hidden,
                                        event_date = event.date,
                                        application = event.application,
                                        interest_level = interest_level)
                    eventvolunteer.put()
              
                    #session = self._session()
                    if event.in_past:
                        self.add_notification_message('Thanks for attending!')
                    else:
                        self.add_notification_message('You are now signed up for "%s"!'%event.name)
                        (to, subject, body) = self.get_message_text(event = event, 
                                                                      volunteer = volunteer,
                                                                      sign_up = True)
                        
                        self.send_message( to = to, 
                                subject = subject, 
                                body = body, 
                                type = MessageType.all().filter('name =', 'event_coord').get(),
                                domain = self.get_domain())
                else:
                    if interest_level != eventvolunteer.interest_level:
                        eventvolunteer.interest_level = interest_level
                        eventvolunteer.put()
                        
        self.redirect('/#/events/' + url_data)
        return

    def get_message_text(self, event, volunteer, sign_up = True):
        to = (ev.volunteer for ev in event.eventvolunteers.filter('isowner =', True).fetch(limit=10))
                          
        if sign_up:
            msg = type1_vol
        else:
            msg = type1_unvol

        params = {
            'event_name': event.name.strip(),
            'owner_name': ', '.join([owner.get_name().strip() for owner in to]),
            'event_url': '%s%s'%(self._get_base_url(), event.url()),
            'vol_count': event.volunteer_count(),
            'vol_name': volunteer.get_name()
        }
        body = msg.body%params
        subject = msg.subject%params
        
        return to, subject, body