#!/usr/bin/python
import sys,os
from gui_integration_tests.test_settings import PYTHON_LIB, app_id, host, auth_user, auth_psswd, auth_domain

sys.path.append(PYTHON_LIB)
sys.path.append("%s/lib/yaml/lib"%PYTHON_LIB)

os.environ['AUTH_DOMAIN'] = auth_domain
os.environ['USER_EMAIL'] = '' 
   
from google.appengine.ext.remote_api import remote_api_stub
from google.appengine.ext import db
from google.appengine.api.users import User
from google.appengine.ext.db import put, delete

from models.neighborhood import Neighborhood
from models.volunteer import Volunteer
from models.event import Event
from models.eventvolunteer import EventVolunteer
from models.volunteerfollower import VolunteerFollower

import datetime, copy


def auth_func():
    return auth_user, auth_psswd  
    #raw_input('Username:'), getpass.getpass('Password:')

remote_api_stub.ConfigureRemoteDatastore(app_id, '/remote_api', auth_func, host)


def create_environment(name, session_id):
    exec('from gui_integration_tests.test_environments.%s import my_env'%name)

    (volunteers, organizations, neighborhoods, events, event_volunteers, social_network) = copy.deepcopy(my_env)
    
    for k,v in neighborhoods.items():
        n = Neighborhood(
             name = v['name'],
             session_id = session_id,
        )
        neighborhoods[k] = n
    put(neighborhoods.values())
        
    for k,v in volunteers.items():
        email = k.replace(' ', '_').lower() + '@volunteer.org'
        u = User(email)
    
        v = Volunteer(
          name = k,
          user = u,
          avatar = v['avatar'],
          quote = v['quote'],
          #twitter = None,
          home_neighborhood = neighborhoods[v['home_neighborhood']],
          work_neighborhood = neighborhoods[v['work_neighborhood']],
          session_id = session_id,
          create_rights = v['create_rights'])    
    
        volunteers[k] = v
    put(volunteers.values())
        
    for k,v in organizations.items():
        email = k.replace(' ', '_').lower() + '@organization.org'
        u = User(email)
    
        v = Volunteer(
          name = k,
          user = u,
          avatar = v['avatar'],
          quote = v['quote'],
          #twitter = None,
          home_neighborhood = neighborhoods[v['home_neighborhood']],
          work_neighborhood = neighborhoods[v['work_neighborhood']],
          session_id = session_id,
          create_rights = v['create_rights'])    
    
        organizations[k] = v
    put(organizations.values())
        
    for k,v in events.items():
        date = datetime.datetime.strptime(v['time'] + " " + v['date'], "%H:%M %m/%d/%Y")
        try:
            date_created = datetime.datetime.strptime(v['time'] + " " + v['date_created'], "%H:%M %m/%d/%Y").date()
        except:
            date_created = date.date()

        
                    
        e = Event(
          name = k,
          neighborhood = neighborhoods[v['neighborhood']],
          date_created = date_created,
          date = date,
          description = v['description'],
          special_instructions = v['special_instructions'],
          address = v['address']
                  
        )
        e.put()
        events[k] = e
 
    put(events.values())
    
    ev_volunteers = []
    for k,v in event_volunteers.items():
        for vol in v:
            volunteer = volunteers[vol['volunteer']]
            ev = EventVolunteer(
                event = events[k],
                volunteer = volunteer,
                isowner = 'is_owner' in vol and vol['is_owner']
            )
            ev_volunteers.append(ev)
            
    put(ev_volunteers)
    
    friends = social_network['friends']
    followers = social_network['followers']
                
    for follower, followed in friends:
        followers += [(follower, followed), (followed, follower)]
    
    volunteer_followers = []
    for follower, followed in followers:
        vf = VolunteerFollower(
           follower = volunteers[follower],
           volunteer = volunteers[followed]
        )
        volunteer_followers.append(vf)

    put(volunteer_followers)
    
    test_objects = {
       'organizations': organizations.values(),
       'volunteers': volunteers.values(),
       'events': events.values(),
       'volunteerfollowers': volunteer_followers,
       'eventvolunteers': ev_volunteers,
       'neighborhoods': neighborhoods.values()
    }

    return test_objects

# populates the FV datastore with some elements for use in the testing environment    
def populate(sessionid):
    print 'Populating FV...'
    
    neighborhoods = dict([(n.name, n) for n in db.GqlQuery('SELECT * from Neighborhood')])
    
    for i in range(3):
        email = 'volunteer%i@test.org'%i
        u = User(email)

        v = Volunteer(
          name = email,
          user = u,
          #avatar = None,
          #quote = 'test quote',
          #twitter = None,
          home_neighborhood = neighborhoods['Capitol Hill'],
          #work_neighborhood = None,
          session_id = sessionid,
          create_rights = False)
        
        v.put()      

    for i in range(3):
        email = 'organization%i@test.org'%i
        u = User(email)

        v = Volunteer(
          name = email,
          user = u,
          #avatar = None,
          #quote = 'test quote',
          #twitter = None,
          home_neighborhood = neighborhoods['Capitol Hill'],
          #work_neighborhood = None,
          session_id = sessionid,
          create_rights = True)
        
        v.put()      


#    for i in range(5):
#        e = Event(
#                  
#        )
            
# eliminates all datastore items with the given sessionid
def armageddon(test_objects):
    print 'De-populating FV...'

    for k,v in test_objects.items():
        delete(v)

def check_if_user_exists(name):
    vols = db.GqlQuery('SELECT * from Volunteer WHERE name = :name',
                name = name)
    v = [v.name for v in vols]
    return v != []            

def set_create_rights(name):
    vols = db.GqlQuery('SELECT * from Volunteer WHERE name = :name',
                name = name)
    for v in vols:
        v.create_rights = True
        v.put()
        
def delete_user(name):
    vols = db.GqlQuery('SELECT * from Volunteer WHERE name = :name',
                name = name)
    for v in vols:
        v.delete()
        
def get_events(name):
    events = db.GqlQuery('SELECT * from Event WHERE name = :name',
                name = name)
    return events
    
def delete_event(name):
    events = db.GqlQuery('SELECT * from Event WHERE name = :name',
                name = name)
    for e in events:
      if e.eventvolunteers:
        for ev in e.eventvolunteers:
          ev.delete()
      # TODO: Delete interest categories    
      #if e.eventinterestcategories:
      #  for ei in e.eventinterestcategories:
      #    ei.delete()
      e.delete()
        
if __name__ == '__main__':

    test_objects = create_environment(name = 'revolutionary_war', session_id = 'test')

#    armageddon(test_objects = test_objects)
        