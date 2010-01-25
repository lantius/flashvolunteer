import os, logging

from google.appengine.ext import webapp, db


import wsgiref.handlers

from controllers.admin.migrate_datastore import MigrateDatastore
from controllers.admin.message_dispatcher import MessageDispatcher
from controllers.admin.event_message_factory import EventMessageFactory, RecommendedEventMessageFactory
from controllers.admin.site_wide_message import SiteWideMessage

from controllers.admin.afg_interface import AllForGoodInterface

from controllers.settings import SettingsPage
from controllers.admin.home import AdminPage

webapp.template.register_template_library('templatetags.filters')


def main():
    session = self._session()
    application = webapp.WSGIApplication([
        ('/admin', AdminPage),
        ('/admin/migrate', MigrateDatastore),
        ('/admin/message_dispatch', MessageDispatcher),
        ('/admin/event_message_factory', EventMessageFactory),
        ('/admin/recommended_events_message_factory', RecommendedEventMessageFactory),
        ('/admin/send_message', SiteWideMessage),
        
        ('/admin/afg_interface(|/rebuild|/publish|/dismiss)', AllForGoodInterface),
        #TODO: route here? admin tools
          
    ], debug=True)

    wsgiref.handlers.CGIHandler().run(application)
    
if __name__ == '__main__':
    main()