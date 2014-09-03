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

    // Variations 1-5 are Firefox
    if (window.isFirefox()) {

        // Variation #5: Firefox for Android
        if (window.isFirefoxMobile()) {

            $('body').addClass('state-fx-android');

        // Variation #1-4: Firefox for Desktop
        } else {

            if (fxMasterVersion >= 31) {

                // Query if the UITour API is working before we use the API
                Mozilla.UITour.getConfiguration('sync', function (config) {

                    // Variation #1: Firefox 31+ signed IN to Sync (default)
                    if (config.setup) {

                        $('body').addClass('state-fx-31-signed-in');

                    // Variation #2: Firefox 31+ signed OUT of Sync
                    } else {
                        $('body').addClass('state-fx-31-signed-out');
                    }

                });

            // Variation #3: Firefox 29 or 30
            } else if (fxMasterVersion === 29 || fxMasterVersion === 30) {
                $('body').addClass('state-fx-29-30');

            // Variation #4: Firefox 28 or older
            } else if (fxMasterVersion <= 28) {
                $('body').addClass('state-fx-28-older');
            }

        }

    // Variation #6: Not Firefox
    } else {
        $('body').addClass('state-not-fx');
    }

})(window.jQuery);
