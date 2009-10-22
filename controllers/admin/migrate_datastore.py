from components.sessions import Session
from controllers._utils import get_server, get_application
from components.applications.operations import add_applications, add_messaging, synchronize_apps
from controllers.abstract_handler import AbstractHandler
from google.appengine.api import memcache
from google.appengine.ext import webapp
from models.application import Application
from models.applicationdomain import ApplicationDomain
from models.event import Event
from models.interestcategory import InterestCategory
from models.neighborhood import Neighborhood
from models.volunteer import Volunteer

import os, logging

class MigrateDatastore(AbstractHandler):

    def get(self):
        
        ## do migration here
        synchronize_apps()
            
        for v in Volunteer.all():
            if v.preferred_email and v.preferred_email.endswith('@Facebook'):
                v.preferred_email = None
                v.put()
                
        self.update_messages()
        return
    
##########################################################################
## Various migration methods that may or may not be useful in the future.
##########################################################################

    def update_messages(self):
        from models.messages import Message
        for m in Message.all():
            for rid in m.recipients:
                recipient = Volunteer.get_by_id(rid)
                nm = Message(
                    subject = m.subject,
                    body = m.body,
                    date = m.date,
                    trigger = m.trigger,
                    sent = m.sent,
                    sender = m.sender,
                    recipient = recipient,
                    flagged = m.flagged,
                    verified = m.verified,
                    type = m.type,
                    read = recipient.key().id() not in m.unread,
                    autogen = m.autogen,
                    mailbox = recipient.key().id() in m.show_in_mailbox
                )
                nm.put()
            m.delete()
        
        
    def __set_default_application_data(self):
        logging.info('MIGRATE: add application data')
        seattle = Application.all().filter('name =', "seattle").get()
        for v in Volunteer.all():
            
            if not v.applications:
                v.add_application(seattle)
                logging.info('MIGRATE: added seattle to volunteer "%s"'%v.name)

        for e in Event.all():
            try:
                if e.application is None:
                    e.application = seattle
                    e.put()
                    logging.info('MIGRATE: added seattle to event "%s"'%e.name)
            except:
                e.application = seattle
                e.put()
                logging.info('MIGRATE: added seattle to event "%s"'%e.name)

        for n in Neighborhood.all():
            try:
                if not n.application:
                    n.application = seattle
                    n.put()
                    logging.info('MIGRATE: added seattle to neighborhood "%s"'%e.name)
            except:
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