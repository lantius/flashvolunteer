from google.appengine.api import urlfetch
from django.utils import simplejson
import urllib, os, logging

from utils.misc_methods import get_neighborhood
from controllers.abstract_handler import AbstractHandler
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext.webapp import template

from models.afg_opportunity import AFGOpportunity

from django.utils import simplejson
import datetime

class AllForGoodInterface(AbstractHandler):

    def get(self, urldata = None):
        logging.info('in afg')
        if not urldata:
            self.list()
        elif urldata == '/publish':
            params = self.parameterize() 
            afg_id = params['id']
            opp = AFGOpportunity.all().filter('afg_id =', afg_id).get()            
            self.publish(opportunity = opp)
            

    def list(self): 
        try:
            account = self.auth(require_login = True, require_admin = True)
        except:
            return
        
        opportunities = [ o for o in sorted(AFGOpportunity.all().filter('status =', None).fetch(limit=500),
                               lambda a,b:int(a.score-b.score),reverse=True)
                               if o.source.get() is None ] 
                    
        template_values = {
            'volunteer': account.get_user(),
            'opportunities': opportunities,
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__),'..', '..', 'views', 'admin', 'afg_publish.html')
        self.response.out.write(template.render(path, template_values, debug=self.is_debugging()))

    
    def post(self, urldata = None):
        try:
            account = self.auth(require_login=True, require_admin = True)
        except:
            return   
        
        params = self.parameterize() 
        
        if urldata == '/dismiss':
            afg_id = params['id']
            opp = AFGOpportunity.all().filter('afg_id =', afg_id).get()
            opp.status = False
            opp.put()
        elif urldata == '/publish':
            afg_id = params['id']
            opp.status = True
            opp.put()
        elif urldata == '/rebuild':
            self.rebuild()
            #self.redirect('/#/admin/afg_interface')
        
    #much of this code is derived from controllers.events.edit
    def publish(self, opportunity):
        from models.event import Event
        from models.interestcategory import InterestCategory
        from controllers._helpers import NeighborhoodHelper
        
        try:
            account = self.auth(require_login=True, require_admin = True)
        except:
            return   

        opp = opportunity 
        
        try:
            neighborhood = get_neighborhood(application = self.get_application(), 
                                        address = opp.location)[1]
        except:
            self._session()['notification_message'] = ['Error: could not find neighborhood around "%s"'%opp.location]
            neighborhood = None
            
        event = Event(
            application = self.get_application(),
            name = opp.title,
            description = opp.description, #TODO: make sure to pull down full desc
            enddate = opp.enddate,
            date = opp.startdate,
            special_instructions = opp.skills,
            neighborhood = neighborhood, 
            address = opp.location,
            event_url = opp.url,
            contact_email = opp.contact_email
        )
        
        template_values = { 
            'event' : event, 
            'volunteer': account.get_user(), 
            'neighborhoods': NeighborhoodHelper().selected(self.get_application(),event.neighborhood),
            'interestcategories' : InterestCategory.all().order('name').fetch(limit=500),
            'afg_opp': opp
        }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__),'..', '..', 'views', 'events', 'event_edit.html')
        self.response.out.write(template.render(path, template_values, debug=self.is_debugging()))

        
    def rebuild(self):

        try:
            account = self.auth(require_login=True, require_admin = True)
        except:
            return   
                
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
            except:
                skipped += 1

        self.response.out.write(simplejson.dumps({'added':added, 'existed':existed, 'skipped':skipped}))
    
    def _score_opportunity(self, opp):
        score = 0
        
        #+1 for coming from a high-quality provider (i.e United Way (Volunteer Solutions portal), Seattle Works (Hands On Network)
        if opp.provider in ['unitedway', 'handsonnetwork']:
            score += 2
        if get_neighborhood(self.get_application(), opp.location) is not None:
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