# -*- coding: utf-8 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from ordereddict import OrderedDict

from bedrock.mozorg import credits
from bedrock.mozorg.tests import TestCase


class TestCredits(TestCase):
    def test_credits_list(self):
        names = credits.get_credits_list([
            'The Dude,Dude',
            'Walter Sobchak,Sobchak',
            'Theodore Donald Kerabatsos,Kerabatsos',
        ])
        self.assertListEqual(names, [
            ['The Dude', 'DUDE'],
            ['Theodore Donald Kerabatsos', 'KERABATSOS'],
            ['Walter Sobchak', 'SOBCHAK'],
        ])

    def test_credits_list_sort_non_ascii(self):
        names = credits.get_credits_list([
            '\xd0\xa7\xd1\x83\xd0\xb2\xd0\xb0\xd0\xba,\xd0\xa7\xd1\x83\xd0\xb2\xd0\xb0\xd0\xba',
            'Walter \xc3\x9f\xc3\xb8bchak,\xc3\x9f\xc3\xb8bchak',
            'Theodore Donald Kerabatsos,Kerabatsos',
        ])
        self.assertListEqual(names, [
            [u'\u0427\u0443\u0432\u0430\u043a', 'CHUVAK'],
            [u'Theodore Donald Kerabatsos', 'KERABATSOS'],
            [u'Walter \xdf\xf8bchak', 'SSOBCHAK'],
        ])

    def test_credits_ordered_no_sortkey(self):
        """Should give an ordered dict or ordered lists keyed on first letter of name."""
        names = credits.get_credits_ordered([
            'Bunny Lebowski',
            'Maude Lebowski',
            'Jeffrey Lebowski',
            'Uli Kunkel',
            'The Dude',
            'Walter Sobchak',
            'Theodore Donald Kerabatsos',
        ])
        good_names = OrderedDict()
        good_names['B'] = ['Bunny Lebowski']
        good_names['J'] = ['Jeffrey Lebowski']
        good_names['M'] = ['Maude Lebowski']
        good_names['T'] = ['The Dude', 'Theodore Donald Kerabatsos']
        good_names['U'] = ['Uli Kunkel']
        good_names['W'] = ['Walter Sobchak']
        self.assertEqual(names, good_names)

    def test_credits_ordered(self):
        """Should give an ordered dict or ordered lists keyed on first letter of sortkey."""
        names = credits.get_credits_ordered([
            'Bunny Lebowski,Lebowski Bunny',
            'Maude Lebowski,Lebowski Maude',
            'Jeffrey Lebowski,Lebowski Jeffrey',
            'Uli Kunkel,Kunkel',
            'The Dude,Dude',
            'Walter Sobchak,Sobchak',
            'Theodore Donald Kerabatsos,Kerabatsos',
        ])
        good_names = OrderedDict()
        good_names['D'] = ['The Dude']
        good_names['K'] = ['Theodore Donald Kerabatsos', 'Uli Kunkel']
        good_names['L'] = ['Bunny Lebowski', 'Jeffrey Lebowski', 'Maude Lebowski']
        good_names['S'] = ['Walter Sobchak']
        self.assertEqual(names, good_names)

    def test_credits_ordered_skips(self):
        """Should skip lines with more than 2 items."""
        names = credits.get_credits_ordered([
            'Bunny Lebowski,Lebowski Bunny',
            'Maude Lebowski,Lebowski Maude',
            'Jeffrey Lebowski,Lebowski Jeffrey',
            'Karl Hungus,Karl,Inappropriate',
            'Uli Kunkel,Kunkel',
            'The Dude,Dude',
            'Walter Sobchak,Sobchak',
            'Theodore Donald Kerabatsos,Kerabatsos',
        ])
        good_names = OrderedDict()
        good_names['D'] = ['The Dude']
        good_names['K'] = ['Theodore Donald Kerabatsos', 'Uli Kunkel']
        good_names['L'] = ['Bunny Lebowski', 'Jeffrey Lebowski', 'Maude Lebowski']
        good_names['S'] = ['Walter Sobchak']
        self.assertEqual(names, good_names)
