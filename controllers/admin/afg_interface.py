from google.appengine.api import urlfetch
from django.utils import simplejson
import urllib, os

from components.sessions import Session
from controllers._utils import get_server, get_application, is_debugging, get_neighborhood
from controllers.abstract_handler import AbstractHandler
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext.webapp import template

from models.afg_opportunity import AFGOpportunity

import datetime

class AllForGoodInterface(AbstractHandler):

    def get(self, urldata = None):
        
        if not urldata:
            self.list()
        elif urldata == '/publish':
            params = self.parameterize() 
            afg_id = params['id']
            opp = AFGOpportunity.all().filter('afg_id =', afg_id).get()            
            self.publish(opportunity = opp)
        elif urldata == '/rebuild':
            self.rebuild()
            self.redirect('/admin/afg_interface')

    def list(self): 
        try:
            account = self.auth(require_login = True)
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

    
    def post(self, urldata = None):
        params = self.parameterize() 
        afg_id = params['id']
        if urldata == '/dismiss':
            opp = AFGOpportunity.all().filter('afg_id =', afg_id).get()
            opp.status = False
            opp.put()
        elif urldata == '/publish':
            ##TODO
            opp.status = True
            #opp.fv_event = event
            opp.put()
        
    #much of this code is derived from controllers.events.edit
    def publish(self, opportunity):
        from models.event import Event
        from models.interestcategory import InterestCategory
        from controllers._helpers import NeighborhoodHelper
        
        try:
            account = self.auth(require_login=True)
        except:
            return   

        opp = opportunity 
        
        event = Event(
            application = get_application(),
            name = opp.title,
            description = opp.description, #TODO: make sure to pull down full desc
            enddate = opp.enddate,
            date = opp.startdate,
            special_instructions = opp.skills,
            neighborhood = get_neighborhood(opp.location), 
            address = opp.location
            #TODO: need to add event host
        )

    
        template_values = { 
            'event' : event, 
            'volunteer': account.get_user(), 
            'neighborhoods': NeighborhoodHelper().selected(event.neighborhood),
            'interestcategories' : InterestCategory.all().order('name').fetch(limit=500),
        }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__),'..', '..', 'views', 'events', 'event_edit.html')
        self.response.out.write(template.render(path, template_values, debug=is_debugging()))

        
    def rebuild(self):
        
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

    def _score_opportunity(self, opp):
        score = 0
        
        #+1 for coming from a high-quality provider (i.e United Way (Volunteer Solutions portal), Seattle Works (Hands On Network)
        if opp.provider in ['unitedway', 'handsonnetwork']:
            score += 2
        if get_neighborhood(opp.location) is not None:
            score += 2
        
        try:
            rng = opp.enddate - opp.startdate
            tot = rng.days * 24*60*60 + rng.seconds
            if tot > 0:
                if tot < 1440*60:
                    #less than a day range
                    score += 3
                elif tot < 10080*60:
                    #less than a week range
                    score += 2
            else:
                score += 1

        except:
            pass
        
        if len(opp.description) > 5:
            score += 2

        if len(opp.contact_email) > 1:
            score += 1
            
        if len(opp.url) > 4:
            score += 1
    
        return score        