import os, logging

from google.appengine.ext import webapp, db


import wsgiref.handlers

from controllers.admin.migrate_datastore import MigrateDatastore
from controllers.admin.cron_jobs.message_dispatcher import MessageDispatcher
from controllers.admin.cron_jobs.event_message_factory import EventMessageFactory, RecommendedEventMessageFactory
from controllers.admin.site_wide_message import SiteWideMessage
from controllers.admin.custom_query import CustomQueryHandler
from controllers.admin.sync_with_mail_chimp import SyncWithMailChimp

from controllers.admin.afg_interface import AllForGoodInterface

from controllers.settings import SettingsPage
from controllers.admin.home import AdminPage

webapp.template.register_template_library('templatetags.filters')


def main():
    application = webapp.WSGIApplication([
        ('/admin', AdminPage),
        ('/admin/migrate', MigrateDatastore),
        ('/admin/send_message', SiteWideMessage),
        ('/admin/afg_interface(|/rebuild|/publish|/dismiss)', AllForGoodInterface),
        
        ('/admin/cron_jobs/message_dispatch', MessageDispatcher),
        ('/admin/cron_jobs/event_message_factory', EventMessageFactory),
        ('/admin/cron_jobs/recommended_events_message_factory', RecommendedEventMessageFactory),
          
        ('/admin/custom_query', CustomQueryHandler),
        
        ('/admin/sync_with_mail_chimp', SyncWithMailChimp),
    ], debug=True)

    wsgiref.handlers.CGIHandler().run(application)
    
if __name__ == '__main__':
    main()