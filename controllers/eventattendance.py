import os, string

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db

from models.event import Event
from models.eventvolunteer import EventVolunteer

from components.time_zones import now

from controllers.abstract_handler import AbstractHandler

################################################################################
# VerifyEventAttendance
################################################################################
class VerifyEventAttendance(AbstractHandler):
  
    ################################################################################
    # GET
    def get(self, url_data):
        try:
            volunteer = self.auth(require_login=True)
        except:
            return
        
        params = self.parameterize() 
        params['id'] = url_data
        
        self.show(params, volunteer)
    
    ################################################################################
    # POST
    def post(self, url_data):
        try:
            volunteer = self.auth(require_login=True)
        except:
            return
           
        params = self.parameterize() 
        params['id'] = url_data
        
        event = Event.get_by_id(int(params['id']))
        self.update(params, volunteer)
        
        if not self.ajax_request():
            self.redirect(event.url())
    
    ################################################################################
    # SHOW
    def show(self, params, volunteer):
        event = Event.get_by_id(int(params['id']))    
        if not event:
            self.redirect('/#' + event.url())
            return
        
        ev = event.eventvolunteers.filter('volunteer =', volunteer).get()
                            
        if not ev:
            self.redirect('/#' + event.url())
            return
        
        template_values = {
            'eventvolunteer': ev,
            'volunteer' : volunteer,
            'event' : event,
            'now' : now().strftime("%A, %d %B %Y"),
          }
        
        self._add_base_template_values(vals = template_values)
        path = os.path.join(os.path.dirname(__file__),'..', 'views', 'events', 'receipt.html')
        self.response.out.write(template.render(path, template_values))
      
    ################################################################################
    # UPDATE
    def update(self, params, volunteer):
        event = Event.get_by_id(int(params['id']))
        
        if not event:
            return
        
        eventvolunteer = event.eventvolunteers.filter('volunteer =', volunteer).get()
        owner = eventvolunteer.isowner

        i = len('event_volunteer_')
        deleted = 0
        hours_logged = 0
        session = self._session()
        
        for key in params.keys():
            if key.startswith('event_volunteer_'):
                event_volunteer_id = key[i:]
                eventvolunteer = EventVolunteer.get_by_id(int(event_volunteer_id))
                if owner or int(event_volunteer_id) == eventvolunteer.key().id():
                    attended = params[key]
                    if params['event_volunteer_%s'%event_volunteer_id] == 'True':
                        hours = params['hours_' + event_volunteer_id]
                        self.update_volunteer_attendance(event_volunteer_id, attended, hours)
                        if not owner:
                            self.add_notification_message('Thanks for volunteering for %s hours!'%hours)
                        else: 
                            hours_logged += 1
                    elif params['event_volunteer_%s'%event_volunteer_id] == 'False':
                        if not eventvolunteer.isowner:
                            eventvolunteer.delete()
                            if not owner:
                                self.add_notification_message('Thanks for removing yourself from the attendees!')
                            else:
                                deleted += 1
        if deleted + hours_logged > 0: 
            if deleted > 0 and hours_logged > 0:
                self.add_notification_message('You have logged hours for %i volunteers, and removed %i people from the attendees list.'%(hours_logged, deleted))
            elif deleted > 0: 
                self.add_notification_message('You have removed %i people from the attendees list.'%(deleted))
            else:
                self.add_notification_message('You have logged hours for %i volunteers.'%(hours_logged))

                
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
                eventvolunteer.hours = int(float(hours))
                eventvolunteer.put()
            except:
                eventvolunteer.hours = None          
        