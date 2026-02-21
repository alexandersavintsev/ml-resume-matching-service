function getCookie(name) {
  const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
  return match ? decodeURIComponent(match[2]) : null;
}

function setCookie(name, value) {
  document.cookie = `${name}=${encodeURIComponent(value)}; Path=/; SameSite=Lax`;
}

function clearCookie(name) {
  document.cookie = `${name}=; Path=/; Max-Age=0; SameSite=Lax`;
}

function token() {
  return getCookie("access_token");
}

function requireAuth() {
  if (!token()) {
    window.location.href = "/login";
    return false;
  }
  return true;
}

function showGlobalAlert(kind, title, message, details) {
  const root = document.getElementById("globalAlert");
  if (!root) return;

  const det = details ? `<pre class="mt-2 mb-0 small bg-light p-2 rounded">${escapeHtml(JSON.stringify(details, null, 2))}</pre>` : "";
  root.innerHTML = `
    <div class="alert alert-${kind} alert-dismissible fade show" role="alert">
      <div class="fw-semibold">${escapeHtml(title)}</div>
      <div>${escapeHtml(message || "")}</div>
      ${det}
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
  `;
}

function escapeHtml(s) {
  return String(s).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
}

async function apiFetch(path, options = {}) {
  const headers = Object.assign(
    { "Content-Type": "application/json" },
    options.headers || {}
  );

  const t = token();
  if (t) headers["Authorization"] = `Bearer ${t}`;

  const res = await fetch(path, Object.assign({}, options, { headers }));

  if (res.ok) {
    const ct = res.headers.get("content-type") || "";
    if (ct.includes("application/json")) return await res.json();
    return await res.text();
  }

  // parse backend error format: {detail: {error: {code,message,details}}}
  let payload = null;
  try {
    payload = await res.json();
  } catch (_) {}

  const err = payload?.detail?.error;
  const code = err?.code || "HTTP_ERROR";
  const message = err?.message || `Request failed with status ${res.status}`;
  const details = err?.details || null;

  const e = new Error(message);
  e.status = res.status;
  e.code = code;
  e.details = details;
  throw e;
}

// ---------- Pages ----------

async function initLogin() {
  const form = document.getElementById("loginForm");
  const btn = document.getElementById("loginBtn");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    btn.disabled = true;

    try {
      const fd = new FormData(form);
      const email = fd.get("email");

      const data = await apiFetch("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email })
      });

      setCookie("access_token", data.token);
      showGlobalAlert("success", "Успешный вход", "Токен сохранён, переходим в кабинет.");
      setTimeout(() => (window.location.href = "/cabinet"), 400);
    } catch (err) {
      showGlobalAlert("danger", err.code || "ERROR", err.message, err.details);
    } finally {
      btn.disabled = false;
    }
  });
}

async function initRegister() {
  const form = document.getElementById("registerForm");
  const btn = document.getElementById("registerBtn");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    btn.disabled = true;

    try {
      const fd = new FormData(form);
      const email = fd.get("email");
      const role = fd.get("role");
      const initial_credits = Number(fd.get("initial_credits") || 0);

      const data = await apiFetch("/auth/register", {
        method: "POST",
        body: JSON.stringify({ email, role, initial_credits })
      });

      showGlobalAlert("success", "Аккаунт создан", `user_id=${data.user_id}. Теперь выполните вход.`);
      setTimeout(() => (window.location.href = "/login"), 600);
    } catch (err) {
      showGlobalAlert("danger", err.code || "ERROR", err.message, err.details);
    } finally {
      btn.disabled = false;
    }
  });
}

async function loadBalanceInto(elId) {
  const el = document.getElementById(elId);
  if (!el) return;

  const data = await apiFetch("/balance", { method: "GET" });
  el.textContent = String(data.credits);
}

async function initCabinet() {
  if (!requireAuth()) return;

  const refreshBtn = document.getElementById("refreshBalanceBtn");
  const form = document.getElementById("topUpForm");
  const btn = document.getElementById("topUpBtn");

  async function refresh() {
    try {
      await loadBalanceInto("balanceValue");
    } catch (err) {
      showGlobalAlert("danger", err.code || "ERROR", err.message, err.details);
    }
  }

  refreshBtn?.addEventListener("click", refresh);
  await refresh();

  form?.addEventListener("submit", async (e) => {
    e.preventDefault();
    btn.disabled = true;

    try {
      const fd = new FormData(form);
      const amount = Number(fd.get("amount"));
      const data = await apiFetch("/balance/top-up", {
        method: "POST",
        body: JSON.stringify({ amount })
      });
      showGlobalAlert("success", "Баланс пополнен", `Новый баланс: ${data.new_balance}`);
      await refresh();
    } catch (err) {
      showGlobalAlert("danger", err.code || "ERROR", err.message, err.details);
    } finally {
      btn.disabled = false;
    }
  });
}

function parseKeywords(s) {
  return String(s)
    .split(",")
    .map(x => x.trim())
    .filter(Boolean);
}

