import './edit.less'
jQuery(document).ready(function ($) {

  // Limit uploaded files sizes to 20Mo (without reaching the server)

  $("input[type='file']").on("change", function () {
    if(this.files[0].size > 20*1024*1024) {
      // TODO: translate this message
      alert("Le poids de votre image/fichier dépasse les 20Mo autorisés. Veuillez alléger votre fichier.");
      $(this).val(null);
    }
  });


  // Toggle on add / edit forms fieldsets

  // 1. hide default fieldset legend (ckass : expanded)
  $("form.tabbed-form-with-toggle fieldset:first legend").hide();
  $("form.tabbed-form-with-toggle fieldset:first legend").addClass("expanded");

  // 2. hide all fieldsets content except first (class : collapsed)
  $("form.tabbed-form-with-toggle fieldset:not(:first) legend").siblings().hide();
  $("form.tabbed-form-with-toggle fieldset:not(:first) legend").addClass("dropdown-toggle collapsed");

  // 3. add toggle on all fieldsets legends & toggle expanded / collapsed classes
  $("form.tabbed-form-with-toggle fieldset:not(:first) legend").click(function(){
     var legend = $(this);
     var changed_class = false;
     $(this).siblings().slideToggle("fast", function() {
         if (!changed_class) {
            legend.toggleClass("collapsed");
            legend.toggleClass("expanded");
            changed_class = true;
        }
     });
  });
});
