import os, string, logging
from datetime import datetime

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp


from models.messages import MessageType
from models.volunteer import Volunteer
from models.event import Event
from models.neighborhood import Neighborhood

from utils.message_text import event_forum_txt, neighborhood_forum_txt

from controllers.abstract_handler import AbstractHandler

class AbstractSendMessage(AbstractHandler):
    ################################################################################
    # POST
    def _send_message(self, sender, recipients, type, params, autogen = False, forum = True): 
        ##TODO: eliminate this method, just call send_message directly           
        if len(recipients) == 0: return
        
        logging.info('recipient list size is %i'%len(recipients))
        
        self.send_message(to = recipients, 
                     subject = params['subject'], 
                     body = params['body'], 
                     type = type, 
                     sender = sender,
                     autogen = autogen,
                     forum = forum,
                     domain = self.get_domain())
        
        return
    
    def _redirect_to(self):
        return '/messages'

    def _get_recipients(self, id, sender):
        raise
    def _get_message_type(self):
        raise
    def _get_recipient_type(self):
        raise
    def _get_render_path(self):
        raise
    def _is_forum_post(self):
        return False
    def _get_url(self, recipients):
        return recipients[0].url()

    
    def _do_additional_post_processing(self, id, sender, params):
        pass
    
    def post(self, url_data = None):
        try:
            volunteer = self.auth(require_login=True)
        except:
            return
        
        id = url_data
        
        recipients = self._get_recipients(id, volunteer)
         
        params = self.parameterize() 
        
        mt = MessageType.all().filter('name = ', self._get_message_type()).get()  
        
        self._send_message(sender = volunteer, recipients = recipients, type = mt, params = params, forum = self._is_forum_post())
        self._do_additional_post_processing(id = id, sender = volunteer, params = params)

        session = self._session()
        
        self.add_notification_message('Message delivered.')
        
        if 'message_redirect' in session:
            self.redirect(session['message_redirect'])
            del session['message_redirect']
        else:
            self.redirect(self._redirect_to())
            
    #show message entry form
    def get(self, url_data = None):
        try:
            volunteer = self.auth(require_login=True)
        except:
            return
        params = self.parameterize() 
        session = self._session()
        if 'redirect' in params:
            session['message_redirect'] = params['redirect']
        id = url_data
 
        template_values = {}
        recipients = self._get_recipients(id, volunteer)
        render_path = self._get_render_path()
        
        url = self._get_url(recipients)
        
        if len(recipients) > 10: 
            recipients = ', '.join([r.name for r in recipients[:10]]) + '...'
        else:
            recipients = ', '.join([r.name for r in recipients])
            
        template_values.update({
          'volunteer': volunteer,
          'recipients': recipients,
          'url': url,
          'recipient_type': self._get_recipient_type()
          })
        self._add_base_template_values(vals = template_values)
      
        self.response.out.write(template.render(render_path, template_values))        

    @classmethod
    def get_all_recipients(self):
        recipients = []
        CHUNK_SIZE = 250
        
        last_key = None
        while True:
            if last_key:
                query = Volunteer.gql('WHERE __key__ > :1 ORDER BY __key__', last_key)
            else:
                query = Volunteer.gql('ORDER BY __key__')
            
            recips = query.fetch(limit = CHUNK_SIZE + 1)
            
            if len(recips) == CHUNK_SIZE + 1:
                recipients += recips[:-1]
                last_key = recips[-1].key()
            else:
                recipients += recips
                break

        return recipients
    
class SendMessage_Personal(AbstractSendMessage):
    #enter message into database

    def _get_recipients(self, id, sender):
        #send to person
        return [Volunteer.get_by_id(int(id))]

    def _get_message_type(self):
        return 'person_to_person'
    
    def _get_recipient_type(self):
        return 'volunteer'
    
    def _get_render_path(self):
        return os.path.join(os.path.dirname(__file__),'..', 'views', 'messages', 'create_message.html')
    
class SendMessage_Event(AbstractSendMessage):
    def _get_recipients(self, id, sender):
        event = Event.get_by_id(int(id))
        return [event]

    def _get_message_type(self):
        return 'event_forum_main_message'

    def _get_recipient_type(self):
        return 'event'
    
    def _get_render_path(self):
        return os.path.join(os.path.dirname(__file__),'..', 'views', 'messages', 'create_forumpost.html')

    def _is_forum_post(self):
        return True


    def _do_additional_post_processing(self, id, sender, params):
        event = Event.get_by_id(int(id))
        recipients = [ev.volunteer for ev in event.eventvolunteers if ev.volunteer.key().id() != sender.key().id()]
        
        mt = MessageType.all().filter('name = ', 'event_forum').get()
        substitution_params = {
            'message_body': params['body'],
            'message_subject': params['subject'],
            'sender_name' : sender.name,
            'event_name': event.name,
            'event_url' : self._get_base_url() + event.url()
        }
        
        params['body'] = event_forum_txt.body%substitution_params
        params['subject'] = event_forum_txt.subject%substitution_params
        
        self._send_message(sender = sender, recipients = recipients, type = mt, params = params, autogen = True, forum = False)
        

class SendMessage_Neighborhood(AbstractSendMessage):
    def _get_recipients(self, id, sender):
        neighborhood = Neighborhood.get_by_id(int(id))
        return [neighborhood]
    
    def _get_message_type(self):
        return 'neighborhood_forum_main_message'

    def _get_recipient_type(self):
        return 'neighborhood'
    
    def _get_render_path(self):
        return os.path.join(os.path.dirname(__file__),'..', 'views', 'messages', 'create_forumpost.html')

    def _is_forum_post(self):
        return True

    def _do_additional_post_processing(self, id, sender, params):
        neighborhood = Neighborhood.get_by_id(int(id))
        recips = dict([(v.key().id(),v) for v in neighborhood.home_neighborhood if v.key().id() != sender.key().id()])
        recips.update(dict([(v.key().id(),v) for v in neighborhood.work_neighborhood if v.key().id() != sender.key().id()]))
        recipients = recips.values()
        
        mt = MessageType.all().filter('name = ', 'neighborhood_forum').get()
        substitution_params = {
            'message_body': params['body'],
            'message_subject': params['subject'],
            'sender_name' : sender.name,
            'neighborhood_name': neighborhood.name,
            'neighborhood_url' : self._get_base_url() + neighborhood.url()
        }
        
        params['body'] = neighborhood_forum_txt.body%substitution_params
        params['subject'] = neighborhood_forum_txt.subject%substitution_params
        
        self._send_message(sender = sender, recipients = recipients, type = mt, params = params, autogen = True, forum = False)