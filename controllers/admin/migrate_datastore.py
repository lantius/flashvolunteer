import os, logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from models.volunteer import Volunteer
from models.neighborhood import Neighborhood
from models.event import Event
from models.interestcategory import InterestCategory
from models.application import Application

from components.sessions import Session

import wsgiref.handlers

from controllers.abstract_handler import AbstractHandler

class MigrateDatastore(AbstractHandler):

    def get(self):
        
        ## do migration here
        self.__add_application_data()
        return
    
##########################################################################
## Various migration methods that may or may not be useful in the future.
##########################################################################

    def __add_application_data(self):
        logging.info('MIGRATE: add application data')
        seattle = Application.all().filter('name =', "seattle").get()
        for v in Volunteer.all():
            
            if not v.applications:
                v.add_application(seattle)
                logging.info('MIGRATE: added seattle to volunteer "%s"'%v.name)

        for e in Event.all():
            if not e.application:
                e.application = seattle
                e.put()
                logging.info('MIGRATE: added seattle to event "%s"'%e.name)

        for n in Neighborhood.all():
            if not n.application:
                n.application = seattle
                n.put()
                logging.info('MIGRATE: added seattle to neighborhood "%s"'%e.name)

                
    def __migrate_neighborhoods(self):
        #neighborhoods to add
        new_hoods = []
        
        hoods = {}
        for n in Neighborhood.all():
            hoods[n.name] = n
            
                      
        for n in new_hoods:
            if not n in hoods:
                hood = Neighborhood(name = n)
                hood.put()
                hoods[n] = hood
                
        #neighborhood transformations; 
        #### From : To
        n_map =  {
                 #'South Lake Union': 'Lake Union',
                 }     
            
        for v in Volunteer.all():
            if v.work_neighborhood and v.work_neighborhood.name in n_map:
                v.work_neighborhood = hoods[n_map[v.work_neighborhood.name]]
                v.put()
            if v.home_neighborhood and v.home_neighborhood.name in n_map:
                v.home_neighborhood = hoods[n_map[v.home_neighborhood.name]]
                v.put()
                
        for e in Event.all():
            if e.neighborhood and e.neighborhood.name in n_map:
                e.neighborhood = hoods[n_map[e.neighborhood.name]]
                e.put()
                
        #neighborhoods to delete
        hoods_to_remove = []      
        for n in hoods_to_remove:
            if n in hoods:
                hoods[n].delete()  
            
    def __clear_stale_events(self):
        for ev in EventVolunteer.all():
            try:
                event = ev.event
            except:
                ev.delete()
                
        for ec in EventInterestCategory.all():
            try:
                event = ec.event
            except:
                ec.delete()
                
application = webapp.WSGIApplication([('/admin/migrate', MigrateDatastore)],
                                      debug=True)

def main():
    run_wsgi_app(application)                                    

if __name__ == '__main__':
    main()