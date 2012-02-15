from django.conf import settings
from django.conf.urls.defaults import *
from django.conf.urls.static import static

from django.contrib.auth.views import logout_then_login
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
	#(r'^admin/', include(admin.site.urls)),
	(r'^blog/', include('berdar.bdblog.urls')),
	(r'^publish/', include('berdar.bdblog.urls'), {'admin': True}),
	(r'^getinto/logout/', logout_then_login),
	(r'^getinto/', include('django_openid_auth.urls'))
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
