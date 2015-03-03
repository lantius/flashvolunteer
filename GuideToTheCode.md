


In this document, the high level organization of the codebase is described. A number of descriptions of critical subsystems are also linked to. These subsystems tend to cross-cut the codebase. Note that some of the documentation may be out of date, but it should at least provide some general guidance.

And don't worry if you don't understand much of this document. Its a resource to come back to as you learn the codebase.

## High-level code organization ##

If you look at the code you've just [checked out from the SVN repository](SVNCheckout.md), you will see a number of directories. The most important directories are **models**, **views**, and **controllers**. In other words, our code follows a [model-view-controller architecture](http://en.wikipedia.org/wiki/Model_view_controller). This is hardly surprising, as Google App Engine runs a a highly modified version of [Django](http://en.wikipedia.org/wiki/Django_%28web_framework%29) as its web framework. Our code also follows a [RESTful](http://en.wikipedia.org/wiki/Representational_State_Transfer#RESTful_web_services) web services model.

To break down the directories you'll see:

  * **/models** The models represent the underlying objects and have some relatively complex methods to manage relationships.  The models are stored in the Appengine datastore. Note that we say datastore and not database. This is because the [Appengine datastore](http://code.google.com/appengine/docs/python/datastore/) is **not** a [relational database](http://en.wikipedia.org/wiki/Relational_database) in that you cannot use joins in your queries. Consequently, some of our Models are essentially frozen joins. See for example ` models.eventvolunteer ` and ` models.volunteerfollower `.
  * **/views** The views are the webpages (or pieces of webpages) that the end user interacts with.  They are built using the [Django templating system](http://docs.djangoproject.com/en/dev/ref/templates/builtins/).  We make heavy use of the extends and include directives to import reusable subtemplates. Note that Google App engine uses a [\*really\* old version of Django (.96)](http://code.google.com/appengine/docs/python/runtime.html#Pure_Python).
  * **/controllers** The controllers implement the logic -- mapping from the models to the views.  They include all of the display and update logic.  ` controllers.route ` is a special controller which controls which controllers a url is mapped to. Most other controllers possibly support the following methods. Not every controller currently follows this convention but that's the goal.
    * SHOW: Render a single model.  GET URL is /models/model\_id
    * LIST: List a number of the same model.  GET URL is /models/
    * NEW: Editing form for creating a new model. GET URL is /models/new
    * EDIT: Editing form for an existing model.  GET URL is /models/model\_id/edit
    * DELETE: Delete an existing model. POST URL is /models/model\_id with the isDelete parameter set.  (Would be HTTP delete if it was better supported.)
    * CREATE: Create a new model with the post data.  POST URL is /models/
    * UPDATE: Update an existing model with post data. POST URL is /models/model\_id

The other major folders in the codebase are:
  * /components - external modules that we're referencing, i.e. Sessions or Twitter
  * /gui\_integration\_tests - the Selenium-based integration tests. These are currently obsolete.
  * /stylesheets - css, js, and image files. name is a little misleading and it seriously needs cleanup.
  * /test - GAEUnit-based unit tests that are embarrassingly out of date.

In the root, you will also find a few important files:
  * **` app.yaml `** This defines the google app engine application ID and version that is currently being used (should generally be _flashvolunteer-dev_ / _development_ unless deploying to the real site). Also defines the controllers and access rules that govern different aspects of the site. Go [here](TestingDeploying.md) to read about how to deploy the site to www.flashvolunteer.org or www.development.flashvolunteer.org.
  * **` cron.yaml `** Defines jobs that will be run at certain intervals. Go [here](http://code.google.com/appengine/docs/python/config/cron.html) for general info on cron jobs.
  * **` index.yaml `** Defines the indexes on the datastore. Don't worry about this unless you're modifying the models.
  * **` queue.yaml `** Defined [task queues](http://code.google.com/appengine/docs/python/config/queue.html). Don't worry about this :)

## Subsystems ##

Some descriptions of the subsystems at work. Most of the descriptions actually don't exist though :)
  * [messaging](http://code.google.com/p/flashvolunteer/wiki/communicationPlatform)
  * applications
  * social network
  * abstract handler
  * sessions
  * [login](http://code.google.com/p/flashvolunteer/wiki/LoginAuthentication?ts=1266817592&updated=LoginAuthentication)
  * [All For Good integration](http://code.google.com/p/flashvolunteer/wiki/AllforGoodIntegration?ts=1266816821&updated=AllforGoodIntegration)
  * [Full-text search](FullTextSearch.md)