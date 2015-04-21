# coding: utf-8

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from operator import itemgetter

import re
from datetime import datetime
from random import randrange

from django import forms
from django.forms import widgets
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

import basket
from basket.base import request

from lib.l10n_utils.dotlang import _
from lib.l10n_utils.dotlang import _lazy
from product_details import product_details

from .email_contribute import INTEREST_CHOICES


FORMATS = (('H', _lazy('HTML')), ('T', _lazy('Text')))
LANGS_TO_STRIP = ['en-US', 'es']
PARENTHETIC_RE = re.compile(r' \([^)]+\)$')
LANG_FILES = ['firefox/partners/index', 'mozorg/contribute', 'mozorg/contribute/index']


def strip_parenthetical(lang_name):
    """
    Remove the parenthetical from the end of the language name string.
    """
    return PARENTHETIC_RE.sub('', lang_name, 1)


class SideRadios(widgets.RadioFieldRenderer):
    """Render radio buttons as labels"""

    def render(self):
        radios = [unicode(w) for idx, w in enumerate(self)]

        return mark_safe(''.join(radios))


class PrivacyWidget(widgets.CheckboxInput):
    """Render a checkbox with privacy text. Lots of pages need this so
    it should be standardized"""

    def render(self, name, value, attrs=None):
        attrs['required'] = 'required'
        input_txt = super(PrivacyWidget, self).render(name, value, attrs)

        policy_txt = _(u'I’m okay with Mozilla handling my info as explained '
                       u'in <a href="%s">this Privacy Policy</a>')
        return mark_safe(
            '<label for="%s" class="privacy-check-label">'
            '%s '
            '<span class="title">%s</span></label>'
            % (attrs['id'], input_txt,
               policy_txt % reverse('privacy'))
        )


class HoneyPotWidget(widgets.TextInput):
    """Render a text field to (hopefully) trick bots. Will be used on many pages."""

    def render(self, name, value, attrs=None):
        honeypot_txt = _(u'Leave this field empty.')
        # semi-randomized in case we have more than one per page.
        # this is maybe/probably overthought
        honeypot_id = 'office-fax-' + str(randrange(1001)) + '-' + str(datetime.now().strftime("%Y%m%d%H%M%S%f"))
        return mark_safe(
            '<div class="super-priority-field">'
            '<label for="%s">%s</label>'
            '<input type="text" name="office_fax" id="%s">'
            '</div>' % (honeypot_id, honeypot_txt, honeypot_id))


class URLInput(widgets.TextInput):
    input_type = 'url'


class EmailInput(widgets.TextInput):
    input_type = 'email'


class DateInput(widgets.DateInput):
    input_type = 'date'


class TimeInput(widgets.TimeInput):
    input_type = 'time'


class TelInput(widgets.TextInput):
    input_type = 'tel'


class NumberInput(widgets.TextInput):
    input_type = 'number'


class L10nSelect(forms.Select):
    def render_option(self, selected_choices, option_value, option_label):
        if option_value == '':
            option_label = u'-- {0} --'.format(_('select'))
        return super(L10nSelect, self).render_option(selected_choices, option_value, option_label)


class ContributeSignupForm(forms.Form):
    required_attr = {'required': 'required'}
    empty_choice = ('', '')
    category_choices = (
        ('coding', _lazy('Coding')),
        ('testing', _lazy('Testing')),
        ('writing', _lazy('Writing')),
        ('teaching', _lazy('Teaching')),
        ('helping', _lazy('Helping')),
        ('translating', _lazy('Translating')),
        ('activism', _lazy('Activism')),
        ('dontknow', _lazy(u'I don’t know')),
    )
    coding_choices = (
        empty_choice,
        ('coding-firefox', _lazy('Firefox')),
        ('coding-firefoxos', _lazy('Firefox OS')),
        ('coding-websites', _lazy('Websites')),
        ('coding-addons', _lazy('Firefox add-ons')),
        ('coding-marketplace', _lazy('HTML5 apps')),
        ('coding-webcompat', _lazy('Diagnosing Web compatibility issues')),
        ('coding-cloud', _lazy('Online services')),
    )
    testing_choices = (
        empty_choice,
        ('testing-firefox', _lazy('Firefox and Firefox OS')),
        ('testing-addons', _lazy('Firefox add-ons')),
        ('testing-marketplace', _lazy('HTML5 apps')),
        ('testing-websites', _lazy('Websites')),
        ('testing-webcompat', _lazy('Web compatibility')),
    )
    translating_choices = (
        empty_choice,
        ('translating-products', _lazy('Products')),
        ('translating-websites', _lazy('Websites')),
        ('translating-tools', _lazy(u'I’d like to work on localization tools')),
    )
    writing_choices = (
        empty_choice,
        ('writing-social', _lazy('Social media')),
        ('writing-journalism', _lazy('Journalism')),
        ('writing-techusers', _lazy('Technical docs for users')),
        ('writing-techdevs', _lazy('Technical docs for developers')),
        ('writing-addons', _lazy('Technical docs for Firefox add-ons')),
        ('writing-marketplace', _lazy('Technical docs for HTML5 apps')),
    )
    teaching_choices = (
        empty_choice,
        ('teaching-webmaker', _lazy('Teach the Web (Webmaker)')),
        ('teaching-fellowships', _lazy('Open News fellowships')),
        ('teaching-hive', _lazy('Hive - Community networks of educators/mentors')),
        ('teaching-science', _lazy('Open Web science research')),
    )

    email = forms.EmailField(widget=EmailInput(attrs=required_attr))
    privacy = forms.BooleanField(widget=PrivacyWidget)
    category = forms.ChoiceField(choices=category_choices,
                                 widget=forms.RadioSelect(attrs=required_attr))
    area_coding = forms.ChoiceField(choices=coding_choices, required=False, widget=L10nSelect)
    area_testing = forms.ChoiceField(choices=testing_choices, required=False, widget=L10nSelect)
    area_translating = forms.ChoiceField(choices=translating_choices, required=False,
                                         widget=L10nSelect)
    area_writing = forms.ChoiceField(choices=writing_choices, required=False, widget=L10nSelect)
    area_teaching = forms.ChoiceField(choices=teaching_choices, required=False, widget=L10nSelect)
    name = forms.CharField(widget=forms.TextInput(attrs=required_attr))
    message = forms.CharField(widget=forms.Textarea, required=False)
    newsletter = forms.BooleanField(required=False)
    format = forms.ChoiceField(widget=forms.RadioSelect(attrs=required_attr), choices=(
        ('H', _lazy('HTML')),
        ('T', _lazy('Text')),
    ))

    def __init__(self, locale, *args, **kwargs):
        regions = product_details.get_regions(locale)
        regions = sorted(regions.iteritems(), key=itemgetter(1))
        regions.insert(0, self.empty_choice)
        super(ContributeSignupForm, self).__init__(*args, **kwargs)
        self.locale = locale
        self.fields['country'] = forms.ChoiceField(choices=regions, widget=L10nSelect)

    def clean(self):
        cleaned_data = super(ContributeSignupForm, self).clean()
        category = cleaned_data.get('category')
        # only bother if category was supplied
        if category:
            area_name = 'area_' + category
            if area_name in cleaned_data and not cleaned_data[area_name]:
                required_message = self.fields[area_name].error_messages['required']
                self._errors[area_name] = self.error_class([required_message])
                del cleaned_data[area_name]

        return cleaned_data


