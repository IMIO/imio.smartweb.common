import './view.less'
jQuery(document).ready(function ($) {

  var portal_url = $("body").data("portal-url");

  // Remove cookies banner if already opted-in/out
  var url = $('#gdpr-consent-banner form').data('json-url');
  $.ajax({
    type: "GET",
    url: url,
    headers: {"Cache-Control": "no-cache"},
    cache: false,
  }).done(function(data) {
    if (data.length == 0) $('#gdpr-consent-banner').remove();
    else {
        $('#gdpr-consent-banner').show();
        // Focus on 'Accept all' submit button for a11y
        $('#gdpr-consent-banner').find("input[type='submit']:first").focus();
    }
  });


  var handleCookiesFeatures = function() {

    // Load analytics JS if allowed
    $.ajax({
      type: "GET",
      url: portal_url + "/@@get_analytics",
      headers: {"Cache-Control": "no-cache"},
      cache: false,
    }).done(function(html) {
        $('div#plone-analytics').html(html);
    });

    // See if we need to un-hide blocked iframes
    if ($('.gdpr-iframe').length > 0) {
      $.ajax({
        type: "GET",
        url: portal_url + "/@@allow_iframes",
        headers: {"Cache-Control": "no-cache"},
        cache: false,
      }).done(function(data) {
          if (data == true) {
            $('.gdpr-iframe-message').hide();
            $('.gdpr-iframe').each(function() {
              $(this).attr("src", $(this).attr("gdpr-src"));
              if ($(this).attr("gdpr-height")) {
                  $(this).attr("height", $(this).attr("gdpr-height"));
              }
              else {
                  $(this).removeAttr("height");
              }
              if ($(this).attr("gdpr-width")) {
                  $(this).attr("width", $(this).attr("gdpr-width"));
              }
              else {
                  $(this).removeAttr("width");
              }
            });
          }
      });
    }
  };

  if(window.Faceted){
    jQuery(Faceted.Events).bind(Faceted.Events.AJAX_QUERY_SUCCESS, function(){
        handleCookiesFeatures();
    });
  }

  handleCookiesFeatures();

});
