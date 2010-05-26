from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext import db
import os, random, logging

from models.neighborhood import Neighborhood
from models.messages.message import Message
from models.messages.message_receipt import MessageReceipt

from controllers.abstract_handler import AbstractHandler
from google.appengine.api import memcache

################################################################################
# Neighborhoods page
################################################################################
class NeighborhoodsPage(AbstractHandler):
    def get(self, url_data):    
        try:
            volunteer = self.auth()
        except:
            return
        
        params = self.parameterize() 
        
        application = self.get_application()
        neighborhoods = application.neighborhoods.order('name').fetch(limit=500) 

        is_json = self.is_json(params)
        
        col1 = None
        col2 = None
        col3 = None
        
        template_values = {                              
            'neighborhoods': neighborhoods,
            'volunteer': volunteer                                
          }
        self._add_base_template_values(vals = template_values)
        
        LIMIT = 15
        if not is_json:
            
            neighborhood_stats = memcache.get('%s-neighborhood_stats'%application.name)
            
            if not neighborhood_stats: 
                neighborhood_stats = []
            
            cnt = application.neighborhoods.count()                           
            col1 = neighborhoods[:cnt/3]
            col2 = neighborhoods[cnt/3:2*cnt/3]
            col3 = neighborhoods[2*cnt/3:]
        
            template_values.update({                              
                'neighborhoods1': col1,
                'neighborhoods2': col2,
                'neighborhoods3': col3,
                'most_active_neighborhoods': neighborhood_stats[:LIMIT],
                'LIMIT': LIMIT,                                                                       
            })         
            path = os.path.join(os.path.dirname(__file__),'..', 'views', 'neighborhoods', 'neighborhoods.html')
            render_out = template.render(path, template_values)
        else:
            path = os.path.join(os.path.dirname(__file__),'..', 'views', 'neighborhoods', 'neighborhoods.json')
            render_out = template.render(path, template_values)
            if (('jsoncallback' in params)):
                render_out = params['jsoncallback'] + '(' + render_out + ');'
          
        self.response.out.write(render_out)
        return
    
    def is_json(self, params):
        if ((self.request.headers["Accept"] == "application/json") or 
             ('format' in params and params['format'] == 'json')):
            return True
        else:
            return False
    
class NeighborhoodDetailPage(AbstractHandler):
    ################################################################################
    # GET
    def get(self, neighborhood_id):
        LIMIT = 4
        try:
            volunteer = self.auth()
        except:
            return
        
        neighborhood = Neighborhood.get_by_id(int(neighborhood_id))
        if not neighborhood:
            self.error(404)
            return
        
        candidates_living = list(neighborhood.volunteers_living_here())
        candidates_working = list(neighborhood.volunteers_working_here())
        
        volunteers_living = neighborhood.volunteers_living_here().count()
        volunteers_working = neighborhood.volunteers_working_here().count()                
        p_events = neighborhood.events_past().count()                 
        u_events = neighborhood.events_future().count()                    
        vhours = 0 
        for e in neighborhood.events_past():
            vhours += sum([ev.hours for ev in e.eventvolunteers if ev.hours])

        n_stats = (volunteers_living, volunteers_working, p_events, u_events, vhours)                                        
            #memcache.add('n_stats', n_stats, 10000) 
        
        #fill forum block
        forum = {}
        message_receipts = neighborhood.incoming_messages.order('-timestamp').fetch(limit=6)
        messages = [mr.message for mr in message_receipts]
        
        if (len(messages) > 5): 
            messages = messages[0:4]
            forum['more_messages'] = True
            
        forum['messages'] = messages 
        forum['path'] = self.request.path
        #end fill forum block
        
        template_values = {
            'volunteer': volunteer,
            'neighborhood': neighborhood,
            'volunteers_living_here': random.sample(candidates_living, min(len(candidates_living),LIMIT)), 
            'volunteers_working_here': random.sample(candidates_working, min(len(candidates_working),LIMIT)), 
            'past_events': neighborhood.events_past().fetch(LIMIT),
            'upcoming_events':neighborhood.events_future().fetch(LIMIT),
            'ongoing_opportunities':neighborhood.ongoing_opportunities().fetch(LIMIT),
            'n_stats':n_stats,
            'forum': forum
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__),'..', 'views', 'neighborhoods', 'neighborhood.html')
        self.response.out.write(template.render(path, template_values))
