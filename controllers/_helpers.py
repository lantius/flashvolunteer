from models import Volunteer, Event, Neighborhood, InterestCategory

class NeighborhoodHelper():
  def selected(self, selected_neighborhood):
    neighborhoods = []
    for neighborhood in Neighborhood.all():
      if selected_neighborhood and neighborhood.key().id() == selected_neighborhood.key().id():
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