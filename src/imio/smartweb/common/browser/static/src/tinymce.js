// Traductions françaises directement dans le JS
tinymce.i18n.add("fr_FR", {
  text_expand_label: "Développer le texte",
  text_improve_label: "Améliorer le texte",
  text_shorter_label: "Raccourcir le texte",
  text_shorter_label: "Raccourcir le texte",
});

tinymce.i18n.add("nl_NL", {
  text_expand_label: "Tekst uitbreiden",
  text_improve_label: "Tekst verbeteren",
  text_shorter_label: "Tekst verkorten",
  text_shorter_label: "Tekst verkorten",
});

tinymce.i18n.add("de_DE", {
  text_expand_label: "Text erweitern",
  text_improve_label: "Text verbessern",
  text_shorter_label: "Text verkürzen",
  text_shorter_label: "Text verkürzen",
});

// --- CSRF helper -------------------------------------------------------------
function getCsrfTokenSync() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  if (meta && meta.content) return meta.content;
  try {
    const xhr = new XMLHttpRequest();
    xhr.open("GET", "@@authenticator", false);
    xhr.send(null);
    const m = /value="([^"]+)"/.exec(xhr.responseText);
    return m ? m[1] : "";
  } catch (e) {
    return "";
  }
}

// --- HTTP helper -------------------------------------------------------------
async function postProcess(url, payload) {
  // const token = getCsrfTokenSync();
  const resp = await fetch(url, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json; charset=utf-8",
      "X-CSRF-TOKEN": token,
    },
    credentials: "same-origin",
    body: JSON.stringify(payload),
  });
  if (!resp.ok) {
    const txt = await resp.text().catch(() => "");
    throw new Error("HTTP " + resp.status + " – " + txt);
  }
  const ct = resp.headers.get("Content-Type") || "";
  return ct.includes("application/json")
    ? resp.json()
    : { html: await resp.text() };
}

// --- UI helpers (spinner + disable button) -----------------------------------
function startProcessingUI(editor, btnApi) {
  if (btnApi) btnApi.setEnabled(false);
  editor.setProgressState?.(true); // spinner intégré TinyMCE
}
function stopProcessingUI(editor, btnApi) {
  editor.setProgressState?.(false);
  if (btnApi) btnApi.setEnabled(true);
}
async function withProcessingUI(editor, btnApi, fn) {
  try {
    startProcessingUI(editor, btnApi);
    await fn();
    stopProcessingUI(editor, btnApi);
    editor.notificationManager.open({
      text: "Terminé",
      type: "success",
      timeout: 1800,
    });
  } catch (e) {
    console.error("[tinymce-process] error:", e);
    stopProcessingUI(editor, btnApi);
    editor.notificationManager.open({
      text: "Échec du traitement",
      type: "error",
      timeout: 2500,
    });
  }
}

// --- Selection helper --------------------------------------------------------
function getSelectedHtml(editor) {
  // TinyMCE renvoie du HTML formaté si on demande format:"html"
  return editor.selection?.getContent({ format: "html" }) || "";
}

