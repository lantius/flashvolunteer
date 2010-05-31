import os, logging

from google.appengine.ext import webapp, db

import wsgiref.handlers

from controllers.settings import SettingsPage
from controllers.google_api.map import MapHandler, NeighborhoodMapHandler, NeighborhoodsMapHandler, RegionMapHandler

webapp.template.register_template_library('controllers._filters')


def main():
    application = webapp.WSGIApplication([
        ('/google/map', MapHandler),
        ('/google/neighborhood_map', NeighborhoodMapHandler),
        ('/google/neighborhoods_map', NeighborhoodsMapHandler),
        ('/google/regional_map', RegionMapHandler)
        #TODO: route here? admin tools
          
    ], debug=True)

    wsgiref.handlers.CGIHandler().run(application)
    
if __name__ == '__main__':
    main()