class ContributeForm(forms.Form):
    email = forms.EmailField(widget=EmailInput(attrs={'required': 'required'}))
    privacy = forms.BooleanField(widget=PrivacyWidget)
    newsletter = forms.BooleanField(required=False)
    interest = forms.ChoiceField(
        choices=INTEREST_CHOICES,
        widget=forms.Select(attrs={'required': 'required'}))
    comments = forms.CharField(
        widget=forms.widgets.Textarea(attrs={'rows': '4',
                                             'cols': '30'}))
    # honeypot
    office_fax = forms.CharField(widget=HoneyPotWidget, required=False)


class WebToLeadForm(forms.Form):
    interests_standard = (
        ('Firefox for Desktop', _lazy(u'Firefox for Desktop')),
        ('Firefox for Android', _lazy(u'Firefox for Android')),
        ('Firefox Marketplace', _lazy(u'Firefox Marketplace')),
        ('Firefox OS', _lazy(u'Firefox OS')),
        ('Persona', _lazy(u'Persona')),
        ('Marketing and Co-promotions', _lazy(u'Marketing and Co-promotions')),
        ('Promoted Content ("Tiles")', _lazy(u'Promoted Content ("Tiles")')),
        ('Other', _lazy(u'Other')),
    )

    interests_fx = (
        ('Firefox for Android', _lazy(u'Firefox for Android')),
        ('Firefox Marketplace', _lazy(u'Firefox Marketplace')),
        ('Firefox OS', _lazy(u'Firefox OS')),
        ('Other', _lazy(u'Other')),
    )

    industries = (
        ('', 'Select Industry'),
        ('Agriculture', _lazy(u'Agriculture')),
        ('Apparel', _lazy(u'Apparel')),
        ('Banking', _lazy(u'Banking')),
        ('Biotechnology', _lazy(u'Biotechnology')),
        ('Chemicals', _lazy(u'Chemicals')),
        ('Communications', _lazy(u'Communications')),
        ('Construction', _lazy(u'Construction')),
        ('Consulting', _lazy(u'Consulting')),
        ('Education', _lazy(u'Education')),
        ('Electronics', _lazy(u'Electronics')),
        ('Energy', _lazy(u'Energy')),
        ('Engineering', _lazy(u'Engineering')),
        ('Entertainment', _lazy(u'Entertainment')),
        ('Environmental', _lazy(u'Environmental')),
        ('Finance', _lazy(u'Finance')),
        ('Food &amp; Beverage', _lazy(u'Food &amp; Beverage')),
        ('Government', _lazy(u'Government')),
        ('Healthcare', _lazy(u'Healthcare')),
        ('Hospitality', _lazy(u'Hospitality')),
        ('Insurance', _lazy(u'Insurance')),
        ('Machinery', _lazy(u'Machinery')),
        ('Manufacturing', _lazy(u'Manufacturing')),
        ('Media', _lazy(u'Media')),
        ('Not For Profit', _lazy(u'Not For Profit')),
        ('Other', _lazy(u'Other')),
        ('Recreation', _lazy(u'Recreation')),
        ('Retail', _lazy(u'Retail')),
        ('Shipping', _lazy(u'Shipping')),
        ('Technology', _lazy(u'Technology')),
        ('Telecommunications', _lazy(u'Telecommunications')),
        ('Transportation', _lazy(u'Transportation')),
        ('Utilities', _lazy(u'Utilities')),
    )

    first_name = forms.CharField(
        max_length=40,
        required=True,
        error_messages={
            'required': _lazy(u'Please enter your first name.')
        },
        widget=forms.TextInput(
            attrs={
                'size': 20,
                'placeholder': _lazy(u'First Name'),
                'class': 'required',
                'required': 'required',
                'aria-required': 'true'
            }
        )
    )
    last_name = forms.CharField(
        max_length=80,
        required=True,
        error_messages={
            'required': _('Please enter your last name.')
        },
        widget=forms.TextInput(
            attrs={
                'size': 20,
                'placeholder': _lazy(u'Last Name'),
                'class': 'required',
                'required': 'required',
                'aria-required': 'true'
            }
        )
    )
    title = forms.CharField(
        max_length=40,
        required=False,
        widget=forms.TextInput(
            attrs={
                'size': 20,
                'placeholder': _lazy(u'Title')
            }
        )
    )
    company = forms.CharField(
        max_length=40,
        required=True,
        error_messages={
            'required': _lazy(u'Please enter your company name.')
        },
        widget=forms.TextInput(
            attrs={
                'size': 20,
                'placeholder': _lazy(u'Company'),
                'class': 'required',
                'required': 'required',
                'aria-required': 'true'
            }
        )
    )
    URL = forms.URLField(
        max_length=80,
        required=False,
        error_messages={
            'invalid': _lazy(u'Please supply a valid URL.')
        },
        widget=forms.TextInput(
            attrs={
                'size': 20,
                'placeholder': _lazy(u'Website')
            }
        )
    )
    email = forms.EmailField(
        max_length=80,
        required=True,
        error_messages={
            'required': _lazy(u'Please enter your email address.'),
            'invalid': _lazy(u'Please enter a valid email address')
        },
        widget=forms.TextInput(
            attrs={
                'size': 20,
                'placeholder': _lazy(u'Email'),
                'class': 'required',
                'required': 'required',
                'aria-required': 'true'
            }
        )
    )
    phone = forms.CharField(
        max_length=40,
        required=False,
        widget=forms.TextInput(
            attrs={
                'size': 20,
                'placeholder': _lazy(u'Phone')
            }
        )
    )
    mobile = forms.CharField(
        max_length=40,
        required=False,
        widget=forms.TextInput(
            attrs={
                'size': 20,
                'placeholder': _lazy(u'Mobile')
            }
        )
    )
    street = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                'placeholder': _lazy(u'Address'),
                'rows': '',
                'cols': ''
            }
        )
    )
    city = forms.CharField(
        required=False,
        max_length=40,
        widget=forms.TextInput(
            attrs={
                'placeholder': _lazy(u'City')
            }
        )
    )
    state = forms.CharField(
        required=False,
        max_length=40,
        widget=forms.TextInput(
            attrs={
                'placeholder': _lazy(u'State/Province')
            }
        )
    )
    country = forms.CharField(
        required=False,
        max_length=40,
        widget=forms.TextInput(
            attrs={
                'placeholder': _lazy(u'Country')
            }
        )
    )
    zip = forms.CharField(
        required=False,
        max_length=40,
        widget=forms.TextInput(
            attrs={
                'placeholder': _lazy(u'Zip')
            }
        )
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                'placeholder': _lazy(u'Description'),
                'rows': '',
                'cols': ''
            }
        )
    )
    interested_countries = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                'placeholder': _lazy(u'Countries of Interest'),
                'rows': '',
                'cols': ''
            }
        )
    )
    interested_languages = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                'placeholder': _lazy(u'Languages of Interest'),
                'rows': '',
                'cols': ''
            }
        )
    )
    industry = forms.ChoiceField(
        choices=industries,
        required=False,
        widget=forms.Select(
            attrs={
                'title': _lazy('Industry'),
                'size': 1
            }
        )
    )
    campaign_type = forms.ChoiceField(
        choices=(
            ('', _lazy(u'Select Campaign Type')),
            ('Brand', _lazy(u'Brand')),
            ('Direct Response', _lazy(u'Direct Response'))
        ),
        required=False,
        widget=forms.Select(
            attrs={
                'title': _lazy('Campaign Type')
            }
        )
    )
    # honeypot
    office_fax = forms.CharField(widget=HoneyPotWidget, required=False)
    # uncomment below to debug salesforce
    # debug = forms.IntegerField(required=False)
    # debugEmail = forms.EmailField(required=False)

    def __init__(self, *args, **kwargs):
        interest_set = kwargs.pop('interest_set', 'standard')
        interest_choices = self.interests_fx if (interest_set == 'fx') else self.interests_standard
        kwargs.pop('lead_source', None)

        super(WebToLeadForm, self).__init__(*args, **kwargs)

        self.fields['interest'] = forms.MultipleChoiceField(
            choices=interest_choices,
            required=False,
            widget=forms.SelectMultiple(
                attrs={
                    'title': _lazy(u'Interest'),
                    'size': 8
                }
            )
        )


