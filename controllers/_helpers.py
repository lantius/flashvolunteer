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


class InitializeStore():
      
  def init(self):
    if not self.is_initialized():
      self.initialize_store()

  def initialize_store(self):

    
#    neighborhoods = (
#      'Ballard','Beacon Hill','Belltown','Capitol Hill','Central District',
#      'Downtown','Fremont','Georgetown','Green Lake',
#      'Greenwood','International District', 'Bitter Lake','Lake City',
#      'Leschi','Madison Park','Madrona','Magnolia','Maple Leaf',
#      'Northgate','Phinney Ridge','Queen Anne','Rainier Valley',
#      'Ravenna','Sand Point',
#      'Lake Union','South Park','University District','Wallingford',
#      'Wedgwood','West Seattle','Delridge','Rainier Beach', 
#                       'Shoreline',
#                        'Edmonds',
#                        'Lynnwood',
#                        'Bothell',
#                        'Kirkland',
#                        'Redmond',
#                        'Bellevue',
#                        'Mercer Island',
#                        'Tukwila',
#                        'Burien',
#                        'White Center',
#                        'Bainbridge Island',)
#    
#          
#          
#    for neighborhood_name in neighborhoods:
#      n = Neighborhood(name=neighborhood_name)
#      n.put()    
    
    
    server = get_server()
    if server == 0:
        #TODO: generalize this
        domain = 'localhost:9999'
    elif server == 1:
        domain = 'flashvolunteer-dev.appspot.com'
    else:
        domain = 'flashvolunteer.org'
        
    applications = {
       'seattle': (domain, 'seattle.%s'%domain), 
       'los-angeles': ('la.%s'%domain, 'los-angeles.%s'%domain),
       'tacoma': ('tacoma.%s'%domain,),
    }
    
    if Application.all().count() == 0:
        for app, domains in applications.items():
            a = Application(name = app)
            a.put()
            for domain in domains:
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
    return Application().all().count() > 0


