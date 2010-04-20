from google.appengine.api import urlfetch
import urllib, os, logging

from controllers.abstract_handler import AbstractHandler
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext.webapp import template


from django.utils import simplejson
from google.appengine.api import urlfetch

from components.mailchimp.chimpy import Connection as MailChimp
from google.appengine.ext import deferred


from models.auth.account import Account

def sync_with_mail_chimp():
    api_key = '125fa723ae114a190658112cdb647040'
    #list_key = 'c9f05e3284' #master list
    list_key = 'fbed0440b0' #test list
    
    recipients = []
    CHUNK_SIZE = 250
    
    last_key = None
    while True:
        if last_key:
            query = Account.gql('WHERE __key__ > :1 ORDER BY __key__', last_key)
        else:
            query = Account.gql('ORDER BY __key__')
        
        recips = query.fetch(limit = CHUNK_SIZE + 1)
        
        if len(recips) == CHUNK_SIZE + 1:
            recipients += recips[:-1]
            last_key = recips[-1].key()
        else:
            recipients += recips
            break

    batch = []
    recipients = ['koos42@gmail.com', 'eva.ringstrom@gmail.com', 'brad@flashvolunteer.org', 'sara@flashvolunteer.org', 'mellicia@gmail.com','justin@flashvolunteer.org', 'amy@flashvolunteer.org']
    
    for acnt in recipients:
        batch.append({
         'EMAIL': acnt,#acnt.get_email(),
         'EMAIL_TYPE': 'html'              
        })
        
    conn = MailChimp(apikey = api_key)
    
    #msg = conn.list_batch_subscribe(
    #                          id = list_key, 
    #                          batch = batch,
    #                          double_optin = True)
    #logging.info(msg)
        
    
class SyncWithMailChimp(AbstractHandler):

    def get(self):
        try:
            account = self.auth(require_login = True, require_admin = True)
        except:
            return

        template_values = {
            'volunteer': account.get_user(),
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__),'..', '..', 'views', 'admin', 'sync_with_mail_chimp.html')
        self.response.out.write(template.render(path, template_values, debug=self.is_debugging()))

    def post(self):
        try:
            account = self.auth(require_login=True, require_admin = True)
        except:
            return   

        deferred.defer(sync_with_mail_chimp)
        
        self.redirect('/admin')
