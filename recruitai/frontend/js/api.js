/* RecruitAI — shared API client & session helpers */

const API_BASE = ""; // same origin (Flask serves the frontend too)

const Api = {
  async post(path, body) {
    const res = await fetch(API_BASE + path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || "Request failed");
    return data;
  },
  async put(path, body) {
    const res = await fetch(API_BASE + path, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || "Request failed");
    return data;
  },
  async get(path) {
    const res = await fetch(API_BASE + path);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || "Request failed");
    return data;
  },
};

const Session = {
  save(user) {
    localStorage.setItem("recruitai_user", JSON.stringify(user));
  },
  get() {
    const raw = localStorage.getItem("recruitai_user");
    return raw ? JSON.parse(raw) : null;
  },
  clear() {
    localStorage.removeItem("recruitai_user");
  },
  requireRole(role) {
    const u = Session.get();
    if (!u || u.role !== role) {
      window.location.href = "login.html";
      return null;
    }
    return u;
  },
};

function initials(name) {
  return (name || "?")
    .split(" ")
    .map((p) => p[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

function scoreTier(score) {
  if (score >= 70) return "high";
  if (score >= 45) return "mid";
  return "low";
}

// Renders shimmering skeleton placeholder rows while data is loading.
function skeletonRows(n) {
  n = n || 3;
  let out = "";
  for (let i = 0; i < n; i++) {
    out += `
      <div class="skeleton-row">
        <div class="skeleton-flex">
          <div class="skeleton skeleton-avatar"></div>
          <div class="skeleton-body">
            <div class="skeleton skeleton-line w-40"></div>
            <div class="skeleton skeleton-line w-60"></div>
            <div class="skeleton skeleton-line w-80" style="margin-bottom:0;"></div>
          </div>
        </div>
      </div>
    `;
  }
  return out;
}

// Renders a small radial score-ring SVG (replaces plain score numbers).
function scoreRingSVG(score, size) {
  size = size || 56;
  const r = 22;
  const c = 2 * Math.PI * r;
  const pct = Math.max(0, Math.min(100, score));
  const offset = c - (pct / 100) * c;
  const tier = scoreTier(pct);
  return `
    <div class="score-ring ${tier}" style="width:${size}px;height:${size}px;">
      <svg viewBox="0 0 56 56">
        <circle class="ring-track" cx="28" cy="28" r="${r}"></circle>
        <circle class="ring-value" cx="28" cy="28" r="${r}" stroke-dasharray="${c}" stroke-dashoffset="${offset}"></circle>
      </svg>
      <div class="ring-num">${Math.round(pct)}</div>
    </div>
  `;
}

function timeAgo(dateStr) {
  const diff = (Date.now() - new Date(dateStr + "Z")) / 1000;
  if (diff < 60) return "just now";
  if (diff < 3600) return Math.floor(diff / 60) + "m ago";
  if (diff < 86400) return Math.floor(diff / 3600) + "h ago";
  return Math.floor(diff / 86400) + "d ago";
}

// ---------- Notifications (bell icon, dropdown) ----------
async function initNotifications(userId) {
  const btn = document.getElementById("notif-btn");
  const dropdown = document.getElementById("notif-dropdown");
  const badge = document.getElementById("notif-badge");
  if (!btn) return;

  async function refresh() {
    const data = await Api.get(`/api/notifications/${userId}`);
    if (data.unread_count > 0) {
      badge.textContent = data.unread_count;
      badge.style.display = "flex";
    } else {
      badge.style.display = "none";
    }
    dropdown.innerHTML = data.notifications.length === 0
      ? `<div class="notif-empty">${I18n.t("notif.empty")}</div>`
      : data.notifications.map(n => `
        <div class="notif-item ${n.is_read ? "" : "unread"}" data-id="${n.id}" data-link="${n.link || ""}">
          ${n.message}
          <div class="notif-time">${timeAgo(n.created_at)}</div>
        </div>
      `).join("");
    dropdown.querySelectorAll(".notif-item").forEach(item => {
      item.addEventListener("click", async () => {
        await fetch(`/api/notifications/${item.dataset.id}/read`, { method: "PATCH" });
        if (item.dataset.link) window.location.href = item.dataset.link;
        else refresh();
      });
    });
  }

  btn.addEventListener("click", (e) => {
    e.stopPropagation();
    dropdown.classList.toggle("open");
    if (dropdown.classList.contains("open")) refresh();
  });
  document.addEventListener("click", () => dropdown.classList.remove("open"));
  refresh();
}

// ---------- Help modal ----------
const HELP_CONTENT = {
  recruiter: [
    ["What's a match score?", "A 0-100 score combining how well a candidate's skills, experience, and resume wording fit the job. Higher is a stronger fit."],
    ["What does 'required' vs skill tags mean?", "Skills you mark as required count twice as much toward the score as nice-to-have ones."],
    ["What's the pipeline for?", "Move a candidate through Applied, Shortlisted, Interview, Hired, or Rejected. They see their status update in real time."],
  ],
  candidate: [
    ["Why do I need to complete my profile first?", "Applying is blocked until you've added a resume and at least one skill, otherwise there's nothing for the AI to score you against."],
    ["How is my match score calculated?", "It combines your skills overlap with the job's requirements, your experience level, and how closely your resume's wording matches the job description."],
    ["What happens when I save a job?", "It's bookmarked under \"Saved jobs\" so you can come back to it later without applying right away."],
    ["Will I know if my status changes?", "Yes, you'll get a notification (the bell icon) the moment a recruiter moves you to a new stage."],
  ],
  admin: [
    ["What can I do here?", "See every recruiter, candidate, and job on the platform, and remove any job or user account."],
    ["Can I edit a job instead of removing it?", "Not yet, only removal is supported for now."],
  ],
};

function initHelpModal(role) {
  const btn = document.getElementById("help-btn");
  if (!btn) return;
  const backdrop = document.createElement("div");
  backdrop.className = "help-modal-backdrop";
  const items = HELP_CONTENT[role] || [];
  backdrop.innerHTML = `
    <div class="help-modal">
      <h2>${I18n.t("help.title")}</h2>
      <dl>
        ${items.map(([q, a]) => `<dt>${q}</dt><dd>${a}</dd>`).join("")}
      </dl>
      <button class="btn btn-primary" id="help-close">${I18n.t("help.gotIt")}</button>
    </div>
  `;
  document.body.appendChild(backdrop);
  btn.addEventListener("click", () => backdrop.classList.add("open"));
  backdrop.addEventListener("click", (e) => { if (e.target === backdrop) backdrop.classList.remove("open"); });
  backdrop.querySelector("#help-close").addEventListener("click", () => backdrop.classList.remove("open"));
}
