# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import csv
from operator import itemgetter

from django.conf import settings

from ordereddict import OrderedDict
from unidecode import unidecode


_credits_names = None


def get_credits():
    global _credits_names
    if _credits_names is None:
        try:
            with open(settings.CREDITS_NAMES_FILE, 'rb') as names_fh:
                _credits_names = get_credits_ordered(names_fh)
        except IOError:
            _credits_names = {}

    return _credits_names


def get_credits_list(credits_data):
    names = []
    for row in csv.reader(credits_data):
        if len(row) == 1:
            name = sortkey = row[0]
        elif len(row) == 2:
            name, sortkey = row
        else:
            continue

        names.append([name.decode('utf8'),
                      unidecode(sortkey.decode('utf8')).upper()])

    return sorted(names, key=itemgetter(1))


def get_credits_ordered(credits_data):
    names = get_credits_list(credits_data)
    ordered_names = OrderedDict()
    for name, sortkey in names:
        letter = sortkey[0]
        if letter not in ordered_names:
            ordered_names[letter] = []

        ordered_names[letter].append(name)

    return ordered_names