class ContentServicesForm(forms.Form):
    countries = (
        ('', 'Select country'),
        ('Afghanistan', _lazy(u'Afghanistan')),
        ('Albania', _lazy(u'Albania')),
        ('Algeria', _lazy(u'Algeria')),
        ('American Samoa', _lazy(u'American Samoa')),
        ('Andorra', _lazy(u'Andorra')),
        ('Angola', _lazy(u'Angola')),
        ('Anguilla', _lazy(u'Anguilla')),
        ('Antigua and Barbuda', _lazy(u'Antigua and Barbuda')),
        ('Argentina', _lazy(u'Argentina')),
        ('Armenia', _lazy(u'Armenia')),
        ('Aruba', _lazy(u'Aruba')),
        ('Australia', _lazy(u'Australia')),
        ('Austria', _lazy(u'Austria')),
        ('Azerbaijan', _lazy(u'Azerbaijan')),
        ('Bahamas', _lazy(u'Bahamas')),
        ('Bahrain', _lazy(u'Bahrain')),
        ('Bangladesh', _lazy(u'Bangladesh')),
        ('Barbados', _lazy(u'Barbados')),
        ('Belarus', _lazy(u'Belarus')),
        ('Belgium', _lazy(u'Belgium')),
        ('Belize', _lazy(u'Belize')),
        ('Benin', _lazy(u'Benin')),
        ('Bermuda', _lazy(u'Bermuda')),
        ('Bhutan', _lazy(u'Bhutan')),
        ('Bolivia', _lazy(u'Bolivia')),
        ('Bosnia and Herzegovina', _lazy(u'Bosnia and Herzegovina')),
        ('Botswana', _lazy(u'Botswana')),
        ('Brazil', _lazy(u'Brazil')),
        ('British Virgin Islands', _lazy(u'British Virgin Islands')),
        ('British Indian Ocean Territory', _lazy(u'British Indian Ocean Territory')),
        ('Brunei', _lazy(u'Brunei')),
        ('Bulgaria', _lazy(u'Bulgaria')),
        ('Burkina Faso', _lazy(u'Burkina Faso')),
        ('Burundi', _lazy(u'Burundi')),
        ('Cambodia', _lazy(u'Cambodia')),
        ('Cameroon', _lazy(u'Cameroon')),
        ('Canada', _lazy(u'Canada')),
        ('Cape Verde', _lazy(u'Cape Verde')),
        ('Cayman Islands', _lazy(u'Cayman Islands')),
        ('Central African Republic', _lazy(u'Central African Republic')),
        ('Chad', _lazy(u'Chad')),
        ('Chile', _lazy(u'Chile')),
        ('China', _lazy(u'China')),
        ('Christmas Island', _lazy(u'Christmas Island')),
        ('Colombia', _lazy(u'Colombia')),
        ('Comoros Islands', _lazy(u'Comoros Islands')),
        ('Congo, Democratic Republic of the', _lazy(u'Congo, Democratic Republic of the')),
        ('Congo, Republic of the', _lazy(u'Congo, Republic of the')),
        ('Cook Islands', _lazy(u'Cook Islands')),
        ('Costa Rica', _lazy(u'Costa Rica')),
        ('Cote D\'ivoire', _lazy(u'Cote D\'ivoire')),
        ('Croatia', _lazy(u'Croatia')),
        ('Cuba', _lazy(u'Cuba')),
        ('Cyprus', _lazy(u'Cyprus')),
        ('Czech Republic', _lazy(u'Czech Republic')),
        ('Denmark', _lazy(u'Denmark')),
        ('Djibouti', _lazy(u'Djibouti')),
        ('Dominica', _lazy(u'Dominica')),
        ('Dominican Republic', _lazy(u'Dominican Republic')),
        ('East Timor', _lazy(u'East Timor')),
        ('Ecuador', _lazy(u'Ecuador')),
        ('Egypt', _lazy(u'Egypt')),
        ('El Salvador', _lazy(u'El Salvador')),
        ('Equatorial Guinea', _lazy(u'Equatorial Guinea')),
        ('Eritrea', _lazy(u'Eritrea')),
        ('Estonia', _lazy(u'Estonia')),
        ('Ethiopia', _lazy(u'Ethiopia')),
        ('Falkland Islands (Malvinas)', _lazy(u'Falkland Islands (Malvinas)')),
        ('Faroe Islands', _lazy(u'Faroe Islands')),
        ('Fiji', _lazy(u'Fiji')),
        ('Finland', _lazy(u'Finland')),
        ('France', _lazy(u'France')),
        ('French Guiana', _lazy(u'French Guiana')),
        ('French Polynesia', _lazy(u'French Polynesia')),
        ('French Southern Territories', _lazy(u'French Southern Territories')),
        ('Gabon', _lazy(u'Gabon')),
        ('Gambia', _lazy(u'Gambia')),
        ('Georgia', _lazy(u'Georgia')),
        ('Germany', _lazy(u'Germany')),
        ('Ghana', _lazy(u'Ghana')),
        ('Gibraltar', _lazy(u'Gibraltar')),
        ('Greece', _lazy(u'Greece')),
        ('Greenland', _lazy(u'Greenland')),
        ('Grenada', _lazy(u'Grenada')),
        ('Guadeloupe', _lazy(u'Guadeloupe')),
        ('Guam', _lazy(u'Guam')),
        ('Guatemala', _lazy(u'Guatemala')),
        ('Guinea', _lazy(u'Guinea')),
        ('Guinea-Bissau', _lazy(u'Guinea-Bissau')),
        ('Guyana', _lazy(u'Guyana')),
        ('Haiti', _lazy(u'Haiti')),
        ('Holy See (Vatican City State)', _lazy(u'Holy See (Vatican City State)')),
        ('Honduras', _lazy(u'Honduras')),
        ('Hong Kong', _lazy(u'Hong Kong')),
        ('Hungary', _lazy(u'Hungary')),
        ('Iceland', _lazy(u'Iceland')),
        ('India', _lazy(u'India')),
        ('Indonesia', _lazy(u'Indonesia')),
        ('Iran', _lazy(u'Iran')),
        ('Iraq', _lazy(u'Iraq')),
        ('Ireland', _lazy(u'Ireland')),
        ('Israel', _lazy(u'Israel')),
        ('Italy', _lazy(u'Italy')),
        ('Jamaica', _lazy(u'Jamaica')),
        ('Japan', _lazy(u'Japan')),
        ('Jordan', _lazy(u'Jordan')),
        ('Kazakhstan', _lazy(u'Kazakhstan')),
        ('Kenya', _lazy(u'Kenya')),
        ('Kiribati', _lazy(u'Kiribati')),
        ('South Korea', _lazy(u'South Korea')),
        ('Kosovo', _lazy(u'Kosovo')),
        ('Kuwait', _lazy(u'Kuwait')),
        ('Kyrgyzstan', _lazy(u'Kyrgyzstan')),
        ('Laos', _lazy(u'Laos')),
        ('Latvia', _lazy(u'Latvia')),
        ('Lebanon', _lazy(u'Lebanon')),
        ('Lesotho', _lazy(u'Lesotho')),
        ('Liberia', _lazy(u'Liberia')),
        ('Liechtenstein', _lazy(u'Liechtenstein')),
        ('Lithuania', _lazy(u'Lithuania')),
        ('Luxembourg', _lazy(u'Luxembourg')),
        ('Macau', _lazy(u'Macau')),
        ('Macedonia', _lazy(u'Macedonia')),
        ('Madagascar', _lazy(u'Madagascar')),
        ('Malawi', _lazy(u'Malawi')),
        ('Malaysia', _lazy(u'Malaysia')),
        ('Maldives', _lazy(u'Maldives')),
        ('Mali', _lazy(u'Mali')),
        ('Malta', _lazy(u'Malta')),
        ('Marshall Islands', _lazy(u'Marshall Islands')),
        ('Martinique', _lazy(u'Martinique')),
        ('Mauritania', _lazy(u'Mauritania')),
        ('Mauritius', _lazy(u'Mauritius')),
        ('Mayotte', _lazy(u'Mayotte')),
        ('Mexico', _lazy(u'Mexico')),
        ('Micronesia', _lazy(u'Micronesia')),
        ('Moldova, Republic of', _lazy(u'Moldova, Republic of')),
        ('Monaco', _lazy(u'Monaco')),
        ('Mongolia', _lazy(u'Mongolia')),
        ('Montenegro', _lazy(u'Montenegro')),
        ('Montserrat', _lazy(u'Montserrat')),
        ('Morocco', _lazy(u'Morocco')),
        ('Mozambique', _lazy(u'Mozambique')),
        ('Myanmar', _lazy(u'Myanmar')),
        ('Namibia', _lazy(u'Namibia')),
        ('Nauru', _lazy(u'Nauru')),
        ('Nepal', _lazy(u'Nepal')),
        ('Netherlands', _lazy(u'Netherlands')),
        ('Netherlands Antilles', _lazy(u'Netherlands Antilles')),
        ('New Caledonia', _lazy(u'New Caledonia')),
        ('New Zealand', _lazy(u'New Zealand')),
        ('Nicaragua', _lazy(u'Nicaragua')),
        ('Niger', _lazy(u'Niger')),
        ('Nigeria', _lazy(u'Nigeria')),
        ('Niue', _lazy(u'Niue')),
        ('Norfolk Island', _lazy(u'Norfolk Island')),
        ('Northern Mariana Islands', _lazy(u'Northern Mariana Islands')),
        ('Norway', _lazy(u'Norway')),
        ('Oman', _lazy(u'Oman')),
        ('Pakistan', _lazy(u'Pakistan')),
        ('Palau', _lazy(u'Palau')),
        ('Panama', _lazy(u'Panama')),
        ('Papua New Guinea', _lazy(u'Papua New Guinea')),
        ('Paraguay', _lazy(u'Paraguay')),
        ('Peru', _lazy(u'Peru')),
        ('Philippines', _lazy(u'Philippines')),
        ('Pitcairn Island', _lazy(u'Pitcairn Island')),
        ('Poland', _lazy(u'Poland')),
        ('Portugal', _lazy(u'Portugal')),
        ('Puerto Rico', _lazy(u'Puerto Rico')),
        ('Qatar', _lazy(u'Qatar')),
        ('Reunion', _lazy(u'Reunion')),
        ('Romania', _lazy(u'Romania')),
        ('Russian Federation', _lazy(u'Russian Federation')),
        ('Rwanda', _lazy(u'Rwanda')),
        ('Saint Kitts and Nevis', _lazy(u'Saint Kitts and Nevis')),
        ('Saint Lucia', _lazy(u'Saint Lucia')),
        ('Saint Vincent and the Grenadines', _lazy(u'Saint Vincent and the Grenadines')),
        ('Samoa', _lazy(u'Samoa')),
        ('San Marino', _lazy(u'San Marino')),
        ('Sao Tome and Principe', _lazy(u'Sao Tome and Principe')),
        ('Saudi Arabia', _lazy(u'Saudi Arabia')),
        ('Senegal', _lazy(u'Senegal')),
        ('Serbia', _lazy(u'Serbia')),
        ('Seychelles', _lazy(u'Seychelles')),
        ('Sierra Leone', _lazy(u'Sierra Leone')),
        ('Singapore', _lazy(u'Singapore')),
        ('Slovakia', _lazy(u'Slovakia')),
        ('Slovenia', _lazy(u'Slovenia')),
        ('Solomon Islands', _lazy(u'Solomon Islands')),
        ('Somalia', _lazy(u'Somalia')),
        ('South Africa', _lazy(u'South Africa')),
        ('Spain', _lazy(u'Spain')),
        ('Sri Lanka', _lazy(u'Sri Lanka')),
        ('St. Helena', _lazy(u'St. Helena')),
        ('St. Pierre and Miquelon', _lazy(u'St. Pierre and Miquelon')),
        ('Sudan', _lazy(u'Sudan')),
        ('Suriname', _lazy(u'Suriname')),
        ('Swaziland', _lazy(u'Swaziland')),
        ('Sweden', _lazy(u'Sweden')),
        ('Switzerland', _lazy(u'Switzerland')),
        ('Syria', _lazy(u'Syria')),
        ('Taiwan', _lazy(u'Taiwan')),
        ('Tajikistan', _lazy(u'Tajikistan')),
        ('Tanzania', _lazy(u'Tanzania')),
        ('Thailand', _lazy(u'Thailand')),
        ('Togo', _lazy(u'Togo')),
        ('Tokelau', _lazy(u'Tokelau')),
        ('Tonga', _lazy(u'Tonga')),
        ('Trinidad and Tobago', _lazy(u'Trinidad and Tobago')),
        ('Tunisia', _lazy(u'Tunisia')),
        ('Turkey', _lazy(u'Turkey')),
        ('Turkmenistan', _lazy(u'Turkmenistan')),
        ('Turks and Caicos Islands', _lazy(u'Turks and Caicos Islands')),
        ('Tuvalu', _lazy(u'Tuvalu')),
        ('Uganda', _lazy(u'Uganda')),
        ('Ukraine', _lazy(u'Ukraine')),
        ('United Arab Emirates', _lazy(u'United Arab Emirates')),
        ('United Kingdom', _lazy(u'United Kingdom')),
        ('United States', _lazy(u'United States')),
        ('Uruguay', _lazy(u'Uruguay')),
        ('Uzbekistan', _lazy(u'Uzbekistan')),
        ('Vanuatu', _lazy(u'Vanuatu')),
        ('Venezuela', _lazy(u'Venezuela')),
        ('Viet Nam', _lazy(u'Viet Nam')),
        ('Virgin Islands (U.S.)', _lazy(u'Virgin Islands (U.S.)')),
        ('Wallis and Futuna Islands', _lazy(u'Wallis and Futuna Islands')),
        ('Western Sahara', _lazy(u'Western Sahara')),
        ('Yemen', _lazy(u'Yemen')),
        ('Zambia', _lazy(u'Zambia')),
        ('Zimbabwe', _lazy(u'Zimbabwe'))
    )

    states = (
        ('California', _lazy(u'California')),
        ('Texas', _lazy(u'Texas')),
        ('Florida', _lazy(u'Florida')),
        ('New York', _lazy(u'New York')),
        ('Illinois', _lazy(u'Illinois')),
        ('Pennsylvania', _lazy(u'Pennsylvania')),
        ('Ohio', _lazy(u'Ohio')),
        ('Georgia', _lazy(u'Georgia')),
        ('North Carolina', _lazy(u'North Carolina')),
        ('Michigan', _lazy(u'Michigan')),
        ('New Jersey', _lazy(u'New Jersey')),
        ('Virginia', _lazy(u'Virginia')),
        ('Washington', _lazy(u'Washington')),
        ('Massachusetts', _lazy(u'Massachusetts')),
        ('Arizona', _lazy(u'Arizona')),
        ('Indiana', _lazy(u'Indiana')),
        ('Tennessee', _lazy(u'Tennessee')),
        ('Missouri', _lazy(u'Missouri')),
        ('Maryland', _lazy(u'Maryland')),
        ('Wisconsin', _lazy(u'Wisconsin')),
        ('Minnesota', _lazy(u'Minnesota')),
        ('Colorado', _lazy(u'Colorado')),
        ('Alabama', _lazy(u'Alabama')),
        ('South Carolina', _lazy(u'South Carolina')),
        ('Louisiana', _lazy(u'Louisiana')),
        ('Kentucky', _lazy(u'Kentucky')),
        ('Oregon', _lazy(u'Oregon')),
        ('Oklahoma', _lazy(u'Oklahoma')),
        ('Puerto Rico', _lazy(u'Puerto Rico')),
        ('Connecticut', _lazy(u'Connecticut')),
        ('Iowa', _lazy(u'Iowa')),
        ('Mississippi', _lazy(u'Mississippi')),
        ('Arkansas', _lazy(u'Arkansas')),
        ('Utah', _lazy(u'Utah')),
        ('Kansas', _lazy(u'Kansas')),
        ('Nevada', _lazy(u'Nevada')),
        ('New Mexico', _lazy(u'New Mexico')),
        ('Nebraska', _lazy(u'Nebraska')),
        ('West Virginia', _lazy(u'West Virginia')),
        ('Idaho', _lazy(u'Idaho')),
        ('Hawaii', _lazy(u'Hawaii')),
        ('Maine', _lazy(u'Maine')),
        ('New Hampshire', _lazy(u'New Hampshire')),
        ('Rhode Island', _lazy(u'Rhode Island')),
        ('Montana', _lazy(u'Montana')),
        ('Delaware', _lazy(u'Delaware')),
        ('South Dakota', _lazy(u'South Dakota')),
        ('North Dakota', _lazy(u'North Dakota')),
        ('Alaska', _lazy(u'Alaska')),
        ('District of Columbia', _lazy(u'District of Columbia')),
        ('Vermont', _lazy(u'Vermont')),
        ('Wyoming', _lazy(u'Wyoming')),
        ('Guam', _lazy(u'Guam')),
        ('U.S. Virgin Islands', _lazy(u'U.S. Virgin Islands')),
        ('American Samoa', _lazy(u'American Samoa')),
        ('Northern Mariana Islands', _lazy(u'Northern Mariana Islands'))
    )

    industries = (
        ('', 'Select Industry'),
        ('Agriculture', _lazy(u'Agriculture')),
        ('Apparel', _lazy(u'Apparel')),
        ('Banking', _lazy(u'Banking')),
        ('Biotechnology', _lazy(u'Biotechnology')),
        ('Chemicals', _lazy(u'Chemicals')),
        ('Communications', _lazy(u'Communications')),
        ('Construction', _lazy(u'Construction')),
        ('Consulting', _lazy(u'Consulting')),
        ('Education', _lazy(u'Education')),
        ('Electronics', _lazy(u'Electronics')),
        ('Energy', _lazy(u'Energy')),
        ('Engineering', _lazy(u'Engineering')),
        ('Entertainment', _lazy(u'Entertainment')),
        ('Environmental', _lazy(u'Environmental')),
        ('Finance', _lazy(u'Finance')),
        ('Food &amp; Beverage', _lazy(u'Food &amp; Beverage')),
        ('Government', _lazy(u'Government')),
        ('Healthcare', _lazy(u'Healthcare')),
        ('Hospitality', _lazy(u'Hospitality')),
        ('Insurance', _lazy(u'Insurance')),
        ('Machinery', _lazy(u'Machinery')),
        ('Manufacturing', _lazy(u'Manufacturing')),
        ('Media', _lazy(u'Media')),
        ('Not For Profit', _lazy(u'Not For Profit')),
        ('Other', _lazy(u'Other')),
        ('Recreation', _lazy(u'Recreation')),
        ('Retail', _lazy(u'Retail')),
        ('Shipping', _lazy(u'Shipping')),
        ('Technology', _lazy(u'Technology')),
        ('Telecommunications', _lazy(u'Telecommunications')),
        ('Transportation', _lazy(u'Transportation')),
        ('Utilities', _lazy(u'Utilities')),
    )

    first_name = forms.CharField(
        max_length=40,
        required=True,
        error_messages={
            'required': _lazy(u'Please enter your first name.')
        },
        widget=forms.TextInput(
            attrs={
                'size': 20,
                'class': 'required',
                'required': 'required',
                'aria-required': 'true'
            }
        )
    )
    last_name = forms.CharField(
        max_length=40,
        required=True,
        error_messages={
            'required': _lazy(u'Please enter your last name.')
        },
        widget=forms.TextInput(
            attrs={
                'size': 20,
                'class': 'required',
                'required': 'required',
                'aria-required': 'true'
            }
        )
    )
    company = forms.CharField(
        max_length=40,
        required=True,
        error_messages={
            'required': _lazy(u'Please enter your company name.')
        },
        widget=forms.TextInput(
            attrs={
                'size': 20,
                'class': 'required',
                'required': 'required',
                'aria-required': 'true'
            }
        )
    )
    email = forms.EmailField(
        max_length=80,
        required=True,
        error_messages={
            'required': _lazy(u'Please enter your email address.'),
            'invalid': _lazy(u'Please enter a valid email address')
        },
        widget=forms.TextInput(
            attrs={
                'size': 20,
                'class': 'required',
                'required': 'required',
                'aria-required': 'true'
            }
        )
    )
    phone = forms.CharField(
        max_length=40,
        required=True,
        error_messages={
            'required': _lazy(u'Please enter your phone number.')
        },
        widget=forms.TextInput(
            attrs={
                'size': 20,
            }
        )
    )
    mobile = forms.CharField(
        max_length=40,
        required=False,
        widget=forms.TextInput(
            attrs={
                'size': 20
            }
        )
    )
    street = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                'rows': '',
                'cols': ''
            }
        )
    )
    city = forms.CharField(
        required=False,
        max_length=40
    )
    state = forms.CharField(
        required=False,
        max_length=40
    )
    province = forms.CharField(
        required=False,
        max_length=40
    )
    country = forms.ChoiceField(
        choices=countries,
        required=True,
        widget=forms.Select(
            attrs={
                'title': _lazy('Country'),
                'size': 1
            }
        )
    )
    zip = forms.CharField(
        required=False,
        max_length=40
    )
    campaign_type_description = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                'rows': '',
                'cols': ''
            }
        )
    )
    interested_countries = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                'rows': '',
                'cols': ''
            }
        )
    )
    interested_languages = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                'rows': '',
                'cols': ''
            }
        )
    )
    industry = forms.ChoiceField(
        choices=industries,
        required=False,
        widget=forms.Select(
            attrs={
                'title': _lazy('Industry'),
                'size': 1
            }
        )
    )
    campaign_type = forms.ChoiceField(
        choices=(
            ('', _lazy(u'Select Campaign Type')),
            ('Brand', _lazy(u'Brand')),
            ('Direct Response', _lazy(u'Direct Response')),
            ('Other', _lazy(u'Other'))
        ),
        required=False,
        widget=forms.Select(
            attrs={
                'title': _lazy('Campaign Type')
            }
        )
    )
    # honeypot
    office_fax = forms.CharField(widget=HoneyPotWidget, required=False)
    # uncomment below to debug salesforce
    # debug = forms.IntegerField(required=False)
    # debugEmail = forms.EmailField(required=False)

    def __init__(self, *args, **kwargs):
        kwargs.pop('lead_source', None)

        super(ContentServicesForm, self).__init__(*args, **kwargs)


