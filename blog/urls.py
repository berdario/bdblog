from django.conf.urls.defaults import *
from views import test
urlpatterns = patterns('',
	(r'^$', test),
	(r'^(?P<year>\d{4})/$', test),
	(r'^(?P<year>\d{4})/(?P<month>\d{1,2}|\w{3,9})/$', test),
	(r'^(?P<year>\d{4})/(?P<month>\d{1,2}|\w{3,9})/(?P<day>\d{1,2})/$', test),
	(r'^((?P<year>\d{4})/(?P<month>\d{1,2}|\w{3,9})/(?P<day>\d{1,2})/)?(?P<slug>\w+[\w-]+\w+)/$', test),	
)
