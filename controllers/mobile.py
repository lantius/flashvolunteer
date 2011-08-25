from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from models.event import Event
from models.new_checkin import NewCheckin
import os


from controllers.abstract_handler import AbstractHandler

################################################################################
# Mobile pages
################################################################################
class CheckinPage(AbstractHandler):
    def get(self, event_id):    
        try:
            volunteer = self.auth()
        except:
            return
        
        event_id = event_id.replace("/","")
        if event_id:
            event = Event.get_by_id(int(event_id))
        else:
            event = None
        
        template_values = {
            'volunteer': volunteer,
            'event' : event,
          }
        self._add_base_template_values(vals = template_values)
        
        if event:
            path = os.path.join(os.path.dirname(__file__),'..', 'views', 'mobile', 'checkin.html')
        else:
            path = os.path.join(os.path.dirname(__file__),'..', 'views', 'mobile', 'checkin_finish.html')
        
        self.response.out.write(template.render(path, template_values))
        return
        
    def post(self, event_id):    
        try:
            volunteer = self.auth()
        except:
            return
        
        
        params = self.parameterize() 
        
        name = None
        email = None
        if 'name' in params:
            name = params['name']
        if 'email' in params:
            email = params['email']
            
            
        event_id = event_id.replace("/","")
        if event_id:
            event = Event.get_by_id(int(event_id))
        else:
            event = None
            
        if email and name:
            checkin = NewCheckin(params['name'], params['email'], event)
            checkin.put()

        template_values = {
            'volunteer': volunteer,
          }
        self.redirect('/#/mobile/checkin')