#!/usr/bin/python
import sys,os, getopt
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
    print 'Populating FV...'
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
    
        if 'privacy__event_attendance' in v:
            privacy__event_attendance = v['privacy__event_attendance']
        else:
            privacy__event_attendance = 'friends'
            
        v = Volunteer(
          name = k,
          user = u,
          avatar = v['avatar'],
          quote = v['quote'],
          #twitter = None,
          home_neighborhood = neighborhoods[v['home_neighborhood']],
          work_neighborhood = neighborhoods[v['work_neighborhood']],
          session_id = session_id,
          create_rights = v['create_rights'],
          privacy__event_attendance = privacy__event_attendance)    
    
        volunteers[k] = v

        
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
        
    for k,v in events.items():
        date = datetime.datetime.strptime(v['time'] + " " + v['date'], "%H:%M %m/%d/%Y")
        try:
            date_created = datetime.datetime.strptime(v['time'] + " " + v['date_created'], "%H:%M %m/%d/%Y").date()
        except:
            date_created = date.date()

        try:
            duration = int(v['duration'])
        except:
            duration = None  
        e = Event(
          name = k,
          neighborhood = neighborhoods[v['neighborhood']],
          date_created = date_created,
          date = date,
          duration = duration,
          description = v['description'],
          special_instructions = v['special_instructions'],
          address = v['address']
                  
        )
        e.put()
        events[k] = e

    put(events.values() + \
        organizations.values() + \
        volunteers.values())
 
    
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

    
    test_objects = {
       'organizations': organizations.values(),
       'volunteers': volunteers.values(),
       'events': events.values(),
       'volunteerfollowers': volunteer_followers,
       'eventvolunteers': ev_volunteers,
       'neighborhoods': neighborhoods.values()
    }

    put(volunteer_followers + ev_volunteers)

    return test_objects

# eliminates all datastore items with the given sessionid
def armageddon(test_objects):
    print 'De-populating FV...'

    all_objects = []
    for k,v in test_objects.items():
        all_objects += v
    delete(all_objects)
        
def manual_armageddon(name):
    "removes population from datastore, slowly"
    print 'Bye-bye population'
    exec('from gui_integration_tests.test_environments.%s import my_env'%name)

    (volunteers, organizations, neighborhoods, events, event_volunteers, social_network) = copy.deepcopy(my_env)
    
    for k,v in neighborhoods.items():
        neighborhoods = db.GqlQuery("SELECT * FROM Neighborhood WHERE name = :name", 
                                   name = k)
        for n in neighborhoods:
          n.delete()
        
    for k,v in volunteers.items():
      delete_user(k)
      
    for k,v in organizations.items():
      delete_user(k)
       
    for k,v in events.items():
      delete_event(k)
    
    #TODO: destroy relationships, follower, followed etc.
    friends = social_network['friends']
    followers = social_network['followers']
                
    for follower, followed in friends:
      pass
    
    volunteer_followers = []
    for follower, followed in followers:
      pass

def check_if_user_exists(name):
    vols = db.GqlQuery('SELECT * from Volunteer WHERE name = :name',
                name = name)
    v = [v.name for v in vols]
    return v != []          
    
def get_users(name):
    users = db.GqlQuery('SELECT * from Volunteer WHERE name = :name',
                name = name)
    return users
    

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
      if v.eventvolunteers:
        for ev in v.eventvolunteers:
          ev.delete()
      v.delete()
        
def get_events(name):
    events = db.GqlQuery('SELECT * from Event WHERE name = :name',
                name = name)
    return events

def get_eventvolunteers(volunteer, event):
    eventvolunteers = db.GqlQuery('SELECT * from EventVolunteer WHERE volunteer = :volunteer AND event = :event',
                volunteer = volunteer, event = event)
    return eventvolunteers

    
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
      
def delete_eventvolunteer(volunteer, event):
  volunteers = db.GqlQuery('SELECT * from Volunteer WHERE name = :name', name = volunteer)
  events = db.GqlQuery('SELECT * from Event WHERE name = :name', name = event)

  for vol in volunteers:
    for ev in events:
      eventvolunteers = db.GqlQuery('SELECT * from EventVolunteer WHERE volunteer = :volunteer AND event = :event',
                    volunteer = vol, event = ev)
      for evvol in eventvolunteers:
        evvol.delete()
     
        
if __name__ == '__main__':
    #have create, delete options"
    try:
        opts, args = getopt.getopt(sys.argv[1:], "cd", ["create", "delete"])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        sys.exit(2)
    opt_create = True
    opt_delete = False
    for o, a in opts:
      if o in ("-c", "--create"):
        opt_create = True
      elif o in ("-d", "--delete"):
        opt_create = False
        opt_delete = True
      else:
        assert False, "unhandled option"
                    
    if opt_create:      
      test_objects = create_environment(name = 'revolutionary_war', session_id = 'test')
    if opt_delete:             
      manual_armageddon(name = 'revolutionary_war')

#    armageddon(test_objects = test_objects)
        