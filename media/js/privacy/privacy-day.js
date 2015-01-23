/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

$(function() {
    'use strict';

    var pager = Mozilla.Pager.pagers[0];

    // scroll to top of pager when switching tabs so all
    // tab content is visible after switching tabs
    pager.$container.on('changePage', function() {

        // Get the current document scroll position
        var scrollPos = $(document).scrollTop();

        // Get the offset of the top of the pager section
        var pagerTopPos = $('.pager').first().offset().top;

        // If we're scrolled passed the header, jump back up
        // to the tabs when the tab is switched
        if (scrollPos > pagerTopPos) {
            $('html, body').scrollTop($('.pager').first().offset().top);
        }
    });

    // enable sticky tab nagivation
    $('#button-nav-wrapper').waypoint('sticky');

    var trackClick = function (gaArgs, href, event) {
        if (event.metaKey || event.ctrlKey) {
            // Open link in new tab
            gaTrack(gaArgs);
        } else {
            event.preventDefault();
            gaTrack(gaArgs, function() { window.location = href; });
        }
    };

    // Setup GA tracking for main tabs
    $('#tips-nav-direct a').on('click', function(e) {
        var thisTabName = $(this).attr('href');
        trackClick([
            '_trackEvent',
            '/privacy/ Interactions',
            thisTabName.substr(1), // strip # char from tab hash
            'Tab Click'
        ], $(this).attr('href'), e);
    });

    // Setup GA tracking for paragraph and list links
    $('.tip-column p a, .tip-column li a').on('click', function(e) {
        trackClick([
            '_trackEvent',
            '/privacy/ Interactions',
            pager.currentPage.id,
            $(this).attr('href')
        ], $(this).attr('href'), e);
    });

    // Setup GA tracking TED video link
    $('.greenwald a').on('click', function(e) {
        trackClick([
            '_trackEvent',
            '/privacy/ Interactions',
            pager.currentPage.id,
            'Why Privacy Matters CTA Btn'
        ], $(this).attr('href'), e);
    });

    // Setup GA tracking for next tab buttons
    $('.tip-footer .next a').on('click', function(e) {
        trackClick([
            '_trackEvent',
            '/privacy/ Interactions',
            pager.currentPage.id,
            'Next'
        ], $(this).attr('href'), e);
    });

    // Setup GA tracking for previous tab buttons
    $('.tip-footer .previous a').on('click', function(e) {
        trackClick([
            '_trackEvent',
            '/privacy/ Interactions',
            pager.currentPage.id,
            'Previous'
        ], $(this).attr('href'), e);
    });

});
