/* This Source Code Form is subject to the terms of the Mozilla Public
* License, v. 2.0. If a copy of the MPL was not distributed with this
* file, You can obtain one at http://mozilla.org/MPL/2.0/. */

;(function($, Modernizr, site) {
    'use strict';

    var $html = $(document.documentElement);
    var $shield = $('#tracking-protection-animation');

    Mozilla.HighlightTarget.init('.button-flat-dark');

    if (window.isFirefox()) {
        if (window.isFirefoxUpToDate()) {
            $html.addClass('firefox-up-to-date');
            $('.button-flat-dark').on('highlight-target', function() {
                $shield.addClass('blocked');
            });
        } else {
            $html.addClass('firefox-old');
        }
    } else {
        $html.addClass('non-firefox');
        if (site.platform === 'android') {
            $html.addClass('android-device'); 
        } else if (site.platform === 'ios') {
            $html.addClass('ios-device');
        }
    }

})(window.jQuery, window.Modernizr, window.site);
