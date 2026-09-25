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
    if (protocol === "file:" || !origin || origin === "null")
      return "http://localhost:8001";
    if (hostname === "localhost" || hostname === "127.0.0.1")
      return "http://localhost:8001";
    return origin;
  }

  const DEFAULT_API_BASE = detectApiBase();

  // Only overridden if the deployment sets PUBLIC_API_BASE in Vercel's env vars
  async function resolveApiBase() {
    try {
      const res = await fetch(`${DEFAULT_API_BASE}/api/config`);
      if (!res.ok) return DEFAULT_API_BASE;
      const data = await res.json();
      return data?.apiBase ? data.apiBase.replace(/\/$/, "") : DEFAULT_API_BASE;
    } catch (e) {
      return DEFAULT_API_BASE;
    }
  }

  let session = {
    apiBase: DEFAULT_API_BASE,
    student: null, // { id, name, email, collegeId, language }
    language: "python",
    problemStates: {}, // slug -> { current: 0, submissions: {}, drafts: {} }
  };

  let currentProblemSlug = null;
  let PROBLEM = null;
  let STAGES = null;

  const authScreen = document.getElementById("auth-screen");
  const dashboardScreen = document.getElementById("dashboard-screen");
  const stageScreen = document.getElementById("stage-screen");
  const summaryScreen = document.getElementById("summary-screen");

  const authNameInput = document.getElementById("authName");
  const authEmailInput = document.getElementById("authEmail");
  const authCollegeIdInput = document.getElementById("authCollegeId");
  const languageSelect = document.getElementById("languageSelect");
  const authError = document.getElementById("authError");
  const authSubmitBtn = document.getElementById("authSubmitBtn");

  const problemList = document.getElementById("problemList");
  const dashboardSignOutBtn = document.getElementById("dashboardSignOutBtn");

  const candidateBadge = document.getElementById("candidateBadge");
  const signOutBtn = document.getElementById("signOutBtn");
  const topBarTitle = document.getElementById("topBarTitle");
  const progressEl = document.getElementById("progress");
  const stageNum = document.getElementById("stageNum");
  const stageTitle = document.getElementById("stageTitle");
  const stageComplexity = document.getElementById("stageComplexity");
  const stageStatement = document.getElementById("stageStatement");
  const samplesContainer = document.getElementById("samplesContainer");
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
  const backToDashboardBtn = document.getElementById("backToDashboardBtn");

  function persist() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
  }

  function loadPersisted() {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    try {
      const parsed = JSON.parse(raw);
      if (parsed?.student) {
        session = parsed;
        if (!session.problemStates) {
          // migrate old session
          session.problemStates = {};
          if (session.submissions) {
            session.problemStates["contains-duplicate-progressive"] = {
              current: session.current || 0,
              submissions: session.submissions || {},
              drafts: session.drafts || {},
            };
          }
        }
      }
    } catch (e) {
      /* ignore corrupt storage */
    }
  }

  function showScreen(el) {
    [authScreen, dashboardScreen, stageScreen, summaryScreen].forEach((s) =>
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
      if (!session.problemStates) session.problemStates = {};
      assignContest();
      persist();
      enterDashboard();
    } catch (err) {
      authError.textContent = err.message || "Something went wrong.";
      authError.classList.remove("hidden");
    } finally {
      authSubmitBtn.disabled = false;
      authSubmitBtn.textContent = "Start solving →";
    }
  });

  function assignContest() {
    if (session.assignedContest) return;
    const hashmaps = PROBLEMS.filter(
      (p) =>
        p.problem.tags &&
        (p.problem.tags.includes("hash-map") ||
          p.problem.tags.includes("hash-table") ||
          p.problem.slug === "two-sum" ||
          p.problem.slug === "group-anagrams"),
    );
    const twopointers = PROBLEMS.filter(
      (p) =>
        p.problem.tags &&
        (p.problem.tags.includes("two-pointers") ||
          p.problem.slug === "valid-palindrome" ||
          p.problem.slug === "merge-sorted-array" ||
          p.problem.slug === "reverse-string" ||
          p.problem.slug === "trapping-rain-water"),
    );

    const hm =
      hashmaps.length > 0
        ? hashmaps[Math.floor(Math.random() * hashmaps.length)]
        : PROBLEMS[0];
    const tp =
      twopointers.length > 0
        ? twopointers[Math.floor(Math.random() * twopointers.length)]
        : PROBLEMS[1 % PROBLEMS.length];

    session.assignedContest = {
      problem: { title: "25-ai/ml Contest", slug: "25-ai-ml-contest" },
      stages: [
        { ...hm.stages[0], title: "Q1 - " + hm.stages[0].title },
        { ...tp.stages[0], title: "Q2 - " + tp.stages[0].title },
      ],
    };
  }

  // ---- Dashboard Screen ----
  function enterDashboard() {
    try {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => {});
      }
    } catch (e) {}

    showScreen(dashboardScreen);
    problemList.innerHTML = "";

    const p = session.assignedContest;
    if (!p) return;

    const slug = p.problem.slug;
    const state = session.problemStates[slug] || {
      current: 0,
      submissions: {},
    };
    const submittedCount = Object.keys(state.submissions).length;
    const isComplete = submittedCount === p.stages.length;

    const card = document.createElement("div");
    card.className =
      "problem-card" +
      (isComplete ? " completed" : submittedCount > 0 ? " in-progress" : "");
    card.style.cursor = "pointer";

    let badgeText = isComplete
      ? "Completed ✓"
      : submittedCount + " / " + p.stages.length + " completed";

    card.innerHTML = `
      <h3>
        <span>${p.problem.title}</span>
        <span class="status-badge">${badgeText}</span>
      </h3>
      <p>Contains 1 Hashmap question and 1 Two Pointers question. Only one submission is allowed per question.</p>
    `;

    card.addEventListener("click", () => {
      selectProblem(slug);
    });

    problemList.appendChild(card);
  }

  function selectProblem(slug) {
    currentProblemSlug = slug;
    const p = session.assignedContest;
    PROBLEM = p.problem;
    STAGES = p.stages;

    if (!session.problemStates[slug]) {
      session.problemStates[slug] = { current: 0, submissions: {}, drafts: {} };
      persist();
    }

    enterStages();
  }

  async function enterStages() {
    topBarTitle.innerHTML = `${PROBLEM.title} <span class="accent">— Code War</span>`;
    candidateBadge.textContent = session.student
      ? `${session.student.name} · ${session.student.collegeId || session.student.email}`
      : "";
    buildProgressDots();

    // Pull back any submissions already stored server-side
    try {
      const remote = await apiFetch(
        `/api/submissions?studentId=${encodeURIComponent(session.student.id)}&problemSlug=${encodeURIComponent(PROBLEM.slug)}`,
      );
      const state = session.problemStates[currentProblemSlug];
      remote.forEach((r) => {
        state.submissions[r.stage - 1] = {
          language: r.language,
          code: r.code,
          submittedAt: r.submittedAt,
          synced: true,
        };
      });
    } catch (e) {
      /* offline or server unreachable */
    }

    persist();
    const state = session.problemStates[currentProblemSlug];
    if (Object.keys(state.submissions).length === STAGES.length) {
      goToSummary();
    } else {
      state.current = Math.min(
        Object.keys(state.submissions).length,
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
    const state = session.problemStates[currentProblemSlug];
    if (state.submissions[i]) return "dot done";
    if (i === state.current) return "dot active";
    return "dot";
  }

  function updateProgressDots() {
    [...progressEl.children].forEach((dot, i) => {
      dot.className = dotClass(i);
    });
  }

  function currentCode(index) {
    const state = session.problemStates[currentProblemSlug];
    if (state.drafts[index] !== undefined) return state.drafts[index];
    if (state.submissions[index]) return state.submissions[index].code;
    return BOILERPLATE[session.language] || "";
  }

  function renderStage() {
    const state = session.problemStates[currentProblemSlug];
    const idx = state.current;
    const s = STAGES[idx];

    stageNum.textContent = idx + 1;
    stageTitle.textContent = s.title;
    stageComplexity.textContent = `Target: ${s.complexity}`;
    stageStatement.innerHTML = s.statement;

    samplesContainer.innerHTML = "";
    if (s.samples && s.samples.length > 0) {
      s.samples.forEach((sample, i) => {
        const pair = document.createElement("div");
        pair.className = "samples";
        pair.style.marginBottom = "1rem";
        pair.innerHTML = `
          <div class="sample">
            <div class="sample-label">INPUT ${s.samples.length > 1 ? i + 1 : ""}</div>
            <pre>${sample.input}</pre>
          </div>
          <div class="sample">
            <div class="sample-label">EXPECTED OUTPUT ${s.samples.length > 1 ? i + 1 : ""}</div>
            <pre>${sample.output}</pre>
          </div>
        `;
        samplesContainer.appendChild(pair);
      });
    }

    editorLanguage.value = session.language;
    codeEditor.value = currentCode(idx);

    updateProgressDots();
    stageIndicator.textContent = `Stage ${idx + 1} of ${STAGES.length}`;
    prevBtn.disabled = idx === 0;
    nextBtn.textContent =
      idx === STAGES.length - 1 ? "Submit & Finish 🏆" : "Submit & Continue →";

    const sub = state.submissions[idx];
    saveIndicator.textContent = sub
      ? saveIndicatorText(sub)
      : "Not submitted yet";

    if (sub) {
      codeEditor.disabled = true;
      codeEditor.style.opacity = "0.7";
      nextBtn.textContent =
        idx === STAGES.length - 1 ? "End Contest 🏆" : "Already Submitted →";
      resetBtn.disabled = true;
    } else {
      codeEditor.disabled = false;
      codeEditor.style.opacity = "1";
      resetBtn.disabled = false;
    }
  }

  function saveIndicatorText(sub) {
    const status = sub.synced
      ? "Saved to server"
      : "Saved locally (retry pending)";
    return `${status} · ${new Date(sub.submittedAt).toLocaleTimeString()}`;
  }

  async function submitCurrentStage() {
    const state = session.problemStates[currentProblemSlug];
    const idx = state.current;
    const record = {
      language: editorLanguage.value,
      code: codeEditor.value,
      submittedAt: new Date().toISOString(),
      synced: false,
    };
    state.submissions[idx] = record;
    delete state.drafts[idx];
    persist();

    saveIndicator.textContent = "Saved locally";
  }

  function summaryStatusText(sub) {
    if (!sub) return "Not submitted";
    return sub.synced
      ? `✓ synced · ${sub.language}`
      : `⚠ local only · ${sub.language}`;
  }

  function summaryStatusClass(sub) {
    if (!sub) return "missing";
    return sub.synced ? "ok" : "pending";
  }

  function goToSummary() {
    showScreen(summaryScreen);
    const state = session.problemStates[currentProblemSlug];
    const submittedCount = Object.keys(state.submissions).length;
    const syncedCount = Object.values(state.submissions).filter(
      (s) => s.synced,
    ).length;
    summaryLine.textContent = `${session.student.name} submitted ${submittedCount}/${STAGES.length} stages (${syncedCount} synced to server) for ${PROBLEM.title}.`;
    summaryList.innerHTML = "";
    STAGES.forEach((s, i) => {
      const sub = state.submissions[i];
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
    const state = session.problemStates[currentProblemSlug];
    const idx = state.current;
    if (!state.submissions[idx] && !state.drafts[idx]) {
      codeEditor.value = BOILERPLATE[session.language] || "";
    }
    persist();
  });

  codeEditor.addEventListener("input", () => {
    const state = session.problemStates[currentProblemSlug];
    state.drafts[state.current] = codeEditor.value;
    saveIndicator.textContent = "Draft saved locally";
    persist();
  });

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
    if (!confirm("Reset this stage's editor to the starter boilerplate?"))
      return;
    codeEditor.value = BOILERPLATE[session.language] || "";
    codeEditor.dispatchEvent(new Event("input"));
  });

  prevBtn.addEventListener("click", () => {
    const state = session.problemStates[currentProblemSlug];
    if (state.current > 0) {
      state.current--;
      persist();
      renderStage();
    }
  });

  nextBtn.addEventListener("click", async () => {
    nextBtn.disabled = true;
    const state = session.problemStates[currentProblemSlug];
    if (!state.submissions[state.current]) {
      await submitCurrentStage();
    }
    nextBtn.disabled = false;

    if (state.current < STAGES.length - 1) {
      state.current++;
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
      problemStates: {},
    };
    authNameInput.value = "";
    authEmailInput.value = "";
    authCollegeIdInput.value = "";
    showScreen(authScreen);
  }

  signOutBtn.addEventListener("click", signOut);
  dashboardSignOutBtn.addEventListener("click", signOut);

  // ---- Summary screen ----
  downloadBtn.addEventListener("click", async () => {
    const state = session.problemStates[currentProblemSlug];
    const payload = {
      student: session.student,
      problem: PROBLEM,
      exportedAt: new Date().toISOString(),
      stages: STAGES.map((s, i) => ({
        stage: i + 1,
        title: s.title,
        submission: state.submissions[i] || null,
      })),
    };

    const originalText = downloadBtn.textContent;
    downloadBtn.textContent = "Saving to Server & Downloading...";
    downloadBtn.disabled = true;

    try {
      await apiFetch("/api/submit-bulk", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      // Mark all as synced visually if it succeeds
      for (const idx in state.submissions) {
        state.submissions[idx].synced = true;
      }
      persist();
      goToSummary();
    } catch (err) {
      console.warn("Bulk submit failed:", err.message);
      alert(
        "Could not reach the server to save your progress, but your JSON backup will download now.",
      );
    }

    downloadBtn.textContent = originalText;
    downloadBtn.disabled = false;

    const blob = new Blob([JSON.stringify(payload, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    const safeName = (session.student?.name || "candidate").replace(
      /\\s+/g,
      "_",
    );
    a.href = url;
    a.download = `${safeName}_${PROBLEM.slug}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  });

  backToDashboardBtn.addEventListener("click", () => {
    enterDashboard();
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
      assignContest();
      persist();
      enterDashboard();
    } else {
      showScreen(authScreen);
    }
  }

  // --- Anti-Cheat Tab Switching Logic ---
  const lockScreen = document.getElementById("lock-screen");
  const unlockBtn = document.getElementById("unlock-btn");
  const unlockPassword = document.getElementById("unlock-password");
  const lockError = document.getElementById("lock-error");
  const PROCTOR_PASSWORD = "zapadmin"; // Hardcoded password

  function checkLockState() {
    if (localStorage.getItem("tab_locked") === "true") {
      lockScreen.classList.remove("hidden");
    }
  }

  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden") {
      localStorage.setItem("tab_locked", "true");
      lockScreen.classList.remove("hidden");
    }
  });

  unlockBtn.addEventListener("click", () => {
    if (unlockPassword.value === PROCTOR_PASSWORD) {
      localStorage.removeItem("tab_locked");
      lockScreen.classList.add("hidden");
      unlockPassword.value = "";
      lockError.classList.add("hidden");
    } else {
      lockError.classList.remove("hidden");
    }
  });

  // --- Strict Proctoring Controls ---

  // 1. Block Context Menu (Right Click / Inspect)
  document.addEventListener("contextmenu", (e) => {
    e.preventDefault();
  });

  // 2. Block Copy, Cut, Paste globally
  document.addEventListener("copy", (e) => {
    e.preventDefault();
  });
  document.addEventListener("cut", (e) => {
    e.preventDefault();
  });
  document.addEventListener("paste", (e) => {
    e.preventDefault();
  });

  // 3. Block Keyboard Shortcuts (F12, Ctrl+Shift+I/J/C)
  document.addEventListener("keydown", (e) => {
    // F12
    if (e.key === "F12") {
      e.preventDefault();
    }
    // Ctrl+Shift+I, J, C or Cmd+Option+I, J, C
    if ((e.ctrlKey || e.metaKey) && (e.shiftKey || e.altKey)) {
      if (
        e.key === "I" ||
        e.key === "i" ||
        e.key === "J" ||
        e.key === "j" ||
        e.key === "C" ||
        e.key === "c"
      ) {
        e.preventDefault();
      }
    }
  });

  // 4. Force Fullscreen enforcement (if they exit fullscreen, trigger lock)
  document.addEventListener("fullscreenchange", () => {
    if (!document.fullscreenElement && session.student) {
      // They exited full screen
      localStorage.setItem("tab_locked", "true");
      lockScreen.classList.remove("hidden");
    }
  });

  init();
  checkLockState();
})();