function parseResumes(text) {
  // one resume per line
  return String(text)
    .split("\n")
    .map(x => x.trim())
    // keep even empty lines? backend will mark invalid; we can keep empties to demonstrate validation
    // but to show partially_valid better, keep them as-is:
    .map(x => x); 
}

function renderPredictResult(data) {
  const meta = document.getElementById("predictMeta");
  const invalidBlock = document.getElementById("invalidBlock");
  const invalidList = document.getElementById("invalidList");
  const tbody = document.getElementById("predictTableBody");

  if (meta) {
    meta.textContent = `task_id=${data.task_id} | status=${data.status} | charged_credits=${data.charged_credits}`;
  }

  const invalid = data.invalid_items || [];
  if (invalid.length > 0) {
    invalidBlock.style.display = "";
    invalidList.innerHTML = invalid.map(x => `<li><code>${escapeHtml(x)}</code></li>`).join("");
  } else {
    invalidBlock.style.display = "none";
    invalidList.innerHTML = "";
  }

  const top = data.top || [];
  if (top.length === 0) {
    tbody.innerHTML = `<tr><td colspan="3" class="text-muted">Пусто</td></tr>`;
    return;
  }

  tbody.innerHTML = top.map((item, idx) => `
    <tr>
      <td>${idx + 1}</td>
      <td><span class="badge text-bg-secondary">${Number(item.score).toFixed(3)}</span></td>
      <td class="small">${escapeHtml(item.resume_text)}</td>
    </tr>
  `).join("");
}

async function initPredict() {
  if (!requireAuth()) return;

  const refreshBtn = document.getElementById("predictRefreshBalanceBtn");
  const form = document.getElementById("predictForm");
  const btn = document.getElementById("predictBtn");

  async function refreshBalance() {
    try {
      await loadBalanceInto("predictBalance");
    } catch (err) {
      showGlobalAlert("danger", err.code || "ERROR", err.message, err.details);
    }
  }

  refreshBtn?.addEventListener("click", refreshBalance);
  await refreshBalance();

  form?.addEventListener("submit", async (e) => {
    e.preventDefault();
    btn.disabled = true;

    try {
      const fd = new FormData(form);
      const keywords = parseKeywords(fd.get("keywords"));
      const resumes = parseResumes(fd.get("resumes"));
      const top_k = Number(fd.get("top_k") || 5);
      const cost_credits = Number(fd.get("cost_credits") || 10);

      const data = await apiFetch("/predict", {
        method: "POST",
        body: JSON.stringify({ keywords, resumes, top_k, cost_credits })
      });

      showGlobalAlert("success", "Успешно", `Статус: ${data.status}`);
      renderPredictResult(data);
      await refreshBalance();
    } catch (err) {
      // special message for insufficient balance
      if (err.code === "INSUFFICIENT_BALANCE") {
        showGlobalAlert("warning", err.code, "Недостаточно средств на балансе.", err.details);
      } else {
        showGlobalAlert("danger", err.code || "ERROR", err.message, err.details);
      }
    } finally {
      btn.disabled = false;
    }
  });
}

function fmtDate(s) {
  // ISO -> readable
  const d = new Date(s);
  if (isNaN(d.getTime())) return String(s);
  return d.toLocaleString();
}

async function initHistory() {
  if (!requireAuth()) return;

  const txBody = document.getElementById("txBody");
  const predBody = document.getElementById("predBody");

  try {
    const txs = await apiFetch("/history/transactions", { method: "GET" });
    if (!txs.length) {
      txBody.innerHTML = `<tr><td colspan="4" class="text-muted">Нет транзакций</td></tr>`;
    } else {
      txBody.innerHTML = txs.map(tx => `
        <tr>
          <td class="small">${escapeHtml(fmtDate(tx.created_at))}</td>
          <td><span class="badge text-bg-dark">${escapeHtml(tx.tx_type)}</span></td>
          <td>${tx.amount_credits}</td>
          <td class="small"><code>${tx.task_id || ""}</code></td>
        </tr>
      `).join("");
    }

    const preds = await apiFetch("/history/predictions", { method: "GET" });
    if (!preds.length) {
      predBody.innerHTML = `<tr><td colspan="4" class="text-muted">Нет записей</td></tr>`;
    } else {
      predBody.innerHTML = preds.map(p => `
        <tr>
          <td class="small">${escapeHtml(fmtDate(p.created_at))}</td>
          <td><span class="badge text-bg-secondary">${escapeHtml(p.status)}</span></td>
          <td>${p.charged_credits}</td>
          <td class="small"><code>${p.task_id}</code></td>
        </tr>
      `).join("");
    }
  } catch (err) {
    showGlobalAlert("danger", err.code || "ERROR", err.message, err.details);
  }
}

// ---------- Boot ----------
document.addEventListener("DOMContentLoaded", async () => {
  const page = document.body?.dataset?.page;

  if (page === "login") await initLogin();
  if (page === "register") await initRegister();
  if (page === "cabinet") await initCabinet();
  if (page === "predict") await initPredict();
  if (page === "history") await initHistory();
});
