/* This Source Code Form is subject to the terms of the Mozilla Public
* License, v. 2.0. If a copy of the MPL was not distributed with this
* file, You can obtain one at http://mozilla.org/MPL/2.0/. */

;(function($) {
    'use strict';

    setTimeout(Mozilla.syncAnimation, 1000);

    /* This shows six different content variations, depending on the browser/state
     * 1. Firefox 31+ (signed-in to Sync) <-- default
     * 2. Firefox 31+ (signed-out of Sync)
     * 3. Firefox 29 or 30
     * 4. Firefox 28 or older
     * 5. Firefox for Android
     * 6. Not Firefox (any other browser)
     */

    // Variation #1: Firefox 31+ signed-in to Sync
    // Default (do nothing)

    var fxMasterVersion = window.getFirefoxMasterVersion();
    var state = 'Unknown';


    // Variations 1-5 are Firefox
    if (window.isFirefox()) {

        // Variation #5: Firefox for Android
        if (window.isFirefoxMobile()) {

            $('body').addClass('state-fx-android');
            state = 'Firefox for Android';


        // Variation #1-4: Firefox for Desktop
        } else {

            if (fxMasterVersion >= 31) {

                // Query if the UITour API is working before we use the API
                Mozilla.UITour.getConfiguration('sync', function (config) {

                    // Variation #1: Firefox 31+ signed IN to Sync (default)
                    if (config.setup) {

                        $('body').addClass('state-fx-31-signed-in');
                        state = 'Latest Version of Firefox or Higher: Signed-In';

                    // Variation #2: Firefox 31+ signed OUT of Sync
                    } else {
                        $('body').addClass('state-fx-31-signed-out');
                        state = 'Latest Version of Firefox or Higher: Signed-Out';
                    }

                });

            // Variation #3: Firefox 29 or 30
            } else if (fxMasterVersion === 29 || fxMasterVersion === 30) {
                $('body').addClass('state-fx-29-30');
                state = 'Previous 2 Versions of Firefox';

            // Variation #4: Firefox 28 or older
            } else if (fxMasterVersion <= 28) {
                $('body').addClass('state-fx-28-older');
                state = 'Older Version of Firefox';
            }

        }

    // Variation #6: Not Firefox
    } else {
        $('body').addClass('state-not-fx');
        state = 'Not Firefox';
    }

    // Send page state to GA
    _gaq.push(['_trackEvent', '/sync/ Page Interactions', 'load', state]);

    // Setup GA tracking for Firefox download button
    $('#cta-firefox').on('click', function() {
        _gaq.push(['_trackEvent', 'Firefox Downloads', 'download click', 'Firefox']);
    });

    // Setup GA tracking for Firefox for primary Android download button
    $('#cta-android').on('click', function() {
        _gaq.push(['_trackEvent', 'Firefox Downloads', 'top', 'Firefox for Android']);
    });

    // Setup GA tracking for Firefox for Android footer download button
    $('#cta-android-footer').on('click', function() {
        _gaq.push(['_trackEvent', 'Firefox Downloads', 'bottom', 'Firefox for Android']);
    });

    // Setup GA tracking for Sync button
    $('#cta-sync').on('click', function() {
        _gaq.push(['_trackEvent', '/sync/ Page Interactions', 'button click', 'Sync CTA']);
    });


})(window.jQuery);
