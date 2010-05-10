import logging
import urllib

from components.time_zones import now

from google.appengine.api import urlfetch

from google.appengine.ext import db
from google.appengine.api import memcache


################################################################################
# RegionDomain
class Application(db.Model):
    name = db.StringProperty()
    ne_coord = db.GeoPtProperty() # No default
    sw_coord = db.GeoPtProperty()
    
    def get_alias(self):
        return self.name.replace('-', ' ').title()

  
    def ongoing_opportunities(self):
        memcached = memcache.get('%s-ongoing_opportunities'%self.name)
        if not memcached:
            date = now()
                    
            memcached = self.events.filter(
                'date >= ', date).filter(
                'hidden = ', False).filter(
                'is_ongoing = ', True).order(
                'date')
            memcache.set('%s-ongoing_opportunities'%self.name, memcached, 60 * 10)
        
        return memcached        
        
    def upcoming_events(self):
        memcached = memcache.get('%s-upcoming_events'%self.name)
        if not memcached:
            date = now()
                    
            memcached = self.events.filter(
                'date >= ', date).filter(
                'hidden = ', False).filter(
                'is_ongoing = ', False).order(
                'date')
                
            memcache.set('%s-upcoming_events'%self.name, memcached, 60 * 10)
        return memcached

from components.appengine_admin.model_register import register, ModelAdmin
## Admin views ##
class AdminApplication(ModelAdmin):
    model = Application
    listFields = ('name', 'ne_coord', 'sw_coord')
    editFields = ('name', 'ne_coord', 'sw_coord')
    readonlyFields = ()

register(AdminApplication)
