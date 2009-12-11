from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os, random

from google.appengine.ext.db import Key

from models.interestcategory import InterestCategory
from models.neighborhood import Neighborhood
from models.volunteer import Volunteer
from models.event import Event

from controllers.abstract_handler import AbstractHandler

from controllers._utils import is_debugging, get_application
from components.sessions import Session

class BaseVolunteerListPage(AbstractHandler):
    LIST_LIMIT = 12
    
    def set_context(self):  
        try:
            self.account = self.auth(require_login=True)
        except:
            return
        
        self.application = get_application()
        session = Session()
        
        bookmark = self.request.get("bookmark", None)
        params = self.parameterize()
        
        if self.account: self.volunteer = self.account.get_user()
        else: self.volunteer = None
         
        first_page = not bookmark or bookmark == '-'
        if not first_page:
            trace = session.get('vol_pagination', None)
            if not trace or trace == []:
                session['vol_pagination'] = [bookmark]
                prev = '-'
            else:                
                if 'back' in params and params['back'] == '1':
                    prev = trace.pop() 
                    while prev >= bookmark:
                        try:
                            prev = trace.pop()
                        except: 
                            prev = '-'
                            break
                else:
                    prev = trace[-1]
                    trace.append(bookmark)
    
                session['vol_pagination'] = trace
                
        else:
            prev = ''
            if 'vol_pagination' in session:
                del session['vol_pagination']
            bookmark = None
      
      
      
      
        if bookmark:
            volunteers = self._get_volunteers(self.LIST_LIMIT + 1, Key(bookmark))
        else:
            volunteers = self._get_volunteers(self.LIST_LIMIT + 1)

        if len(volunteers) == self.LIST_LIMIT + 1:
            next = volunteers[-1].key() 
            volunteers = volunteers[:self.LIST_LIMIT]
        else:
            next = None
                     
        template_values = { 
                            'title' : self._get_title(),
                            'volunteer' : self.volunteer,
                            'team': volunteers,
                            'next': next,
                            'prev': prev,
                            'url': self._get_url()
                            }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__),'..', 'views', 'volunteers', 'person_lists', '_paginated_volunteer_page.html')
        self.response.out.write(template.render(path, template_values))

    
class PaginatedTeamPage(BaseVolunteerListPage):
  
    def get(self):
        self.set_context()
          
    def _get_volunteers(self, limit, bookmark = None):
        vols = [vf.follows.get_user() for vf in self.account.following.fetch(limit=1000)]
        if bookmark:
            vols = [v for v in vols if v.key() >= bookmark]                      
        vols.sort(lambda a,b: cmp(a.key(),b.key()))

        return vols[:limit]
    
    def _get_title(self):
        return 'My FlashTeam'
    
    def _get_url(self):
        return '/team/list'
 
 
class PaginatedVolunteerCategoryPage(BaseVolunteerListPage):
  
  def get(self, category_id):
      self.category = InterestCategory.get_by_id(int(category_id))
      if not self.category:
          self.error(404)
          self.response.out.write('404 page! boo!')

      self.set_context()

  def _get_volunteers(self, limit, bookmark = None):
     qry = self.category.user_interests.order('__key__')
     if bookmark: 
         qry = qry.filter('__key__ >=', bookmark)
     return [i.account for i in qry.fetch(limit)]  
         
  def _get_title(self):
     return 'Interested in %s'%self.category.name
 
  def _get_url(self):
     return '/category/%i/volunteers'%self.category.key().id()

class PaginatedNeighborhoodVolunteerWorkPage(BaseVolunteerListPage):
  
  def get(self, neighborhood_id):
      self.neighborhood = Neighborhood.get_by_id(int(neighborhood_id))
      if not self.neighborhood:
          self.error(404)
          self.response.out.write('404 page! boo!')

      self.set_context()

  def _get_volunteers(self, limit, bookmark = None):
     qry = self.neighborhood.work_neighborhood.order('__key__')
     if bookmark: 
         qry = qry.filter('__key__ >=', bookmark)
     return [v for v in qry.fetch(limit)]
         
  def _get_title(self):
     return 'Working in %s'%self.neighborhood.name
 
  def _get_url(self):
     return '/neighborhoods/%i/volunteers_work/'%self.neighborhood.key().id()

class PaginatedNeighborhoodVolunteerHomePage(BaseVolunteerListPage):
  
  def get(self, neighborhood_id):
      self.neighborhood = Neighborhood.get_by_id(int(neighborhood_id))
      if not self.neighborhood:
          self.error(404)
          self.response.out.write('404 page! boo!')

      self.set_context()

  def _get_volunteers(self, limit, bookmark = None):
     qry = self.neighborhood.home_neighborhood.order('__key__')
     if bookmark: 
         qry = qry.filter('__key__ >=', bookmark)
     return [v for v in qry.fetch(limit)]
 
  def _get_title(self):
     return 'Living in %s'%self.neighborhood.name
 
  def _get_url(self):
     return '/neighborhoods/%i/volunteers_home'%self.neighborhood.key().id()

class PaginatedVolunteerTeam(BaseVolunteerListPage):
  
  def get(self, volunteer_id):
      self.page_volunteer = Volunteer.get_by_id(int(volunteer_id))
      if not self.page_volunteer:
          self.error(404)
          self.response.out.write('404 page! boo!')

      self.set_context()

  def _get_volunteers(self, limit, bookmark = None):
        vols = [vf.follows.get_user() for vf in self.account.following.fetch(limit=1000)]
        if bookmark:
            vols = [v for v in vols if v.key() >= bookmark]                      
        vols.sort(lambda a,b: cmp(a.key(),b.key()))
        
  def _get_title(self):
     return '%s\'s FlashTeam'%self.page_volunteer.name
 
  def _get_url(self):
     return '/volunteers/%i/team'%self.page_volunteer.key().id()

    
class PaginatedEventAttendeesPage(BaseVolunteerListPage):
  
    def get(self, event_id):
        self.event = Event.get_by_id(int(event_id))
        if not self.event:
            self.error(404)
            self.response.out.write('404 page! boo!')
    
        self.set_context()
    
    def _get_volunteers(self, limit, bookmark = None):
        eventvolunteer = self.event.eventvolunteers.filter('volunteer =', self.volunteer).get() 
    
        qry = self.event.eventvolunteers.order('__key__')
        if bookmark: qry = qry.filter('__key__ >=', bookmark)
                     
        if eventvolunteer and (eventvolunteer.isowner or self.event.in_past): 
            return list(qry.fetch(limit))
        else:
            results = []
            for v in qry.fetch(limit):
                if v.event_access(account=self.account):
                    results.append(v)
                    if len(results) >= limit:
                        break
            return results
 
    def _get_title(self):
        return '%s\'s Attendees'%self.event.name
    
    def _get_url(self):
        return '/events/%i/attendees'%self.event.key().id()