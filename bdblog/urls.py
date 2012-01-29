from django.conf.urls.defaults import *
from views import index, post, posts, tags, publish_post
urlpatterns = patterns('',
	(r'^(page(?P<page>\d+)/)?$', index),
	(r'^(?P<year>\d{4})/((?P<month>\d{1,2}|\w{3,9})/((?P<day>\d{1,2})/)?)?(page(?P<page>\d+)/)?$', posts),
	(r'^tag/(?P<tags>\w[\w\+]+\w)/(page(?P<page>\d+)/)?$', tags, {'separator': "_"}),
	(r'^tag/(?P<tags>\w[\w\+\.]+\w)/(page(?P<page>\d+)/)?$', tags),
	(r'^publish/$', publish_post),
	(r'^((?P<year>\d{4})/(?P<month>\d{1,2}|\w{3,9})/(?P<day>\d{1,2})/)?(?P<slug>\w+[\w-]+\w+)/$', post),
)
