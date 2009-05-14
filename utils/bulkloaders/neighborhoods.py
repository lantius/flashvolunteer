#!/usr/bin/env python
#
# Bulk uploader to Google AppEngine.
#
# Based on article at: 
#    http://code.google.com/appengine/articles/bulkload.html
#
# Usage:
#    ./tools/bulkload_client.py --filename locations.csv \
#                     --kind MyModel \
#                     --url http://localhost:8080/load
#
# Csv must be formatted properly:
#     neighborhood_name


from google.appengine.ext import db
from google.appengine.tools import bulkloader
import models

# There is an app engine bug that forced me to copy the Neighborhood definition here
class Neighborhood(db.Model):
  name = db.StringProperty()

  def url(self):
    return '/neighborhoods/' + str(self.key().id())

class NeighborhoodLoader(bulkloader.Loader):
  def __init__(self):
    bulkloader.Loader.__init__(self, 'Neighborhood',
                               [('name', str)])

loaders = [NeighborhoodLoader]