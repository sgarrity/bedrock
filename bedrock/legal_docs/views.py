# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from os import path
import re
import StringIO

from django.conf import settings
from django.http import Http404
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView

import markdown as md
from bs4 import BeautifulSoup

from bedrock.settings import path as base_path
from lib import l10n_utils

LEGAL_DOCS_PATH = base_path('vendor-local', 'src', 'legal-docs')
HN_PATTERN = re.compile(r'^h(\d)$')
HREF_PATTERN = re.compile(r'^https?\:\/\/www\.mozilla\.org')
CACHE_TIMEOUT = getattr(settings, 'LEGAL_DOCS_CACHE_TIMEOUT', 60 * 60)


def get_legal_doc_content(doc_name, locale):
    """
    Return the HTML content of a legal doc in the requested locale.

    :param doc_name: name of the legal doc folder
    :param locale: preferred language version of the doc
    :return: string content of the file or None
    """
    source = path.join(LEGAL_DOCS_PATH, doc_name, locale + '.md')
    output = StringIO.StringIO()
    if not path.exists(source):
        source = path.join(LEGAL_DOCS_PATH, doc_name, 'en-US.md')

    try:
        # Parse the Markdown file
        md.markdownFromFile(input=source, output=output,
                            extensions=['attr_list', 'outline(wrapper_cls=)'])
        content = output.getvalue().decode('utf8')
    except IOError:
        return None
    finally:
        output.close()

    return content


def load_legal_doc(doc_name, locale):
    """
    Load a static Markdown file and return the document as a BeautifulSoup
    object for easier manipulation.

    :param: doc_name String name of the folder containing the documents.
    :param: locale Language version of the document requested.
    """
    content = get_legal_doc_content(doc_name, locale)
    if content is None:
        return None

    soup = BeautifulSoup(content)

    # Manipulate the markup
    for section in soup.find_all('section'):
        level = 0
        header = soup.new_tag('header')
        div = soup.new_tag('div')

        section.insert(0, header)
        section.insert(1, div)

        # Append elements to <header> or <div>
        for tag in section.children:
            match = HN_PATTERN.match(tag.name)
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
    for link in soup.find_all(href=HREF_PATTERN):
        link['href'] = HREF_PATTERN.sub('', link['href'])

    # Return the HTML fragment as a BeautifulSoup object
    return soup


class LegalDocView(TemplateView):
    """
    Generic view for loading a legal doc and displaying it with a template.

    Class attributes in addition to standard Django TemplateView:

    * legal_doc_name: The name of the folder in the legal_docs repo.
    * legal_doc_context_name: (default 'doc') template variable name for legal doc.

    This view automatically adds the `cache_page` decorator. The default timeout
    is 1 hour, configurable by setting the `LEGAL_DOCS_CACHE_TIMEOUT` setting to change
    the default for all views, or the `cache_timeout` property for an single instance.

    See `bedrock/privacy/views.py` for usage examples.
    """
    legal_doc_name = None
    legal_doc_context_name = 'doc'
    cache_timeout = CACHE_TIMEOUT

    def render_to_response(self, context, **response_kwargs):
        response_kwargs.setdefault('content_type', self.content_type)
        return l10n_utils.render(self.request,
                                 self.get_template_names()[0],
                                 context, **response_kwargs)

    def get_context_data(self, **kwargs):
        locale = l10n_utils.get_locale(self.request)
        legal_doc = load_legal_doc(self.legal_doc_name, locale)
        if legal_doc is None:
            raise Http404('Legal doc not found')

        context = super(LegalDocView, self).get_context_data(**kwargs)
        context[self.legal_doc_context_name] = legal_doc
        return context

    @classmethod
    def as_view(cls, **initkwargs):
        cache_timeout = initkwargs.pop('cache_timeout', cls.cache_timeout)
        return cache_page(cache_timeout)(super(LegalDocView, cls).as_view(**initkwargs))
