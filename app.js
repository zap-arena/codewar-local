// Minimal client: no login/password — a student just enters name, email,
// college ID and preferred language, then their per-stage code is captured
// against a standalone Neon-backed API (api/index.py in this same folder).
// No code execution/judging is involved anywhere in this flow.

(function () {
  const STORAGE_KEY = "codewar_offline_session_v1";

  // On Vercel the API is rewritten under the same domain (see vercel.json), so the page's
  // own origin is always the right API base. file:// / localhost dev falls back to :8000.
  function detectApiBase() {
    const { origin, protocol, hostname } = window.location;
    if (protocol === "file:" || !origin || origin === "null") return "http://localhost:8001";
    if (hostname === "localhost" || hostname === "127.0.0.1") return "http://localhost:8001";
    return origin;
  }

  const DEFAULT_API_BASE = detectApiBase();

  // Only overridden if the deployment sets PUBLIC_API_BASE in Vercel's env vars
  // (frontend and API on different domains); there is no UI control for this.
  async function resolveApiBase() {
    try {
      const res = await fetch(`${DEFAULT_API_BASE}/api/config`);
      if (!res.ok) return DEFAULT_API_BASE;
      const data = await res.json();
      return data?.apiBase ? data.apiBase.replace(/\/$/, "") : DEFAULT_API_BASE;
    } catch (e) {
      // /api/config unreachable — fall back to the auto-detected same-origin base.
      return DEFAULT_API_BASE;
    }
  }

  let session = {
    apiBase: DEFAULT_API_BASE,
    student: null, // { id, name, email, collegeId, language }
    language: "python",
    current: 0,
    submissions: {}, // stageIndex -> { language, code, submittedAt, synced }
    drafts: {}, // stageIndex -> code (unsubmitted working copy)
  };

  const authScreen = document.getElementById("auth-screen");
  const stageScreen = document.getElementById("stage-screen");
  const summaryScreen = document.getElementById("summary-screen");

  const authNameInput = document.getElementById("authName");
  const authEmailInput = document.getElementById("authEmail");
  const authCollegeIdInput = document.getElementById("authCollegeId");
  const languageSelect = document.getElementById("languageSelect");
  const authError = document.getElementById("authError");
  const authSubmitBtn = document.getElementById("authSubmitBtn");

  const candidateBadge = document.getElementById("candidateBadge");
  const signOutBtn = document.getElementById("signOutBtn");
  const progressEl = document.getElementById("progress");
  const stageNum = document.getElementById("stageNum");
  const stageTitle = document.getElementById("stageTitle");
  const stageComplexity = document.getElementById("stageComplexity");
  const stageStatement = document.getElementById("stageStatement");
  const sampleInput = document.getElementById("sampleInput");
  const sampleOutput = document.getElementById("sampleOutput");
  const editorLanguage = document.getElementById("editorLanguage");
  const codeEditor = document.getElementById("codeEditor");
  const resetBtn = document.getElementById("resetBtn");
  const saveIndicator = document.getElementById("saveIndicator");
  const prevBtn = document.getElementById("prevBtn");
  const nextBtn = document.getElementById("nextBtn");
  const stageIndicator = document.getElementById("stageIndicator");

  const summaryLine = document.getElementById("summaryLine");
  const summaryList = document.getElementById("summaryList");
  const downloadBtn = document.getElementById("downloadBtn");
  const restartBtn = document.getElementById("restartBtn");

  function persist() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
  }

  function loadPersisted() {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    try {
      const parsed = JSON.parse(raw);
      if (parsed?.student) session = parsed;
    } catch (e) {
      /* ignore corrupt storage */
    }
  }

  function showScreen(el) {
    [authScreen, stageScreen, summaryScreen].forEach((s) =>
      s.classList.add("hidden"),
    );
    el.classList.remove("hidden");
  }

  async function apiFetch(path, options = {}) {
    const res = await fetch(`${session.apiBase}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
    });
    let body = null;
    try {
      body = await res.json();
    } catch (e) {
      /* empty body */
    }
    if (!res.ok) {
      throw new Error(body?.detail || `Request failed (${res.status})`);
    }
    return body;
  }

  // ---- Details screen ----
  authSubmitBtn.addEventListener("click", async () => {
    const name = authNameInput.value.trim();
    const email = authEmailInput.value.trim();
    const collegeId = authCollegeIdInput.value.trim();
    authError.classList.add("hidden");

    if (!name || !email) {
      authError.textContent = "Name and email are required.";
      authError.classList.remove("hidden");
      return;
    }

    authSubmitBtn.disabled = true;
    authSubmitBtn.textContent = "Please wait…";
    try {
      const student = await apiFetch("/api/register", {
        method: "POST",
        body: JSON.stringify({
          name,
          email,
          collegeId,
          language: languageSelect.value,
        }),
      });
      session.student = student;
      session.language = student.language || languageSelect.value;
      session.current = 0;
      persist();
      await enterStages();
    } catch (err) {
      authError.textContent = err.message || "Something went wrong.";
      authError.classList.remove("hidden");
    } finally {
      authSubmitBtn.disabled = false;
      authSubmitBtn.textContent = "Start solving →";
    }
  });

  async function enterStages() {
    candidateBadge.textContent = session.student
      ? `${session.student.name} · ${session.student.collegeId || session.student.email}`
      : "";
    buildProgressDots();

    // Pull back any submissions already stored server-side (e.g. resuming on another device).
    try {
      const remote = await apiFetch(
        `/api/submissions?studentId=${encodeURIComponent(session.student.id)}&problemSlug=${encodeURIComponent(PROBLEM.slug)}`,
      );
      remote.forEach((r) => {
        session.submissions[r.stage - 1] = {
          language: r.language,
          code: r.code,
          submittedAt: r.submittedAt,
          synced: true,
        };
      });
    } catch (e) {
      /* offline or server unreachable — fall back to whatever is local */
    }

    persist();
    if (Object.keys(session.submissions).length === STAGES.length) {
      goToSummary();
    } else {
      session.current = Math.min(
        Object.keys(session.submissions).length,
        STAGES.length - 1,
      );
      showScreen(stageScreen);
      renderStage();
    }
  }

  function buildProgressDots() {
    progressEl.innerHTML = "";
    STAGES.forEach(() => {
      const dot = document.createElement("div");
      dot.className = "dot";
      progressEl.appendChild(dot);
    });
  }

  function dotClass(i) {
    if (session.submissions[i]) return "dot done";
    if (i === session.current) return "dot active";
    return "dot";
  }

  function updateProgressDots() {
    [...progressEl.children].forEach((dot, i) => {
      dot.className = dotClass(i);
    });
  }

  function currentCode(index) {
    if (session.drafts[index] !== undefined) return session.drafts[index];
    if (session.submissions[index]) return session.submissions[index].code;
    return BOILERPLATE[session.language] || "";
  }

  function renderStage() {
    const idx = session.current;
    const s = STAGES[idx];

    stageNum.textContent = idx + 1;
    stageTitle.textContent = s.title;
    stageComplexity.textContent = `Target: ${s.complexity}`;
    stageStatement.innerHTML = s.statement;
    sampleInput.textContent = s.input;
    sampleOutput.textContent = s.output;

    editorLanguage.value = session.language;
    codeEditor.value = currentCode(idx);

    updateProgressDots();
    stageIndicator.textContent = `Stage ${idx + 1} of ${STAGES.length}`;
    prevBtn.disabled = idx === 0;
    nextBtn.textContent =
      idx === STAGES.length - 1 ? "Submit & Finish 🏆" : "Submit & Continue →";

    const sub = session.submissions[idx];
    saveIndicator.textContent = sub
      ? saveIndicatorText(sub)
      : "Not submitted yet";
  }

  function saveIndicatorText(sub) {
    const status = sub.synced ? "Saved to server" : "Saved locally (retry pending)";
    return `${status} · ${new Date(sub.submittedAt).toLocaleTimeString()}`;
  }

  async function submitCurrentStage() {
    const idx = session.current;
    const record = {
      language: editorLanguage.value,
      code: codeEditor.value,
      submittedAt: new Date().toISOString(),
      synced: false,
    };
    session.submissions[idx] = record;
    delete session.drafts[idx];
    persist();

    saveIndicator.textContent = "Saved locally";
    record.synced = false; // We'll just mark it unsynced locally for now
  }


  function summaryStatusText(sub) {
    if (!sub) return "Not submitted";
    return sub.synced ? `✓ synced · ${sub.language}` : `⚠ local only · ${sub.language}`;
  }

  function summaryStatusClass(sub) {
    if (!sub) return "missing";
    return sub.synced ? "ok" : "pending";
  }

  function goToSummary() {
    showScreen(summaryScreen);
    const submittedCount = Object.keys(session.submissions).length;
    const syncedCount = Object.values(session.submissions).filter((s) => s.synced).length;
    summaryLine.textContent = `${session.student.name} submitted ${submittedCount}/${STAGES.length} stages (${syncedCount} synced to server).`;
    summaryList.innerHTML = "";
    STAGES.forEach((s, i) => {
      const sub = session.submissions[i];
      const row = document.createElement("div");
      row.className = "summary-row";
      row.innerHTML = `
        <span class="summary-stage">${i + 1}. ${s.title}</span>
        <span class="summary-status ${summaryStatusClass(sub)}">${summaryStatusText(sub)}</span>
      `;
      summaryList.appendChild(row);
    });
  }

  // ---- Stage screen ----
  editorLanguage.addEventListener("change", () => {
    session.language = editorLanguage.value;
    // Swap in boilerplate for the new language only if nothing typed yet for this stage
    const idx = session.current;
    if (!session.submissions[idx] && !session.drafts[idx]) {
      codeEditor.value = BOILERPLATE[session.language] || "";
    }
    persist();
  });

  codeEditor.addEventListener("input", () => {
    session.drafts[session.current] = codeEditor.value;
    saveIndicator.textContent = "Draft saved locally";
    persist();
  });

  // Basic tab-key support in the textarea
  codeEditor.addEventListener("keydown", (e) => {
    if (e.key === "Tab") {
      e.preventDefault();
      const start = codeEditor.selectionStart;
      const end = codeEditor.selectionEnd;
      codeEditor.value =
        codeEditor.value.slice(0, start) + "    " + codeEditor.value.slice(end);
      codeEditor.selectionStart = codeEditor.selectionEnd = start + 4;
      codeEditor.dispatchEvent(new Event("input"));
    }
  });

  resetBtn.addEventListener("click", () => {
    if (!confirm("Reset this stage's editor to the starter boilerplate?")) return;
    codeEditor.value = BOILERPLATE[session.language] || "";
    codeEditor.dispatchEvent(new Event("input"));
  });

  prevBtn.addEventListener("click", () => {
    if (session.current > 0) {
      session.current--;
      persist();
      renderStage();
    }
  });

  nextBtn.addEventListener("click", async () => {
    nextBtn.disabled = true;
    await submitCurrentStage();
    nextBtn.disabled = false;
    if (session.current < STAGES.length - 1) {
      session.current++;
      persist();
      renderStage();
    } else {
      goToSummary();
    }
  });

  function signOut() {
    localStorage.removeItem(STORAGE_KEY);
    session = {
      apiBase: session.apiBase,
      student: null,
      language: "python",
      current: 0,
      submissions: {},
      drafts: {},
    };
    authNameInput.value = "";
    authEmailInput.value = "";
    authCollegeIdInput.value = "";
    showScreen(authScreen);
  }

  signOutBtn.addEventListener("click", signOut);

  // ---- Summary screen ----
  downloadBtn.addEventListener("click", async () => {
    const payload = {
      student: session.student,
      problem: PROBLEM,
      exportedAt: new Date().toISOString(),
      stages: STAGES.map((s, i) => ({
        stage: i + 1,
        title: s.title,
        submission: session.submissions[i] || null,
      })),
    };
    
    const originalText = downloadBtn.textContent;
    downloadBtn.textContent = "Saving to Server & Downloading...";
    downloadBtn.disabled = true;
    
    try {
      await apiFetch("/api/submit-bulk", {
        method: "POST",
        body: JSON.stringify(payload)
      });
      // Mark all as synced visually if it succeeds
      for (const idx in session.submissions) {
        session.submissions[idx].synced = true;
      }
      persist();
      goToSummary(); // Re-render summary with synced status
    } catch (err) {
      console.warn("Bulk submit failed:", err.message);
      alert("Could not reach the server to save your progress, but your JSON backup will download now.");
    }

    downloadBtn.textContent = originalText;
    downloadBtn.disabled = false;

    const blob = new Blob([JSON.stringify(payload, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    const safeName = (session.student?.name || "candidate").replace(/\s+/g, "_");
    a.href = url;
    a.download = `${safeName}_contains-duplicate-responses.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  });

  restartBtn.addEventListener("click", () => {
    if (!confirm("Sign out and clear this device's local cache?")) return;
    signOut();
  });

  // ---- Init ----
  async function init() {
    loadPersisted();
    session.apiBase = await resolveApiBase();
    persist();

    if (session.student) {
      authNameInput.value = session.student.name || "";
      authEmailInput.value = session.student.email || "";
      authCollegeIdInput.value = session.student.collegeId || "";
      languageSelect.value = session.language;
      enterStages();
    } else {
      showScreen(authScreen);
    }
  }

  init();
})();


