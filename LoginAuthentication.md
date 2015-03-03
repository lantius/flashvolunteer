

This article is basically just notes.

We have two methods of authenticating: using RPXnow to login through a third party account (e.g. google, facebook) or an FV account.

We have a few Models that relate to this process:
  * ` models.auth.auth ` A mapping from an authentication method to an ` Account `. Many auth objects can map to a single ` Account `. An {{Auth}} object stores the login strategy (e.g. Google, FV, Facebook). If its a FV account, an encrypted password is stored, as well as the salt (which is the session id at the time of account creation).
  * ` Account `. This has basic information, like the User, name, email. Multiple Auth objects can map to an Account.
  * ` Volunteer ` and ` Organization ` models are each associated with an Account.

This system gives us leverage for allowing people to authenticate through
multiple services (Facebook, fv, etc), while linking to the same account. We
can detect if two accounts (or if a new auth method) is associated with the
same email, whereup we can prompt the user if they want to link the
accounts. Note that our system doesn't have that intelligence built in yet,
but it should be pretty straight forward to add.