class ContributeStudentAmbassadorForm(forms.Form):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField(max_length=100)
    status = forms.ChoiceField(
        choices=(('', ''),
                 ('student', _lazy('Student')), ('teacher', _lazy('Teacher')),
                 ('administrator', _lazy('Administrator')),
                 ('other', _lazy('Other'))))
    school = forms.CharField(max_length=100)
    grad_year = forms.ChoiceField(
        required=False,
        choices=([('', _lazy('Expected Graduation Year'))] +
                 [(i, str(i)) for i in range(datetime.now().year,
                                             datetime.now().year + 8)]))
    major = forms.ChoiceField(
        required=False,
        choices=[('', ''),
                 ('computer science', _lazy('Computer Science')),
                 ('computer engineering', _lazy('Computer Engineering')),
                 ('engineering', _lazy('Engineering (other)')),
                 ('social science', _lazy('Social Science')),
                 ('science', _lazy('Science (other)')),
                 ('business/marketing', _lazy('Business/Marketing')),
                 ('education', _lazy('Education')),
                 ('mathematics', _lazy('Mathematics')),
                 ('other', _lazy('Other'))])
    major_free_text = forms.CharField(max_length=100, required=False)
    city = forms.CharField(max_length=100)
    country = forms.ChoiceField()
    fmt = forms.ChoiceField(widget=forms.RadioSelect(renderer=SideRadios),
                            label=_lazy('Email format preference:'),
                            choices=FORMATS, initial='H')
    age_confirmation = forms.BooleanField(
        widget=widgets.CheckboxInput(),
        label=_lazy(u'I’m 18 years old and eligible to participate in '
                    'the program'))
    share_information = forms.BooleanField(
        required=False,
        widget=widgets.CheckboxInput(),
        label=_lazy(u'Please share my contact information and interests with '
                    'related Mozilla contributors for the purpose of '
                    'collaborating on Mozilla projects'))
    privacy = forms.BooleanField(widget=PrivacyWidget)
    nl_mozilla_and_you = forms.BooleanField(
        required=False,
        widget=widgets.CheckboxInput(),
        label=_lazy(u'Firefox & You: A monthly newsletter packed with tips to'
                    ' improve your browsing experience'))
    nl_mobile = forms.BooleanField(
        required=False,
        widget=widgets.CheckboxInput(),
        label=_lazy(u'Firefox for Android: Get the power of Firefox in the'
                    ' palm of your hand'))
    nl_firefox_flicks = forms.BooleanField(
        required=False,
        widget=widgets.CheckboxInput(),
        label=_lazy(u'Firefox Flicks'))
    nl_about_mozilla = forms.BooleanField(
        required=False,
        widget=widgets.CheckboxInput(),
        label=_lazy(u'About Mozilla: News from the Mozilla Project'))
    # honeypot
    office_fax = forms.CharField(widget=HoneyPotWidget, required=False)
    source_url = forms.URLField(required=False)

    def __init__(self, *args, **kwargs):
        locale = kwargs.get('locale', 'en-US')
        super(ContributeStudentAmbassadorForm, self).__init__(*args, **kwargs)
        country_list = product_details.get_regions(locale).items()
        country_list = sorted(country_list, key=lambda country: country[1])
        country_list.insert(0, ('', ''))
        self.fields['country'].choices = country_list

    def clean(self, *args, **kwargs):
        super(ContributeStudentAmbassadorForm, self).clean(*args, **kwargs)
        if (self.cleaned_data.get('status', '') == 'student' and
                not self.cleaned_data.get('grad_year', '')):
            self._errors['grad_year'] = (
                self.error_class([_('This field is required.')]))
        return self.cleaned_data

    def clean_grad_year(self):
        return self.cleaned_data.get('grad_year', '')

    def clean_major(self):
        return self.cleaned_data.get('major_free_field',
                                     self.cleaned_data['major'])

    def clean_share_information(self):
        if self.cleaned_data.get('share_information', False):
            return 'Y'
        return 'N'

    def clean_office_fax(self):
        honeypot = self.cleaned_data.pop('office_fax', None)

        if honeypot:
            raise forms.ValidationError(
                _('Your submission could not be processed'))

    def newsletters(self):
        newsletters = ['ambassadors']
        for newsletter in ['nl_mozilla_and_you', 'nl_mobile',
                           'nl_firefox_flicks', 'nl_about_mozilla']:
            if self.cleaned_data.get(newsletter, False):
                newsletters.append(newsletter[3:].replace('_', '-'))
        return newsletters

    def save(self):
        data = self.cleaned_data
        result = basket.subscribe(data['email'], self.newsletters(),
                                  format=data['fmt'], country=data['country'],
                                  welcome_message='Student_Ambassadors_Welcome',
                                  source_url=data['source_url'], sync='Y')

        data = {
            'FIRST_NAME': data['first_name'],
            'LAST_NAME': data['last_name'],
            'STUDENTS_CURRENT_STATUS': data['status'],
            'STUDENTS_SCHOOL': data['school'],
            'STUDENTS_GRAD_YEAR': data['grad_year'],
            'STUDENTS_MAJOR': data['major'],
            'COUNTRY_': data['country'],
            'STUDENTS_CITY': data['city'],
            'STUDENTS_ALLOW_SHARE': data['share_information'],
        }
        request('post', 'custom_update_student_ambassadors',
                token=result['token'], data=data)
