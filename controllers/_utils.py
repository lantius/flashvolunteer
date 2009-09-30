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
    1 == flashvolunteer-dev.appspot.com
    2 == flashvolunteer.org etc.    
    """
    
    if os.environ['SERVER_SOFTWARE'].startswith('Development'): 
        return 0
    else:
        domain = os.environ['HTTP_HOST']
        if domain.find('flashvolunteer-dev') > -1:
            return 1
        else:
            return 2

def get_application(just_id = False):
    domain = os.environ['HTTP_HOST']
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
        #todo: register api key for flashvolunteer-dev.appspot.com and add it here
        return 'ABQIAAAApwXNBqL2vnoPPZzBT8fEFBT8o8BW0NprhG7ZQBw6sHycsndbhRS7hhGpRgOy2Kssletcr3BQkAy7jg'
    elif server == 2: 
        return 'ABQIAAAApwXNBqL2vnoPPZzBT8fEFBT8o8BW0NprhG7ZQBw6sHycsndbhRS7hhGpRgOy2Kssletcr3BQkAy7jg'
    
    
def send_mail(sender, to, subject, body):
    from google.appengine.api import mail

    mail.send_mail(sender=sender,
                   to=to,
                   subject=subject,
                   body=body)
