import os, logging
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template
from models.volunteer import Volunteer
from google.appengine.ext.db import Key

from controllers.abstract_handler import AbstractHandler

# AdminPage
class NewUsersPage(AbstractHandler):
    def get(self):
        try:
            volunteer = self.auth(require_login=True, require_admin = True)
        except:
            return   

        application = self.get_application()
        (volunteers, prev, next) = self.do_search()
        
        template_values = {
            'volunteer' : volunteer,
            'volunteers' : volunteers,
            'prev' : prev,
            'next' : next
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__), '..', '..', 'views', 'admin', 'newusers.html')
        self.response.out.write(template.render(path, template_values))
        
    def do_search(self):
        SEARCH_LIST = 25
        session = self._session()
        application = self.get_application()
        volunteers_query = Volunteer.all().filter('applications =', application.key().id()).order('__key__')
        
        bookmark = self.request.get("bookmark", None)
        if bookmark and bookmark != '-':
            volunteers_query = volunteers_query.filter('__key__ >=', Key(encoded=bookmark))
            
            trace = session.get('volunteers_search_prev', None)
            if not trace or trace == []:
                session['volunteers_search_prev'] = [bookmark]
                prev = '-'
            else:                
                isBack = self.request.get("back", None)
                if isBack and isBack == '1':
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
                    
                session['volunteers_search_prev'] = trace
                
        else:
            if 'volunteers_search_prev' in session:
                del session['volunteers_search_prev']
                    
            prev = ''
        
        volunteers = volunteers_query.fetch(limit = SEARCH_LIST + 1)

        if len(volunteers) == SEARCH_LIST+1:
            next = volunteers[-1].key()
            volunteers = volunteers[:SEARCH_LIST]
        else:
            next = None
            
        return (volunteers, prev, next)
