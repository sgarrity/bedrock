# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from os import path
import re
import StringIO

from lib import l10n_utils
from funfactory.settings_base import path as base_path
import jingo
import markdown as md
from bs4 import BeautifulSoup

from django.core.mail import EmailMessage
from django.shortcuts import redirect
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_protect

from funfactory.urlresolvers import reverse

from forms import FraudReportForm


FRAUD_REPORT_EMAIL_FROM = 'Mozilla.com <noreply@mozilla.com>'
FRAUD_REPORT_EMAIL_SUBJECT = 'New violating website report'
FRAUD_REPORT_EMAIL_TO = ['trademarks@mozilla.com', 'mozilla@mofo.com']

LEGAL_DOCS_PATH = base_path('vendor-local', 'src', 'legal-docs')



def load_legal_doc(request, doc_name):
    """
    Load a static Markdown file and return the document as a BeautifulSoup
    object for easier manipulation.
    """
    locale = l10n_utils.get_locale(request)
    source = path.join(LEGAL_DOCS_PATH, doc_name, locale + '.md')
    output = StringIO.StringIO()

    if not path.exists(source):
        source = path.join(LEGAL_DOCS_PATH, doc_name, 'en-US.md')

    # Parse the Markdown file
    md.markdownFromFile(input=source, output=output,
                        extensions=['attr_list', 'outline(wrapper_cls=)'])
    content = output.getvalue().decode('utf8')
    output.close()

    soup = BeautifulSoup(content)
    hn_pattern = re.compile(r'^h(\d)$')
    href_pattern = re.compile(r'^https?\:\/\/www\.mozilla\.org')

    # Manipulate the markup
    for section in soup.find_all('section'):
        level = 0
        header = soup.new_tag('header')
        div = soup.new_tag('div')

        section.insert(0, header)
        section.insert(1, div)

        # Append elements to <header> or <div>
        for tag in section.children:
            match = hn_pattern.match(tag.name)
            if match:
                header.append(tag)
                level = int(match.group(1))
            if tag.name == 'p':
                (header if level == 1 else div).append(tag)
            if tag.name in ['ul', 'hr']:
                div.append(tag)

        if level > 3:
            section.parent.div.append(section)

        # Remove empty <div>s
        if len(div.contents) == 0:
            div.extract()

    # Convert the site's full URLs to absolute paths
    for link in soup.find_all(href=href_pattern):
        link['href'] = href_pattern.sub('', link['href'])

    # Return the HTML flagment as a BeautifulSoup object
    return soup


@cache_page(60 * 60)  # cache for 1 hour
def firefox_terms(request):
    return l10n_utils.render(request, 'legal/terms/firefox.html',
                             {'doc': load_legal_doc(request, 'firefox_about_rights')})


def submit_form(request, form):
    form_submitted = True

    if form.is_valid():
        form_error = False

        subject = FRAUD_REPORT_EMAIL_SUBJECT
        sender = FRAUD_REPORT_EMAIL_FROM
        to = FRAUD_REPORT_EMAIL_TO
        msg = jingo.render_to_string(request, 'legal/emails/fraud-report.txt', form.cleaned_data)

        email = EmailMessage(subject, msg, sender, to)

        attachment = form.cleaned_data['input_attachment']

        if (attachment):
            email.attach(attachment.name, attachment.read(), attachment.content_type)

        email.send()
    else:
        form_error = True

    return {'form_submitted': form_submitted, 'form_error': form_error}


@csrf_protect
def fraud_report(request):
    form = FraudReportForm(auto_id='%s')

    form_submitted = False
    form_error = False

    if request.method == 'POST':
        form = FraudReportForm(request.POST, request.FILES)
        form_results = submit_form(request, form)

        form_submitted = form_results['form_submitted']
        form_error = form_results['form_error']

    template_vars = {
        'form': form,
        'form_submitted': form_submitted,
        'form_error': form_error,
    }

    if request.POST and not form_error:
        # Seeing the form was submitted without error, redirect, do not simply
        # send a response to avoid problem described below.
        # @see https://bugzilla.mozilla.org/show_bug.cgi?id=873476 (3.2)
        response = redirect(reverse('legal.fraud-report'), template_vars)
        response['Location'] += '?submitted=%s' % form_submitted

        return response
    else:
        # If the below is called after a redirect the template_vars will be lost, therefore
        # we need to update the form_submitted state from the submitted url parameter.
        submitted = request.GET.get('submitted') == 'True'
        template_vars['form_submitted'] = submitted
        return l10n_utils.render(request, 'legal/fraud-report.html', template_vars)
