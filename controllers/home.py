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
  
  def get(self):
    try:
      (user, volunteer) = Authorize.login(self, requireUser=False, requireVolunteer=False)
    except:
      return
    
    # if user is logged in, then they get their login page
    # otherwise, they get the splash page
    
    if not volunteer:
      self.splashpage()
    else:
      self.homepage(volunteer)

  ################################################################################
  # splashpage
  def splashpage(self):
    
    login_url = users.create_login_url(self.request.uri)      
    
    template_values = { 
      'login_url' : login_url 
    }
    path = os.path.join(os.path.dirname(__file__), '..', 'views', 'home', 'splash.html')
    self.response.out.write(template.render(path, template_values))

  ################################################################################
  # homepage
  def homepage(self, volunteer):
    events = { 'Your events' : volunteer.events() }
    byinterest = None
    
    if volunteer.home_neighborhood:
      events['Neighborhood events'] = volunteer.home_neighborhood.events
      home_neighborhood = volunteer.home_neighborhood
    
    for ic in volunteer.interestcategories():
      if ic.events():
        byinterest.append(ic)
  
    logout_url = users.create_logout_url(self.request.uri)
    template_values = {
        'logout_url': logout_url,
        'volunteer' : volunteer,
        'neighborhoods': NeighborhoodHelper().selected(home_neighborhood),
      }
    path = os.path.join(os.path.dirname(__file__), '..', 'views', 'home', 'index.html')
    self.response.out.write(template.render(path, template_values))


    



