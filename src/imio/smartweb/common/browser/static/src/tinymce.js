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

  // ===== Plugin 2 : suggest_titles =====
  tinymce.PluginManager.add("suggest_titles", function (editor) {
    let btnApi = null;

    editor.addCommand("suggestTitlesRun", async function () {
      const selectedHtml = getSelectedHtml(editor);
      if (!selectedHtml.trim()) {
        editor.notificationManager.open({
          text: "Sélectionnez le passage pour proposer des titres.",
          type: "warning",
          timeout: 2000,
        });
        return;
      }

      const bookmark = editor.selection.getBookmark(2, true);

      await withProcessingUI(editor, btnApi, async () => {
        const data = await postProcess("@@process-suggesttitles", {
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

    editor.ui.registry.addButton("suggest_titles", {
      text: "Suggest titles",
      tooltip: "Proposer des titres",
      onAction: () => editor.execCommand("suggestTitlesRun"),
      onSetup: (api) => {
        btnApi = api;
        return () => (btnApi = null);
      },
    });
  });

  // ===== Plugin 3 : text_improve =====
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

  // ===== Plugin 4 : text_shorter =====
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

    editor.ui.registry.addIcon(
      "iatitle",
      `
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24.32 23.79">
        <path d="m20.84.07.35 1.62c.15.72.72 1.29 1.44 1.44l1.62.35c.1.02.1.16 0 .19l-1.62.35c-.72.15-1.29.72-1.44 1.44l-.35 1.62c-.02.1-.16.1-.19 0l-.35-1.62c-.15-.72-.72-1.29-1.44-1.44l-1.62-.35c-.1-.02-.1-.16 0-.19l1.62-.35c.72-.15 1.29-.72 1.44-1.44l.35-1.62c.02-.1.16-.1.19 0Z"/>
        <path d="M14.96 11.08c-.29-1.22-.88-2.24-1.14-2.61-.48-.56-.69-.77-2.26-.77h-1.7v12.51c0 2.24.27 2.4 2.64 2.58v.99H3.65v-.99c2.26-.19 2.5-.35 2.5-2.58V7.7H4.53c-1.49 0-1.92.24-2.42.88-.37.51-.75 1.46-1.09 2.53H0c.19-1.94.37-4.02.43-5.3h.8c.4.61.72.67 1.52.67H13.4c.72 0 1.09-.16 1.54-.67h.77c.03 1.12.13 3.46.27 5.19l-1.01.08Zm6.97 4.66c-.12-.52-.37-.95-.48-1.1-.2-.24-.29-.33-.96-.33h-.72v5.29c0 .95.11 1.01 1.12 1.09v.42h-3.74v-.42c.96-.08 1.06-.15 1.06-1.09v-5.29h-.69c-.63 0-.81.1-1.02.37-.16.21-.32.62-.46 1.07h-.43c.08-.82.16-1.7.18-2.24h.34c.17.26.3.28.64.28h4.5c.3 0 .46-.07.65-.28h.33c.01.47.06 1.46.11 2.2l-.43.03Z" class="cls-1"/>
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
            text: "Text expand",
            icon: "iashorter",
            onAction: () => editor.execCommand("textExpandRun"),
          },
          {
            type: "menuitem",
            text: "Suggest titles",
            icon: "iatitle",
            onAction: () => editor.execCommand("suggestTitlesRun"),
          },
          {
            type: "menuitem",
            text: "Text improve",
            icon: "ai-prompt",
            onAction: () => editor.execCommand("textImproveRun"),
          },
          {
            type: "menuitem",
            text: "Text shorter",
            icon: "iashorter",
            onAction: () => editor.execCommand("textShorterRun"),
          },
        ]);
      },
    });
  });

  // Menu bouton "IA" dans la toolbar façon Seb
  tinymce.PluginManager.add("ia_menuitems", function (editor) {
    editor.ui.registry.addMenuItem("ia_text_expand", {
      text: "Text expand",
      onAction: () => editor.execCommand("textExpandRun"),
    });
    editor.ui.registry.addMenuItem("ia_suggest_titles", {
      text: "Suggest titles",
      onAction: () => editor.execCommand("suggestTitlesRun"),
    });
  });
})();
