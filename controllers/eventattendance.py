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
        
        event = Event.get_by_id(int(params['id']))
        self.update(params, account)
        
        self.redirect("/#" + event.url())
    
    ################################################################################
    # SHOW
    def show(self, params, account):
        event = Event.get_by_id(int(params['id']))    
        if not event:
            self.redirect("/#" + event.url())
            return
        
        if account: user = account.get_user()
        ev = event.eventvolunteers.filter('volunteer =', user).get()
                            
        if not ev:
            self.redirect("/#" + event.url())
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
        eventvolunteer = event.eventvolunteers.filter('volunteer =', user).get()
        owner = eventvolunteer.isowner

        i = len('event_volunteer_')  
        for key in params.keys():
            if key.startswith('event_volunteer_'):
                event_volunteer_id = key[i:]
                if owner or int(event_volunteer_id) == eventvolunteer.key().id():
                    attended = params[key]
                    if params['event_volunteer_%s'%event_volunteer_id] == 'True':
                        hours = params['hours_' + event_volunteer_id]
                        self.update_volunteer_attendance(event_volunteer_id, attended, hours)
                    elif params['event_volunteer_%s'%event_volunteer_id] == 'False':
                        ev = EventVolunteer.get_by_id(int(event_volunteer_id))
                        if not ev.isowner:
                            ev.delete()
    
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
        