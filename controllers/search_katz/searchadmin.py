#from django.utils import simplejson
#import urllib, os
import logging

from controllers.abstract_handler import AbstractHandler
from models.event import Event
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext import deferred
from controllers.search_katz.search import index_all

#import datetime
import os, string, random
from components.time_zones import now

class SearchAdmin(AbstractHandler):

    # make search index for all events
    def get(self, urldata = None):
        try:
            account = self.auth(require_login=True, require_admin = True)
        except:
            return   
        logging.info('SearchAdmin: get')
        #params = self.parameterize() 

        pathstem = '/admin/searchadmin'
        if (self.request.path == pathstem + '/createeventindex'):
            deferred.defer(index_all, Event)

        #just get the main search admin page
        template_values = {
            'account' : account
        }
        self._add_base_template_values(vals = template_values)

        path = os.path.join(os.path.dirname(__file__),'..', '..', 'views', 'admin', 'searchadmin.html')
        self.response.out.write(template.render(path, template_values, debug=self.is_debugging()))
        
    # make search index for all events
    def post(self, urldata = None):
        try:
            account = self.auth(require_login=True, require_admin = True)
        except:
            return   
        logging.info('SearchAdmin: get')
        #params = self.parameterize() 

        pathstem = '/admin/searchadmin'
        if (self.request.path == pathstem + '/createeventindex'):
            deferred.defer(index_all, Event)
            #just get the main search admin page
            self.redirect('/admin/searchadmin')

            

