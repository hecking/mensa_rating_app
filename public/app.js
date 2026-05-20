const API_BASE = "http://127.0.0.1:5000/api";
const SESSION_KEY = "mensa-session-v2";

const weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];

const registerForm = document.getElementById("register-form");
const loginForm = document.getElementById("login-form");
const logoutButton = document.getElementById("logout-button");
const authStatus = document.getElementById("auth-status");
const authOnlySections = [...document.querySelectorAll(".auth-only")];

const weekSelect = document.getElementById("week-select");
const menuGrid = document.getElementById("menu-grid");

const ratingForm = document.getElementById("rating-form");
const ratingWeekSelect = document.getElementById("rating-week");
const ratingsList = document.getElementById("ratings-list");
const emptyRatings = document.getElementById("empty-ratings");

const suggestionForm = document.getElementById("suggestion-form");
const suggestionsList = document.getElementById("suggestions-list");
const emptySuggestions = document.getElementById("empty-suggestions");

let session = loadObject(SESSION_KEY);
let menus = [];
let ratings = [];
let suggestions = [];

function loadObject(key) {
  const raw = localStorage.getItem(key);
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw);
    return typeof parsed === "object" && parsed ? parsed : null;
  } catch {
    return null;
  }
}

function save(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}

function getWeekKey(date = new Date()) {
  const base = new Date(Date.UTC(date.getFullYear(), 0, 1));
  const dayOffset = Math.floor((date - base) / 86400000);
  const week = Math.ceil((dayOffset + base.getUTCDay() + 1) / 7);
  return `${date.getFullYear()}-W${String(week).padStart(2, "0")}`;
}

function currentUser() {
  return session?.user ?? null;
}

function updateAuthUI() {
  const user = currentUser();
  const loggedIn = Boolean(user);
  authStatus.textContent = loggedIn ? `Logged in as ${user.name}` : "Not logged in";
  authOnlySections.forEach((section) => {
    section.hidden = !loggedIn;
  });
  logoutButton.hidden = !loggedIn;
}

