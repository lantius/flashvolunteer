import os

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template

from models.volunteer import Volunteer
from models.event import Event
from models.eventvolunteer import EventVolunteer
from models.neighborhood import Neighborhood
from models.eventinterestcategory import EventInterestCategory
from models.interestcategory import InterestCategory

from controllers._auth import Authorize
from controllers._params import Parameters

from controllers.events import _get_recommended_events, _get_upcoming_events 

class BaseEventListPage(webapp.RequestHandler):
  LIST_LIMIT = 12
    
  def set_context(self):  
    try:
      self.volunteer = Authorize.login(self, requireVolunteer=False)
    except:
      return
    
    LIST_LIMIT = BaseEventListPage.LIST_LIMIT

    page = self.page
    item_list, extract_style = self._get_event_generator()
    
    
    start = (page-1) * LIST_LIMIT + 1
    offset = start - 1 
    if isinstance(item_list, list):
        total = len(item_list)
        
        if extract_style == 'direct':
            events = item_list[offset:offset+LIST_LIMIT]      
        else:
            events = [e.event for e in item_list[offset:offset+LIST_LIMIT]]      

    else:
        #total = generator.count()
        
        if extract_style == 'direct':
            events = [e for e in item_list.fetch(limit = LIST_LIMIT, offset = offset)]        
        else:
            events = item_list.fetch(limit = LIST_LIMIT, offset = offset)
        
    
    end = start + len(events) - 1
                                                
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
                        'events': events,
                        'total': total,
                        'start': start,
                        'end': end,
                        'next_page': next_page,
                        'prev_page': prev_page,
                        'url': self._get_url()
                        }
    
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'events', 'paginated_event_page.html')
    self.response.out.write(template.render(path, template_values))

class PaginatedUpcomingPage(BaseEventListPage):
  
  def get(self, page):
      self.page = int(page)
      self.set_context()
        
  def _get_event_generator(self):
     return (_get_upcoming_events(), 'generator')
 
  def _get_title(self):
     return 'Upcoming Events'
 
  def _get_url(self):
     return '/events/upcoming/'
 
 
class PaginatedRecommendedPage(BaseEventListPage):
  def get(self, page):
      self.page = int(page)
      self.set_context()
        
  def _get_event_generator(self):
     return (list(_get_recommended_events(volunteer = self.volunteer)), 'direct')
 
  def _get_title(self):
     return 'Recommended Events'
 
  def _get_url(self):
     return '/events/recommended/'


class PaginatedVolunteerCompletedPage(BaseEventListPage):
  def get(self, volunteerid, page):
      self.page = int(page)
      self.volunteerid = int(volunteerid)
      self.set_context()
        
  def _get_event_generator(self):
     return (self.volunteer.events_past(), 'direct')
 
  def _get_title(self):
     if self.volunteer.key().id() == self.volunteerid:
         return 'My Completed Events'
     else:
         return '%s\'s Completed Events'%self.volunteer.name
 
  def _get_url(self):
     return '/events/past/volunteer/%i/'%self.volunteerid


class PaginatedCategoryCompletedPage(BaseEventListPage):
  def get(self, categoryid, page):
      self.page = int(page)
      self.categoryid = int(categoryid)
      self.category = InterestCategory.get_by_id(self.categoryid)
      self.set_context()
        
  def _get_event_generator(self):
     return (list(self.category.past_events()), 'direct')
 
  def _get_title(self):
     return '%s\'s Past Events'%self.category.name
 
  def _get_url(self):
     return '/events/past/category/%i/'%self.categoryid


class PaginatedNeighborhoodCompletedPage(BaseEventListPage):
  def get(self, neighborhoodid, page):
      self.page = int(page)
      self.neighborhoodid = int(neighborhoodid)
      self.neighborhood = Neighborhood.get_by_id(self.neighborhoodid)
      self.set_context()
        
  def _get_event_generator(self):
     return (self.neighborhood.events_past(), 'direct')
 
  def _get_title(self):
     return '%s\'s Completed Events'%self.neighborhood.name
 
  def _get_url(self):
     return '/events/past/neighborhood/%i/'%self.neighborhoodid


class PaginatedVolunteerUpcomingPage(BaseEventListPage):
  def get(self, volunteerid, page):
      self.page = int(page)
      self.volunteerid = int(volunteerid)
      self.set_context()
        
  def _get_event_generator(self):
     return (self.volunteer.events_future(), 'direct')
 
  def _get_title(self):
     return '%s\'s Upcoming Events'%self.volunteer.name
 
  def _get_url(self):
     return '/events/upcoming/volunteer/%i/'%self.volunteerid
 
class PaginatedVolunteerHostedPage(BaseEventListPage):
  def get(self, volunteerid, page):
      self.page = int(page)
      self.volunteerid = int(volunteerid)
      self.set_context()
        
  def _get_event_generator(self):
     return (self.volunteer.events_coordinating(), 'direct')
 
  def _get_title(self):
     return 'Events %s is coordinating'%self.volunteer.name
 
  def _get_url(self):
     return '/events/hosted/volunteer/%i/'%self.volunteerid



class PaginatedNeighborhoodUpcomingPage(BaseEventListPage):
  def get(self, neighborhoodid, page):
      self.page = int(page)
      self.neighborhoodid = int(neighborhoodid)
      self.neighborhood = Neighborhood.get_by_id(self.neighborhoodid)
      self.set_context()
        
  def _get_event_generator(self):
     return (self.neighborhood.events_future(), 'direct')
 
  def _get_title(self):
     return '%s\'s Upcoming Events'%self.neighborhood.name
 
  def _get_url(self):
     return '/events/upcoming/neighborhood/%i/'%self.neighborhoodid

class PaginatedCategoryUpcomingPage(BaseEventListPage):
  def get(self, categoryid, page):
      self.page = int(page)
      self.categoryid = int(categoryid)
      self.category = InterestCategory.get_by_id(self.categoryid)
      self.set_context()
        
  def _get_event_generator(self):
     return (list(self.category.upcoming_events()), 'direct')
 
  def _get_title(self):
     return '%s\'s Upcoming Events'%self.category.name
 
  def _get_url(self):
     return '/events/upcoming/category/%i/'%self.categoryid