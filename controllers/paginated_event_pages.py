import os

from google.appengine.ext.webapp import template

from models.neighborhood import Neighborhood
from models.interestcategory import InterestCategory

from controllers.events import _get_upcoming_events 

from controllers.abstract_handler import AbstractHandler

from controllers._utils import is_debugging, get_application, get_google_maps_api_key
from components.sessions import Session
from datetime import datetime

from models.volunteer import Volunteer

class BaseEventListPage(AbstractHandler):
    LIST_LIMIT = 12

    def set_context(self):  
        try:
            self.account = self.auth()
        except:
            return
        
        self.application = get_application()
        session = Session()

        bookmark_loc = self.request.get("bookmark", None)
        params = self.parameterize()
        
        if self.account: 
            if self.volunteerid:
                self.volunteer = Volunteer.get_by_id(self.volunteerid)
            else:
                self.volunteer = self.account.get_user()
            
        else: 
            self.volunteer = None



        first_page = not bookmark_loc or bookmark_loc == '-'
        if not first_page:
            bookmark = datetime.strptime(bookmark_loc, '%Y-%m-%d%H:%M:%S')              
            trace = session.get('events_pagination', None)
            if not trace or trace == []:
                session['events_pagination'] = [bookmark_loc]
                prev = '-'
            else:                
                if 'back' in params and params['back'] == '1':
                    prev = trace.pop() 
                    while prev >= bookmark_loc:
                        try:
                            prev = trace.pop()
                        except: 
                            prev = '-'
                            break
                else:
                    prev = trace[-1]
                    trace.append(bookmark_loc)

                session['events_pagination'] = trace
                
        else:
            prev = ''
            if 'events_pagination' in session:
                del session['events_pagination']
        
        if first_page:
            events = self._get_events(self.LIST_LIMIT + 1)
        else: 
            events = self._get_events(self.LIST_LIMIT, bookmark)

        if len(events) == self.LIST_LIMIT+1:
            next = events[-1].date.strftime('%Y-%m-%d%H:%M:%S')  
            events = events[:self.LIST_LIMIT]
        else:
            next = None
            
        template_values = { 
            'title' : self._get_title(),
            'volunteer' : self.volunteer,
            'events': events,
            'next': next,
            'prev': prev,
            'url': self._get_url()
        }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__),'..', 'views', 'events', 'paginated_event_page.html')
        self.response.out.write(template.render(path, template_values))




class PaginatedCategoryCompletedPage(BaseEventListPage):
    def get(self, categoryid):
        self.categoryid = int(categoryid)
        self.category = InterestCategory.get_by_id(self.categoryid)
        self.set_context()
        self.volunteerid = None

    def _get_events(self, limit, bookmark = None):
        qry = self.category.past_events()
        if bookmark:
            qry = qry.filter('date >=', bookmark)
        
        events = qry.fetch(limit)
        return events
              
    def _get_title(self):
        return '%s\'s Past Events'%self.category.name
    
    def _get_url(self):
        return '/events/past/category/%i'%self.categoryid


class PaginatedNeighborhoodCompletedPage(BaseEventListPage):
    def get(self, neighborhoodid):
        self.neighborhoodid = int(neighborhoodid)
        self.neighborhood = Neighborhood.get_by_id(self.neighborhoodid)
        self.set_context()
        self.volunteerid = None

    def _get_events(self, limit, bookmark = None):
        qry = self.neighborhood.events_past()
        if bookmark:
            qry = qry.filter('date >=', bookmark)
        
        events = qry.fetch(limit)
        return events
    
    def _get_title(self):
        return '%s\'s Completed Events'%self.neighborhood.name
    
    def _get_url(self):
        return '/events/past/neighborhood/%i'%self.neighborhoodid

class PaginatedVolunteerCompletedPage(BaseEventListPage):
    def get(self, volunteerid):
        self.volunteerid = int(volunteerid)
        self.set_context()

    def _get_events(self, limit, bookmark = None):
        qry = self.volunteer.events_past()
        if bookmark:
            qry = qry.filter('event_date >=', bookmark)
        
        events = [ev.event for ev in qry.fetch(limit)] 
        return events
    
    def _get_title(self):
        if self.account.get_user().key().id() == self.volunteerid:
            return 'My Completed Events'
        else:
            return '%s\'s Completed Events'%self.volunteer.name
    
    def _get_url(self):
        return '/events/past/volunteer/%i'%self.volunteerid
    
