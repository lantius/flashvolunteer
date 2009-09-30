import datetime
import logging
import urllib
from components.geostring import *
from components.time_zones import Pacific

from google.appengine.api import urlfetch

from google.appengine.ext import db
from models.application import Application

################################################################################
# ApplicationDomain
class ApplicationDomain(db.Model):
  domain = db.StringProperty()
  application = db.ReferenceProperty(Application,
                                required = True,
                                collection_name = 'domains')
