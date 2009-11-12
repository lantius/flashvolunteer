import os, logging
from google.appengine.api import memcache
from components.sessions import Session

from models.applicationdomain import ApplicationDomain

def is_debugging():
    """Detects if app is running in production or not.

    Returns a boolean.
    """
    return get_server() == 0

def get_server():
    """Determines which host requests are being served from. 
    
    0 == development server
    1 == flashvolunteer-dev.appspot.com or development.flashvolunteer.org
    2 == flashvolunteer.org etc.    
    """
    
    if 'SERVER_SOFTWARE' not in os.environ or os.environ['SERVER_SOFTWARE'].startswith('Development'): 
        return 0
    else:
        domain = get_domain()
        if domain.find('flashvolunteer-dev.appspot.com') > -1 or domain.find('development.flashvolunteer.org') > -1:
            return 1
        else:
            return 2
        
def get_domain():
    session = Session()
    logging.info('HTTP_HOST=%s'%os.environ['HTTP_HOST'])
    if 'this_domain' not in session:
        domain = os.environ['HTTP_HOST']
        if domain.startswith('www.'):
            domain = domain[4:]
        
        if domain.endswith('flashvolunteer.appspot.com') > -1:
            domain = domain.replace('flashvolunteer.appspot.com', 'flashvolunteer.org')
        elif domain.endswith('flashvolunteer-dev.appspot.com') > -1: 
            domain = 'development.flashvolunteer.org'

        session['this_domain'] = domain
    return session['this_domain']

def get_application(just_id = False):
    domain = get_domain()
    key = "app-%s"%domain
    app_domain = memcache.get(key)
    if app_domain is None:
        app_domain = ApplicationDomain.all().filter('domain = ',domain).get()
        if app_domain is None:
            logging.error('got bad domain name: %s'%domain)
        memcache.add(key, app_domain, 100000)

    if just_id: return app_domain.application.key().id()
    else: return app_domain.application
    
def get_google_maps_api_key():
    server = get_server()
    if server == 0:
        return 'ABQIAAAApwXNBqL2vnoPPZzBT8fEFBT8o8BW0NprhG7ZQBw6sHycsndbhRS7hhGpRgOy2Kssletcr3BQkAy7jg'
    elif server == 1 and get_domain().find('appspot.com') > -1:
        return 'ABQIAAAApwXNBqL2vnoPPZzBT8fEFBRzNuM6YWShM3q9_tmx1xqncfIVVBTbiYMhS-lVDJ8Xb4gcYINCK_rBMA'
    else: 
        return 'ABQIAAAApwXNBqL2vnoPPZzBT8fEFBSQPgw8JI6IbILJlYJvqzvWY-lLQBTXCrJQnsm-dzTVGDCeBq80bPNwUQ'



def send_message(to, subject, body, type, sender = None, immediate=False, autogen = True, forum = False):
    from models.messages.message import Message
    from models.messages import MessageReceipt
    from components.time_zones import now
    from google.appengine.ext.db import put, delete
    
    logging.info('to size is %i'%len(to))
    
    if subject == '' or subject is None:
        subject = '(No subject)'

    message = Message(
      subject = subject,
      body = body,
      sent_by = sender,
      type = type,
      autogen = autogen,
      forum_msg = forum
    )
    message.put()
    mrs = []        
    for recipient in to:
        mr = MessageReceipt(
          recipient = recipient,
          message = message)
        mrs.append(mr)

    try:
        logging.info('putting %i recipients'%len(mrs))
        put(mrs)
    except:
        for mr in mrs:
            if not mr.is_saved():
                try:
                    mr.put()
                except:
                    logging.error('Could not add message receipt of message %i for recipient %i'%(message.key().id(), mr.recipient.key().id()))

    if immediate:
        message.send()

from datetime import datetime
from google.appengine.ext import deferred

def check_messages():
    from models.messages.message import Message
    if Message.all().filter('sent =', False).filter('in_task_queue =', False).filter('trigger <', datetime.now()).count() > 0:
        deferred.defer(_check_messages)
    
def _check_messages():
    from models.messages.message import Message
    
    logging.info('Checking messages in task queue')
    messages_to_send = Message.all().filter('sent =', False).filter('in_task_queue =', False).filter('trigger <', datetime.now())

    for message in messages_to_send:
        try:
            message.in_task_queue = True
            message.put()
            message.send()    
        finally:
            message.in_task_queue = False
            message.put()