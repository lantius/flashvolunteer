import os
from google.appengine.api import memcache

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
        
def get_domain(keep_www = False):
    if not keep_www and os.environ['HTTP_HOST'].startswith('www.'):
        return os.environ['HTTP_HOST'][4:]
    return os.environ['HTTP_HOST']

def get_application(just_id = False):
    domain = get_domain()
    key = "app-%s"%domain
    app_domain = memcache.get(key)
    if app_domain is None:
        app_domain = ApplicationDomain.all().filter('domain = ',domain).get()
        memcache.add(key, app_domain, 3600)

    if just_id: return app_domain.application.key().id()
    else: return app_domain.application
    
def get_google_maps_api_key():
    # flashvolunteer-dev.appspot.com
    #GOOGLE_MAPS_API_KEY = 'ABQIAAAA5caWoMd1eNfUNui_l1ovGxRzNuM6YWShM3q9_tmx1xqncfIVVBR0Vl7Dzc-1cpY5wjaMPmq_fwpBYA'
    # flashvolunteer.appspot.com
    #GOOGLE_MAPS_API_KEY = 'ABQIAAAA5caWoMd1eNfUNui_l1ovGxQ_mWzt9DEjH1LJGfRCLKaKtSAdHRQXsI-fBQAVUzaYlblLSlzQ1ctnSQ'
    # flashvolunteer.org
    #GOOGLE_MAPS_API_KEY = 'ABQIAAAApwXNBqL2vnoPPZzBT8fEFBT8o8BW0NprhG7ZQBw6sHycsndbhRS7hhGpRgOy2Kssletcr3BQkAy7jg'
    #http://v01-1.latest.flashvolunteer.appspot.com
    #GOOGLE_MAPS_API_KEY = 'ABQIAAAApwXNBqL2vnoPPZzBT8fEFBRKcpMVieIGuRjmcVoCEVomVUOSzxQXzU7Vr92SCk5CZf8Fq_G1wz5bIA'
    
    server = get_server()
    if server == 0:
        return 'ABQIAAAApwXNBqL2vnoPPZzBT8fEFBT8o8BW0NprhG7ZQBw6sHycsndbhRS7hhGpRgOy2Kssletcr3BQkAy7jg'
    elif server == 1:
        return 'ABQIAAAApwXNBqL2vnoPPZzBT8fEFBRzNuM6YWShM3q9_tmx1xqncfIVVBTbiYMhS-lVDJ8Xb4gcYINCK_rBMA'
    elif server == 2: 
        return 'ABQIAAAApwXNBqL2vnoPPZzBT8fEFBT8o8BW0NprhG7ZQBw6sHycsndbhRS7hhGpRgOy2Kssletcr3BQkAy7jg'
    

from models.messages.message import Message
from components.time_zones import now
from controllers.admin.message_dispatcher import check_messages

def send_message(to, subject, body, type, sender = None, trigger = None, referral_url = None, immediate=False):
    return
#    if trigger is None:
#        trigger = now()
#    
#    if sender:
#        sender_id = sender.key().id()
#    else:
#        sender_id = -1
#        
#    message = Message(
#      subject = subject,
#      body = body,
#      recipients = [u.key().id() for u in to],
#      sender = sender_id,
#      #referral_url = referral_url,
#      trigger = trigger,
#      type = type
#    )
#
#    message.put()
#    if immediate:
#        check_messages()
