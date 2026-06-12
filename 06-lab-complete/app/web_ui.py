"""HTML UI for the deployed shopping assistant."""


def render_homepage() -> str:
    return """<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Day09 Shopping Agent</title>
  <style>
    :root {
      color-scheme: light;
      --ink: #17212b;
      --muted: #657180;
      --line: #d9e2ec;
      --panel: #ffffff;
      --soft: #f5f8fb;
      --accent: #0f766e;
      --accent-2: #2563eb;
      --warn: #b45309;
      --ok: #15803d;
      --shadow: 0 18px 45px rgba(27, 39, 51, 0.12);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background:
        linear-gradient(180deg, rgba(245, 248, 251, 0.92), rgba(233, 239, 245, 0.92)),
        repeating-linear-gradient(90deg, rgba(23, 33, 43, 0.05) 0 1px, transparent 1px 72px),
        repeating-linear-gradient(0deg, rgba(23, 33, 43, 0.04) 0 1px, transparent 1px 72px);
    }

    button, input, textarea { font: inherit; }

    .app {
      width: min(1380px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 24px 0;
    }

    .topbar {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 16px;
      align-items: center;
      margin-bottom: 18px;
    }

    .brand {
      display: flex;
      gap: 14px;
      align-items: center;
      min-width: 0;
    }

    .mark {
      width: 48px;
      height: 48px;
      border-radius: 8px;
      background: #102033;
      color: #ffffff;
      display: grid;
      place-items: center;
      box-shadow: var(--shadow);
      flex: 0 0 auto;
    }

    .mark svg { width: 30px; height: 30px; }

    h1 {
      margin: 0;
      font-size: 22px;
      line-height: 1.2;
      letter-spacing: 0;
    }

    .subtitle {
      margin-top: 4px;
      color: var(--muted);
      font-size: 14px;
    }

    .statusbar {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      justify-content: flex-end;
    }

    .pill {
      border: 1px solid var(--line);
      background: rgba(255, 255, 255, 0.72);
      border-radius: 999px;
      padding: 7px 10px;
      font-size: 13px;
      color: var(--muted);
      white-space: nowrap;
    }

    .pill strong { color: var(--ink); font-weight: 700; }

    .layout {
      display: grid;
      grid-template-columns: minmax(0, 1.15fr) minmax(340px, 0.85fr);
      gap: 18px;
      align-items: stretch;
    }

    .workspace,
    .inspector {
      background: rgba(255, 255, 255, 0.82);
      border: 1px solid rgba(217, 226, 236, 0.9);
      border-radius: 8px;
      box-shadow: var(--shadow);
      overflow: hidden;
    }

    .workspace {
      min-height: calc(100vh - 138px);
      display: grid;
      grid-template-rows: auto 1fr auto;
    }

    .toolbar {
      display: grid;
      grid-template-columns: minmax(180px, 1fr) minmax(160px, 0.55fr);
      gap: 12px;
      padding: 14px;
      border-bottom: 1px solid var(--line);
      background: rgba(245, 248, 251, 0.9);
    }

    .field label {
      display: block;
      margin-bottom: 6px;
      font-size: 12px;
      font-weight: 700;
      color: #405064;
      text-transform: uppercase;
    }

    .field input,
    .composer textarea {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #ffffff;
      color: var(--ink);
      outline: none;
      transition: border-color 120ms ease, box-shadow 120ms ease;
    }

    .field input {
      min-height: 42px;
      padding: 0 12px;
    }

    .field input:focus,
    .composer textarea:focus {
      border-color: rgba(37, 99, 235, 0.55);
      box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.14);
    }

    .messages {
      padding: 18px;
      overflow: auto;
      min-height: 360px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }

    .message {
      max-width: min(820px, 100%);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      background: #fff;
      line-height: 1.55;
      white-space: pre-wrap;
    }

    .message.user {
      align-self: flex-end;
      background: #eaf4ff;
      border-color: #b9d8ff;
    }

    .message.agent {
      align-self: flex-start;
    }

    .meta {
      display: flex;
      gap: 8px;
      align-items: center;
      margin-bottom: 8px;
      font-size: 12px;
      color: var(--muted);
      text-transform: uppercase;
      font-weight: 800;
    }

    .dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--accent);
    }

    .composer {
      border-top: 1px solid var(--line);
      padding: 14px;
      background: rgba(245, 248, 251, 0.9);
    }

    .suggestions {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 12px;
    }

    .chip,
    .icon-button,
    .send {
      border: 1px solid var(--line);
      background: #ffffff;
      color: var(--ink);
      border-radius: 8px;
      cursor: pointer;
      transition: transform 120ms ease, border-color 120ms ease, background 120ms ease;
    }

    .chip {
      padding: 8px 10px;
      font-size: 13px;
    }

    .chip:hover,
    .icon-button:hover,
    .send:hover {
      transform: translateY(-1px);
      border-color: #9fb3c8;
    }

    .composer-row {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 10px;
      align-items: end;
    }

    .composer textarea {
      min-height: 74px;
      max-height: 180px;
      resize: vertical;
      padding: 12px;
      line-height: 1.45;
    }

    .send {
      width: 52px;
      height: 52px;
      display: grid;
      place-items: center;
      background: var(--accent);
      border-color: var(--accent);
      color: #ffffff;
    }

    .send:disabled {
      opacity: 0.55;
      cursor: wait;
      transform: none;
    }

    .send svg { width: 23px; height: 23px; }

    .inspector {
      min-height: calc(100vh - 138px);
      display: grid;
      grid-template-rows: auto auto 1fr;
    }

    .panel-head {
      padding: 16px;
      border-bottom: 1px solid var(--line);
      background: #102033;
      color: #ffffff;
    }

    .panel-head h2 {
      margin: 0;
      font-size: 17px;
      letter-spacing: 0;
    }

    .panel-head p {
      margin: 6px 0 0;
      color: rgba(255, 255, 255, 0.76);
      font-size: 13px;
    }

    .metrics {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      border-bottom: 1px solid var(--line);
    }

    .metric {
      padding: 14px;
      border-right: 1px solid var(--line);
      background: #ffffff;
      min-width: 0;
    }

    .metric:last-child { border-right: 0; }

    .metric span {
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 5px;
    }

    .metric strong {
      display: block;
      font-size: 18px;
      overflow-wrap: anywhere;
    }

    .details {
      padding: 16px;
      overflow: auto;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }

    .section {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #ffffff;
      overflow: hidden;
    }

    .section h3 {
      margin: 0;
      padding: 11px 12px;
      font-size: 13px;
      text-transform: uppercase;
      color: #405064;
      background: var(--soft);
      border-bottom: 1px solid var(--line);
      letter-spacing: 0;
    }

    .section pre {
      margin: 0;
      padding: 12px;
      max-height: 260px;
      overflow: auto;
      white-space: pre-wrap;
      word-break: break-word;
      color: #1f2937;
      font-size: 12px;
      line-height: 1.45;
    }

    .empty {
      color: var(--muted);
      padding: 12px;
      font-size: 13px;
      line-height: 1.5;
    }

    .toast {
      position: fixed;
      right: 18px;
      bottom: 18px;
      max-width: min(420px, calc(100vw - 36px));
      background: #fff7ed;
      color: #7c2d12;
      border: 1px solid #fed7aa;
      border-radius: 8px;
      padding: 12px 14px;
      box-shadow: var(--shadow);
      display: none;
      z-index: 10;
    }

    .toast.show { display: block; }

    @media (max-width: 960px) {
      .topbar,
      .layout,
      .toolbar {
        grid-template-columns: 1fr;
      }

      .statusbar { justify-content: flex-start; }
      .workspace,
      .inspector { min-height: auto; }
      .metrics { grid-template-columns: 1fr; }
      .metric { border-right: 0; border-bottom: 1px solid var(--line); }
      .metric:last-child { border-bottom: 0; }
    }

    @media (max-width: 560px) {
      .app { width: min(100vw - 20px, 1380px); padding: 12px 0; }
      .brand { align-items: flex-start; }
      .mark { width: 42px; height: 42px; }
      h1 { font-size: 19px; }
      .composer-row { grid-template-columns: 1fr; }
      .send { width: 100%; }
    }
  </style>
</head>
<body>
  <main class="app">
    <header class="topbar">
      <div class="brand">
        <div class="mark" aria-hidden="true">
          <svg viewBox="0 0 48 48" fill="none">
            <path d="M12 14h24v20H12z" stroke="currentColor" stroke-width="3" />
            <path d="M18 21h12M18 27h8M24 7v7M24 34v7M7 24h5M36 24h5" stroke="currentColor" stroke-width="3" stroke-linecap="round" />
          </svg>
        </div>
        <div>
          <h1>Day09 Shopping Agent</h1>
          <div class="subtitle">Cloud dashboard for orders, vouchers, return policy, and deployment evidence.</div>
        </div>
      </div>
      <div class="statusbar">
        <div class="pill">API <strong id="apiState">waiting</strong></div>
        <div class="pill">Health <strong id="healthState">checking</strong></div>
        <div class="pill">Mode <strong>Day09</strong></div>
      </div>
    </header>

    <section class="layout">
      <div class="workspace">
        <div class="toolbar">
          <div class="field">
            <label for="apiKey">App API key</label>
            <input id="apiKey" type="password" autocomplete="off" placeholder="AGENT_API_KEY / X-API-Key" value="dev-key-change-me" />
          </div>
          <div class="field">
            <label for="userId">User</label>
            <input id="userId" type="text" autocomplete="off" value="web-demo" />
          </div>
        </div>

        <div class="messages" id="messages" aria-live="polite">
          <article class="message agent">
            <div class="meta"><span class="dot"></span>Agent</div>
            Chào mừng bạn đến với Day09 Shopping Agent. Hãy hỏi về đơn hàng 1971, voucher của C001, chính sách hoàn trả, hoặc các tình huống cần làm rõ.
          </article>
        </div>

        <form class="composer" id="askForm">
          <div class="suggestions">
            <button class="chip" type="button" data-question="Đơn hàng 1971 có được hoàn trả không?">Đơn 1971 hoàn trả</button>
            <button class="chip" type="button" data-question="Voucher của khách hàng C001 còn những mã nào dùng được?">Voucher C001</button>
            <button class="chip" type="button" data-question="Chính sách hoàn trả hàng ra sao?">Chính sách hoàn trả</button>
            <button class="chip" type="button" data-question="Kiểm tra đơn hàng 9999 giúp tôi">Đơn 9999</button>
          </div>
          <div class="composer-row">
            <textarea id="question" required maxlength="2000" placeholder="Nhập câu hỏi về đơn hàng, voucher hoặc chính sách..."></textarea>
            <button class="send" id="sendButton" type="submit" aria-label="Gửi">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M4 12L20 4L16 20L12 13L4 12Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round" />
              </svg>
            </button>
          </div>
        </form>
      </div>

      <aside class="inspector">
        <div class="panel-head">
          <h2>Runtime Inspector</h2>
          <p>Route, evidence, budget, and storage signals from the latest response.</p>
        </div>
        <div class="metrics">
          <div class="metric"><span>Route</span><strong id="routeMetric">-</strong></div>
          <div class="metric"><span>Cost</span><strong id="costMetric">-</strong></div>
          <div class="metric"><span>Store</span><strong id="storeMetric">-</strong></div>
        </div>
        <div class="details">
          <div class="section">
            <h3>Route</h3>
            <pre id="routeBox">{}</pre>
          </div>
          <div class="section">
            <h3>Evidence</h3>
            <pre id="evidenceBox">{}</pre>
          </div>
          <div class="section">
            <h3>Usage</h3>
            <pre id="usageBox">{}</pre>
          </div>
        </div>
      </aside>
    </section>
  </main>
  <div class="toast" id="toast"></div>

  <script>
    const messages = document.getElementById("messages");
    const form = document.getElementById("askForm");
    const questionInput = document.getElementById("question");
    const apiKeyInput = document.getElementById("apiKey");
    const userIdInput = document.getElementById("userId");
    const sendButton = document.getElementById("sendButton");
    const toast = document.getElementById("toast");

    const apiState = document.getElementById("apiState");
    const healthState = document.getElementById("healthState");
    const routeMetric = document.getElementById("routeMetric");
    const costMetric = document.getElementById("costMetric");
    const storeMetric = document.getElementById("storeMetric");
    const routeBox = document.getElementById("routeBox");
    const evidenceBox = document.getElementById("evidenceBox");
    const usageBox = document.getElementById("usageBox");

    let sessionId = null;

    function showToast(message) {
      toast.textContent = message;
      toast.classList.add("show");
      window.setTimeout(() => toast.classList.remove("show"), 4200);
    }

    function addMessage(role, text) {
      const article = document.createElement("article");
      article.className = `message ${role}`;
      const meta = document.createElement("div");
      meta.className = "meta";
      const dot = document.createElement("span");
      dot.className = "dot";
      meta.append(dot, document.createTextNode(role === "user" ? "Bạn" : "Agent"));
      const body = document.createElement("div");
      body.textContent = text;
      article.append(meta, body);
      messages.appendChild(article);
      messages.scrollTop = messages.scrollHeight;
    }

    function pretty(value) {
      return JSON.stringify(value ?? {}, null, 2);
    }

    function updateInspector(payload) {
      const route = payload.route || {};
      const usage = payload.usage || {};
      const evidence = payload.evidence || {};
      const routeName = route.status === "clarification_needed"
        ? "clarify"
        : [route.needs_policy ? "policy" : null, route.needs_data ? "data" : null].filter(Boolean).join("+") || "direct";

      routeMetric.textContent = routeName;
      costMetric.textContent = usage.cost_usd !== undefined ? `$${usage.cost_usd}` : "-";
      storeMetric.textContent = payload.storage || "-";
      routeBox.textContent = pretty(route);
      evidenceBox.textContent = pretty(evidence);
      usageBox.textContent = pretty(usage);
    }

    async function checkHealth() {
      try {
        const response = await fetch("/health");
        const payload = await response.json();
        healthState.textContent = payload.status || "ok";
      } catch (error) {
        healthState.textContent = "offline";
      }
    }

    async function ask(question) {
      const apiKey = apiKeyInput.value.trim();
      const userId = userIdInput.value.trim() || "web-demo";
      if (!apiKey) {
        showToast("Thiếu API key.");
        apiState.textContent = "missing";
        return;
      }

      addMessage("user", question);
      questionInput.value = "";
      sendButton.disabled = true;
      apiState.textContent = "sending";

      try {
        const response = await fetch("/ask", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-API-Key": apiKey
          },
          body: JSON.stringify({
            user_id: userId,
            session_id: sessionId,
            question
          })
        });

        const payload = await response.json();
        if (!response.ok) {
          const detail = typeof payload.detail === "string" ? payload.detail : JSON.stringify(payload.detail || payload);
          throw new Error(`${response.status}: ${detail}`);
        }

        sessionId = payload.session_id;
        addMessage("agent", payload.answer || "(empty)");
        updateInspector(payload);
        apiState.textContent = "ready";
      } catch (error) {
        apiState.textContent = "error";
        const message = error.message || "Request failed";
        showToast(message);
        if (message.startsWith("401") || message.startsWith("403")) {
          addMessage("agent", "App API key không đúng. Ô này dùng AGENT_API_KEY của app, không phải Gemini API key. Gemini API key cần set trong Railway Variables.");
        } else {
          addMessage("agent", "Không gọi được API. Kiểm tra Railway Variables hoặc log deploy.");
        }
      } finally {
        sendButton.disabled = false;
        questionInput.focus();
      }
    }

    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const question = questionInput.value.trim();
      if (question) ask(question);
    });

    document.querySelectorAll("[data-question]").forEach((button) => {
      button.addEventListener("click", () => {
        questionInput.value = button.dataset.question;
        questionInput.focus();
      });
    });

    checkHealth();
  </script>
</body>
</html>"""
