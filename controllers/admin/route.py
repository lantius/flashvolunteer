import os, logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from models.volunteer import Volunteer
from models.neighborhood import Neighborhood
from models.event import Event
from models.interestcategory import InterestCategory
from models.application import Application

from components.sessions import Session

import wsgiref.handlers

from controllers.admin.migrate_datastore import MigrateDatastore

application = webapp.WSGIApplication([(
    '/admin/migrate', MigrateDatastore)

], debug=True)

def main():
    run_wsgi_app(application)                                    

if __name__ == '__main__':
    main()