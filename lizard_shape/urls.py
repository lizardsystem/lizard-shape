# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf import settings
from django.conf.urls.defaults import include, patterns, url
from django.contrib import admin

from lizard_ui.urls import debugmode_urlpatterns

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$',
     'lizard_shape.views.homepage',
     name='lizard_shape.homepage'),
    url(r'^category/(?P<root_slug>.*)/$',
     'lizard_shape.views.homepage',
     name='lizard_shape.homepage'),
    (r'^map/', include('lizard_map.urls')),
    )

urlpatterns += debugmode_urlpatterns()

if settings.DEBUG:
    # Add this also to the projects that use this application
    urlpatterns += patterns(
        '',
        (r'^admin/', include(admin.site.urls)),
    )
