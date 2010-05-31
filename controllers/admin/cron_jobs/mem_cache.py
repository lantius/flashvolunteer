from google.appengine.ext.webapp import template 
from controllers.abstract_handler import AbstractHandler

from google.appengine.api import memcache

import os, logging

from datetime import datetime
from google.appengine.ext import deferred
from models.application import Application
    
def mem_cache(app_id, is_debugging): 
    application = Application.get_by_id(app_id)  
    if application is None: return
     
    if not memcache.get('%s-upcoming_events'%application.name):
        upcoming_events = application.upcoming_events()
        ongoing_events = application.ongoing_events()
            
class MemCache(AbstractHandler):

    def get(self):
        for app in Application.all():
            deferred.defer(mem_cache, app.key().id(), self.is_debugging())