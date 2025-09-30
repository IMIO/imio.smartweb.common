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

  // Menu bouton "IA" dans la toolbar façon Antoine B.
  tinymce.PluginManager.add("ia", function (editor) {
    editor.ui.registry.addMenuButton("ia", {
      text: "IA",
      tooltip: "Outils IA",
      fetch: (callback) => {
        callback([
          {
            type: "menuitem",
            text: "Text expand",
            onAction: () => editor.execCommand("textExpandRun"),
          },
          {
            type: "menuitem",
            text: "Suggest titles",
            onAction: () => editor.execCommand("suggestTitlesRun"),
          },
          {
            type: "menuitem",
            text: "Text improve",
            onAction: () => editor.execCommand("textImproveRun"),
          },
          {
            type: "menuitem",
            text: "Text shorter",
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
