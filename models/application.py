import datetime
import logging
import urllib
from components.geostring import *
from components.time_zones import Pacific

from google.appengine.api import urlfetch

from google.appengine.ext import db

################################################################################
# RegionDomain
class Application(db.Model):
  name = db.StringProperty()