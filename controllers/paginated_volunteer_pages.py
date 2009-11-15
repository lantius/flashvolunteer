from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os, random


from models.interestcategory import InterestCategory
from models.neighborhood import Neighborhood
from models.volunteer import Volunteer
from models.event import Event

from controllers.abstract_handler import AbstractHandler

class BaseVolunteerListPage(AbstractHandler):
  LIST_LIMIT = 12
    
  def set_context(self):  
    try:
      self.account = self.auth(require_login=True)
    except:
      return

    if self.account: self.volunteer = self.account.get_user()
    else: self.volunteer = None
    
    LIST_LIMIT = BaseVolunteerListPage.LIST_LIMIT
    
    page = self.page
    generator, extract_style = self._get_volunteer_generator()
    
    start = (page-1) * LIST_LIMIT + 1
    offset = start - 1 
    if isinstance(generator, list):
        total = len(generator)
        
        if extract_style == 'direct':
            volunteers = generator[offset:offset+LIST_LIMIT]      
        else:
            volunteers = [ev.volunteer for ev in generator[offset:offset+LIST_LIMIT]]      

    else:
        total = generator.count()
        
        if extract_style == 'direct':
            volunteers = [ev for ev in generator.fetch(limit = LIST_LIMIT, offset = offset)]        
        else:
            volunteers = [ev.volunteer for ev in generator.fetch(limit = LIST_LIMIT, offset = offset)]
    
    end = start + len(volunteers) - 1
                                                
    if end == total:
        next_page = -1
    else: 
        next_page = page + 1
    
    if page == 1:
        prev_page = -1
    else:
        prev_page = page -1
        
    template_values = { 
                        'title' : self._get_title(),
                        'volunteer' : self.volunteer,
                        'team': volunteers,
                        'total': total,
                        'start': start,
                        'end': end,
                        'next_page': next_page,
                        'prev_page': prev_page,
                        'url': self._get_url()
                        }
    self._add_base_template_values(vals = template_values)
    
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'volunteers', 'person_lists', '_paginated_volunteer_page.html')
    self.response.out.write(template.render(path, template_values))

    
class PaginatedTeamPage(BaseVolunteerListPage):
  
  def get(self, page):
      self.page = int(page)
      self.set_context()
        
  def _get_volunteer_generator(self):
     return (list(self.volunteer.friends()) + list(self.volunteer.following_only()), 'direct')
 
  def _get_title(self):
     return 'My FlashTeam'
 
  def _get_url(self):
     return '/team/'
 
 
class PaginatedVolunteerCategoryPage(BaseVolunteerListPage):
  
  def get(self, category_id, page):
      self.page = int(page)
      self.category = InterestCategory.get_by_id(int(category_id))
      if not self.category:
          self.error(404)
          self.response.out.write('404 page! boo!')

      self.set_context()
        
  def _get_volunteer_generator(self):
     return (self.category.user_interests, 'indirect')
 
  def _get_title(self):
     return 'Interested in %s'%self.category.name
 
  def _get_url(self):
     return '/category/%i/volunteers/'%self.category.key().id()

class PaginatedNeighborhoodVolunteerWorkPage(BaseVolunteerListPage):
  
  def get(self, neighborhood_id, page):
      self.page = int(page)
      self.neighborhood = Neighborhood.get_by_id(int(neighborhood_id))
      if not self.neighborhood:
          self.error(404)
          self.response.out.write('404 page! boo!')

      self.set_context()
        
  def _get_volunteer_generator(self):
     return (self.neighborhood.work_neighborhood, 'direct')
 
  def _get_title(self):
     return 'Working in %s'%self.neighborhood.name
 
  def _get_url(self):
     return '/neighborhoods/%i/volunteers_work/'%self.neighborhood.key().id()

class PaginatedNeighborhoodVolunteerHomePage(BaseVolunteerListPage):
  
  def get(self, neighborhood_id, page):
      self.page = int(page)
      self.neighborhood = Neighborhood.get_by_id(int(neighborhood_id))
      if not self.neighborhood:
          self.error(404)
          self.response.out.write('404 page! boo!')

      self.set_context()
        
  def _get_volunteer_generator(self):
     return (self.neighborhood.home_neighborhood, 'direct')
 
  def _get_title(self):
     return 'Living in %s'%self.neighborhood.name
 
  def _get_url(self):
     return '/neighborhoods/%i/volunteers_home/'%self.neighborhood.key().id()

class PaginatedVolunteerTeam(BaseVolunteerListPage):
  
  def get(self, volunteer_id, page):
      self.page = int(page)
      self.page_volunteer = Volunteer.get_by_id(int(volunteer_id))
      if not self.page_volunteer:
          self.error(404)
          self.response.out.write('404 page! boo!')

      self.set_context()
        
  def _get_volunteer_generator(self):
     return (self.page_volunteer.volunteerfollowing, 'indirect')
 
  def _get_title(self):
     return '%s\'s FlashTeam'%self.page_volunteer.name
 
  def _get_url(self):
     return '/volunteers/%i/team/'%self.page_volunteer.key().id()

    
class PaginatedEventAttendeesPage(BaseVolunteerListPage):
  
  def get(self, event_id, page):
      self.page = int(page)
      self.event = Event.get_by_id(int(event_id))
      if not self.event:
          self.error(404)
          self.response.out.write('404 page! boo!')

      self.set_context()
        
  def _get_volunteer_generator(self):
      
     eventvolunteer = self.event.eventvolunteers.filter('volunteer =', self.volunteer).get() 
                                             
     if eventvolunteer and (eventvolunteer.isowner or self.event.inpast()): 
        return (self.event.eventvolunteers,'indirect')        

     return ([v for v in self.event.volunteers() \
              if v.event_access(account=self.account) and \
                 v.key().id() != self.volunteer.key().id()],
            'direct')
 
  def _get_title(self):
     return '%s\'s Attendees'%self.event.name
 
  def _get_url(self):
     return '/events/%i/attendees/'%self.event.key().id()