/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

(function($) {
    'use strict';

    var $sfForm = $('#sf-form');
    var $sfFormSubmit = $('#sf-form-submit');
    var $campaign_type = $('#campaign_type');
    var $typeFields = $('.type-field');
    var $typeInputs = $typeFields.find('input, textarea, select');

    var $partnerFormError = $('#partner-form-error');
    var $mainContent = $('#main-content');
    var $htmlBody = $('html, body');

    $sfForm.validate();

    var scrollup = function() {
        $htmlBody.animate({ scrollTop: $mainContent.offset().top }, 500);
    };

    var campaign_type_other = function() {
        return $campaign_type.val().indexOf('Other') > -1;
        // TODO: Is this an l10n issue?
    };

    var toggleTypeFields = function(activate) {
        if (activate) {
            $typeFields.show();
        } else {
            $typeFields.hide();
        }
    };

    $campaign_type.on('change', function() {
        toggleTypeFields(campaign_type_other());
    });

    $sfFormSubmit.on('click', function(e) {
        e.preventDefault();

        if ($sfForm.valid()) {
            // if not interested in tiles, clear out the tiles fields
            if (!campaign_type_other()) {
                $typeInputs.val('');
            }

            $.ajax({
                url: $sfForm.attr('action'),
                data: $sfForm.serialize(),
                type: $sfForm.attr('method'),
                dataType: 'json',
                success: function(data, status, xhr) {
                    $('#partner-form').fadeOut('fast', function() {
                        $('#partner-form-success').css('visibility', 'visible').fadeIn('fast', function() {
                            scrollup();
                        });
                    });
                },
                error: function(xhr, status, error) {
                    // grab json string from server and convert to JSON obj
                    var json = $.parseJSON(xhr.responseText);
                    Mozilla.FormHelper.displayErrors(json.errors);
                    $partnerFormError.css('visibility', 'visible').slideDown('fast', function() {
                        scrollup();
                    });
                }
            });
        }
    });
})(window.jQuery);
