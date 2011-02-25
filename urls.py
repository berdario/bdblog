from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	(r'^publish/', include(admin.site.urls)),
	(r'^blog/', include('berdar.blog.urls'))
)