function renderWeekOptions() {
  if (menus.length === 0) {
    weekSelect.innerHTML = "";
    ratingWeekSelect.innerHTML = "";
    return;
  }
  const options = menus.map((menu) => `<option value="${menu.weekKey}">${menu.weekKey}</option>`).join("");
  weekSelect.innerHTML = options;
  ratingWeekSelect.innerHTML = options;
  const currentWeek = getWeekKey();
  weekSelect.value = menus.some((m) => m.weekKey === currentWeek) ? currentWeek : menus[0].weekKey;
  ratingWeekSelect.value = weekSelect.value;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderMenu() {
  const selectedWeek = weekSelect.value;
  const menu = menus.find((item) => item.weekKey === selectedWeek);
  if (!menu) {
    menuGrid.innerHTML = "<p>No menu for this week.</p>";
    return;
  }
  menuGrid.innerHTML = weekdays
    .map((day) => {
      const items = (menu.days[day] ?? []).map((meal) => `<li>${escapeHtml(meal)}</li>`).join("");
      return `
        <article class="menu-day">
          <h3>${day}</h3>
          <ul>${items}</ul>
        </article>
      `;
    })
    .join("");
}

function renderRatings() {
  ratingsList.innerHTML = "";
  if (ratings.length === 0) {
    emptyRatings.hidden = false;
    return;
  }
  emptyRatings.hidden = true;

  ratings
    .slice()
    .sort((a, b) => b.createdAt.localeCompare(a.createdAt))
    .forEach((item) => {
      const li = document.createElement("li");
      li.className = "rating-item";
      li.innerHTML = `
        <strong>${escapeHtml(item.dishName || item.meal)}</strong> (${escapeHtml(item.day)}, ${escapeHtml(item.weekKey)})
        <div class="meta">${escapeHtml(item.userName)} • ${"★".repeat(item.score)}${"☆".repeat(5 - item.score)}</div>
        ${item.comment ? `<p>${escapeHtml(item.comment)}</p>` : ""}
        ${item.photoDataUrl ? `<img class="image-preview" src="${item.photoDataUrl}" alt="Food image uploaded by student">` : ""}
      `;
      ratingsList.appendChild(li);
    });
}

function renderSuggestions() {
  suggestionsList.innerHTML = "";
  if (suggestions.length === 0) {
    emptySuggestions.hidden = false;
    return;
  }
  emptySuggestions.hidden = true;

  const user = currentUser();
  suggestions
    .slice()
    .sort((a, b) => b.supportCount - a.supportCount)
    .forEach((item) => {
      const supported = Boolean(user && item.supportedByCurrentUser);
      const li = document.createElement("li");
      li.className = "rating-item";
      li.innerHTML = `
        <strong>${escapeHtml(item.title)}</strong>
        <div class="meta">by ${escapeHtml(item.createdByName)} • 👍 ${item.supportCount}</div>
        <p><button type="button" class="recipe-button" data-id="${escapeHtml(item.id)}">Download recipe: ${escapeHtml(item.recipeName || "recipe")}</button></p>
      `;
      const btn = document.createElement("button");
      btn.className = "thumb-button";
      btn.textContent = supported ? "Supported" : "👍 Support";
      btn.disabled = !user || supported;
      btn.addEventListener("click", async () => {
        const activeUser = currentUser();
        if (!activeUser) return;
        const response = await apiFetch(`/suggestions/${encodeURIComponent(item.id)}/support`, {
          method: "POST",
          auth: true,
        });
        if (!response.ok) return;
        await refreshSuggestions();
      });
      li.appendChild(btn);
      li.querySelector(".recipe-button")?.addEventListener("click", async () => {
        const response = await apiFetch(`/suggestions/${encodeURIComponent(item.id)}/recipe`);
        if (!response.ok) return;
        const data = await response.json();
        const href = `data:application/octet-stream;base64,${data.dataBase64}`;
        const a = document.createElement("a");
        a.href = href;
        a.download = data.fileName || "recipe";
        document.body.appendChild(a);
        a.click();
        a.remove();
      });
      suggestionsList.appendChild(li);
    });
}

async function apiFetch(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (options.json && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (options.auth && session?.token) {
    headers.set("Authorization", `Bearer ${session.token}`);
  }
  const response = await fetch(`${API_BASE}${path}`, {
    method: options.method || "GET",
    headers,
    body: options.json ? JSON.stringify(options.json) : options.body,
  });
  return response;
}

async function refreshWeeksAndMenu() {
  const response = await apiFetch("/weeks");
  if (!response.ok) return;
  const data = await response.json();
  const weekKeys = Array.isArray(data.weeks) ? data.weeks : [];
  menus = [];
  for (const weekKey of weekKeys) {
    const menuRes = await apiFetch(`/menus/${encodeURIComponent(weekKey)}`);
    if (!menuRes.ok) continue;
    const menuData = await menuRes.json();
    menus.push({ weekKey: menuData.weekKey, days: menuData.days || {} });
  }
  renderWeekOptions();
  renderMenu();
}

async function refreshRatings() {
  const response = await apiFetch("/ratings");
  if (!response.ok) return;
  const data = await response.json();
  ratings = Array.isArray(data.ratings) ? data.ratings : [];
  for (const item of ratings) {
    item.photoDataUrl = "";
    if (item.hasPhoto && item.id) {
      const photoRes = await apiFetch(`/ratings/${encodeURIComponent(item.id)}/photo`);
      if (!photoRes.ok) continue;
      const photo = await photoRes.json();
      item.photoDataUrl = `data:image/*;base64,${photo.dataBase64}`;
    }
  }
  renderRatings();
}

async function refreshSuggestions() {
  const response = await apiFetch("/suggestions");
  if (!response.ok) return;
  const data = await response.json();
  suggestions = Array.isArray(data.suggestions) ? data.suggestions : [];
  suggestions = suggestions.map((item) => ({
    ...item,
    supportedByCurrentUser: false,
  }));
  renderSuggestions();
}

registerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = new FormData(registerForm);
  const name = String(data.get("name")).trim();
  const email = String(data.get("email")).trim().toLowerCase();
  const password = String(data.get("password"));
  if (!name || !email || !password) return;
  const response = await apiFetch("/auth/register", {
    method: "POST",
    json: { name, email, password },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    alert(body.error || "Registration failed.");
    return;
  }
  registerForm.reset();
  alert("Account created. You can now log in.");
});

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = new FormData(loginForm);
  const email = String(data.get("email")).trim().toLowerCase();
  const password = String(data.get("password"));
  const response = await apiFetch("/auth/login", {
    method: "POST",
    json: { email, password },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    alert(body.error || "Invalid email or password.");
    return;
  }
  const body = await response.json();
  session = { token: body.token, user: body.user };
  save(SESSION_KEY, session);
  loginForm.reset();
  updateAuthUI();
  await refreshSuggestions();
});

logoutButton.addEventListener("click", async () => {
  await apiFetch("/auth/logout", { method: "POST", auth: true });
  session = null;
  localStorage.removeItem(SESSION_KEY);
  updateAuthUI();
  await refreshSuggestions();
});

weekSelect.addEventListener("change", () => {
  ratingWeekSelect.value = weekSelect.value;
  renderMenu();
});

ratingForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const user = currentUser();
  if (!user) {
    alert("Please log in first.");
    return;
  }
  const data = new FormData(ratingForm);
  const response = await apiFetch("/ratings", {
    method: "POST",
    body: data,
    auth: true,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    alert(body.error || "Could not save rating.");
    return;
  }
  ratingForm.reset();
  ratingWeekSelect.value = weekSelect.value;
  await refreshRatings();
});

suggestionForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const user = currentUser();
  if (!user) {
    alert("Please log in first.");
    return;
  }
  const data = new FormData(suggestionForm);
  const response = await apiFetch("/suggestions", {
    method: "POST",
    body: data,
    auth: true,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    alert(body.error || "Could not submit suggestion.");
    return;
  }
  suggestionForm.reset();
  await refreshSuggestions();
});

async function init() {
  updateAuthUI();
  await refreshWeeksAndMenu();
  await refreshRatings();
  await refreshSuggestions();
}

init();