class PaginatedVolunteerCoordinatedCompletedPage(BaseEventListPage):
    def get(self, volunteerid):
        self.volunteerid = int(volunteerid)
        self.set_context()

    def _get_events(self, limit, bookmark = None):
        qry = self.volunteer.past_events_coordinated()
        if bookmark:
            qry = qry.filter('event_date >=', bookmark)
        
        events = [ev.event for ev in qry.fetch(limit)] 
        return events
    
    def _get_title(self):
        if self.account.get_user().key().id() == self.volunteerid:
            return 'Events I Coordinated'
        else:
            return '%s\'s Coordinated Events'%self.volunteer.name
    
    def _get_url(self):
        return '/events/past/coordinated/%i'%self.volunteerid

class PaginatedUpcomingPage(BaseEventListPage):
    def get(self):
        self.set_context()
        self.volunteerid = None

    def _get_events(self, limit, bookmark = None):
        qry = _get_upcoming_events()
        if bookmark:
            qry = qry.filter('date >=', bookmark)
        
        events = qry.fetch(limit)
        return events
              
    def _get_title(self):
        return 'Upcoming Events'
    
    def _get_url(self):
        return '/events/upcoming'
    
class PaginatedVolunteerUpcomingPage(BaseEventListPage):
    def get(self, volunteerid):
        self.volunteerid = int(volunteerid)
        self.set_context()

    def _get_events(self, limit, bookmark = None):
        qry = self.volunteer.events_future()
        if bookmark:
            qry = qry.filter('event_date >=', bookmark)
        
        events = [ev.event for ev in qry.fetch(limit)] 
        return events
       
    def _get_title(self):
        return '%s\'s Upcoming Events'%self.volunteer.name
    
    def _get_url(self):
        return '/events/upcoming/volunteer/%i'%self.volunteerid
    
class PaginatedVolunteerHostedPage(BaseEventListPage):
    def get(self, volunteerid):
        self.volunteerid = int(volunteerid)
        self.set_context()
          
    def _get_events(self, limit, bookmark = None):
        qry = self.volunteer.events_coordinating()
        if bookmark:
            qry = qry.filter('event_date >=', bookmark)
        
        events = [ev.event for ev in qry.fetch(limit)] 
        return events
        
    def _get_title(self):
        return 'Events %s is coordinating'%self.volunteer.name
    
    def _get_url(self):
        return '/events/hosted/volunteer/%i'%self.volunteerid


class PaginatedNeighborhoodUpcomingPage(BaseEventListPage):
    def get(self, neighborhoodid):
        self.neighborhoodid = int(neighborhoodid)
        self.neighborhood = Neighborhood.get_by_id(self.neighborhoodid)
        self.set_context()
        self.volunteerid = None
        
    def _get_events(self, limit, bookmark = None):
        qry = self.neighborhood.events_future().filter('application =', self.application)
        if bookmark:
            qry = qry.filter('date >=', bookmark)
        
        events = qry.fetch(limit)
        return events
              
    def _get_title(self):
        return '%s\'s Upcoming Events'%self.neighborhood.name
    
    def _get_url(self):
        return '/events/upcoming/neighborhood/%i'%self.neighborhoodid

class PaginatedCategoryUpcomingPage(BaseEventListPage):
    def get(self, categoryid):
        self.categoryid = int(categoryid)
        self.category = InterestCategory.get_by_id(self.categoryid)
        self.set_context()
        self.volunteerid = None

    def _get_events(self, limit, bookmark = None):
        qry = self.category.upcoming_events().filter('application =', self.application)
        if bookmark:
            qry = qry.filter('date >=', bookmark)
        
        events = [eic.event for eic in qry][:limit] 
        return events
    
    def _get_title(self):
        return '%s\'s Upcoming Events'%self.category.name
    
    def _get_url(self):
        return '/events/upcoming/category/%i'%self.categoryid

class PaginatedRecommendedPage(BaseEventListPage):
    def get(self):
        self.set_context()
        self.volunteerid = None

    def _get_events(self, bookmark = None):
        return [e for e in self.volunteer.recommended_events()
                if (bookmark is None or e.date > bookmark) and e.application.key().id() == self.application.key().id()][:self.LIST_LIMIT + 1]
    
    def _get_title(self):
        return 'Recommended Events'
    
    def _get_url(self):
        return '/events/recommended'
