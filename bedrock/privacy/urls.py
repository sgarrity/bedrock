# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.conf.urls import patterns, url

from bedrock.mozorg.util import page
from bedrock.privacy import views

urlpatterns = patterns('',
    url(r'^/$', views.privacy, name='privacy'),
    page('/you', 'privacy/privacy-day.html'),
    page('/principles', 'privacy/principles.html'),
    page('/firefox', 'privacy/notices/firefox.html'),
    page('/firefox-os', 'privacy/notices/firefox-os.html'),
    page('/websites', 'privacy/notices/websites.html'),
    url(r'^/facebook/$', views.facebook, name='privacy/facebook'),

    page('/archive', 'privacy/archive/index.html'),
    page('/archive/firefox/2006-10', 'privacy/archive/firefox-2006-10.html'),
    page('/archive/firefox/2008-06', 'privacy/archive/firefox-2008-06.html'),
    page('/archive/firefox/2009-01', 'privacy/archive/firefox-2009-01.html'),
    page('/archive/firefox/2009-09', 'privacy/archive/firefox-2009-09.html'),
    page('/archive/firefox/2010-01', 'privacy/archive/firefox-2010-01.html'),
    page('/archive/firefox/2010-12', 'privacy/archive/firefox-2010-12.html'),
    page('/archive/firefox/2011-06', 'privacy/archive/firefox-2011-06.html'),
    page('/archive/firefox/2012-06', 'privacy/archive/firefox-2012-06.html'),
    page('/archive/firefox/2012-09', 'privacy/archive/firefox-2012-09.html'),
    page('/archive/firefox/2012-12', 'privacy/archive/firefox-2012-12.html'),
    page('/archive/firefox/2013-05', 'privacy/archive/firefox-2013-05.html'),
    page('/archive/firefox/third-party', 'privacy/archive/firefox-third-party.html'),
)
