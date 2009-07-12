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

################################################################################
# MainPage
class MainPage(webapp.RequestHandler):
  LIMIT = 12 
  def get(self):
    try:
      volunteer = Authorize.login(self, requireVolunteer=False)
    except:
      return
    
    # if volunteer is logged in, then they get their login page
    # otherwise, they get the splash page
    
    if not volunteer:
      self.splashpage()
    else:
      self.homepage(volunteer)

  ################################################################################
  # splashpage
  def splashpage(self):
    
    login_url = users.create_login_url(self.request.uri)      
    account_url = users.create_login_url('/settings')
    
    template_values = { 
      'login_url' : login_url,
      'account_url' : account_url
    }
    path = os.path.join(os.path.dirname(__file__), '..', 'views', 'home', 'splash.html')
    self.response.out.write(template.render(path, template_values))

  ################################################################################
  # homepage
  def homepage(self, volunteer):
    events = { 'Your events' : volunteer.events() }
    byinterest = []
    
    if volunteer.home_neighborhood:
      events['Neighborhood events'] = volunteer.home_neighborhood.events
    
    for ic in volunteer.interestcategories():
      if ic.events():
        byinterest.append(ic)
  
    my_future_events = volunteer.events_future()[:MainPage.LIMIT]
    template_values = {
        'volunteer' : volunteer,
        'neighborhoods': NeighborhoodHelper().selected(volunteer.home_neighborhood),
        'my_future_events': my_future_events,
        'interest_categories': InterestCategory.all()
      }
    path = os.path.join(os.path.dirname(__file__), '..', 'views', 'home', 'index.html')
    self.response.out.write(template.render(path, template_values))


    



