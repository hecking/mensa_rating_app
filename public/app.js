const USERS_KEY = "mensa-users-v1";
const SESSION_KEY = "mensa-session-v1";
const MENUS_KEY = "mensa-menus-v1";
const RATINGS_KEY = "mensa-ratings-v2";
const SUGGESTIONS_KEY = "mensa-suggestions-v1";

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

let users = loadArray(USERS_KEY);
let session = loadObject(SESSION_KEY);
let menus = loadMenus();
let ratings = loadArray(RATINGS_KEY);
let suggestions = loadArray(SUGGESTIONS_KEY);

function loadArray(key) {
  const raw = localStorage.getItem(key);
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

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

function nextWeeks(count = 4) {
  const start = new Date();
  return Array.from({ length: count }, (_, i) => {
    const d = new Date(start);
    d.setDate(d.getDate() + i * 7);
    return getWeekKey(d);
  });
}

function defaultMealsFor(weekKey) {
  return {
    weekKey,
    days: {
      Monday: ["Pasta Arrabbiata", "Vegan Bowl", "Chicken Wrap"],
      Tuesday: ["Potato Soup", "Tofu Stir Fry", "Fish Curry"],
      Wednesday: ["Lentil Stew", "Veggie Burger", "Beef Chili"],
      Thursday: ["Pumpkin Risotto", "Falafel Plate", "Turkey Rice"],
      Friday: ["Spinach Lasagna", "Sushi Bowl", "Pizza Margherita"],
    },
  };
}

function loadMenus() {
  const existing = loadArray(MENUS_KEY);
  const weekKeys = nextWeeks(6);
  const byWeek = new Map(existing.map((item) => [item.weekKey, item]));
  weekKeys.forEach((weekKey) => {
    if (!byWeek.has(weekKey)) {
      byWeek.set(weekKey, defaultMealsFor(weekKey));
    }
  });
  const merged = [...byWeek.values()].sort((a, b) => a.weekKey.localeCompare(b.weekKey));
  save(MENUS_KEY, merged);
  return merged;
}

function currentUser() {
  if (!session?.email) return null;
  return users.find((user) => user.email === session.email) ?? null;
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
        <strong>${escapeHtml(item.meal)}</strong> (${escapeHtml(item.day)}, ${escapeHtml(item.weekKey)})
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
    .sort((a, b) => b.supporters.length - a.supporters.length)
    .forEach((item) => {
      const supported = Boolean(user && item.supporters.includes(user.email));
      const li = document.createElement("li");
      li.className = "rating-item";
      li.innerHTML = `
        <strong>${escapeHtml(item.title)}</strong>
        <div class="meta">by ${escapeHtml(item.createdByName)} • 👍 ${item.supporters.length}</div>
        <p><a href="${item.recipeDataUrl}" download="${escapeHtml(item.recipeName)}">Download recipe: ${escapeHtml(item.recipeName)}</a></p>
      `;
      const btn = document.createElement("button");
      btn.className = "thumb-button";
      btn.textContent = supported ? "Supported" : "👍 Support";
      btn.disabled = !user || supported;
      btn.addEventListener("click", () => {
        const activeUser = currentUser();
        if (!activeUser) return;
        const target = suggestions.find((entry) => entry.id === item.id);
        if (!target || target.supporters.includes(activeUser.email)) return;
        target.supporters.push(activeUser.email);
        save(SUGGESTIONS_KEY, suggestions);
        renderSuggestions();
      });
      li.appendChild(btn);
      suggestionsList.appendChild(li);
    });
}

function fileToDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result));
    reader.onerror = () => reject(new Error("Could not read file."));
    reader.readAsDataURL(file);
  });
}

registerForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const data = new FormData(registerForm);
  const name = String(data.get("name")).trim();
  const email = String(data.get("email")).trim().toLowerCase();
  const password = String(data.get("password"));
  if (!name || !email || !password) return;
  if (users.some((user) => user.email === email)) {
    alert("Email already exists.");
    return;
  }
  users.push({ name, email, password });
  save(USERS_KEY, users);
  registerForm.reset();
  alert("Account created. You can now log in.");
});

loginForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const data = new FormData(loginForm);
  const email = String(data.get("email")).trim().toLowerCase();
  const password = String(data.get("password"));
  const user = users.find((entry) => entry.email === email && entry.password === password);
  if (!user) {
    alert("Invalid email or password.");
    return;
  }
  session = { email: user.email };
  save(SESSION_KEY, session);
  loginForm.reset();
  updateAuthUI();
  renderSuggestions();
});

logoutButton.addEventListener("click", () => {
  session = null;
  localStorage.removeItem(SESSION_KEY);
  updateAuthUI();
  renderSuggestions();
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
  const file = data.get("photo");
  let photoDataUrl = "";
  if (file instanceof File && file.size > 0) {
    photoDataUrl = await fileToDataUrl(file);
  }
  const entry = {
    id: crypto.randomUUID(),
    userEmail: user.email,
    userName: user.name,
    weekKey: String(data.get("weekKey")),
    day: String(data.get("day")),
    meal: String(data.get("meal")).trim(),
    score: Number(data.get("score")),
    comment: String(data.get("comment")).trim(),
    photoDataUrl,
    createdAt: new Date().toISOString(),
  };
  ratings.unshift(entry);
  save(RATINGS_KEY, ratings);
  ratingForm.reset();
  ratingWeekSelect.value = weekSelect.value;
  renderRatings();
});

suggestionForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const user = currentUser();
  if (!user) {
    alert("Please log in first.");
    return;
  }
  const data = new FormData(suggestionForm);
  const title = String(data.get("title")).trim();
  const recipe = data.get("recipe");
  if (!(recipe instanceof File) || recipe.size === 0) {
    alert("Please upload a recipe file.");
    return;
  }
  const suggestion = {
    id: crypto.randomUUID(),
    title,
    createdByEmail: user.email,
    createdByName: user.name,
    recipeName: recipe.name,
    recipeDataUrl: await fileToDataUrl(recipe),
    supporters: [user.email],
    createdAt: new Date().toISOString(),
  };
  suggestions.unshift(suggestion);
  save(SUGGESTIONS_KEY, suggestions);
  suggestionForm.reset();
  renderSuggestions();
});

updateAuthUI();
renderWeekOptions();
renderMenu();
renderRatings();
renderSuggestions();
