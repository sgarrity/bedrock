# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.conf.urls import patterns, url

from bedrock.mozorg.util import page
from bedrock.legal import views

urlpatterns = patterns('',
    page('', 'legal/index.html'),

    page('eula', 'legal/eula.html'),
    page('eula/firefox-2', 'legal/eula/firefox-2-eula.html'),
    page('eula/firefox-3', 'legal/eula/firefox-3-eula.html'),

    page('firefox', 'legal/firefox.html'),

    page('terms/mozilla', 'legal/terms/mozilla.html'),
    page('terms/persona', 'legal/terms/persona.html'),

    page('licensing', 'legal/licensing.html'),
    page('licensing/website-content', 'legal/licensing/website-content.html'),
    page('licensing/website-markup', 'legal/licensing/website-markup.html'),
    page('licensing/binary-components', 'legal/licensing/binary-components.html'),
    page('licensing/binary-components/rationale', 'legal/licensing/binary-components-rationale.html'),

    page('trademarks', 'legal/trademarks.html'),
    page('trademarks/policy', 'legal/trademarks/policy.html'),
    page('trademarks/list', 'legal/trademarks/list.html'),
    page('trademarks/faq', 'legal/trademarks/faq.html'),
    page('trademarks/l10n-website-policy', 'legal/trademarks/l10n-website-policy.html'),
    page('trademarks/distribution-policy', 'legal/trademarks/distribution-policy.html'),
    page('trademarks/community-edition-permitted-changes', 'legal/trademarks/community-edition-permitted-changes.html'),
    page('trademarks/community-edition-policy', 'legal/trademarks/community-edition-policy.html'),
    page('trademarks/poweredby/faq', 'legal/trademarks/poweredby/faq.html'),

    url('^fraud-report/$', views.fraud_report, name='legal.fraud-report'),
)
