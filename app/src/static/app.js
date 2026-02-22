// ====== Token storage ======
const TOKEN_KEY = "ml_token";

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}
function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}
function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

// ====== UI helpers ======
function $(sel) { return document.querySelector(sel); }
function $all(sel) { return Array.from(document.querySelectorAll(sel)); }

function applyAuthVisibility() {
  const has = !!getToken();
  $all(".nav-auth-only").forEach(el => el.classList.toggle("d-none", !has));
  $all(".nav-guest-only").forEach(el => el.classList.toggle("d-none", has));
}

function toast(title, body, meta="") {
  const t = $("#appToast");
  if (!t) return alert(body);
  $("#toastTitle").textContent = title;
  $("#toastBody").textContent = body;
  $("#toastMeta").textContent = meta;
  const instance = bootstrap.Toast.getOrCreateInstance(t, { delay: 4500 });
  instance.show();
}

function formatError(e) {
  // FastAPI errors are like: { detail: { error: { code, message, details } } }
  if (!e) return "Unknown error";
  if (typeof e === "string") return e;
  if (e.message) return e.message;
  return JSON.stringify(e);
}

// ====== API client ======
async function apiFetch(path, { method="GET", body=null } = {}) {
  const headers = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(path, {
    method,
    headers,
    body: body ? JSON.stringify(body) : null
  });

  const text = await res.text();
  const data = text ? JSON.parse(text) : null;

  if (!res.ok) {
    const err = data?.detail?.error || data?.error || { message: "Request failed" };
    const message = err.message || "Request failed";
    const code = err.code || `HTTP_${res.status}`;
    const details = err.details ? JSON.stringify(err.details) : "";
    const full = `${code}: ${message}${details ? " • " + details : ""}`;
    throw new Error(full);
  }

  return data;
}

