from models.neighborhood import *
from models.interestcategory import *

class NeighborhoodHelper():
  def selected(self, selected_neighborhood):
    neighborhoods = []
    for neighborhood in Neighborhood.all():
      if selected_neighborhood:
        if neighborhood.key().id() == selected_neighborhood.key().id():
          neighborhood.selected = True
      neighborhoods.append(neighborhood)
    return neighborhoods

class InterestCategoryHelper():
  def selected(self, selector):
    interestcategories = []
    for interestcategory in InterestCategory.all():
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
    neighborhoods = (
      'Ballard','Beacon Hill','Belltown','Capitol Hill','Central District/ Madison Valley',
      'Columbia City','Downtown','Eastlake','First Hill','Fremont','Georgetown','Green Lake',
      'Greenwood','Interbay','International District','Haller Lake/ Bitter Lake','Lake City',
      'Laurelhurst','Leschi','Madison Park','Madrona','Magnolia','Maple Leaf','Montlake',
      'Mount Baker','Northgate','Phinney Ridge','Pioneer Square','Queen Anne','Rainier Valley',
      'Ravenna','Roosevelt','Sand Point','Seattle Center / Lower Queen Anne','SoDo',
      'South Lake Union','South Park','University District','View Ridge','Wallingford',
      'Wedgwood','West Seattle')
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
