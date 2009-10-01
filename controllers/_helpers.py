import random

from models.neighborhood import Neighborhood
from models.interestcategory import InterestCategory
from models.eventvolunteer import EventVolunteer
from models.eventinterestcategory import EventInterestCategory
from models.volunteer import Volunteer
from models.event import Event
from models.application import Application
from models.applicationdomain import ApplicationDomain

from google.appengine.api import memcache

from controllers._utils import get_server, get_application

class SessionID():
  #TODO: Optimize random string generation
  def generate(self):
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    random_string = ''
    for count in xrange(1,64):
      random_string += random.sample(alphabet,1)[0]

    return random_string

class NeighborhoodHelper():
  def selected(self, selected_neighborhood):
    neighborhoods = []
    application = get_application()
    for neighborhood in application.neighborhoods.order('name').fetch(limit=500):
      if selected_neighborhood:
        if neighborhood.key().id() == selected_neighborhood.key().id():
          neighborhood.selected = True
      neighborhoods.append(neighborhood)
    return neighborhoods

#TODO: convert interest category helper to application-specific data model
class InterestCategoryHelper():
  def selected(self, selector):
    interestcategories = []
    for interestcategory in InterestCategory.all().order('name').fetch(limit=500):
      for sic in selector.interestcategories():
        if sic.key().id() == interestcategory.key().id():
          interestcategory.selected = True
      interestcategories.append(interestcategory)
    return interestcategories


APPLICATIONS = {
   'seattle': ['','seattle'],
   'los-angeles': ['la', 'los-angeles'],
   'tacoma': ['tacoma']
}
    
class InitializeStore():
      
  def init(self):
    if not self.is_initialized():
      self.initialize_store()

  def initialize_store(self):
    
    server = get_server()
    if server == 0:
        from gui_integration_tests.test_settings import host
        domains = [host]
        
    elif server == 1:
        domains = ['flashvolunteer-dev.appspot.com', 'development.flashvolunteer.org']
    else:
        domains = ['flashvolunteer.org']

    applications = {}
    
    for application, subdomains in APPLICATIONS.items():
        if Application().all().filter('name =', application).count() > 0: continue
        
        applications[application] = []
        for d in domains:
            for sd in subdomains:
                if sd == '':
                    applications[application].append(d)
                else: 
                    applications[application].append('%s.%s'%(sd,d))
    
    if Application.all().count() == 0:
        for app, qualified_domains in applications.items():
            a = Application(name = app)
            a.put()
            for domain in qualified_domains:
                d = ApplicationDomain(domain = domain, application = a)
                d.put()

    if InterestCategory.all().count() == 0:
        categories = ("Animals","Arts & Culture","Children & Youth", "Education & Literacy", 
                      "Environment", "Gay, Lesbian, Bi, & Transgender", "Homeless & Housing",
                      "Hunger", "Justice & Legal", "Senior Citizens")
        for category_name in categories:
          c = InterestCategory(name = category_name)
          c.put()  

  def is_initialized(self):
    return Application().all().count() == len(APPLICATIONS.keys())


