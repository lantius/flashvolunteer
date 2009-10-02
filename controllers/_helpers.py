import random

from models.neighborhood import Neighborhood
from models.interestcategory import InterestCategory
from models.eventvolunteer import EventVolunteer
from models.eventinterestcategory import EventInterestCategory
from models.volunteer import Volunteer
from models.event import Event

from controllers._utils import get_application

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
