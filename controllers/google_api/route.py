import os, logging

from google.appengine.ext import webapp, db

from components.sessions import Session

import wsgiref.handlers

from controllers.settings import SettingsPage
from controllers.google_api.map import MapHandler

webapp.template.register_template_library('templatetags.filters')


def main():
    session = Session()
    application = webapp.WSGIApplication([
        ('/google/map', MapHandler),
        #TODO: route here? admin tools
          
    ], debug=True)

    wsgiref.handlers.CGIHandler().run(application)
    
if __name__ == '__main__':
    main()