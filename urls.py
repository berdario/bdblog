from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	(r'^admin/', include(admin.site.urls)),
	(r'^blog/', include('berdar.bdblog.urls')),
	(r'^publish/', include('berdar.bdblog.urls'), {'admin': True})
)
