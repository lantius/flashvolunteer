# Steps #

  1. Visit http://www.everydns.com/ (get name/password from Travis)
    1. Add new CNAME record (fully qual name: e.g. www.pierce-county.flashvolunteer.org; record val = ghs.google.com)
  1. go to flashvolunteer google apps account (https://www.google.com/a/cpanel/flashvolunteer.org/Dashboard)
    1. go to service-settings=>flashvolunteer (app engine)
    1. add URL (e.g. www.pierce-county)
  1. add your application def to controllers.applications.defs.regions (if its not a region, we'll need to create another similar module)
  1. add your app to the import in controllers.applications.defs.init
  1. make sure that controllers.admin.migrate\_datastore is going to invoke add\_applications from controllers.applications.operations
  1. visit /admin/migrate while logged in as an admin
