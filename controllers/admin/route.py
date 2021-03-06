import os, logging

from google.appengine.ext import webapp, db


import wsgiref.handlers

from controllers.admin.migrate_datastore import MigrateDatastore
from controllers.admin.cron_jobs.message_dispatcher import MessageDispatcher
from controllers.admin.cron_jobs.stats_gen import StatsGen
from controllers.admin.cron_jobs.mem_cache import MemCache

from controllers.admin.cron_jobs.event_message_factory import EventMessageFactory, RecommendedEventMessageFactory
from controllers.admin.site_wide_message import SiteWideMessage
from controllers.admin.custom_query import CustomQueryHandler
from controllers.admin.sync_with_mail_chimp import SyncWithMailChimp
from controllers.admin.sync_application import SyncApplication


from controllers.admin.afg_interface import AllForGoodInterface

from controllers.settings import SettingsPage
from controllers.admin.home import AdminPage
from controllers.admin.newusers import NewUsersPage

from components.appengine_admin.views import Admin as AppEngineAdmin

from controllers.search_katz.searchadmin import SearchAdmin

webapp.template.register_template_library('controllers._filters')

from google.appengine.ext.webapp.util import run_wsgi_app


def main():
    application = webapp.WSGIApplication([
        ('/admin', AdminPage),
        ('/admin/migrate', MigrateDatastore),
        ('/admin/newusers', NewUsersPage),
        ('/admin/send_message', SiteWideMessage),
        ('/admin/afg_interface(|/rebuild|/publish|/dismiss)', AllForGoodInterface),
        
        ('/admin/cron_jobs/message_dispatch', MessageDispatcher),
        ('/admin/cron_jobs/event_message_factory', EventMessageFactory),
        ('/admin/cron_jobs/recommended_events_message_factory', RecommendedEventMessageFactory),
        ('/admin/searchadmin(.*)', SearchAdmin),
        ('/admin/cron_jobs/stats_gen', StatsGen),
        ('/admin/cron_jobs/mem_cache', MemCache),
          
        ('/admin/custom_query', CustomQueryHandler),
        
        ('/admin/sync_with_mail_chimp', SyncWithMailChimp),
        ('/admin/sync_with_mail_chimp', SyncApplication),

        (r'^(/admin/proj)(.*)$', AppEngineAdmin),
        
    ], debug=True)

    run_wsgi_app(application)
    
if __name__ == '__main__':
    main()