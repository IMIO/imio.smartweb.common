(()=>{"use strict";jQuery(document).ready((function(e){e("input[type='file']").on("change",(function(){this.files[0].size>20971520&&(alert("Le poids de votre image/fichier dépasse les 20Mo autorisés. Veuillez alléger votre fichier."),e(this).val(null))})),e("form.tabbed-form-with-toggle fieldset:first legend").hide(),e("form.tabbed-form-with-toggle fieldset:first legend").addClass("expanded"),e("form.tabbed-form-with-toggle fieldset:not(:first) legend").siblings().hide(),e("form.tabbed-form-with-toggle fieldset:not(:first) legend").addClass("dropdown-toggle collapsed"),e("form.tabbed-form-with-toggle fieldset:not(:first) legend").click((function(){var t=e(this),i=!1;e(this).siblings().slideToggle("fast",(function(){i||(t.toggleClass("collapsed"),t.toggleClass("expanded"),i=!0)}))}))}))})();