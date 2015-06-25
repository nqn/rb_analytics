rb_analytics
============

### Generate outstanding stale reviews email

```
$ python fetch_rrs.py # Populates reviews.db
$ python mail_rrs.py # Will output mail_rrs.html
$ python send_mail.py mail_rrs.html <from email> <to email>
```

### Generate 'given reviews' emails
```
$ python fetch_rrs.py full # Populates reviews.db
$ python fetch_reviews.py # Fetch reviews for all review requests
$ python send_mail.py mail_reviews.html <from email> <to email>
```

### Sending emails

See the README.rst file in the ``mailer`` folder; use the
``send`` bash wrapper.

### Running tests

Unit tests in this projects can be run with [nose](http://nose.readthedocs.org),
just run:
```
nose tests/
```
from the root folder.

