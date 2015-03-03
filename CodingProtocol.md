## Protocol ##

The general design strategy has been one of rapid iteration.  There's plenty of code in need of refactoring - even the primary developers are still learning the intricacies of Appengine and Python on this project. Be attentive to code quality, but also be bold -- make changes confidently as we can deal with their implications **afterwards**.

Be sure to ask someone if you're having trouble. We'd rather help you solve something and get onto fun stuff than have you waste hours laboring alone.

## Some tips ##

Very misc tips/pointers. Feel free to add your own.
  * django debugging: template.render(path, template\_values, debug=True) change in code
  * development console: access local datastore, interactive console
> > ` http://localhost:8080/_ah/admin/datastore `
  * access remote datastore: remote\_api - http://code.google.com/appengine/articles/remote_api.html, command line access