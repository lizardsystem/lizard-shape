# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf import settings
from django.conf.urls.defaults import include, patterns, url
from django.contrib import admin

from lizard_ui.urls import debugmode_urlpatterns
from lizard_shape.views import HomepageView

urlpatterns = patterns(
    '',
    url(r'^$',
     HomepageView.as_view(),
     name='lizard_shape.homepage'),
    url(r'^category/(?P<root_slug>.*)/$',
     HomepageView.as_view(),
     name='lizard_shape.homepage'),
    )

if getattr(settings, 'LIZARD_SHAPE_STANDALONE', False):
    admin.autodiscover()
    urlpatterns += patterns(
        '',
        (r'^map/', include('lizard_map.urls')),
        (r'^admin/', include(admin.site.urls)),
    )
    urlpatterns += debugmode_urlpatterns()
