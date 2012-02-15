from django.conf import settings
from django.conf.urls.defaults import *
from django.conf.urls.static import static

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	(r'^admin/', include(admin.site.urls)),
	(r'^blog/', include('berdar.bdblog.urls')),
	(r'^publish/', include('berdar.bdblog.urls'), {'admin': True}),
	(r'^getinto/', include('django_openid_auth.urls'))
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
