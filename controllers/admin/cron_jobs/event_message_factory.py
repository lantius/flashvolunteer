from controllers.abstract_handler import AbstractHandler

import os, logging

from models.event import Event
from models.messages import MessageType
from models.eventvolunteer import EventVolunteer

from components.time_zones import now

from components.message_text import type5, type6, type7, type8, type9

from models.volunteer import Volunteer
from models.auth.account import Account


class EventMessageFactory(AbstractHandler):

    def get(self):
        s = self._session()
        
        type5_msg = MessageType.all().filter('name =', 'rsvp_vol').get()
        type6_msg = MessageType.all().filter('name =', 'rsvp_host').get()
        type7_msg = MessageType.all().filter('name =', 'post_vol').get()
        type8_msg = MessageType.all().filter('name =', 'post_host').get()

        right_now = now()
        rsvp_events_to_check = [e for e in Event.all().filter('reminder_message_sent =', False).filter('date >', right_now)]
    
        for e in rsvp_events_to_check:
            if (e.date - right_now).days > 0:
                continue
            #it appears that model instances accessed in a cron job do not have referenceproperties resolved; 
            #thats why we're not using e.volunteers() below (and e.hosts() later on...)
            recipients = [ev.volunteer.account for ev in e.eventvolunteers.filter('isowner =', False).fetch(limit=500)]
            params = {
                'event_name': e.name,
                'event_url': '%s%s'%(self._get_base_url(), e.url()),
                'event_start_date': e.get_startdate_short(),
                'event_start_time': e.get_start_time()
            }
            if len(recipients) > 0:
                self.send_message(to = recipients, 
                             subject = type5.subject%params, 
                             body = type5.body%params, 
                             type = type5_msg, 
                             autogen = True,
                             domain = self.get_domain())
            
            if len(recipients) > 0: 
                params['participation_statement'] = "You currently have %i Flash Volunteers signed up."%len(recipients)
            else:
                params['participation_statement'] = "At this time, there are no Flash Volunteers signed up."
            hosts = [ev.volunteer.account for ev in e.eventvolunteers.filter('isowner =', True).fetch(limit=500)]
            self.send_message(to = hosts, 
                         subject = type6.subject%params, 
                         body = type6.body%params, 
                         type = type6_msg, 
                         autogen = True,
                         domain = self.get_domain())
            
            e.reminder_message_sent = True
            e.put()
    
        post_events_to_check = Event.all().filter('post_event_message_sent =', False).filter('enddate <', right_now)    
        for e in post_events_to_check:
            if not e.enddate: continue
            
            for ev in e.eventvolunteers:
                ev.event_is_upcoming = False
                ev.put()
                
            for eic in e.event_categories:
                eic.event_is_upcoming = False
                eic.put()
            
            since_event = right_now - e.enddate
            if since_event.days == 0: 
                params = {
                    'event_name': e.name,
                    'event_url': '%s%s'%(self._get_base_url(), e.url()),
                }
                recipients = [ev.volunteer.account for ev in e.eventvolunteers.filter('isowner =', False).fetch(limit=500)]
                if len(recipients) > 0:
                    self.send_message(to = recipients, 
                                 subject = type7.subject%params, 
                                 body = type7.body%params, 
                                 type = type7_msg, 
                                 autogen = True,
                                 domain = self.get_domain())
                
                if len(recipients) > 0: 
                    params['participation_statement'] = "Please visit the event page at %(event_url)s to record the hours that each of your volunteers spent helping you so that they can get credit. You can also upload photos."%params
                else:
                    params['participation_statement'] = "Unfortunately, it appears that no Flash Volunteers signed up to help out at your event (%(event_url)s)."%params
                
                hosts = [ev.volunteer.account for ev in e.eventvolunteers.filter('isowner =', True).fetch(limit=500)]
                self.send_message(to = hosts, 
                             subject = type8.subject%params, 
                             body = type8.body%params, 
                             type = type8_msg, 
                             autogen = True,
                             domain = self.get_domain())
                e.post_event_message_sent = True
            e.in_past = True
            e.put()
            
        return


def recommend_event(acnt, domain, type9_msg, right_now, cached_descs, base_url, application, session):
    account = Account.get_by_id(acnt)
    user = account.get_user()
    rec_events = [e for e in user.recommended_events(application = application,
                                                  session = session) 
                    if e.enddate and (e.enddate - right_now).days < 7][:10]
    
    desc = []
    for i,e in enumerate(rec_events):
        id = e.key().id()
        if id in cached_descs:
            d = '%i. %s'%(i,cached_descs[id])
        else:
            if e.get_startdate() == e.get_enddate():
                dt = '%s - %s'%(e.get_start_time_full(), e.get_end_time())
            else:
                dt = '%s - %s'%(e.get_start_time_full(), e.get_end_time_full())
                
            url = '%s%s'%(base_url, e.url())
            
            d = '"%s" - %s \nWhen: %s\nWhere: %s\n"%s..."'%(i+1, e.name, url, dt, e.neighborhood.name, e.description[:100])
            cached_descs[id] = d
            d = '%i. %s'%(i,d)
            
        desc.append(d)
    
    if len(rec_events) > 0:
        params = {
            'vol_name': user.name,
            'recommendation_text': '\n\n'.join(desc)
        }

        AbstractHandler.send_message(to = [user], 
                     subject = type9.subject%params, 
                     body = type9.body%params, 
                     type = type9_msg, 
                     autogen = True,
                     domain = domain)    
    
from google.appengine.ext import deferred
class RecommendedEventMessageFactory(AbstractHandler):

    def get(self):
        type9_msg = MessageType.all().filter('name =', 'rec_event').get()
        right_now = now()
        cached_descs = {}
        base_url = self._get_base_url()
        accounts = AbstractSendMessage.get_all_recipients()
        for acnt in accounts:
            deferred.defer(recommend_event, acnt, self.get_domain(), 
                           type9_msg, right_now, cached_descs, base_url,
                           self.get_application(), self._session())
