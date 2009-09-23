import os
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template
from google.appengine.api import users

from controllers._auth import Authorize
from controllers._helpers import NeighborhoodHelper

from models.volunteer import *
from models.neighborhood import *
from models.event import *
from models.interestcategory import *

from controllers.events import _get_recommended_events, _get_upcoming_events 


################################################################################
# MainPage
class MainPage(webapp.RequestHandler):
  LIMIT = 3 
  def get(self):
    try:
      volunteer = Authorize.login(self, requireVolunteer=False)
    except:
      return    
  
    upcoming_events = list(_get_upcoming_events())[:MainPage.LIMIT]

    template_values = {
        'volunteer' : volunteer,
        'upcoming_events': upcoming_events,
      }
    path = os.path.join(os.path.dirname(__file__), '..', 'views', 'home', 'index.html')
    self.response.out.write(template.render(path, template_values))
