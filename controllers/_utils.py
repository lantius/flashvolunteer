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