// ====== Pages ======
document.addEventListener("DOMContentLoaded", () => {
  applyAuthVisibility();

  const logoutBtn = $("#logoutBtn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      clearToken();
      applyAuthVisibility();
      toast("Выход", "Токен удалён. Вы вышли из системы.");
      window.location.href = "/";
    });
  }

  // LOGIN
  const loginForm = $("#loginForm");
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const email = $("#loginEmail").value.trim();

      try {
        const data = await apiFetch("/auth/login", { method: "POST", body: { email } });
        setToken(data.token);
        applyAuthVisibility();
        toast("Успех", "Вы вошли в систему.", "auth");
        window.location.href = "/cabinet";
      } catch (err) {
        toast("Ошибка входа", formatError(err));
      }
    });
  }

  // REGISTER
  const regForm = $("#registerForm");
  if (regForm) {
    regForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const email = $("#regEmail").value.trim();
      const role = $("#regRole").value;
      const initial_credits = Number($("#regCredits").value || 0);

      try {
        await apiFetch("/auth/register", { method: "POST", body: { email, role, initial_credits } });
        toast("Регистрация", "Пользователь создан. Теперь войдите.", "auth");
        window.location.href = "/login";
      } catch (err) {
        toast("Ошибка регистрации", formatError(err));
      }
    });
  }

  // CABINET: balance + topup
  const balanceBox = $("#balanceValue");
  if (balanceBox) {
    (async () => {
      try {
        const b = await apiFetch("/balance");
        balanceBox.textContent = `${b.credits} credits`;
      } catch (err) {
        toast("Баланс недоступен", formatError(err));
        balanceBox.textContent = "—";
      }
    })();
  }

  const topupForm = $("#topUpForm");
  if (topupForm) {
    topupForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const amount = Number($("#topupAmount").value);

      try {
        const r = await apiFetch("/balance/top-up", { method: "POST", body: { amount } });
        $("#balanceValue").textContent = `${r.new_balance} credits`;
        toast("Пополнение", `Баланс обновлён: ${r.new_balance}`, "balance");
        $("#topupAmount").value = "50";
      } catch (err) {
        toast("Ошибка пополнения", formatError(err));
      }
    });
  }

  // PREDICT
  const predictForm = $("#predictForm");
  if (predictForm) {
    predictForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const keywordsRaw = $("#keywords").value.trim();
      const resumesRaw = $("#resumes").value;

      const keywords = keywordsRaw
        .split(",")
        .map(s => s.trim())
        .filter(Boolean);

      const resumes = resumesRaw
        .split("\n")
        .map(s => s.trim())
        .filter(s => s.length > 0);

      const top_k = Number($("#topk").value || 5);
      const cost_credits = Number($("#cost").value || 10);

      const out = $("#predictOut");
      out.innerHTML = "";

      try {
        const r = await apiFetch("/predict", {
          method: "POST",
          body: { keywords, resumes, top_k, cost_credits }
        });

        const badge = `<span class="badgex"><i class="bi bi-cpu me-1"></i> status: <span class="code-pill">${r.status}</span></span>`;
        const charged = `<span class="badgex"><i class="bi bi-coin me-1"></i> charged: <span class="code-pill">${r.charged_credits}</span></span>`;
        const header = `<div class="d-flex flex-wrap gap-2 mb-3">${badge}${charged}</div>`;

        const invalid = (r.invalid_items || []).length
          ? `<div class="alertx p-3 mb-3">
               <div class="fw-semibold mb-1"><i class="bi bi-exclamation-triangle me-1"></i> Частично некорректные данные</div>
               <div class="text-muted small mb-2">Отклонено: ${r.invalid_items.length}</div>
               <ul class="mb-0">${r.invalid_items.map(x => `<li class="small">${x}</li>`).join("")}</ul>
             </div>`
          : "";

        const top = (r.top || []).length
          ? `<div class="cardx p-0">
               <div class="cardx-header">
                 <div class="fw-semibold">Top-${r.top.length} результаты</div>
                 <div class="text-muted small">score ∈ [0..1]</div>
               </div>
               <div class="cardx-body">
                 <div class="d-grid gap-2">
                   ${r.top.map((it, idx) => `
                     <div class="p-3 cardx" style="box-shadow:none">
                       <div class="d-flex justify-content-between align-items-start gap-3">
                         <div class="fw-semibold">#${idx+1}</div>
                         <div class="code-pill">score: ${Number(it.score).toFixed(3)}</div>
                       </div>
                       <div class="hr-soft"></div>
                       <div class="small text-muted">resume</div>
                       <div class="mt-1" style="white-space:pre-wrap">${it.resume_text}</div>
                     </div>
                   `).join("")}
                 </div>
               </div>
             </div>`
          : `<div class="alertx p-3">Нет результатов.</div>`;

        out.innerHTML = header + invalid + top;

        // refresh balance on success (optional)
        try {
          const b = await apiFetch("/balance");
          const bal = $("#balanceMini");
          if (bal) bal.textContent = `${b.credits} credits`;
        } catch(_) {}

      } catch (err) {
        toast("Ошибка ML-запроса", formatError(err));
      }
    });
  }

  // HISTORY
  const historyRoot = $("#historyRoot");
  if (historyRoot) {
    (async () => {
      try {
        const [txs, preds] = await Promise.all([
          apiFetch("/history/transactions"),
          apiFetch("/history/predictions"),
        ]);

        $("#txTable").innerHTML = txs.map(t => `
          <tr>
            <td class="text-muted">${new Date(t.created_at).toLocaleString()}</td>
            <td><span class="code-pill">${t.tx_type}</span></td>
            <td>${t.amount_credits}</td>
            <td class="text-muted">${t.task_id ?? "—"}</td>
          </tr>
        `).join("");

        $("#predTable").innerHTML = preds.map(p => `
          <tr>
            <td class="text-muted">${new Date(p.created_at).toLocaleString()}</td>
            <td class="text-muted">${p.task_id}</td>
            <td>${p.charged_credits}</td>
            <td><span class="code-pill">${p.status}</span></td>
            <td class="text-muted">${(p.invalid_items || []).length ? (p.invalid_items.join(", ")) : "—"}</td>
          </tr>
        `).join("");

      } catch (err) {
        toast("История недоступна", formatError(err));
      }
    })();
  }
});
