/*
 * Add a "generate caption via IA" button under the lead image caption field.
 *
 * Only active on add/edit forms showing both the lead image widget and a
 * visible caption input (the caption is hidden by default in
 * imio.smartweb.common forms, products re-enable it where needed).
 * The chosen image (or the stored one, on edit forms) is sent to
 * @@process-image-metadata, which calls Omnia's deduce-metadata agent; the
 * returned title fills the caption.
 */
(() => {
  'use strict';

  const IMAGE_NAME = 'form.widgets.ILeadImageBehavior.image';
  const CAPTION_ID = 'form-widgets-ILeadImageBehavior-image_caption';

  function getBaseUrl() {
    const body = document.body;
    return (body.dataset.baseUrl || body.dataset.portalUrl || '').replace(/\/$/, '');
  }

  function getFileInput(form) {
    return form.querySelector(`input[type="file"][name="${IMAGE_NAME}"]`);
  }

  // On edit forms, the stored image is kept unless "remove" / "replace" is chosen.
  function keepsStoredImage(form) {
    const action = form.querySelector(`input[type="radio"][name="${IMAGE_NAME}.action"]:checked`);
    return action !== null && action.value === 'nochange';
  }

  function setMessage(el, text, isError) {
    el.textContent = text;
    el.classList.toggle('text-danger', !!isError);
  }

  async function generate(form, caption, button, message) {
    const fileInput = getFileInput(form);
    const file = fileInput && fileInput.files && fileInput.files[0];
    if (!file && !keepsStoredImage(form)) {
      setMessage(message, 'Veuillez d\'abord choisir une image.', true);
      return;
    }
    const data = new FormData();
    if (file) data.append('image', file);
    const authenticator = form.querySelector('input[name="_authenticator"]');
    if (authenticator) data.append('_authenticator', authenticator.value);

    button.disabled = true;
    setMessage(message, 'Génération en cours…', false);
    try {
      const response = await fetch(`${getBaseUrl()}/@@process-image-metadata`, {
        method: 'POST',
        body: data,
        credentials: 'same-origin',
        headers: { Accept: 'application/json' },
      });
      const result = response.ok ? await response.json() : {};
      if (!result.title) {
        setMessage(message, 'Impossible de générer une légende pour cette image.', true);
        return;
      }
      caption.value = result.title;
      caption.dispatchEvent(new Event('change', { bubbles: true }));
      setMessage(message, '', false);
    } catch (e) {
      setMessage(message, 'Impossible de générer une légende pour cette image.', true);
    } finally {
      button.disabled = false;
    }
  }

  function init() {
    const caption = document.getElementById(CAPTION_ID);
    if (!caption || caption.type === 'hidden' || caption.dataset.iaMetadata) return;
    const form = caption.closest('form');
    if (!form || !getFileInput(form)) return;
    caption.dataset.iaMetadata = '1';

    const wrapper = document.createElement('div');
    wrapper.className = 'ia-image-metadata mt-2';
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'btn btn-secondary btn-sm ia-image-metadata-button';
    button.textContent = 'Générer la légende via IA';
    const message = document.createElement('span');
    message.className = 'ia-image-metadata-message ms-2';
    message.setAttribute('aria-live', 'polite');
    wrapper.append(button, message);
    caption.insertAdjacentElement('afterend', wrapper);

    button.addEventListener('click', () => generate(form, caption, button, message));
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
