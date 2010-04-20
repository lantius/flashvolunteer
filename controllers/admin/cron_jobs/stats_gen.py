from controllers.abstract_handler import AbstractHandler


from google.appengine.api import memcache

import os, logging

from datetime import datetime
from google.appengine.ext import deferred

    
def gen_stats(application, is_debugging):    
    stats = {}
    
    neighborhoods = application.neighborhoods.order('name').fetch(limit=500)                 
    
    for n in neighborhoods:                                                     
        volunteers_living = n.volunteers_living_here().count()
        volunteers_working = n.volunteers_working_here().count()             
        past_events = n.events_past().count()                       
        upcoming_events = n.events_future().count()
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
        
    memcache.add('%s-neighborhood_stats'%application.name, neighborhood_stats)    
            
class StatsGen(AbstractHandler):

    def get(self):
        deferred.defer(gen_stats, self.get_application(), self.is_debugging())