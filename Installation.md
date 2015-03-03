

Guide for installing the software necessary for doing development on Flash Volunteer.


## Install Python & Google App Engine ##

Follow the directions at http://code.google.com/appengine/docs/python/gettingstarted/devenvironment.html.

Here are some misc notes by people who have had problems:

  * If you have problems and you're on OSX, you may have a few versions of Python installed. /usr/bin/python determines which version to start.  Use 'defaults write com.apple.versioner.python Version 2.5' to keep 2.5 system-wide, or the env var VERSIONER\_PYTHON\_VERSION=2.5 to interpret with /usr/bin/python2.5.
  * ` dev_appserver.py ` complains if it can't import the Python Imaging Library (PIL) modules, but it doesn't seem to affect anything negatively. But the module isn't really required for many things, so you're fine if you don't have it.
  * GAE SDK includes the correct versions of extra Python modules imported by the environment: PyYAML, Django, Web Obj, Antlr. You can install these into python's site packages, but you only need to do this if you want to be able to run a few of the accessory scripts like ` migrate_datastore.py `. You can do this by running ` /usr/local/google_appengine/lib/yaml/setup.py install `, etc as needed (although you may have to unzip the ` .egg `s in site\_packages manually after that).
  * If you have Python 2.6, logging **might** be messed up. See http://code.google.com/appengine/articles/logging.html. Here's a workaround:
> > ` http://localhost:8080/events?debug `
```
    import logging 
    logging.logMultiprocessing = 0 #needed to avoid problems with Python 2.6
```


## Set your environment variables ##

  * Add the GAE root to your PYTHONPATH environment variable. For me, the path is: ` /usr/local/google_appengine/ `.

## Get an SVN client ##

If you do not already have an SVN client, install one.

I personally use CollabNet: http://www.collab.net/downloads/subversion/. Note that the OSX binary is under the "community" section.

## IDE ##

Maybe you're an emacs or VI hacker. Great, go to town.

For the rest of us, I recommend using the [Eclipse IDE](http://www.eclipse.org/).

Directions for installing, configuring, and using Eclipse with FlashVolunteer can be found [here](WorkingInEclipse.md).