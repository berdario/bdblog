from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	(r'^admin/', include(admin.site.urls)),
	(r'^blog/', include('berdar.blog.urls')),
	(r'^publish/', include('berdar.blog.urls'), {'admin': True})
)
