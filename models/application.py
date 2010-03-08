import logging
import urllib

from components.time_zones import now

from google.appengine.api import urlfetch

from google.appengine.ext import db

################################################################################
# RegionDomain
class Application(db.Model):
    name = db.StringProperty()
    ne_coord = db.GeoPtProperty() # No default
    sw_coord = db.GeoPtProperty()
    
    def get_alias(self):
        return self.name.replace('-', ' ').title()

  
    def ongoing_opportunities(self, date = None):
        if date is None: date = now()
                
        events = self.events.filter(
            'date >= ', date).filter(
            'hidden = ', False).filter(
            'is_ongoing = ', True).order(
            'date')
        
        return events        
        
    def upcoming_events(self, date = None):
        if date is None: date = now()
                
        events = self.events.filter(
            'date >= ', date).filter(
            'hidden = ', False).filter(
            'is_ongoing = ', False).order(
            'date')
        
        return events

from components.appengine_admin.model_register import register, ModelAdmin
## Admin views ##
class AdminApplication(ModelAdmin):
    model = Application
    listFields = ('name', 'ne_coord', 'sw_coord')
    editFields = ('name', 'ne_coord', 'sw_coord')
    readonlyFields = ()

register(AdminApplication)
