from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext import db
import os, random

from controllers._params import Parameters
from models.neighborhood import Neighborhood
from models.eventvolunteer import EventVolunteer
from models.messages.message import Message
from models.messages.message_receipt import MessageReceipt
from controllers._utils import get_application

from controllers.abstract_handler import AbstractHandler
from google.appengine.api import memcache

################################################################################
# Neighborhoods page
################################################################################
class NeighborhoodsPage(AbstractHandler):
  def get(self, url_data):    
    try:
      account = self.auth()
    except:
      return

    if account: user = account.get_user()
    else: user = None
            
    params = Parameters.parameterize(self.request)
    
    application = get_application()
    neighborhoods = application.neighborhoods.fetch(limit=500) 
    is_json = self.is_json(params)
    
    col1 = None
    col2 = None
    col3 = None

    template_values = {                              
        'neighborhoods': neighborhoods,
        'volunteer': user                                
      }
    self._add_base_template_values(vals = template_values)

    LIMIT = 15
    if not is_json:
        
        neighborhood_stats = memcache.get('neighborhood_stats')
        if not neighborhood_stats: 
            stats = {}
            
            for n in neighborhoods:                                                     
                volunteers_living = len(list(n.volunteers_living_here()))
                volunteers_working = len(list(n.volunteers_working_here()))                   
                past_events = len(list(n.events_past()))                       
                upcoming_events = len(list(n.events_future()))                    
                vhours = 0 
                for e in n.events:
                    vhours += sum([ev.hours for ev in e.eventvolunteers if ev.hours])
        
                stats[n] = [volunteers_living, volunteers_working, past_events, upcoming_events, vhours]           
            
            all_scores = []                                             
            for n,scores in stats.items():
                all_scores.append((n, sum(scores), scores)) 
                                                     
            all_scores.sort(lambda (n, total, scores), (n2, total2, scores2): int(total-total2), reverse=True)                            
            
            neighborhood_stats = []
            for n, total, scores in all_scores:
                #scores.append(total)  #dont show total score at this time...
                neighborhood_stats.append((n, scores))
            memcache.add('neighborhood_stats', neighborhood_stats, 10000)
        
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
  def get(self, url_data):
    if url_data:
      self.show(url_data)
    else:
      self.list() 

  ################################################################################
  # POST

  ################################################################################
  # SHOW
  def show(self, neighborhood_id):
    LIMIT = 12
    try:
      account = self.auth()
    except:
      return

    if account: user = account.get_user()
    else: user = None
    neighborhood = Neighborhood.get_by_id(int(neighborhood_id))
    if not neighborhood:
      self.error(404)
      return

    candidates_living = list(neighborhood.volunteers_living_here())
    candidates_working = list(neighborhood.volunteers_working_here())
    
    past_events = list(neighborhood.events_past()) 
    upcoming_events = list(neighborhood.events_future())    
    

    #fill forum block
    forum = {}
    query = db.Query(MessageReceipt)
    message_receipts = query.filter('recipient = ', neighborhood.key()).order('-timestamp').fetch(limit=6)
    messages = []
    for mr in message_receipts:
        messages.append(mr.message)
    
    if (len(messages) > 5): 
        messages = messages[0:4]
        forum['more_messages'] = True
        
    forum['messages'] = messages 
    forum['path'] = self.request.path
    #end fill forum block

    
    
    template_values = {
        'volunteer': user,
        'neighborhood': neighborhood,
        'volunteers_living_here': random.sample(candidates_living, min(len(candidates_living),LIMIT)), 
        'volunteers_working_here': random.sample(candidates_working, min(len(candidates_working),LIMIT)), 
        'past_events': past_events[-LIMIT:],
        'upcoming_events':upcoming_events[:LIMIT],
        'forum': forum
      }
    self._add_base_template_values(vals = template_values)
    
    path = os.path.join(os.path.dirname(__file__),'..', 'views', 'neighborhoods', 'neighborhood.html')
    self.response.out.write(template.render(path, template_values))
