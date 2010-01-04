from google.appengine.api import urlfetch
from django.utils import simplejson
import urllib, os

from components.sessions import Session
from controllers._utils import get_server, get_application, is_debugging
from controllers.abstract_handler import AbstractHandler
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext.webapp import template

from models.afg_opportunity import AFGOpportunity

import datetime

class AccessAllForGood(AbstractHandler):

    def get(self):
        
        SEARCH_RESULTS = 50
        
        url = 'http://www.allforgood.org/api/volopps?vol_loc=Seattle,WA&output=json&key=flashvolunteer&num=%i'%SEARCH_RESULTS
        r = urlfetch.fetch(url=url)
        opportunities = simplejson.loads(r.content)     
        
        current_opps = dict([(co.afg_id,1) for co in AFGOpportunity.all()])
        
        added = 0
        existed = 0
        skipped = 0
        for o in opportunities['items']:
            if o['id'] in current_opps: 
                existed += 1
                continue

            try:
                new_op = AFGOpportunity(
                            afg_id = o['id'],
                            startdate = datetime.datetime.strptime(
                               o['startDate'], "%Y-%m-%d %H:%M:%S"
                               ),
                            enddate = datetime.datetime.strptime(
                               o['endDate'], "%Y-%m-%d %H:%M:%S"
                               ),
                            
                            title = o['title'],
                            provider = o['provider'],
                            description = o['description'],
                            contact_email = o['contactEmail'],
                            skills = o['skills'],
                            url = o['xml_url'],
                            location = o['location_name']
                        )
                new_op.score = self._score_opportunity(new_op)
                new_op.put()  
                added += 1              
            except Exception, e:
                skipped += 1
                print 'title: ', o['title']
                print 'location: ', o['location_name']
                print 'contact: ', o['contactEmail']
            

        print 'added %i\nexisted already %i\nskipped %i'%(added, existed, skipped)

    def _score_opportunity(self, op):
        score = -1
        #+1 for coming from a high-quality provider (i.e United Way (Volunteer Solutions portal), Seattle Works (Hands On Network)
        #+2 for a complete, valid address
        #+2 for date range < 1 day; +1 for date range < 1 week
        #+1 for non-empty description
        #-3 for "virtual" being True
        #+1 for contact email 
    
        return score
        
        
class PublishFromAllForGood(AbstractHandler):

    def get(self):
        self.list()


    def list(self): 
        try:
            account = self.auth()
        except:
            return
        
        opportunities = sorted(AFGOpportunity.all().filter('status =', None).fetch(limit=500),lambda a,b:int(a.score-b.score),reverse=True)
            
        template_values = {
            'volunteer': account.get_user(),
            'opportunities': opportunities,
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__),'..', '..', 'views', 'admin', 'afg_publish.html')
        self.response.out.write(template.render(path, template_values, debug=is_debugging()))

    
    def post(self):
        pass
        