// --- Plugins -----------------------------------------------------------------
(function () {
  if (!window.tinymce) return;

  // ===== Plugin 1 : text_expand =====
  tinymce.PluginManager.add("text_expand", function (editor) {
    let btnApi = null;

    editor.addCommand("textExpandRun", async function () {
      const selectedHtml = getSelectedHtml(editor);
      if (!selectedHtml.trim()) {
        editor.notificationManager.open({
          text: "Sélectionnez du texte à traiter.",
          type: "warning",
          timeout: 2000,
        });
        return;
      }

      // On mémorise la sélection avant l'appel async
      const bookmark = editor.selection.getBookmark(2, true);

      await withProcessingUI(editor, btnApi, async () => {
        const data = await postProcess("@@process-textexpand", {
          html: selectedHtml,
        });
        if (!data || typeof data.html !== "string")
          throw new Error("Réponse invalide");
        editor.undoManager.transact(() => {
          editor.selection.moveToBookmark(bookmark);
          editor.selection.setContent(data.html);
        });
      });
    });

    editor.ui.registry.addButton("text_expand", {
      text: "Text expand",
      tooltip: "Process text expand",
      onAction: () => editor.execCommand("textExpandRun"),
      onSetup: (api) => {
        btnApi = api;
        return () => (btnApi = null);
      },
    });
  });

  // ===== Plugin 2 : text_improve =====
  tinymce.PluginManager.add("text_improve", function (editor) {
    let btnApi = null;

    editor.addCommand("textImproveRun", async function () {
      const selectedHtml = getSelectedHtml(editor);
      if (!selectedHtml.trim()) {
        editor.notificationManager.open({
          text: "Sélectionnez le passage pour améliorer le texte.",
          type: "warning",
          timeout: 2000,
        });
        return;
      }

      const bookmark = editor.selection.getBookmark(2, true);

      await withProcessingUI(editor, btnApi, async () => {
        const data = await postProcess("@@process-textimprove", {
          html: selectedHtml,
        });
        if (!data || typeof data.html !== "string")
          throw new Error("Réponse invalide");
        editor.undoManager.transact(() => {
          editor.selection.moveToBookmark(bookmark);
          editor.selection.setContent(data.html);
        });
      });
    });

    editor.ui.registry.addButton("text_improve", {
      text: "Text improve",
      tooltip: "Améliorer le texte",
      onAction: () => editor.execCommand("textImproveRun"),
      onSetup: (api) => {
        btnApi = api;
        return () => (btnApi = null);
      },
    });
  });

  // ===== Plugin 3 : text_shorter =====
  tinymce.PluginManager.add("text_shorter", function (editor) {
    let btnApi = null;

    editor.addCommand("textShorterRun", async function () {
      const selectedHtml = getSelectedHtml(editor);
      if (!selectedHtml.trim()) {
        editor.notificationManager.open({
          text: "Sélectionnez le passage pour raccourcir le texte.",
          type: "warning",
          timeout: 2000,
        });
        return;
      }

      const bookmark = editor.selection.getBookmark(2, true);

      await withProcessingUI(editor, btnApi, async () => {
        const data = await postProcess("@@process-textshorter", {
          html: selectedHtml,
        });
        if (!data || typeof data.html !== "string")
          throw new Error("Réponse invalide");
        editor.undoManager.transact(() => {
          editor.selection.moveToBookmark(bookmark);
          editor.selection.setContent(data.html);
        });
      });
    });

    editor.ui.registry.addButton("text_shorter", {
      text: "Text shorter",
      tooltip: "Raccourcir le texte",
      onAction: () => editor.execCommand("textShorterRun"),
      onSetup: (api) => {
        btnApi = api;
        return () => (btnApi = null);
      },
    });
  });

  tinymce.PluginManager.add("ia", function (editor) {
    // Déclare ton icône custom (injectée dans le registry de l’éditeur actif)
    editor.ui.registry.addIcon(
      "iacustom",
      `
        <svg width="25" height="23.6"><path d="m9.2 2.6.8 3.9a5 5 0 0 0 3.8 3.8l3.9.8c.3.1.3.5 0 .5l-3.9.9a5 5 0 0 0-3.8 3.8L9.2 20c0 .3-.5.3-.5 0l-.8-3.8A5 5 0 0 0 4 12.4l-3.8-.8c-.3 0-.3-.4 0-.5l3.8-.8A5 5 0 0 0 8 6.5l.8-3.9c0-.2.4-.2.5 0ZM19.4 12.1l.5 2.6a3 3 0 0 0 2.4 2.4l2.6.5v.3l-2.6.6a3 3 0 0 0-2.4 2.3l-.5 2.7H19l-.6-2.7a3 3 0 0 0-2.3-2.3l-2.7-.6v-.3l2.7-.5a3 3 0 0 0 2.3-2.4l.6-2.6c0-.2.2-.2.2 0ZM17.7.1l.3 1.3a3 3 0 0 0 2.4 2.4l1.3.2v.3l-1.3.3A3 3 0 0 0 18 7l-.3 1.3h-.3L17.2 7a3 3 0 0 0-2.4-2.4l-1.3-.3V4l1.3-.2a3 3 0 0 0 2.4-2.4l.2-1.3h.3Z"/></svg>
     `
    );

    editor.ui.registry.addIcon(
      "iashorter",
      `
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24.01 24">
        <path d="m18.58 12.97.54 2.53c.24 1.13 1.12 2 2.25 2.25l2.53.54c.16.03.16.26 0 .29l-2.53.54c-1.13.24-2 1.12-2.25 2.25l-.54 2.53c-.03.16-.26.16-.29 0l-.54-2.53c-.24-1.13-1.12-2-2.25-2.25l-2.53-.54c-.16-.03-.16-.26 0-.29l2.53-.54c1.13-.24 2-1.12 2.25-2.25l.54-2.53c.03-.16.26-.16.29 0ZM0 0h24v2.53H0zm0 5.4h18v2.53H0zm0 5.15h9v2.53H0z"/>
        </svg>
      `
    );

    editor.ui.registry.addIcon(
      "iaexpand",
      `
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24.15 23.97">
        <path d="m18.71.12.54 2.53c.24 1.13 1.12 2 2.25 2.25l2.53.54c.16.03.16.26 0 .29l-2.53.54c-1.13.24-2 1.12-2.25 2.25l-.54 2.53c-.03.16-.26.16-.29 0l-.54-2.53c-.24-1.13-1.12-2-2.25-2.25l-2.53-.54c-.16-.03-.16-.26 0-.29l2.53-.54c1.13-.24 2-1.12 2.25-2.25l.54-2.53c.03-.16.26-.16.29 0ZM.02 9.66h15.13v2.53H.02zm.16 6h11.97v2.53H.18zm15.97 0h8v2.53h-8zM0 21.44h9v2.53H0zm13.15 0H20v2.53h-6.85z"/>
        </svg>
      `
    );

    editor.ui.registry.addMenuButton("ia", {
      text: "IA",
      tooltip: "Outils IA",
      icon: "iacustom", // 👈 maintenant ça marche
      fetch: (callback) => {
        callback([
          {
            type: "menuitem",
            text: tinymce.i18n.translate("text_expand_label"),
            icon: "iashorter",
            onAction: () => editor.execCommand("textExpandRun"),
          },
          {
            type: "menuitem",
            text: tinymce.i18n.translate("text_improve_label"),
            icon: "ai-prompt",
            onAction: () => editor.execCommand("textImproveRun"),
          },
          {
            type: "menuitem",
            text: tinymce.i18n.translate("text_shorter_label"),
            icon: "iashorter",
            onAction: () => editor.execCommand("textShorterRun"),
          },
        ]);
      },
    });
  });
})();
