import random

from models.neighborhood import Neighborhood
from models.interestcategory import InterestCategory
from models.eventvolunteer import EventVolunteer
from models.eventinterestcategory import EventInterestCategory
from models.volunteer import Volunteer
from models.event import Event

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
    for neighborhood in Neighborhood.all().order('name').fetch(limit=500):
      if selected_neighborhood:
        if neighborhood.key().id() == selected_neighborhood.key().id():
          neighborhood.selected = True
      neighborhoods.append(neighborhood)
    return neighborhoods

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
    else:
      self.migrate_store()
    

  def initialize_store(self):

    
    neighborhoods = (
      'Ballard','Beacon Hill','Belltown','Capitol Hill','Central District',
      'Downtown','Fremont','Georgetown','Green Lake',
      'Greenwood','International District', 'Bitter Lake','Lake City',
      'Leschi','Madison Park','Madrona','Magnolia','Maple Leaf',
      'Northgate','Phinney Ridge','Queen Anne','Rainier Valley',
      'Ravenna','Sand Point',
      'Lake Union','South Park','University District','Wallingford',
      'Wedgwood','West Seattle','Delridge','Rainier Beach', 
                       'Shoreline',
                        'Edmonds',
                        'Lynnwood',
                        'Bothell',
                        'Kirkland',
                        'Redmond',
                        'Bellevue',
                        'Mercer Island',
                        'Tukwila',
                        'Burien',
                        'White Center',
                        'Bainbridge Island',)
    
          
          
    for neighborhood_name in neighborhoods:
      n = Neighborhood(name=neighborhood_name)
      n.put()

    categories = ("Animals","Arts & Culture","Children & Youth", "Education & Literacy", 
                  "Environment", "Gay, Lesbian, Bi, & Transgender", "Homeless & Housing",
                  "Hunger", "Justice & Legal", "Senior Citizens")
    for category_name in categories:
      c = InterestCategory(name = category_name)
      c.put()  

  def is_initialized(self):
    n = Neighborhood.gql("WHERE name = :name", name = "Capitol Hill").get()
    if n:
      return True

    return False

  def migrate_store(self):

      def migrate_neighborhoods():
          #neighborhoods to add
          new_hoods = []

          hoods = {}
          for n in Neighborhood.all():
              hoods[n.name] = n
              
                        
          for n in new_hoods:
              if not n in hoods:
                  hood = Neighborhood(name = n)
                  hood.put()
                  hoods[n] = hood
                  
          #neighborhood transformations; 
          #### From : To
          n_map =  {
                   #'South Lake Union': 'Lake Union',
                   }     
              
          for v in Volunteer.all():
              if v.work_neighborhood and v.work_neighborhood.name in n_map:
                  v.work_neighborhood = hoods[n_map[v.work_neighborhood.name]]
                  v.put()
              if v.home_neighborhood and v.home_neighborhood.name in n_map:
                  v.home_neighborhood = hoods[n_map[v.home_neighborhood.name]]
                  v.put()
                  
          for e in Event.all():
              if e.neighborhood and e.neighborhood.name in n_map:
                  e.neighborhood = hoods[n_map[e.neighborhood.name]]
                  e.put()
                  
          #neighborhoods to delete
          hoods_to_remove = []      
          for n in hoods_to_remove:
              if n in hoods:
                  hoods[n].delete()  
              
      def clear_stale_events():
          for ev in EventVolunteer.all():
              try:
                  event = ev.event
              except:
                  ev.delete()
                  
          for ec in EventInterestCategory.all():
              try:
                  event = ec.event
              except:
                  ec.delete()
                  
      pass