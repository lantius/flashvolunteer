


Testing and deploying your code can be a difficult task. This article gives some hints.

Also, to be clear, **checking your code into the SVN repository does NOT deploy your code to the App Engine site**.

## Testing ##

You've just coded up a new controller and view. How do you check if its working properly?

There are two ways you'll want to test it out: (1) run the local google app engine development server and/or (2) deploy the code to www.development.flashvolunteer.org. Typically you would do (1) first, and (2) when you're reasonably sure about your code.

### Running the local development server ###

The development server allows you to run a web server on your machine so that you can debug your code. Changes that you make to the code can be immediately seen in your web browser (after refresh of course).

Details can be found [here](http://code.google.com/appengine/docs/python/tools/devserver.html).

**IMPORTANT** There is a super important caveat for running the local dev server on Flash Volunteer code. You **MUST** edit the ` host ` variable in ` gui_integration_tests.test_settings ` before testing, or appengine will serve blank pages! You should set ` host ` to be the same as the address/port that the development server is running on.

You can start the dev server by:
  * dev\_appserver.py _dir-to-flashvolunteer_
  * on pc: dev\_appserver.py _dir-to-flashvolunteer_ >flashvolunteer.log 2>&1 redirects output to flashvolunteer.log
  * or [through Eclipse](WorkingInEclipse.md)

Note that the cmd argument to dev\_appserver ` clear-datastore ` is useful for resetting the contents of the dev server's datastore.

The documentation about [working in Eclipse](WorkingInEclipse.md) gives some instructions for how to debug your code.

### Populating your local test environment with volunteers & events ###

After you get your development server up and running, you will notice that it is a very lonely Flash Volunteer system you are presented with. No Volunteers! No Events! No Neighborhoods! This also makes it tedious to test the features you're interested in.

To help with this, we have a test environment that can be reconstructed whenever you want. It is based on the American Revolutionary War, just for fun. Anyway, to populate your test environment with these colorful characters, run python on ` gui_integration_tests.datastore_interface `. On the command line, it would look like:
```
python /path/to/flash/volunteer/gui_integration_tests/datastore_interface.py
```

### Deploying to development.flashvolunteer.org ###

www.development.flashvolunteer.org is a Google App Engine hosted application. It has a separate datastore than www.flashvolunteer.org. We use it to test out our code before deploying to the main site. (technically, it is actually located at http://flashvolunteer-dev.appspot.com).

There are two advantages to testing stuff out here:
  1. The local development app server is different than the real google app engine server. Some things that work on the local dev server do not work on the real thing. www.development.flashvolunteer.org is the real thing.
  1. It is easy to share www.development.flashvolunteer.org with other people, including non-programmers. They can give feedback, find bugs, etc, ahead of launch.

In order to test your code on www.development.flashvolunteer.org, you need to [deploy your code there](#Deploying.md).

### FireBug ###

[FireBug](http://getfirebug.com/) is a Firefox extension that is indispensable for analyzing the DOM structure of any webpage (particularly the one you're trying to build!), debugging Javascript (yes, even with breakpoints), and examining AJAX requests.

## Deploying ##

Deploying is when you publish source code to Google App Engine. This will update the code that is running on the remote server. Note that when you deploy you are **uploading your local FV code** not the code that is currently in the SVN repository! Some details about deploying can be found [here](http://code.google.com/appengine/docs/java/gettingstarted/uploading.html).

The location to which you are deploying is controlled in the ` app.yaml ` file in the root of your Flash Volunteer directory, specifically the "application-id" and "version" field. Go [here](http://code.google.com/appengine/docs/python/config/appconfig.html) for a description.

For us, we have two possible applications:

|flashvolunteer|http://www.flashvolunteer.org|http://flashvolunteer.appspot.com|production site|
|:-------------|:----------------------------|:--------------------------------|:--------------|
|flashvolunteer-dev|http://www.development.flashvolunteer.org|http://flashvolunteer-dev.appspot.com|development site|

You should stick with ` flashvolunteer-dev `/` development ` unless you know what you're doing.

I suggest using the Google App Engine Launcher ([mac](http://googleappengine.blogspot.com/2008/05/app-engine-launcher-for-mac-os-x.html), [windows](http://googleappengine.blogspot.com/2009/09/app-engine-launcher-for-windows.html)) for deploying. It comes packaged in the Google App Engine SDK that you've already installed.

## Migrating the datastore ##

When you change the structure of a Model, you are essentially modifying the database schema. Consequently, if you deploy that code, then the model data stored in the hosted datastore may need to be updated to accommodate the new schema. Here is some [documentation](Migration.md) about what to do in this case.