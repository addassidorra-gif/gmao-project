const API = window.GMAO_API || {};
const TOKENS_KEY = "gmao_tokens";
const DEMO_ACCOUNTS = {
  "admin@enib.tn": "admin123",
  "responsable@enib.tn": "resp123",
  "operateur@enib.tn": "oper123",
  "technicien@enib.tn": "tech123",
};

const DB = {
  users: [],
  equipements: [],
  pannes: [],
  interventions: [],
};

let CU = null;
let curTab = "";
let TOKENS = { access: "", refresh: "" };
let donutChart = null;
let dispChart = null;
let mtbfChart = null;
let paretoChart = null;
let mttrChart = null;
let categoryChart = null;
let sparkCharts = [];
let DASH_FILTERS = { site: "Tous", equipmentType: "Tous", criticality: "Tous" };

const ROLE_NAV = {
  admin: [
    { id: "dashboard", label: "Vue d'ensemble", icon: "grid" },
    { id: "equipements", label: "Équipements", icon: "settings" },
    { id: "utilisateurs", label: "Utilisateurs", icon: "users" },
  ],
  responsable: [
    { id: "pannes_resp", label: "Pannes", icon: "alert" },
    { id: "interventions_resp", label: "Interventions", icon: "tool" },
  ],
  operateur: [{ id: "pannes_oper", label: "Pannes", icon: "alert" }],
  technicien: [{ id: "interventions_tech", label: "Mes interventions", icon: "tool" }],
};

const ROLE_LABEL = {
  admin: "Administrateur",
  responsable: "Resp. Atelier",
  operateur: "Opérateur",
  technicien: "Technicien",
};

const CRIT_OPTIONS = ["Très élevée", "Élevée", "Haute", "Moyenne", "Faible"];
const EQUIP_STATUS_OPTIONS = ["En service", "En panne", "En maintenance", "Hors service"];
const INCIDENT_STATUS_OPTIONS = ["En attente", "En cours", "Résolue"];
const INTERVENTION_STATUS_OPTIONS = ["Planifiée", "En cours", "Terminée"];
const INTERVENTION_PRIORITY_OPTIONS = ["Urgente", "Normale", "Faible", "Pas urgente"];
const INTERVENTION_TYPE_OPTIONS = ["Corrective", "Préventive"];

const ICONS = {
  grid: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>`,
  settings: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>`,
  users: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>`,
  alert: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`,
  tool: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>`,
};

function V(id) {
  return (document.getElementById(id) || { value: "" }).value;
}

function formatUserId(pk) {
  return pk ? `U${String(pk).padStart(3, "0")}` : "U000";
}

function makeInitials(name = "") {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return "??";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
}

function fd(dateValue) {
  if (!dateValue) return '<span style="color:var(--g300)">—</span>';
  return new Date(dateValue).toLocaleDateString("fr-FR", { day: "2-digit", month: "short", year: "numeric" });
}

function toInputDate(dateValue) {
  if (!dateValue) return "";
  return String(dateValue).slice(0, 10);
}

function daysBetween(startDate, endDate) {
  if (!startDate || !endDate) return 0;
  const start = new Date(startDate);
  const end = new Date(endDate);
  const diff = Math.round((end - start) / (1000 * 60 * 60 * 24));
  return diff > 0 ? diff : 0;
}

function estimateCost(priority, days) {
  const base = priority === "Urgente" ? 150 : priority === "Normale" ? 80 : 40;
  return base + days * 15;
}

function getToday() {
  return new Date().toISOString().split("T")[0];
}

function bEtat(value) {
  const map = {
    "En service": "b-green",
    "En panne": "b-red",
    "En maintenance": "b-orange",
    "Hors service": "b-red",
    Actif: "b-green",
    actif: "b-green",
    Inactif: "b-gray",
    inactif: "b-gray",
    "Terminée": "b-green",
    "Planifiée": "b-blue",
    "En cours": "b-orange",
    "En attente": "b-yellow",
    "Résolue": "b-green",
  };
  return `<span class="badge ${map[value] || "b-gray"}">${value}</span>`;
}

function bCrit(value) {
  const map = {
    "Très élevée": "b-red",
    "Élevée": "b-red",
    Haute: "b-red",
    Urgente: "b-red",
    Moyenne: "b-orange",
    Normale: "b-blue",
    Faible: "b-green",
    "Pas urgente": "b-blue",
  };
  return `<span class="badge ${map[value] || "b-gray"}">${value}</span>`;
}

function gEq(value) {
  return DB.equipements.find((item) => item.id === value || item.pk === value) || { pk: null, id: "—", nom: "Inconnu", fabricant: "", localisation: "" };
}

function gUs(value) {
  return DB.users.find((item) => item.id === value || item.pk === value) || { pk: null, id: "U000", nom: "Inconnu", initiales: "??", role: "" };
}

function destroyCharts() {
  [donutChart, dispChart, mtbfChart, paretoChart, mttrChart, categoryChart, ...sparkCharts].forEach((chart) => {
    if (chart) chart.destroy();
  });
  donutChart = null;
  dispChart = null;
  mtbfChart = null;
  paretoChart = null;
  mttrChart = null;
  categoryChart = null;
  sparkCharts = [];
}

function toast(message, type = "ok") {
  const el = document.getElementById("toast-el");
  if (!el) return;
  el.textContent = (type === "ok" ? "✓ " : "⚠ ") + message;
  el.className = `toast t-${type === "ok" ? "ok" : "err"}`;
  el.style.display = "block";
  setTimeout(() => {
    el.style.display = "none";
  }, 3000);
}

function openModal(html) {
  document.getElementById("modals").innerHTML = `<div class="overlay" onclick="if(event.target===this)closeModal()">${html}</div>`;
}

function closeModal() {
  document.getElementById("modals").innerHTML = "";
}

function saveTokens(tokens) {
  TOKENS = { access: tokens.access || "", refresh: tokens.refresh || TOKENS.refresh || "" };
  localStorage.setItem(TOKENS_KEY, JSON.stringify(TOKENS));
}

function loadTokens() {
  try {
    const raw = localStorage.getItem(TOKENS_KEY);
    if (raw) TOKENS = JSON.parse(raw);
  } catch (error) {
    TOKENS = { access: "", refresh: "" };
  }
}

function clearAuth() {
  TOKENS = { access: "", refresh: "" };
  localStorage.removeItem(TOKENS_KEY);
  CU = null;
  DB.users = [];
  DB.equipements = [];
  DB.pannes = [];
  DB.interventions = [];
  destroyCharts();
}

async function refreshAccessToken() {
  if (!TOKENS.refresh) throw new Error("Session expirée.");
  const response = await fetch(API.refresh, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh: TOKENS.refresh }),
  });

  if (!response.ok) {
    clearAuth();
    throw new Error("Session expirée.");
  }

  const data = await response.json();
  saveTokens({ access: data.access, refresh: data.refresh || TOKENS.refresh });
}

async function apiFetch(url, options = {}, retry = true) {
  const headers = new Headers(options.headers || {});
  if (!headers.has("Content-Type") && options.body && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  if (TOKENS.access) headers.set("Authorization", `Bearer ${TOKENS.access}`);

  const response = await fetch(url, { ...options, headers });
  if (response.status === 401 && retry && TOKENS.refresh) {
    await refreshAccessToken();
    return apiFetch(url, options, false);
  }

  if (response.status === 204) return null;

  const isJson = response.headers.get("content-type")?.includes("application/json");
  const payload = isJson ? await response.json() : await response.text();

  if (!response.ok) {
    const message =
      (typeof payload === "object" && (payload.detail || payload.error || JSON.stringify(payload))) ||
      "Une erreur est survenue.";
    throw new Error(message);
  }

  return payload;
}

function mapUser(user) {
  return {
    pk: user.id,
    id: user.display_id || formatUserId(user.id),
    nom: user.full_name,
    email: user.email,
    role: user.role,
    roleLabel: user.role_label || ROLE_LABEL[user.role] || user.role,
    statut: user.is_active ? "actif" : "inactif",
    initiales: user.initials || makeInitials(user.full_name),
  };
}

function mapEquipement(item) {
  return {
    pk: item.id,
    id: item.code,
    nom: item.name,
    type: item.equipment_type,
    ref: item.reference || "",
    etat: item.status,
    criticite: item.criticality,
    fabricant: item.manufacturer || "",
    localisation: item.location || "",
    purchaseDate: item.purchase_date || "",
    description: item.description || "",
  };
}

function mapPanne(item) {
  return {
    pk: item.id,
    id: item.code,
    equipementPk: item.equipment,
    equipementId: item.equipment_code || gEq(item.equipment).id,
    technicienPk: item.technician,
    technicienId: item.technician_display_id || formatUserId(item.technician),
    operatorPk: item.operator,
    operatorId: item.operator_display_id || formatUserId(item.operator),
    title: item.title,
    description: item.description,
    criticite: item.criticality,
    priorite: item.priority,
    date: toInputDate(item.reported_at),
    statut: item.status,
  };
}

function mapIntervention(item) {
  const equipment = gEq(item.equipment);
  const days = daysBetween(item.start_date, item.end_date);
  return {
    pk: item.id,
    id: item.code,
    incidentPk: item.incident,
    equipementPk: item.equipment,
    equipementId: item.equipment_code || equipment.id,
    technicienPk: item.technician,
    technicienId: item.technician_display_id || formatUserId(item.technician),
    description: item.description,
    criticite: item.priority,
    dateDebut: item.start_date,
    dateFin: item.end_date || "",
    statut: item.status,
    rapport: item.report || "",
    etatActuel: item.equipment_status_after || equipment.etat || "En maintenance",
    prochaineMaintenance: item.next_maintenance || "",
    fabricant: equipment.fabricant || "",
    type: item.intervention_type,
    duree: days,
    cout: estimateCost(item.priority, days),
  };
}

async function loadData() {
  const [usersData, equipmentsData, incidentsData, interventionsData] = await Promise.all([
    apiFetch(API.users),
    apiFetch(API.equipments),
    apiFetch(API.incidents),
    apiFetch(API.interventions),
  ]);

  DB.users = usersData.map(mapUser);
  DB.equipements = equipmentsData.map(mapEquipement);
  DB.pannes = incidentsData.map(mapPanne);
  DB.interventions = interventionsData.map(mapIntervention);

  if (CU) {
    CU = DB.users.find((user) => user.pk === CU.pk) || CU;
  }
}

async function restoreSession() {
  try {
    if (!TOKENS.access && TOKENS.refresh) {
      await refreshAccessToken();
    }
    const me = await apiFetch(API.me);
    CU = mapUser(me);
    await loadData();
    loginOK();
  } catch (error) {
    clearAuth();
    showLogin();
  }
}

function showLogin() {
  document.getElementById("pg-login").style.display = "flex";
  document.getElementById("app").style.display = "none";
}

function loginOK() {
  document.getElementById("l-err").style.display = "none";
  document.getElementById("pg-login").style.display = "none";
  document.getElementById("app").style.display = "flex";
  setupSidebar();
  gotoDefault();
}

async function doLogin(event) {
  event.preventDefault();
  const email = document.getElementById("l-email").value.trim().toLowerCase();
  const password = document.getElementById("l-pwd").value;
  if (!email || !password) {
    document.getElementById("l-err").textContent = "⚠ Email et mot de passe obligatoires.";
    document.getElementById("l-err").style.display = "block";
    return;
  }
  await loginWithCredentials(email, password);
}

async function ql(email, password) {
  document.getElementById("l-email").value = email;
  document.getElementById("l-pwd").value = password;
  await loginWithCredentials(email, password);
}

async function loginWithCredentials(email, password) {
  try {
    const data = await apiFetch(API.login, {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }, false);
    saveTokens(data);
    CU = mapUser(data.user);
    await loadData();
    loginOK();
  } catch (error) {
    document.getElementById("l-err").textContent = `⚠ ${error.message}`;
    document.getElementById("l-err").style.display = "block";
  }
}

async function logout() {
  try {
    if (TOKENS.refresh) {
      await apiFetch(API.logout, {
        method: "POST",
        body: JSON.stringify({ refresh: TOKENS.refresh }),
      }, false);
    }
  } catch (error) {
    // ignore logout API errors
  }
  clearAuth();
  document.getElementById("l-email").value = "";
  document.getElementById("l-pwd").value = "";
  showLogin();
}

function setupSidebar() {
  const nav = ROLE_NAV[CU.role] || [];
  document.getElementById("sb-av").textContent = CU.initiales;
  document.getElementById("sb-name").textContent = CU.nom;
  document.getElementById("sb-role").textContent = CU.roleLabel || ROLE_LABEL[CU.role] || CU.role;
  document.getElementById("tb-greet").innerHTML = `Bienvenue, <strong>${CU.nom.split(" ")[0]}</strong>`;
  const topAvatar = document.getElementById("tb-av");
  if (topAvatar) topAvatar.textContent = CU.initiales;

  const container = document.getElementById("sb-nav");
  container.innerHTML =
    `<div class="sb-section">Navigation</div>` +
    nav
      .map(
        (item) => `
      <div class="sb-item" id="nav-${item.id}" onclick="go('${item.id}')">
        ${ICONS[item.icon] || ""}
        <span>${item.label}</span>
      </div>`
      )
      .join("");
}

function gotoDefault() {
  const nav = ROLE_NAV[CU.role] || [];
  if (nav.length) go(nav[0].id);
}

function go(id) {
  curTab = id;
  destroyCharts();
  document.querySelectorAll(".sb-item").forEach((item) => item.classList.remove("active"));
  const active = document.getElementById(`nav-${id}`);
  if (active) active.classList.add("active");

  const titles = {
    dashboard: "Vue d'ensemble",
    equipements: "Équipements",
    utilisateurs: "Utilisateurs",
    pannes_resp: "Pannes",
    interventions_resp: "Interventions",
    pannes_oper: "Pannes",
    interventions_tech: "Mes interventions",
  };
  document.getElementById("tb-title").textContent = titles[id] || id;

  const main = document.getElementById("main");
  main.innerHTML = "";
  const div = document.createElement("div");
  div.className = "pg";

  switch (id) {
    case "dashboard":
      div.innerHTML = pgDashboard();
      break;
    case "equipements":
      div.innerHTML = pgEquipements();
      break;
    case "utilisateurs":
      div.innerHTML = pgUtilisateurs();
      break;
    case "pannes_resp":
      div.innerHTML = pgPannesResp();
      break;
    case "interventions_resp":
      div.innerHTML = pgInterventionsResp();
      break;
    case "pannes_oper":
      div.innerHTML = pgPannesOper();
      break;
    case "interventions_tech":
      div.innerHTML = pgInterventionsTech();
      break;
    default:
      div.innerHTML = `<div class="card" style="padding:24px">Section introuvable.</div>`;
  }

  main.appendChild(div);
  if (id === "dashboard") setTimeout(buildDashCharts, 80);
}

function uniqueValues(values) {
  return [...new Set(values.filter(Boolean))].sort((a, b) => a.localeCompare(b, "fr"));
}

function dashboardSelectOptions(values, selected) {
  const options = ["Tous", ...uniqueValues(values)];
  return options.map((value) => `<option value="${value}"${value === selected ? " selected" : ""}>${value}</option>`).join("");
}

function setDashboardFilter(key, value) {
  DASH_FILTERS[key] = value || "Tous";
  renderRoute("dashboard");
}

function getDashboardData() {
  const equipments = DB.equipements.filter((item) => {
    const typeOk = DASH_FILTERS.equipmentType === "Tous" || item.type === DASH_FILTERS.equipmentType;
    const criticalityOk = DASH_FILTERS.criticality === "Tous" || item.criticite === DASH_FILTERS.criticality;
    const siteOk = DASH_FILTERS.site === "Tous" || item.localisation === DASH_FILTERS.site;
    return typeOk && criticalityOk && siteOk;
  });
  const equipmentCodes = new Set(equipments.map((item) => item.id));
  const pannes = DB.pannes.filter((item) => equipmentCodes.has(item.equipementId));
  const interventions = DB.interventions.filter((item) => equipmentCodes.has(item.equipementId));
  return { equipments, pannes, interventions };
}

function calcKPIs(source = null) {
  const equipments = source?.equipments || DB.equipements;
  const pannes = source?.pannes || DB.pannes;
  const interventions = source?.interventions || DB.interventions;
  const total = equipments.length || 1;
  const enSvc = equipments.filter((item) => item.etat === "En service").length;
  const enPanne = equipments.filter((item) => item.etat === "En panne" || item.etat === "Hors service").length;
  const enMaint = equipments.filter((item) => item.etat === "En maintenance").length;
  const dispo = Math.round((enSvc / total) * 100);
  const pannePct = Math.round((enPanne / total) * 100);
  const maintPct = Math.round((enMaint / total) * 100);

  const finished = interventions.filter((item) => item.statut === "Terminée");
  const nbPannes = pannes.length;
  const mtbf = finished.length ? Math.round(finished.reduce((sum, item) => sum + Math.max(item.duree, 1), 0) / finished.length * 4) : 120;
  const mttr = finished.length ? Math.round(finished.reduce((sum, item) => sum + Math.max(item.duree, 1), 0) / finished.length) : 4;
  const maintenab = Math.round((mttr / (mtbf + mttr)) * 100);
  const pannesActives = pannes.filter((item) => item.statut !== "Résolue").length;
  const intervEnCours = interventions.filter((item) => item.statut === "En cours").length;
  const coutTotal = interventions.reduce((sum, item) => sum + (item.cout || 0), 0);
  const txDefaillance = nbPannes > 0 ? Math.round((enPanne / nbPannes) * 100) / 100 : 0;
  return {
    total,
    enSvc,
    enPanne,
    enMaint,
    dispo,
    pannePct,
    maintPct,
    mtbf,
    mttr,
    maintenab,
    pannesActives,
    intervEnCours,
    coutTotal,
    txDefaillance,
    nbPannes,
  };
}

function dashboardCategoryLabel(equipment) {
  const haystack = `${equipment?.type || ""} ${equipment?.nom || ""}`.toLowerCase();
  if (haystack.includes("hydraul")) return "Hydraulique";
  if (haystack.includes("compresseur") || haystack.includes("air") || haystack.includes("pneumat")) return "Pneumatique";
  if (haystack.includes("automate") || haystack.includes("électron") || haystack.includes("info") || haystack.includes("pc")) return "Électrique";
  if (haystack.includes("machine") || haystack.includes("tour") || haystack.includes("robot") || haystack.includes("moteur") || haystack.includes("table")) return "Mécanique";
  return "Autres";
}

function buildDashboardScenario() {
  const dashboardData = getDashboardData();
  const kpis = calcKPIs(dashboardData);
  const months = ["Déc 2023", "Jan 2024", "Fév 2024", "Mar 2024", "Avr 2024", "Mai 2024"];
  const availabilitySeries = [72, 73, 74, 74, 76, kpis.dispo];
  const objectiveSeries = [74, 74, 75, 75, 76, 76];
  const mtbfSeries = [145, 132, 122, 116, 108, kpis.mtbf];
  const mttrSeries = [5, 7, 8, 9, 8, kpis.mttr];
  const uptimeHours = Math.round(kpis.total * 24 * (kpis.dispo / 100));
  const downtimeHours = Math.max(0, Math.round(kpis.total * 24 - uptimeHours));
  const categorySeed = {
    "Mécanique": 0,
    "Électrique": 0,
    "Hydraulique": 0,
    "Pneumatique": 0,
    "Autres": 0,
  };
  const categoryActuals = {
    "Mécanique": 0,
    "Électrique": 0,
    "Hydraulique": 0,
    "Pneumatique": 0,
    "Autres": 0,
  };

  dashboardData.pannes.forEach((item) => {
    const label = dashboardCategoryLabel(gEq(item.equipementId));
    categoryActuals[label] = (categoryActuals[label] || 0) + 1;
  });

  const categories = Object.entries(categorySeed).map(([label, seedValue]) => ({
    label,
    value: Math.max(seedValue, categoryActuals[label] || 0),
  }));

  const paretoTotal = categories.reduce((sum, item) => sum + item.value, 0) || 1;
  let running = 0;
  const paretoCumulative = categories.map((item) => {
    running += (item.value / paretoTotal) * 100;
    return Math.round(running);
  });

  const groupedMttr = {};
  dashboardData.interventions.filter((item) => item.duree > 0).forEach((item) => {
    const key = item.equipementId;
    if (!groupedMttr[key]) groupedMttr[key] = [];
    groupedMttr[key].push(item.duree);
  });

  const mttrEquipment = Object.entries(groupedMttr)
    .map(([equipmentId, values]) => ({
      label: gEq(equipmentId).nom || equipmentId,
      value: Number((values.reduce((sum, value) => sum + value, 0) / values.length).toFixed(1)),
    }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 4);

  const recentSource = [...dashboardData.interventions]
    .sort((a, b) => String(b.dateDebut || "").localeCompare(String(a.dateDebut || "")))
    .slice(0, 5);
  const downtimeSeed = ["12 h 30", "8 h 45", "4 h 20", "6 h 15", "2 h 10"];
  const mttrSeed = ["6 h 20", "4 h 10", "2 h 15", "3 h 05", "1 h 40"];
  const recentRows = recentSource.map((item, index) => {
    const equipment = gEq(item.equipementId);
    const impact = item.criticite === "Urgente" ? "Élevé" : item.criticite === "Faible" ? "Faible" : "Moyen";
    return {
      date: item.dateDebut || getToday(),
      equipment: equipment.nom || item.equipementId,
      category: dashboardCategoryLabel(equipment),
      downtime: downtimeSeed[index] || `${Math.max(item.duree, 1)} h 00`,
      mttr: mttrSeed[index] || `${Math.max(item.duree, 1)} h 00`,
      status: item.statut === "Terminée" ? "Résolue" : item.statut,
      impact,
    };
  });
  const overdueInterventions = planningData().filter((item) => item.planningStatus === "En retard").length;
  const repeatedFaults = dashboardData.pannes.filter((item) => item.statut !== "Résolue").length;

  return {
    title: "Tableau de bord Maintenance",
    subtitle: "Vue consolidée des indicateurs de maintenance ENIB",
    months,
    period: "Mai 2024",
    site: DASH_FILTERS.site,
    equipmentType: DASH_FILTERS.equipmentType,
    criticality: DASH_FILTERS.criticality,
    siteOptions: dashboardSelectOptions(DB.equipements.map((item) => item.localisation), DASH_FILTERS.site),
    equipmentTypeOptions: dashboardSelectOptions(DB.equipements.map((item) => item.type), DASH_FILTERS.equipmentType),
    criticalityOptions: dashboardSelectOptions(CRIT_OPTIONS, DASH_FILTERS.criticality),
    availability: kpis.dispo,
    availabilityTrend: 5,
    uptimeHours,
    downtimeHours,
    mtbf: kpis.mtbf,
    mtbfTrend: 8,
    incidentsCount: kpis.nbPannes,
    failureRate: kpis.txDefaillance,
    mttr: kpis.mttr,
    mttrTrend: -6,
    averageRepairHours: kpis.mttr,
    onTimeRate: 82,
    availabilitySeries,
    objectiveSeries,
    mtbfSeries,
    mttrSeries,
    categories,
    paretoCumulative,
    mttrEquipment,
    recentRows,
    alertTiles: [
      { icon: "❗", tone: "a-red", title: "Disponibilité faible", desc: `${kpis.enPanne} équipements indisponibles` },
      { icon: "⚠️", tone: "a-orange", title: "MTTR élevé", desc: `${Math.round(kpis.mttr)} h de réparation moyenne` },
      { icon: "🚨", tone: "a-red", title: "Pannes répétitives", desc: `Convoyeur 03 (${repeatedFaults} pannes)` },
      { icon: "📌", tone: "a-orange", title: "Interventions en retard", desc: `${overdueInterventions} interventions en retard` },
    ],
  };
}

function pgDashboard() {
  const scenario = buildDashboardScenario();

  return `
  <div class="dash-shell">
    <div class="dash-toolbar">
      <div class="dash-toolbar-copy">
        <h2>${scenario.title}</h2>
        <p>${scenario.subtitle}</p>
      </div>
      <div class="dash-toolbar-controls">
        <label class="dash-select-wrap">
          <span>Période</span>
          <select class="dash-select">
            <option selected>${scenario.period}</option>
          </select>
        </label>
        <label class="dash-select-wrap">
          <span>Site</span>
          <select class="dash-select" onchange="setDashboardFilter('site', this.value)">
            ${scenario.siteOptions}
          </select>
        </label>
        <label class="dash-select-wrap">
          <span>Type d'équipement</span>
          <select class="dash-select" onchange="setDashboardFilter('equipmentType', this.value)">
            ${scenario.equipmentTypeOptions}
          </select>
        </label>
        <label class="dash-select-wrap">
          <span>Criticité</span>
          <select class="dash-select" onchange="setDashboardFilter('criticality', this.value)">
            ${scenario.criticalityOptions}
          </select>
        </label>
      </div>
    </div>

    <div class="kpi-strip">
      <div class="kpi-big kpi-dispo">
        <div class="kpi-top">
          <div class="kpi-top-label"><span class="metric-dot metric-blue"></span>Disponibilité</div>
          <span class="kpi-top-trend trend-up">↑ ${scenario.availabilityTrend}% <small>vs mois précédent</small></span>
        </div>
        <div class="kpi-main-val">${scenario.availability}%</div>
        <div class="kpi-main-unit">Taux de disponibilité</div>
        <canvas id="spark-dispo" class="kpi-sparkline"></canvas>
        <div class="kpi-sub-row">
          <div class="kpi-sub-item"><div class="kpi-sub-val">${scenario.uptimeHours} h</div><div class="kpi-sub-lbl">Temps fonctionnement</div></div>
          <div class="kpi-sub-item"><div class="kpi-sub-val">${scenario.downtimeHours} h</div><div class="kpi-sub-lbl">Temps d'arrêt</div></div>
        </div>
      </div>

      <div class="kpi-big kpi-fiab">
        <div class="kpi-top">
          <div class="kpi-top-label"><span class="metric-dot metric-orange"></span>Fiabilité</div>
          <span class="kpi-top-trend trend-up">↑ ${scenario.mtbfTrend}% <small>vs mois précédent</small></span>
        </div>
        <div class="kpi-main-val">${scenario.mtbf} <span style="font-size:18px;font-weight:500">h</span></div>
        <div class="kpi-main-unit">MTBF</div>
        <canvas id="spark-mtbf" class="kpi-sparkline"></canvas>
        <div class="kpi-sub-row">
          <div class="kpi-sub-item"><div class="kpi-sub-val">${scenario.incidentsCount}</div><div class="kpi-sub-lbl">Nombre de pannes</div></div>
          <div class="kpi-sub-item"><div class="kpi-sub-val">${String(scenario.failureRate).replace(".", ",")}%</div><div class="kpi-sub-lbl">Taux de défaillance</div></div>
        </div>
      </div>

      <div class="kpi-big kpi-maint">
        <div class="kpi-top">
          <div class="kpi-top-label"><span class="metric-dot metric-green"></span>Maintenabilité</div>
          <span class="kpi-top-trend trend-up">↓ ${Math.abs(scenario.mttrTrend)}% <small>vs mois précédent</small></span>
        </div>
        <div class="kpi-main-val">${String(scenario.mttr).replace(".", ",")} <span style="font-size:18px;font-weight:500">h</span></div>
        <div class="kpi-main-unit">MTTR</div>
        <canvas id="spark-mttr" class="kpi-sparkline"></canvas>
        <div class="kpi-sub-row">
          <div class="kpi-sub-item"><div class="kpi-sub-val">${String(scenario.averageRepairHours).replace(".", ",")} h</div><div class="kpi-sub-lbl">Temps moyen d'intervention</div></div>
          <div class="kpi-sub-item"><div class="kpi-sub-val">${scenario.onTimeRate}%</div><div class="kpi-sub-lbl">Interventions dans le délai</div></div>
        </div>
      </div>
    </div>

    <div class="dash-row2">
      <div class="chart-card">
        <div class="chart-hd"><div><div class="chart-title">Évolution de la disponibilité (%)</div><div class="chart-sub">Disponibilité vs objectif</div></div></div>
        <div class="chart-body chart-body-tall"><canvas id="ch-disp"></canvas></div>
      </div>
      <div class="chart-card">
        <div class="chart-hd"><div><div class="chart-title">MTBF et MTTR (heures)</div><div class="chart-sub">Comparatif mensuel</div></div></div>
        <div class="chart-body chart-body-tall"><canvas id="ch-mtbf"></canvas></div>
      </div>
      <div class="chart-card">
        <div class="chart-hd"><div><div class="chart-title">Pannes par catégorie</div><div class="chart-sub">Répartition synthétique</div></div></div>
        <div class="chart-body chart-body-tall"><canvas id="ch-category"></canvas></div>
      </div>
    </div>

    <div class="dash-row4">
      <div class="chart-card">
        <div class="chart-hd"><div><div class="chart-title">Pareto des causes de panne</div><div class="chart-sub">Priorisation des défauts</div></div></div>
        <div class="chart-body chart-body-tall"><canvas id="ch-pareto"></canvas></div>
      </div>
      <div class="chart-card">
        <div class="chart-hd"><div><div class="chart-title">MTTR par équipement (heures)</div><div class="chart-sub">Top des équipements les plus coûteux</div></div></div>
        <div class="chart-body chart-body-tall"><canvas id="ch-mttr"></canvas></div>
      </div>
      <div class="card recent-card">
        <div class="chart-hd"><div class="chart-title">Dernières pannes / interventions</div></div>
        <div class="tbl-wrap">
          <table class="interv-table recent-table">
            <thead><tr><th>Date</th><th>Équipement</th><th>Type de panne</th><th>Durée d'arrêt</th><th>MTTR</th><th>Statut</th><th>Impact</th></tr></thead>
            <tbody>
              ${scenario.recentRows.length ? scenario.recentRows.map((item) => {
                const impactClass = item.impact === "Élevé" ? "ip-eleve" : item.impact === "Faible" ? "ip-faible" : "ip-moyen";
                return `<tr>
                  <td>${fd(item.date)}</td>
                  <td><strong>${item.equipment}</strong></td>
                  <td>${item.category}</td>
                  <td>${item.downtime}</td>
                  <td>${item.mttr}</td>
                  <td>${bEtat(item.status)}</td>
                  <td><span class="impact-pill ${impactClass}">${item.impact}</span></td>
                </tr>`;
              }).join("") : `<tr><td colspan="7" class="empty">Aucune intervention récente.</td></tr>`}
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="dashboard-alerts">
      <div class="dashboard-alerts-title">Alertes et points d'attention</div>
      <div class="alert-strip">
        ${scenario.alertTiles.map((item) => `
          <div class="alert-tile ${item.tone}">
            <div class="alert-tile-icon">${item.icon}</div>
            <div>
              <div class="alert-tile-title">${item.title}</div>
              <div class="alert-tile-desc">${item.desc}</div>
            </div>
          </div>`).join("")}
      </div>
    </div>
  </div>`;
}

function buildSparkline(id, data, color) {
  const canvas = document.getElementById(id);
  if (!canvas || !window.Chart) return;
  const chart = new Chart(canvas, {
    type: "line",
    data: {
      labels: data.map((_, index) => index + 1),
      datasets: [{ data, borderColor: color, borderWidth: 1.5, fill: true, backgroundColor: `${color}18`, tension: 0.4, pointRadius: 0 }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: { enabled: false } },
      scales: { x: { display: false }, y: { display: false } },
    },
  });
  sparkCharts.push(chart);
}

function buildDashCharts() {
  if (!window.Chart) return;
  const k = calcKPIs();
  buildSparkline("spark-dispo", [72, 75, 74, 78, 76, k.dispo], "#2563eb");
  buildSparkline("spark-mtbf", [110, 115, 112, 118, 116, k.mtbf], "#ea580c");
  buildSparkline("spark-mttr", [5, 4.8, 5.2, 4.5, 4.3, k.mttr], "#16a34a");

  const dispCtx = document.getElementById("ch-disp");
  if (dispCtx) {
    dispChart = new Chart(dispCtx, {
      type: "line",
      data: {
        labels: ["Déc", "Jan", "Fév", "Mar", "Avr", "Mai"],
        datasets: [{ label: "Disponibilité", data: [68, 72, 70, 75, 77, k.dispo], borderColor: "#2563eb", backgroundColor: "rgba(37,99,235,.08)", fill: true, tension: 0.4 }],
      },
      options: { responsive: true, plugins: { legend: { position: "bottom" } } },
    });
  }

  const mtbfCtx = document.getElementById("ch-mtbf");
  if (mtbfCtx) {
    new Chart(mtbfCtx, {
      type: "bar",
      data: {
        labels: ["Déc", "Jan", "Fév", "Mar", "Avr", "Mai"],
        datasets: [
          { label: "MTBF", data: [108, 115, 112, 118, 116, k.mtbf], backgroundColor: "rgba(37,99,235,.75)", borderRadius: 4 },
          { label: "MTTR", data: [5, 4.8, 5.2, 4.5, 4.3, k.mttr], backgroundColor: "rgba(249,115,22,.75)", borderRadius: 4 },
        ],
      },
      options: { responsive: true, plugins: { legend: { position: "bottom" } } },
    });
  }

  const paretoCtx = document.getElementById("ch-pareto");
  if (paretoCtx) {
    const typeCounts = {};
    DB.pannes.forEach((item) => {
      const eq = gEq(item.equipementId);
      typeCounts[eq.type] = (typeCounts[eq.type] || 0) + 1;
    });
    const sorted = Object.entries(typeCounts).sort((a, b) => b[1] - a[1]).slice(0, 5);
    const labels = sorted.map(([name]) => name);
    const values = sorted.map(([, value]) => value);
    const total = values.reduce((sum, value) => sum + value, 0) || 1;
    let running = 0;
    const cumulative = values.map((value) => {
      running += (value / total) * 100;
      return Math.round(running);
    });
    paretoChart = new Chart(paretoCtx, {
      type: "bar",
      data: {
        labels,
        datasets: [
          { label: "Nombre de pannes", data: values, backgroundColor: "rgba(37,99,235,.75)", borderRadius: 4, order: 2 },
          { label: "Cumul %", data: cumulative, type: "line", borderColor: "#f97316", yAxisID: "y2", order: 1 },
        ],
      },
      options: { responsive: true, scales: { y2: { position: "right", max: 100 } } },
    });
  }

  const mttrCtx = document.getElementById("ch-mttr");
  if (mttrCtx) {
    const sample = DB.equipements.slice(0, 5);
    mttrChart = new Chart(mttrCtx, {
      type: "bar",
      data: {
        labels: sample.map((item) => item.id),
        datasets: [{ label: "MTTR", data: sample.map((item) => Math.max(1, DB.interventions.find((intervention) => intervention.equipementId === item.id)?.duree || 2)), backgroundColor: ["#2563eb", "#06b6d4", "#16a34a", "#ea580c", "#7c3aed"], borderRadius: 4 }],
      },
      options: { responsive: true, indexAxis: "y", plugins: { legend: { display: false } } },
    });
  }

  const donutCtx = document.getElementById("ch-donut");
  if (donutCtx) {
    donutChart = new Chart(donutCtx, {
      type: "doughnut",
      data: {
        labels: ["Disponible", "Maintenance", "Panne"],
        datasets: [{ data: [k.dispo, k.maintPct, k.pannePct], backgroundColor: ["#2563eb", "#f97316", "#dc2626"], borderWidth: 0 }],
      },
      options: { cutout: "70%", plugins: { legend: { display: false } } },
    });
  }
}

function pgEquipements() {
  return `
    <div class="s-title">
      <div><h2>Tableau des équipements</h2><p>${DB.equipements.length} équipements enregistrés</p></div>
      <button class="btn btn-succ" onclick="modalAddEquip()">＋ Ajouter un équipement</button>
    </div>
    <div class="card"><div class="tbl-wrap"><table>
      <thead><tr><th>Code</th><th>Criticité</th><th>Nom</th><th>Type</th><th>Références</th><th>Localisation</th><th>État</th><th>Actions</th></tr></thead>
      <tbody id="tb-eq">${rowsEq()}</tbody>
    </table></div></div>`;
}

function rowsEq() {
  if (!DB.equipements.length) {
    return `<tr><td colspan="8" class="empty">Aucun équipement enregistré.</td></tr>`;
  }
  return DB.equipements.map((item, index) => `
    <tr>
      <td><span class="chip">${item.id}</span></td>
      <td>${bCrit(item.criticite)}</td>
      <td><strong>${item.nom}</strong></td>
      <td style="font-size:12px;color:var(--g500)">${item.type}</td>
      <td style="font-size:12px;color:var(--g400)">${item.ref}</td>
      <td style="font-size:12px">${item.localisation}</td>
      <td>${bEtat(item.etat)}</td>
      <td style="white-space:nowrap">
        <button class="btn btn-ghost btn-sm" onclick="modalEditEquip(${index})">✏ Modifier</button>
        <button class="btn btn-dang btn-sm" style="margin-left:4px" onclick="delEquip(${index})">🗑</button>
      </td>
    </tr>`).join("");
}

function modalAddEquip() {
  openModal(`<div class="modal"><div class="mhd"><h3>➕ Ajouter un équipement</h3><div class="mx" onclick="closeModal()">✕</div></div>
    <div class="mbd">
      <div class="fr2">
        <div class="fg"><label class="fl">Code</label><input class="fc" id="eq-id" placeholder="ex: FC020"></div>
        <div class="fg"><label class="fl">Nom</label><input class="fc" id="eq-nom" placeholder="Nom"></div>
      </div>
      <div class="fr2">
        <div class="fg"><label class="fl">Type</label><input class="fc" id="eq-type"></div>
        <div class="fg"><label class="fl">Fabricant</label><input class="fc" id="eq-fab"></div>
      </div>
      <div class="fr2">
        <div class="fg"><label class="fl">Références</label><input class="fc" id="eq-ref"></div>
        <div class="fg"><label class="fl">Localisation</label><input class="fc" id="eq-loc"></div>
      </div>
      <div class="fr2">
        <div class="fg"><label class="fl">Criticité</label><select class="fc" id="eq-crit">${CRIT_OPTIONS.map((item) => `<option>${item}</option>`).join("")}</select></div>
        <div class="fg"><label class="fl">État</label><select class="fc" id="eq-etat">${EQUIP_STATUS_OPTIONS.map((item) => `<option>${item}</option>`).join("")}</select></div>
      </div>
      <div class="fg"><label class="fl">Date d'achat</label><input class="fc" id="eq-date" type="date"></div>
    </div>
    <div class="mft"><button class="btn btn-ghost" onclick="closeModal()">Annuler</button><button class="btn btn-prim" onclick="addEquip()">Ajouter</button></div>
  </div>`);
}

async function addEquip() {
  const code = V("eq-id").trim();
  const name = V("eq-nom").trim();
  if (!code || !name) return toast("Code et nom obligatoires.", "err");
  try {
    await apiFetch(API.equipments, {
      method: "POST",
      body: JSON.stringify({
        code,
        name,
        equipment_type: V("eq-type"),
        manufacturer: V("eq-fab"),
        reference: V("eq-ref"),
        location: V("eq-loc"),
        criticality: V("eq-crit"),
        status: V("eq-etat"),
        purchase_date: V("eq-date") || null,
        description: "",
      }),
    });
    await loadData();
    closeModal();
    go(curTab);
    toast("Équipement ajouté.");
  } catch (error) {
    toast(error.message, "err");
  }
}

function modalEditEquip(index) {
  const item = DB.equipements[index];
  openModal(`<div class="modal"><div class="mhd"><h3>✏ Modifier l'équipement</h3><div class="mx" onclick="closeModal()">✕</div></div>
    <div class="mbd">
      <div class="fr2">
        <div class="fg"><label class="fl">Code</label><input class="fc" id="eeq-id" value="${item.id}"></div>
        <div class="fg"><label class="fl">Nom</label><input class="fc" id="eeq-nom" value="${item.nom}"></div>
      </div>
      <div class="fr2">
        <div class="fg"><label class="fl">Type</label><input class="fc" id="eeq-type" value="${item.type}"></div>
        <div class="fg"><label class="fl">Fabricant</label><input class="fc" id="eeq-fab" value="${item.fabricant || ""}"></div>
      </div>
      <div class="fr2">
        <div class="fg"><label class="fl">Références</label><input class="fc" id="eeq-ref" value="${item.ref || ""}"></div>
        <div class="fg"><label class="fl">Localisation</label><input class="fc" id="eeq-loc" value="${item.localisation || ""}"></div>
      </div>
      <div class="fr2">
        <div class="fg"><label class="fl">Criticité</label><select class="fc" id="eeq-crit">${CRIT_OPTIONS.map((value) => `<option${value === item.criticite ? " selected" : ""}>${value}</option>`).join("")}</select></div>
        <div class="fg"><label class="fl">État</label><select class="fc" id="eeq-etat">${EQUIP_STATUS_OPTIONS.map((value) => `<option${value === item.etat ? " selected" : ""}>${value}</option>`).join("")}</select></div>
      </div>
      <div class="fg"><label class="fl">Date d'achat</label><input class="fc" id="eeq-date" type="date" value="${item.purchaseDate || ""}"></div>
    </div>
    <div class="mft"><button class="btn btn-ghost" onclick="closeModal()">Annuler</button><button class="btn btn-prim" onclick="saveEquip(${index})">Enregistrer</button></div>
  </div>`);
}

async function saveEquip(index) {
  const item = DB.equipements[index];
  try {
    await apiFetch(`${API.equipments}${item.pk}/`, {
      method: "PUT",
      body: JSON.stringify({
        code: V("eeq-id").trim(),
        name: V("eeq-nom").trim(),
        equipment_type: V("eeq-type"),
        manufacturer: V("eeq-fab"),
        reference: V("eeq-ref"),
        location: V("eeq-loc"),
        criticality: V("eeq-crit"),
        status: V("eeq-etat"),
        purchase_date: V("eeq-date") || null,
        description: item.description || "",
      }),
    });
    await loadData();
    closeModal();
    go(curTab);
    toast("Équipement modifié.");
  } catch (error) {
    toast(error.message, "err");
  }
}

async function delEquip(index) {
  const item = DB.equipements[index];
  if (!confirm(`Supprimer "${item.nom}" ?`)) return;
  try {
    await apiFetch(`${API.equipments}${item.pk}/`, { method: "DELETE" });
    await loadData();
    go(curTab);
    toast("Équipement supprimé.");
  } catch (error) {
    toast(error.message, "err");
  }
}

function pgUtilisateurs() {
  return `
    <div class="s-title">
      <div><h2>Tableau des utilisateurs</h2><p>${DB.users.length} comptes</p></div>
      <button class="btn btn-succ" onclick="modalAddUser()">＋ Ajouter utilisateur</button>
    </div>
    <div class="card"><div class="tbl-wrap"><table>
      <thead><tr><th>ID</th><th>Nom</th><th>Email</th><th>Rôle</th><th>Statut</th><th>Actions</th></tr></thead>
      <tbody id="tb-users">${rowsUsers()}</tbody>
    </table></div></div>`;
}

function rowsUsers() {
  if (!DB.users.length) {
    return `<tr><td colspan="6" class="empty">Aucun utilisateur disponible.</td></tr>`;
  }
  return DB.users.map((item, index) => `
    <tr>
      <td><span class="chip">${item.id}</span></td>
      <td><div style="display:flex;align-items:center;gap:9px">
        <div style="width:30px;height:30px;border-radius:50%;background:linear-gradient(135deg,var(--cyan),var(--blue2));display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:#fff">${item.initiales}</div>
        <strong>${item.nom}</strong>
      </div></td>
      <td style="font-size:12.5px;color:var(--g500)">${item.email}</td>
      <td><span class="badge b-blue">${ROLE_LABEL[item.role] || item.role}</span></td>
      <td>${bEtat(item.statut === "actif" ? "Actif" : "Inactif")}</td>
      <td style="white-space:nowrap">
        <button class="btn btn-ghost btn-sm" onclick="modalEditUser(${index})">✏ Modifier</button>
        <button class="btn btn-dang btn-sm" style="margin-left:4px" onclick="delUser(${index})">🗑</button>
      </td>
    </tr>`).join("");
}

function modalAddUser() {
  openModal(`<div class="modal"><div class="mhd"><h3>➕ Ajouter un utilisateur</h3><div class="mx" onclick="closeModal()">✕</div></div>
    <div class="mbd">
      <div class="fg"><label class="fl">Nom complet</label><input class="fc" id="u-nom" placeholder="Prénom Nom"></div>
      <div class="fg"><label class="fl">Email</label><input class="fc" id="u-email" type="email" placeholder="email@enib.tn"></div>
      <div class="fg"><label class="fl">Mot de passe</label><input class="fc" id="u-pwd" type="password"></div>
      <div class="fr2">
        <div class="fg"><label class="fl">Rôle</label><select class="fc" id="u-role">${Object.keys(ROLE_LABEL).map((role) => `<option value="${role}">${ROLE_LABEL[role]}</option>`).join("")}</select></div>
        <div class="fg"><label class="fl">Statut</label><select class="fc" id="u-statut"><option value="actif">Actif</option><option value="inactif">Inactif</option></select></div>
      </div>
    </div>
    <div class="mft"><button class="btn btn-ghost" onclick="closeModal()">Annuler</button><button class="btn btn-prim" onclick="addUser()">Ajouter</button></div>
  </div>`);
}

async function addUser() {
  const fullName = V("u-nom").trim();
  const email = V("u-email").trim();
  const password = V("u-pwd").trim();
  if (!fullName || !email || !password) return toast("Nom, email et mot de passe obligatoires.", "err");
  try {
    await apiFetch(API.users, {
      method: "POST",
      body: JSON.stringify({
        full_name: fullName,
        email,
        role: V("u-role"),
        is_active: V("u-statut") === "actif",
        password,
      }),
    });
    await loadData();
    closeModal();
    go(curTab);
    toast("Utilisateur ajouté.");
  } catch (error) {
    toast(error.message, "err");
  }
}

function modalEditUser(index) {
  const item = DB.users[index];
  openModal(`<div class="modal"><div class="mhd"><h3>✏ Modifier l'utilisateur</h3><div class="mx" onclick="closeModal()">✕</div></div>
    <div class="mbd">
      <div class="fg"><label class="fl">Nom complet</label><input class="fc" id="eu-nom" value="${item.nom}"></div>
      <div class="fg"><label class="fl">Email</label><input class="fc" id="eu-email" value="${item.email}"></div>
      <div class="fg"><label class="fl">Mot de passe</label><input class="fc" id="eu-pwd" type="password" placeholder="Laisser vide pour conserver"></div>
      <div class="fr2">
        <div class="fg"><label class="fl">Rôle</label><select class="fc" id="eu-role">${Object.keys(ROLE_LABEL).map((role) => `<option value="${role}"${role === item.role ? " selected" : ""}>${ROLE_LABEL[role]}</option>`).join("")}</select></div>
        <div class="fg"><label class="fl">Statut</label><select class="fc" id="eu-statut"><option value="actif"${item.statut === "actif" ? " selected" : ""}>Actif</option><option value="inactif"${item.statut !== "actif" ? " selected" : ""}>Inactif</option></select></div>
      </div>
    </div>
    <div class="mft"><button class="btn btn-ghost" onclick="closeModal()">Annuler</button><button class="btn btn-prim" onclick="saveUser(${index})">Enregistrer</button></div>
  </div>`);
}

async function saveUser(index) {
  const item = DB.users[index];
  const body = {
    full_name: V("eu-nom").trim(),
    email: V("eu-email").trim(),
    role: V("eu-role"),
    is_active: V("eu-statut") === "actif",
  };
  const password = V("eu-pwd").trim();
  if (password) body.password = password;
  try {
    await apiFetch(`${API.users}${item.pk}/`, { method: "PUT", body: JSON.stringify(body) });
    await loadData();
    closeModal();
    go(curTab);
    toast("Utilisateur modifié.");
  } catch (error) {
    toast(error.message, "err");
  }
}

async function delUser(index) {
  const item = DB.users[index];
  if (!confirm(`Supprimer "${item.nom}" ?`)) return;
  try {
    await apiFetch(`${API.users}${item.pk}/`, { method: "DELETE" });
    await loadData();
    go(curTab);
    toast("Utilisateur supprimé.");
  } catch (error) {
    toast(error.message, "err");
  }
}

function pgPannesResp() {
  return `
    <div class="s-title"><div><h2>Liste des pannes</h2><p>Suivi responsable maintenance</p></div></div>
    <div class="card"><div class="tbl-wrap"><table>
      <thead><tr><th>Code</th><th>Équipement</th><th>Criticité</th><th>Date</th><th>Statut</th><th>Option</th></tr></thead>
      <tbody>${DB.pannes.length ? DB.pannes.map((item, index) => `
        <tr>
          <td><span class="chip">${item.id}</span></td>
          <td><strong>${gEq(item.equipementId).nom}</strong></td>
          <td>${bCrit(item.criticite)}</td>
          <td style="font-size:12px;color:var(--g400)">${fd(item.date)}</td>
          <td>${bEtat(item.statut)}</td>
          <td><button class="btn btn-succ btn-sm" onclick="modalPanneDetail(${index})">👁 Consulter</button></td>
        </tr>`).join("") : `<tr><td colspan="6" class="empty">Aucune panne disponible.</td></tr>`}
      </tbody>
    </table></div></div>`;
}

function modalPanneDetail(index) {
  const item = DB.pannes[index];
  const eq = gEq(item.equipementId);
  const tech = gUs(item.technicienId);
  openModal(`<div class="modal wide"><div class="mhd"><h3>📋 Détail panne — ${eq.nom}</h3><div class="mx" onclick="closeModal()">✕</div></div>
    <div class="mbd">
      <div class="fr2" style="margin-bottom:14px">
        <div><div class="fl">Code</div><p style="font-weight:700;color:var(--navy)">${item.id}</p></div>
        <div><div class="fl">Technicien</div><p>${tech.nom}</p></div>
        <div><div class="fl">Criticité</div>${bCrit(item.criticite)}</div>
        <div><div class="fl">Localisation</div><p>${eq.localisation || "—"}</p></div>
        <div><div class="fl">Date</div><p>${fd(item.date)}</p></div>
        <div><div class="fl">Statut</div>${bEtat(item.statut)}</div>
      </div>
      <div class="fg"><div class="fl">Description</div><div style="background:var(--g50);border:1px solid var(--g200);border-radius:8px;padding:12px;font-size:14px">${item.description}</div></div>
      <div class="fg"><label class="fl">Modifier le statut</label><select class="fc" id="ps-${index}">${INCIDENT_STATUS_OPTIONS.map((status) => `<option${status === item.statut ? " selected" : ""}>${status}</option>`).join("")}</select></div>
    </div>
    <div class="mft">
      ${(CU?.role === "responsable" || CU?.role === "admin") && item.statut !== "Résolue" ? `<button class="btn btn-succ" onclick="modalNewInterv(${item.pk})">Planifier une intervention</button>` : ""}
      <button class="btn btn-ghost" onclick="closeModal()">Fermer</button>
      <button class="btn btn-prim" onclick="updatePanneStatut(${index})">Enregistrer</button>
    </div>
  </div>`);
}

async function updatePanneStatut(index) {
  const item = DB.pannes[index];
  try {
    await apiFetch(`${API.incidents}${item.pk}/`, {
      method: "PATCH",
      body: JSON.stringify({ status: V(`ps-${index}`) }),
    });
    await loadData();
    closeModal();
    go(curTab);
    toast("Statut mis à jour.");
  } catch (error) {
    toast(error.message, "err");
  }
}

function techOptionsHtml(selectedPk = null) {
  return DB.users.filter((user) => user.role === "technicien" && user.statut === "actif")
    .map((user) => `<option value="${user.pk}"${selectedPk === user.pk ? " selected" : ""}>${user.nom}</option>`)
    .join("");
}

function equipmentOptionsHtml(selectedPk = null) {
  return DB.equipements.map((item) => `<option value="${item.pk}"${selectedPk === item.pk ? " selected" : ""}>${item.nom} (${item.id})</option>`).join("");
}

function incidentOptionsHtml(selectedPk = null) {
  const openIncidents = DB.pannes.filter((item) => item.statut !== "Résolue");
  const options = openIncidents.map((item) => {
    const eq = gEq(item.equipementId);
    return `<option value="${item.pk}" data-equipment="${item.equipementPk}"${selectedPk === item.pk ? " selected" : ""}>${item.id} — ${eq.nom}</option>`;
  });
  return `<option value="">Intervention sans panne liée</option>${options.join("")}`;
}

function syncInterventionEquipment() {
  const incidentSelect = document.getElementById("ni-inc");
  const equipmentSelect = document.getElementById("ni-eq");
  const selected = incidentSelect?.selectedOptions?.[0];
  if (!selected || !selected.dataset.equipment || !equipmentSelect) return;
  equipmentSelect.value = selected.dataset.equipment;
}

function pgInterventionsResp() {
  return `
    <div class="s-title">
      <div><h2>Table des interventions</h2><p>Planification, affectation technicien et validation.</p></div>
      <button class="btn btn-prim" onclick="modalNewInterv()">＋ Planifier une intervention</button>
    </div>
    <div class="card"><div class="tbl-wrap"><table>
      <thead><tr><th>Code</th><th>Technicien</th><th>Équipement</th><th>Description</th><th>Type</th><th>Priorité</th><th>Statut</th><th>Début</th><th>Fin</th><th>Option</th></tr></thead>
      <tbody id="tb-irsp">${rowsInterv()}</tbody>
    </table></div></div>`;
}

function rowsInterv() {
  if (!DB.interventions.length) {
    return `<tr><td colspan="10" class="empty">Aucune intervention planifiée.</td></tr>`;
  }
  return DB.interventions.map((item, index) => {
    const eq = gEq(item.equipementId);
    const tech = gUs(item.technicienId);
    return `<tr>
      <td><span class="chip">${item.id}</span></td>
      <td><div style="display:flex;align-items:center;gap:7px">
        <div style="width:27px;height:27px;border-radius:50%;background:linear-gradient(135deg,var(--cyan),var(--blue2));display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;color:#fff">${tech.initiales}</div>
        <span style="font-size:12.5px">${tech.nom.split(" ")[0]}</span>
      </div></td>
      <td><strong style="font-size:13px">${eq.nom}</strong><div style="font-size:11px;color:var(--g400)">${eq.localisation}</div></td>
      <td style="font-size:12px;max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${item.description}</td>
      <td>${bCrit(item.type)}</td>
      <td>${bCrit(item.criticite)}</td>
      <td>${bEtat(item.statut)}</td>
      <td style="font-size:12px;color:var(--g500)">${fd(item.dateDebut)}</td>
      <td style="font-size:12px;color:var(--g500)">${item.dateFin ? fd(item.dateFin) : '<span style="color:var(--g300)">—</span>'}</td>
      <td><button class="btn btn-succ btn-sm" onclick="modalRapport(${index},'resp')">📄 Rapport</button></td>
    </tr>`;
  }).join("");
}

function modalNewInterv(incidentPk = null) {
  const selectedIncident = DB.pannes.find((item) => item.pk === incidentPk);
  const selectedEquipmentPk = selectedIncident?.equipementPk || null;
  openModal(`<div class="modal wide"><div class="mhd"><h3>➕ Nouvelle intervention</h3><div class="mx" onclick="closeModal()">✕</div></div>
    <div class="mbd">
      <div class="fg"><label class="fl">Panne liée</label><select class="fc" id="ni-inc" onchange="syncInterventionEquipment()">${incidentOptionsHtml(incidentPk)}</select></div>
      <div class="fr2">
        <div class="fg"><label class="fl">Technicien</label><select class="fc" id="ni-tech">${techOptionsHtml()}</select></div>
        <div class="fg"><label class="fl">Équipement</label><select class="fc" id="ni-eq">${equipmentOptionsHtml(selectedEquipmentPk)}</select></div>
      </div>
      <div class="fg"><label class="fl">Description</label><textarea class="fc" id="ni-desc" rows="2"></textarea></div>
      <div class="fr2">
        <div class="fg"><label class="fl">Priorité</label><select class="fc" id="ni-crit">${INTERVENTION_PRIORITY_OPTIONS.map((item) => `<option>${item}</option>`).join("")}</select></div>
        <div class="fg"><label class="fl">Type</label><select class="fc" id="ni-type">${INTERVENTION_TYPE_OPTIONS.map((item) => `<option>${item}</option>`).join("")}</select></div>
      </div>
      <div class="fr2">
        <div class="fg"><label class="fl">Date début</label><input class="fc" id="ni-debut" type="date" value="${getToday()}"></div>
        <div class="fg"><label class="fl">Date fin</label><input class="fc" id="ni-fin" type="date"></div>
      </div>
    </div>
    <div class="mft"><button class="btn btn-ghost" onclick="closeModal()">Annuler</button><button class="btn btn-prim" onclick="addInterv()">Créer</button></div>
  </div>`);
}

async function addInterv() {
  try {
    if (!V("ni-tech")) throw new Error("Aucun technicien actif disponible.");
    if (!V("ni-eq")) throw new Error("Aucun équipement disponible.");
    const description = V("ni-desc").trim();
    ensureMinLength(description, 8, "La description");
    await apiFetch(API.interventions, {
      method: "POST",
      body: JSON.stringify({
        incident: V("ni-inc") ? Number(V("ni-inc")) : null,
        technician: Number(V("ni-tech")),
        equipment: Number(V("ni-eq")),
        description,
        priority: V("ni-crit"),
        intervention_type: V("ni-type"),
        status: "En cours",
        start_date: V("ni-debut") || getToday(),
        end_date: V("ni-fin") || null,
        report: "",
        next_maintenance: null,
        equipment_status_after: "En maintenance",
      }),
    });
    await loadData();
    closeModal();
    go(curTab);
    toast("Intervention créée.");
  } catch (error) {
    toast(error.message, "err");
  }
}

function rapportFooter(mode, index) {
  if (mode === "tech") {
    return `
      <button class="btn btn-ghost" onclick="closeModal()">Annuler</button>
      <button class="btn btn-succ" onclick="saveRapport(${index}, 'tech')">Enregistrer</button>`;
  }
  return `
    <button class="btn btn-warn" onclick="reclamer(${index})">Réouvrir</button>
    <button class="btn btn-ghost" onclick="closeModal()">Fermer</button>
    <button class="btn btn-succ" onclick="saveRapport(${index}, 'resp')">Valider</button>`;
}

function modalRapport(index, mode) {
  const item = DB.interventions[index];
  const eq = gEq(item.equipementId);
  const readOnly = false;
  openModal(`<div class="modal wide"><div class="mhd"><h3>📄 Rapport sur l'intervention</h3><div class="mx" onclick="closeModal()">✕</div></div>
    <div class="mbd">
      <div class="rap-grid">
        <div class="rap-sec">
          <h4>Détails de l'équipement</h4>
          <div class="rap-row"><span>ID équipement</span><span class="rap-pill">${item.equipementId}</span></div>
          <div class="rap-row"><span>Fabricant</span><span class="rap-pill">${item.fabricant || eq.fabricant || "—"}</span></div>
        </div>
        <div class="rap-sec">
          <h4>Informations de maintenance</h4>
          <div class="rap-row"><span>Date</span><span class="rap-pill">${item.dateDebut ? new Date(item.dateDebut).toLocaleDateString("fr-FR") : "—"}</span></div>
          <div class="rap-row"><span>Type</span><span class="rap-pill c">${item.type}</span></div>
        </div>
      </div>
      <div class="rap-sec" style="margin-bottom:14px">
        <h4>Suivi</h4>
        <div class="rap-row" style="flex-wrap:wrap;gap:10px">
          <span>Statut intervention</span>
          <select class="fc" id="rap-stat" style="max-width:240px">${INTERVENTION_STATUS_OPTIONS.map((value) => `<option${value === item.statut ? " selected" : ""}>${value}</option>`).join("")}</select>
        </div>
        <div class="rap-row" style="flex-wrap:wrap;gap:10px;margin-top:10px">
          <span>État équipement</span>
          <select class="fc" id="rap-etat" style="max-width:240px">${EQUIP_STATUS_OPTIONS.map((value) => `<option${value === item.etatActuel ? " selected" : ""}>${value}</option>`).join("")}</select>
        </div>
        <div class="rap-row" style="margin-top:10px">
          <span>Date de fin</span>
          <input class="fc" id="rap-end" type="date" value="${item.dateFin || ""}" style="max-width:180px">
        </div>
        <div class="rap-row" style="margin-top:10px">
          <span>Prochaine maintenance</span>
          <input class="fc" id="rap-next" type="date" value="${item.prochaineMaintenance || ""}" style="max-width:180px">
        </div>
      </div>
      <div class="rap-sec">
        <h4>Rapport d'intervention</h4>
        <textarea class="fc" id="rap-txt" rows="4" placeholder="Décrivez les actions effectuées...">${item.rapport || ""}</textarea>
      </div>
    </div>
    <div class="mft">${rapportFooter(mode, index)}</div>
  </div>`);
}

async function saveRapport(index, mode) {
  const item = DB.interventions[index];
  const newStatus = mode === "resp" ? "Terminée" : V("rap-stat");
  const payload = {
    status: newStatus,
    report: V("rap-txt").trim(),
    end_date: V("rap-end") || (newStatus === "Terminée" ? getToday() : null),
    next_maintenance: V("rap-next") || null,
    equipment_status_after: V("rap-etat"),
  };
  try {
    await apiFetch(`${API.interventions}${item.pk}/`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
    await loadData();
    closeModal();
    go(curTab);
    toast(mode === "resp" ? "Rapport validé." : "Rapport enregistré.");
  } catch (error) {
    toast(error.message, "err");
  }
}

async function reclamer(index) {
  const item = DB.interventions[index];
  try {
    await apiFetch(`${API.interventions}${item.pk}/`, {
      method: "PATCH",
      body: JSON.stringify({
        status: "En cours",
        report: V("rap-txt").trim() || item.rapport || "Intervention réouverte pour complément.",
        equipment_status_after: V("rap-etat"),
        next_maintenance: V("rap-next") || null,
        end_date: null,
      }),
    });
    await loadData();
    closeModal();
    go(curTab);
    toast("Intervention réouverte.");
  } catch (error) {
    toast(error.message, "err");
  }
}

function pgPannesOper() {
  return `
    <div class="s-title">
      <div><h2>Liste des pannes</h2><p>Déclarez et suivez vos pannes.</p></div>
      <button class="btn btn-warn" onclick="modalSignalerPanne()">⚠ Signaler une panne</button>
    </div>
    <div class="card"><div class="tbl-wrap"><table>
      <thead><tr><th>Technicien</th><th>Équipement</th><th>Description</th><th>Criticité</th><th>Date</th><th>Statut</th></tr></thead>
      <tbody id="tb-po">${rowsPannesOper()}</tbody>
    </table></div></div>`;
}

function rowsPannesOper() {
  if (!DB.pannes.length) {
    return `<tr><td colspan="6" class="empty">Aucune panne déclarée.</td></tr>`;
  }
  return DB.pannes.map((item) => {
    const tech = gUs(item.technicienId);
    const eq = gEq(item.equipementId);
    return `<tr>
      <td><div style="display:flex;align-items:center;gap:8px">
        <div style="width:27px;height:27px;border-radius:50%;background:linear-gradient(135deg,var(--cyan),var(--blue2));display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;color:#fff">${tech.initiales}</div>
        <span style="font-size:12.5px">${tech.nom}</span>
      </div></td>
      <td><strong>${eq.nom}</strong></td>
      <td style="font-size:12.5px">${item.description}</td>
      <td>${bCrit(item.criticite)}</td>
      <td style="font-size:12px;color:var(--g400)">${fd(item.date)}</td>
      <td>${bEtat(item.statut)}</td>
    </tr>`;
  }).join("");
}

function modalSignalerPanne() {
  openModal(`<div class="modal wide"><div class="mhd"><h3>⚠ Signaler une panne</h3><div class="mx" onclick="closeModal()">✕</div></div>
    <div class="mbd">
      <div class="fr2">
        <div class="fg"><label class="fl">Date</label><input class="fc" id="sp-date" type="date" value="${getToday()}"></div>
        <div class="fg"><label class="fl">Technicien responsable</label><select class="fc" id="sp-tech">${techOptionsHtml()}</select></div>
      </div>
      <div class="fr2">
        <div class="fg"><label class="fl">Équipement</label><select class="fc" id="sp-eq">${equipmentOptionsHtml()}</select></div>
        <div class="fg"><label class="fl">Criticité</label><select class="fc" id="sp-crit">${CRIT_OPTIONS.map((item) => `<option${item === "Moyenne" ? " selected" : ""}>${item}</option>`).join("")}</select></div>
      </div>
      <div class="fg"><label class="fl">Priorité</label><select class="fc" id="sp-prio">${INTERVENTION_PRIORITY_OPTIONS.map((item) => `<option${item === "Normale" ? " selected" : ""}>${item}</option>`).join("")}</select></div>
      <div class="fg"><label class="fl">Titre</label><input class="fc" id="sp-title" placeholder="Exemple : panne moteur"></div>
      <div class="fg"><label class="fl">Description</label><textarea class="fc" id="sp-desc" rows="3" placeholder="Décrivez le problème observé..."></textarea></div>
    </div>
    <div class="mft">
      <button class="btn btn-ghost" onclick="closeModal()">Annuler</button>
      <button class="btn btn-succ" onclick="signalerPanne()">Enregistrer</button>
    </div>
  </div>`);
}

async function signalerPanne() {
  const description = V("sp-desc").trim();
  const title = V("sp-title").trim() || description.slice(0, 40) || "Nouvelle panne";
  if (!description) return toast("Description obligatoire.", "err");
  try {
    await apiFetch(API.incidents, {
      method: "POST",
      body: JSON.stringify({
        equipment: Number(V("sp-eq")),
        technician: Number(V("sp-tech")),
        title,
        description,
        criticality: V("sp-crit"),
        priority: V("sp-prio"),
        status: "En attente",
        reported_at: `${V("sp-date")}T08:00:00+01:00`,
      }),
    });
    await loadData();
    closeModal();
    go(curTab);
    toast("Panne signalée.");
  } catch (error) {
    toast(error.message, "err");
  }
}

function pgInterventionsTech() {
  const mine = DB.interventions.filter((item) => item.technicienPk === CU.pk);
  return `
    <div class="s-title"><div><h2>Mes interventions</h2><p>Rapports et suivi de vos tâches.</p></div></div>
    <div class="card"><div class="tbl-wrap"><table>
      <thead><tr><th>Code</th><th>Équipement</th><th>Localisation</th><th>Description</th><th>Priorité</th><th>Statut</th><th>Date début</th><th>Date fin</th><th>Action</th></tr></thead>
      <tbody>${mine.length ? mine.map((item) => {
        const eq = gEq(item.equipementId);
        const index = DB.interventions.findIndex((candidate) => candidate.pk === item.pk);
        return `<tr>
          <td><span class="chip">${item.id}</span></td>
          <td><strong>${eq.nom}</strong></td>
          <td style="font-size:12px">${eq.localisation}</td>
          <td style="font-size:12px;max-width:140px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${item.description}</td>
          <td>${bCrit(item.criticite)}</td>
          <td>${bEtat(item.statut)}</td>
          <td style="font-size:12px">${fd(item.dateDebut)}</td>
          <td style="font-size:12px">${item.dateFin ? fd(item.dateFin) : '<span style="color:var(--g300)">—</span>'}</td>
          <td style="white-space:nowrap"><button class="btn btn-prim btn-sm" onclick="modalRapport(${index},'tech')">✏ Rapport</button></td>
        </tr>`;
      }).join("") : `<tr><td colspan="9" class="empty">Aucune intervention assignée</td></tr>`}
      </tbody>
    </table></div></div>`;
}

document.addEventListener("DOMContentLoaded", async () => {
  loadTokens();
  if (TOKENS.access || TOKENS.refresh) {
    await restoreSession();
  } else {
    showLogin();
  }
});

let LOADING_COUNT = 0;
let REFRESH_TIMER = null;
let PENDING_CONFIRM = null;
let IGNORE_HASH_CHANGE = false;

DB.auditLogs = [];

ICONS.calendar = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>`;
ICONS.shield = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>`;
ICONS.history = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3v5h5"/><path d="M3.05 13a9 9 0 1 0 .5-5.5L3 8"/></svg>`;

ROLE_NAV.admin = [
  { id: "dashboard", label: "Vue d'ensemble", icon: "grid" },
  { id: "equipements", label: "Équipements", icon: "settings" },
  { id: "utilisateurs", label: "Utilisateurs", icon: "users" },
  { id: "audit_logs", label: "Rapports & audit", icon: "shield" },
];
ROLE_NAV.responsable = [
  { id: "pannes_resp", label: "Gestion des pannes", icon: "alert" },
  { id: "interventions_resp", label: "Planification", icon: "tool" },
];
ROLE_NAV.technicien = [
  { id: "interventions_tech", label: "Mes interventions", icon: "tool" },
];
ROLE_NAV.operateur = [
  { id: "pannes_oper", label: "Mes pannes", icon: "alert" },
];

const ROUTE_TITLES = {
  dashboard: "Vue d'ensemble",
  equipements: "Équipements",
  utilisateurs: "Utilisateurs",
  pannes_resp: "Pannes",
  interventions_resp: "Interventions",
  pannes_oper: "Mes pannes",
  interventions_tech: "Mes interventions",
  planning: "Planning maintenance",
  audit_logs: "Journal d'audit",
};

function setLoading(visible, text = "Chargement...") {
  const loader = document.getElementById("app-loader");
  const label = document.getElementById("loader-text");
  if (!loader || !label) return;
  label.textContent = text;
  if (visible) loader.classList.remove("hidden");
  else loader.classList.add("hidden");
}

function beginLoading(text = "Chargement...") {
  LOADING_COUNT += 1;
  setLoading(true, text);
}

function endLoading() {
  LOADING_COUNT = Math.max(0, LOADING_COUNT - 1);
  if (LOADING_COUNT === 0) setLoading(false);
}

function toast(message, type = "ok") {
  const el = document.getElementById("toast-el");
  if (!el) return;
  const resolved = type === "warn" ? "warn" : type === "err" ? "err" : "ok";
  el.textContent = (resolved === "ok" ? "✓ " : resolved === "warn" ? "⚠ " : "❗ ") + message;
  el.className = `toast t-${resolved}`;
  el.style.display = "block";
  setTimeout(() => {
    el.style.display = "none";
  }, 3200);
}

function normalizeApiError(errorPayload, fallback = "Une erreur est survenue.") {
  if (!errorPayload) return fallback;
  if (typeof errorPayload === "string") return errorPayload;
  if (errorPayload.message && typeof errorPayload.message === "string") return errorPayload.message;
  if (errorPayload.detail && typeof errorPayload.detail === "string") return errorPayload.detail;
  if (errorPayload.errors && typeof errorPayload.errors === "object") {
    const firstKey = Object.keys(errorPayload.errors)[0];
    const firstValue = errorPayload.errors[firstKey];
    if (Array.isArray(firstValue)) return firstValue[0];
    if (typeof firstValue === "string") return firstValue;
  }
  const firstKey = Object.keys(errorPayload)[0];
  const firstValue = errorPayload[firstKey];
  if (Array.isArray(firstValue)) return firstValue[0];
  if (typeof firstValue === "string") return firstValue;
  return fallback;
}

function parseJwtPayload(token) {
  if (!token || token.split(".").length < 2) return null;
  try {
    const segment = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    const padded = segment + "=".repeat((4 - (segment.length % 4 || 4)) % 4);
    return JSON.parse(atob(padded));
  } catch (error) {
    return null;
  }
}

function scheduleTokenRefresh() {
  if (REFRESH_TIMER) {
    clearTimeout(REFRESH_TIMER);
    REFRESH_TIMER = null;
  }
  const payload = parseJwtPayload(TOKENS.access);
  if (!payload?.exp) return;
  const delay = payload.exp * 1000 - Date.now() - 60_000;
  if (delay <= 0) return;
  REFRESH_TIMER = setTimeout(async () => {
    try {
      await refreshAccessToken();
    } catch (error) {
      await logout();
      toast("Votre session a expiré. Merci de vous reconnecter.", "warn");
    }
  }, delay);
}

function saveTokens(tokens) {
  TOKENS = { access: tokens.access || "", refresh: tokens.refresh || TOKENS.refresh || "" };
  localStorage.setItem(TOKENS_KEY, JSON.stringify(TOKENS));
  scheduleTokenRefresh();
}

function loadTokens() {
  try {
    const raw = localStorage.getItem(TOKENS_KEY);
    TOKENS = raw ? JSON.parse(raw) : { access: "", refresh: "" };
  } catch (error) {
    TOKENS = { access: "", refresh: "" };
  }
  scheduleTokenRefresh();
}

function clearAuth() {
  TOKENS = { access: "", refresh: "" };
  localStorage.removeItem(TOKENS_KEY);
  CU = null;
  DB.users = [];
  DB.equipements = [];
  DB.pannes = [];
  DB.interventions = [];
  DB.auditLogs = [];
  if (REFRESH_TIMER) clearTimeout(REFRESH_TIMER);
  REFRESH_TIMER = null;
  destroyCharts();
}

async function refreshAccessToken() {
  if (!TOKENS.refresh) throw new Error("Session expirée.");
  const response = await fetch(API.refresh, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh: TOKENS.refresh }),
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    clearAuth();
    throw new Error(normalizeApiError(payload, "Session expirée."));
  }
  saveTokens({ access: payload.access, refresh: payload.refresh || TOKENS.refresh });
}

const ApiService = {
  async request(url, options = {}, retry = true) {
    const headers = new Headers(options.headers || {});
    if (!headers.has("Content-Type") && options.body && !(options.body instanceof FormData)) {
      headers.set("Content-Type", "application/json");
    }
    if (TOKENS.access) headers.set("Authorization", `Bearer ${TOKENS.access}`);

    if (!options.silent) beginLoading(options.loadingText || "Chargement...");
    try {
      const response = await fetch(url, { ...options, headers });
      if (response.status === 401 && retry && TOKENS.refresh) {
        await refreshAccessToken();
        return this.request(url, { ...options, silent: true }, false);
      }
      if (response.status === 204) return null;

      const isJson = response.headers.get("content-type")?.includes("application/json");
      const payload = isJson ? await response.json() : await response.text();
      if (!response.ok) {
        throw new Error(normalizeApiError(payload));
      }
      return payload;
    } finally {
      if (!options.silent) endLoading();
    }
  },
};

window.GMAOApiService = ApiService;

async function apiFetch(url, options = {}, retry = true) {
  return ApiService.request(url, options, retry);
}

function safeSetHash(route) {
  const nextHash = `#/${route}`;
  if (window.location.hash === nextHash) return;
  IGNORE_HASH_CHANGE = true;
  window.location.hash = nextHash;
  setTimeout(() => {
    IGNORE_HASH_CHANGE = false;
  }, 0);
}

function getRequestedRoute() {
  return window.location.hash.replace(/^#\/?/, "").trim();
}

function getAllowedRoutes() {
  return (ROLE_NAV[CU?.role] || []).map((item) => item.id);
}

function showLogin() {
  document.getElementById("pg-login").style.display = "flex";
  document.getElementById("app").style.display = "none";
  setLoading(false);
}

function loginOK() {
  document.getElementById("l-err").style.display = "none";
  document.getElementById("pg-login").style.display = "none";
  document.getElementById("app").style.display = "flex";
  scheduleTokenRefresh();
  setupSidebar();
  handleRouteChange(true);
}

async function logout() {
  try {
    if (TOKENS.refresh) {
      await apiFetch(API.logout, {
        method: "POST",
        body: JSON.stringify({ refresh: TOKENS.refresh }),
        silent: true,
      }, false);
    }
  } catch (error) {
    // ignore logout errors
  }
  clearAuth();
  document.getElementById("l-email").value = "";
  document.getElementById("l-pwd").value = "";
  safeSetHash("login");
  showLogin();
}

function gotoDefault() {
  const routes = getAllowedRoutes();
  if (!routes.length) return;
  safeSetHash(routes[0]);
  renderRoute(routes[0]);
}

function renderRoute(id) {
  curTab = id;
  destroyCharts();
  document.querySelectorAll(".sb-item").forEach((item) => item.classList.remove("active"));
  const active = document.getElementById(`nav-${id}`);
  if (active) active.classList.add("active");
  document.getElementById("tb-title").textContent = ROUTE_TITLES[id] || id;

  const main = document.getElementById("main");
  main.innerHTML = "";
  const div = document.createElement("div");
  div.className = "pg";
  switch (id) {
    case "dashboard":
      div.innerHTML = pgDashboard();
      break;
    case "equipements":
      div.innerHTML = pgEquipements();
      break;
    case "utilisateurs":
      div.innerHTML = pgUtilisateurs();
      break;
    case "pannes_resp":
      div.innerHTML = pgPannesResp();
      break;
    case "interventions_resp":
      div.innerHTML = pgInterventionsResp();
      break;
    case "pannes_oper":
      div.innerHTML = pgPannesOper();
      break;
    case "interventions_tech":
      div.innerHTML = pgInterventionsTech();
      break;
    case "planning":
      div.innerHTML = pgPlanning();
      break;
    case "audit_logs":
      div.innerHTML = pgAuditLogs();
      break;
    default:
      div.innerHTML = `<div class="card" style="padding:24px">Section introuvable.</div>`;
  }
  main.appendChild(div);
  if (id === "dashboard") setTimeout(buildDashCharts, 80);
}

function go(id) {
  if (!CU) {
    showLogin();
    safeSetHash("login");
    return;
  }
  const allowed = getAllowedRoutes();
  if (!allowed.includes(id)) {
    toast("Accès non autorisé à cette section.", "warn");
    const fallback = allowed[0];
    if (fallback) {
      safeSetHash(fallback);
      renderRoute(fallback);
    }
    return;
  }
  safeSetHash(id);
  renderRoute(id);
}

function handleRouteChange(force = false) {
  if (IGNORE_HASH_CHANGE && !force) return;
  if (!CU) {
    showLogin();
    return;
  }
  const requested = getRequestedRoute();
  const allowed = getAllowedRoutes();
  const target = allowed.includes(requested) ? requested : allowed[0];
  if (!target) return;
  if (requested !== target) safeSetHash(target);
  renderRoute(target);
}

window.addEventListener("hashchange", () => handleRouteChange(false));

function mapAuditLog(item) {
  return {
    id: item.id,
    action: item.action,
    modelName: item.model_name,
    objectId: item.object_id,
    details: item.details || {},
    createdAt: item.created_at,
    userName: item.user_full_name || "Système",
    userEmail: item.user_email || "",
  };
}

async function loadData() {
  const [usersData, equipmentsData] = await Promise.all([
    apiFetch(API.users, { silent: true }),
    apiFetch(API.equipments, { silent: true }),
  ]);
  const incidentsPromise =
    ["admin", "responsable", "operateur"].includes(CU?.role)
      ? apiFetch(API.incidents, { silent: true })
      : Promise.resolve([]);
  const interventionsPromise =
    ["admin", "responsable", "technicien"].includes(CU?.role)
      ? apiFetch(API.interventions, { silent: true })
      : Promise.resolve([]);
  const auditPromise =
    CU?.role === "admin"
      ? apiFetch(API.auditLogs, { silent: true })
      : Promise.resolve([]);

  const [incidentsData, interventionsData, auditData = []] = await Promise.all([
    incidentsPromise,
    interventionsPromise,
    auditPromise,
  ]);
  DB.users = usersData.map(mapUser);
  DB.equipements = equipmentsData.map(mapEquipement);
  DB.pannes = incidentsData.map(mapPanne);
  DB.interventions = interventionsData.map(mapIntervention);
  DB.auditLogs = Array.isArray(auditData) ? auditData.map(mapAuditLog) : [];

  if (CU) CU = DB.users.find((user) => user.pk === CU.pk) || CU;
}

async function restoreSession() {
  try {
    beginLoading("Restauration de la session...");
    if (!TOKENS.access && TOKENS.refresh) {
      await refreshAccessToken();
    }
    const me = await apiFetch(API.me, { silent: true });
    CU = mapUser(me);
    await loadData();
    loginOK();
  } catch (error) {
    clearAuth();
    showLogin();
  } finally {
    endLoading();
  }
}

function validateEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

function ensureMinLength(value, length, label) {
  if (value.trim().length < length) {
    throw new Error(`${label} doit contenir au moins ${length} caractères.`);
  }
}

function confirmAction({ title, message, confirmLabel = "Confirmer", confirmClass = "btn-dang", onConfirm }) {
  PENDING_CONFIRM = onConfirm;
  openModal(`<div class="modal"><div class="mhd"><h3>${title}</h3><div class="mx" onclick="closeModal()">✕</div></div>
    <div class="mbd"><p style="line-height:1.6">${message}</p></div>
    <div class="mft">
      <button class="btn btn-ghost" onclick="closeModal()">Annuler</button>
      <button class="btn ${confirmClass}" onclick="runConfirmedAction()">${confirmLabel}</button>
    </div>
  </div>`);
}

async function runConfirmedAction() {
  const action = PENDING_CONFIRM;
  PENDING_CONFIRM = null;
  closeModal();
  if (action) await action();
}

function incidentHistoryForEquipment(equipmentId) {
  const rows = DB.pannes.filter((item) => item.equipementId === equipmentId).slice(0, 6);
  if (!rows.length) return `<div class="empty" style="padding:18px">Aucun historique pour cet équipement.</div>`;
  return `<div class="tbl-wrap"><table>
    <thead><tr><th>Code</th><th>Date</th><th>Statut</th><th>Criticité</th></tr></thead>
    <tbody>${rows.map((item) => `<tr><td><span class="chip">${item.id}</span></td><td>${fd(item.date)}</td><td>${bEtat(item.statut)}</td><td>${bCrit(item.criticite)}</td></tr>`).join("")}</tbody>
  </table></div>`;
}

function modalPanneDetail(index) {
  const item = DB.pannes[index];
  const eq = gEq(item.equipementId);
  const tech = gUs(item.technicienId);
  openModal(`<div class="modal wide"><div class="mhd"><h3>📋 Détail panne — ${eq.nom}</h3><div class="mx" onclick="closeModal()">✕</div></div>
    <div class="mbd">
      <div class="fr2" style="margin-bottom:14px">
        <div><div class="fl">Code</div><p style="font-weight:700;color:var(--navy)">${item.id}</p></div>
        <div><div class="fl">Technicien</div><p>${tech.nom}</p></div>
        <div><div class="fl">Criticité</div>${bCrit(item.criticite)}</div>
        <div><div class="fl">Priorité</div>${bCrit(item.priorite || "Normale")}</div>
        <div><div class="fl">Date</div><p>${fd(item.date)}</p></div>
        <div><div class="fl">Statut</div>${bEtat(item.statut)}</div>
      </div>
      <div class="fg"><div class="fl">Description</div><div style="background:var(--g50);border:1px solid var(--g200);border-radius:8px;padding:12px;font-size:14px">${item.description}</div></div>
      <div class="fg"><label class="fl">Modifier le statut</label><select class="fc" id="ps-${index}">${INCIDENT_STATUS_OPTIONS.map((status) => `<option${status === item.statut ? " selected" : ""}>${status}</option>`).join("")}</select></div>
      <div class="fg"><div class="fl">Historique des pannes de cet équipement</div>${incidentHistoryForEquipment(item.equipementId)}</div>
    </div>
    <div class="mft">
      <button class="btn btn-ghost" onclick="closeModal()">Fermer</button>
      <button class="btn btn-prim" onclick="updatePanneStatut(${index})">Enregistrer</button>
    </div>
  </div>`);
}

function planningData() {
  const rows = DB.interventions
    .filter((item) => item.prochaineMaintenance || item.statut === "En cours")
    .map((item) => {
      const nextDate = item.prochaineMaintenance || item.dateFin || item.dateDebut;
      const days = nextDate ? Math.ceil((new Date(nextDate) - new Date(getToday())) / (1000 * 60 * 60 * 24)) : null;
      const status = days === null ? "À planifier" : days < 0 ? "En retard" : days <= 30 ? "Bientôt" : "Planifiée";
      return {
        ...item,
        nextDate,
        planningStatus: status,
        daysRemaining: days,
      };
    })
    .sort((a, b) => (a.nextDate || "").localeCompare(b.nextDate || ""));
  return rows;
}

function planningBadge(value) {
  if (value === "En retard") return `<span class="badge b-red">${value}</span>`;
  if (value === "Bientôt") return `<span class="badge b-orange">${value}</span>`;
  if (value === "À planifier") return `<span class="badge b-yellow">${value}</span>`;
  return `<span class="badge b-blue">${value}</span>`;
}

function pgPlanning() {
  const rows = planningData();
  const overdue = rows.filter((item) => item.planningStatus === "En retard").length;
  const upcoming = rows.filter((item) => item.planningStatus === "Bientôt").length;
  const scheduled = rows.filter((item) => item.planningStatus === "Planifiée").length;
  return `
    <div class="s-title">
      <div><h2>Planning de maintenance</h2><p>${CU?.role === "responsable" ? "Planification des interventions et affectation des techniciens." : "Vision des maintenances à venir et des actions en retard."}</p></div>
      ${CU?.role === "responsable" ? `<button class="btn btn-prim" onclick="modalNewInterv()">＋ Planifier une intervention</button>` : ""}
    </div>
    <div class="kpi-mini-grid" style="margin-bottom:16px">
      <div class="kpi-mini"><div class="kpi-mini-icon" style="background:#fee2e2">⏰</div><div class="kpi-mini-data"><div class="kpi-mini-val">${overdue}</div><div class="kpi-mini-lbl">En retard</div></div></div>
      <div class="kpi-mini"><div class="kpi-mini-icon" style="background:#ffedd5">📅</div><div class="kpi-mini-data"><div class="kpi-mini-val">${upcoming}</div><div class="kpi-mini-lbl">Dans 30 jours</div></div></div>
      <div class="kpi-mini"><div class="kpi-mini-icon" style="background:#dbeafe">🧾</div><div class="kpi-mini-data"><div class="kpi-mini-val">${scheduled}</div><div class="kpi-mini-lbl">Planifiées</div></div></div>
      <div class="kpi-mini"><div class="kpi-mini-icon" style="background:#dcfce7">🔧</div><div class="kpi-mini-data"><div class="kpi-mini-val">${DB.interventions.filter((item) => item.type === "Préventive").length}</div><div class="kpi-mini-lbl">Préventives</div></div></div>
    </div>
    <div class="card"><div class="tbl-wrap"><table>
      <thead><tr><th>Code</th><th>Équipement</th><th>Technicien</th><th>Type</th><th>Prochaine date</th><th>Échéance</th><th>Statut</th></tr></thead>
      <tbody>${rows.length ? rows.map((item) => {
        const eq = gEq(item.equipementId);
        const tech = gUs(item.technicienId);
        return `<tr>
          <td><span class="chip">${item.id}</span></td>
          <td><strong>${eq.nom}</strong><div style="font-size:11px;color:var(--g400)">${eq.localisation}</div></td>
          <td>${tech.nom}</td>
          <td>${bCrit(item.type)}</td>
          <td>${fd(item.nextDate)}</td>
          <td>${item.daysRemaining === null ? "—" : item.daysRemaining < 0 ? `${Math.abs(item.daysRemaining)} j de retard` : `${item.daysRemaining} j`}</td>
          <td>${planningBadge(item.planningStatus)}</td>
        </tr>`;
      }).join("") : `<tr><td colspan="7" class="empty">Aucun planning disponible.</td></tr>`}
      </tbody>
    </table></div></div>`;
}

function pgAuditLogs() {
  return `
    <div class="s-title">
      <div><h2>Journal d'audit</h2><p>Traçabilité des actions applicatives.</p></div>
    </div>
    <div class="card"><div class="tbl-wrap"><table>
      <thead><tr><th>Date</th><th>Utilisateur</th><th>Action</th><th>Modèle</th><th>Objet</th><th>Détails</th></tr></thead>
      <tbody>${DB.auditLogs.length ? DB.auditLogs.map((item) => `
        <tr>
          <td style="font-size:12px">${fd(item.createdAt)} ${new Date(item.createdAt).toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" })}</td>
          <td>${item.userName}</td>
          <td><span class="badge b-blue">${item.action}</span></td>
          <td>${item.modelName}</td>
          <td>${item.objectId}</td>
          <td style="font-size:12px;color:var(--g500)">${JSON.stringify(item.details)}</td>
        </tr>`).join("") : `<tr><td colspan="6" class="empty">Aucun log disponible.</td></tr>`}
      </tbody>
    </table></div></div>`;
}

function validateEquipmentPayload(prefix) {
  const code = V(`${prefix}id`).trim();
  const name = V(`${prefix}nom`).trim();
  const type = V(`${prefix}type`).trim();
  const location = V(`${prefix}loc`).trim();
  if (!code) throw new Error("Le code équipement est obligatoire.");
  ensureMinLength(name, 3, "Le nom");
  ensureMinLength(type, 2, "Le type");
  ensureMinLength(location, 2, "La localisation");
  return {
    code,
    name,
    equipment_type: type,
    manufacturer: V(`${prefix}fab`).trim(),
    reference: V(`${prefix}ref`).trim(),
    location,
    criticality: V(`${prefix}crit`),
    status: V(`${prefix}etat`),
    purchase_date: V(`${prefix}date`) || null,
    description: "",
  };
}

async function addEquip() {
  try {
    const payload = validateEquipmentPayload("eq-");
    await apiFetch(API.equipments, { method: "POST", body: JSON.stringify(payload), loadingText: "Ajout de l'équipement..." });
    await loadData();
    closeModal();
    go(curTab);
    toast("Équipement ajouté.");
  } catch (error) {
    toast(error.message, "err");
  }
}

async function saveEquip(index) {
  try {
    const payload = validateEquipmentPayload("eeq-");
    await apiFetch(`${API.equipments}${DB.equipements[index].pk}/`, { method: "PUT", body: JSON.stringify(payload), loadingText: "Mise à jour de l'équipement..." });
    await loadData();
    closeModal();
    go(curTab);
    toast("Équipement modifié.");
  } catch (error) {
    toast(error.message, "err");
  }
}

async function delEquip(index) {
  const item = DB.equipements[index];
  confirmAction({
    title: "Supprimer l'équipement",
    message: `Voulez-vous vraiment supprimer <strong>${item.nom}</strong> ?`,
    confirmLabel: "Supprimer",
    onConfirm: async () => {
      try {
        await apiFetch(`${API.equipments}${item.pk}/`, { method: "DELETE", loadingText: "Suppression..." });
        await loadData();
        go(curTab);
        toast("Équipement supprimé.");
      } catch (error) {
        toast(error.message, "err");
      }
    },
  });
}

function validateUserPayload(prefix, passwordRequired = false) {
  const fullName = V(`${prefix}nom`).trim();
  const email = V(`${prefix}email`).trim().toLowerCase();
  const password = V(`${prefix}pwd`).trim();
  ensureMinLength(fullName, 3, "Le nom complet");
  if (!validateEmail(email)) throw new Error("Adresse email invalide.");
  if (passwordRequired && password.length < 6) throw new Error("Le mot de passe doit contenir au moins 6 caractères.");
  const payload = {
    full_name: fullName,
    email,
    role: V(`${prefix}role`),
    is_active: V(`${prefix}statut`) === "actif",
  };
  if (password) payload.password = password;
  return payload;
}

async function addUser() {
  try {
    const payload = validateUserPayload("u-", true);
    await apiFetch(API.users, { method: "POST", body: JSON.stringify(payload), loadingText: "Création de l'utilisateur..." });
    await loadData();
    closeModal();
    go(curTab);
    toast("Utilisateur ajouté.");
  } catch (error) {
    toast(error.message, "err");
  }
}

async function saveUser(index) {
  try {
    const payload = validateUserPayload("eu-", false);
    await apiFetch(`${API.users}${DB.users[index].pk}/`, { method: "PUT", body: JSON.stringify(payload), loadingText: "Mise à jour de l'utilisateur..." });
    await loadData();
    closeModal();
    go(curTab);
    toast("Utilisateur modifié.");
  } catch (error) {
    toast(error.message, "err");
  }
}

async function delUser(index) {
  const item = DB.users[index];
  confirmAction({
    title: "Supprimer l'utilisateur",
    message: `Voulez-vous vraiment supprimer <strong>${item.nom}</strong> ?`,
    confirmLabel: "Supprimer",
    onConfirm: async () => {
      try {
        await apiFetch(`${API.users}${item.pk}/`, { method: "DELETE", loadingText: "Suppression..." });
        await loadData();
        go(curTab);
        toast("Utilisateur supprimé.");
      } catch (error) {
        toast(error.message, "err");
      }
    },
  });
}

async function signalerPanne() {
  try {
    const description = V("sp-desc").trim();
    const title = V("sp-title").trim() || description.slice(0, 40) || "Nouvelle panne";
    ensureMinLength(title, 4, "Le titre");
    ensureMinLength(description, 8, "La description");
    await apiFetch(API.incidents, {
      method: "POST",
      body: JSON.stringify({
        equipment: Number(V("sp-eq")),
        technician: Number(V("sp-tech")),
        title,
        description,
        criticality: V("sp-crit"),
        priority: V("sp-prio"),
        status: "En attente",
        reported_at: `${V("sp-date")}T08:00:00+01:00`,
      }),
      loadingText: "Signalement de la panne...",
    });
    await loadData();
    closeModal();
    go(curTab);
    toast("Panne signalée.");
  } catch (error) {
    toast(error.message, "err");
  }
}

async function addInterv() {
  try {
    if (!V("ni-tech")) throw new Error("Aucun technicien actif disponible.");
    if (!V("ni-eq")) throw new Error("Aucun équipement disponible.");
    const description = V("ni-desc").trim();
    ensureMinLength(description, 8, "La description");
    const startDate = V("ni-debut") || getToday();
    const endDate = V("ni-fin") || null;
    if (endDate && endDate < startDate) throw new Error("La date de fin doit être postérieure à la date de début.");
    await apiFetch(API.interventions, {
      method: "POST",
      body: JSON.stringify({
        incident: V("ni-inc") ? Number(V("ni-inc")) : null,
        technician: Number(V("ni-tech")),
        equipment: Number(V("ni-eq")),
        description,
        priority: V("ni-crit"),
        intervention_type: V("ni-type"),
        status: "En cours",
        start_date: startDate,
        end_date: endDate,
        report: "",
        next_maintenance: null,
        equipment_status_after: "En maintenance",
      }),
      loadingText: "Création de l'intervention...",
    });
    await loadData();
    closeModal();
    go(curTab);
    toast("Intervention créée.");
  } catch (error) {
    toast(error.message, "err");
  }
}

async function saveRapport(index, mode) {
  const item = DB.interventions[index];
  try {
    const report = V("rap-txt").trim();
    const statusValue = mode === "resp" ? "Terminée" : V("rap-stat");
    if (statusValue === "Terminée") ensureMinLength(report, 5, "Le rapport");
    await apiFetch(`${API.interventions}${item.pk}/`, {
      method: "PATCH",
      body: JSON.stringify({
        status: statusValue,
        report,
        end_date: V("rap-end") || (statusValue === "Terminée" ? getToday() : null),
        next_maintenance: V("rap-next") || null,
        equipment_status_after: V("rap-etat"),
      }),
      loadingText: "Enregistrement du rapport...",
    });
    await loadData();
    closeModal();
    go(curTab);
    toast(mode === "resp" ? "Rapport validé." : "Rapport enregistré.");
  } catch (error) {
    toast(error.message, "err");
  }
}

async function reclamer(index) {
  const item = DB.interventions[index];
  try {
    await apiFetch(`${API.interventions}${item.pk}/`, {
      method: "PATCH",
      body: JSON.stringify({
        status: "En cours",
        report: V("rap-txt").trim() || item.rapport || "Intervention réouverte pour complément.",
        equipment_status_after: V("rap-etat"),
        next_maintenance: V("rap-next") || null,
        end_date: null,
      }),
      loadingText: "Réouverture de l'intervention...",
    });
    await loadData();
    closeModal();
    go(curTab);
    toast("Intervention réouverte.");
  } catch (error) {
    toast(error.message, "err");
  }
}

function resizeCanvas(canvas) {
  const ratio = window.devicePixelRatio || 1;
  const width = canvas.clientWidth || canvas.width || 300;
  const height = canvas.clientHeight || canvas.height || 160;
  canvas.width = Math.floor(width * ratio);
  canvas.height = Math.floor(height * ratio);
  const ctx = canvas.getContext("2d");
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  return { ctx, width, height };
}

function drawPolyline(canvasId, data, color, fill = false) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const { ctx, width, height } = resizeCanvas(canvas);
  ctx.clearRect(0, 0, width, height);
  const max = Math.max(...data, 1);
  const min = Math.min(...data, 0);
  const range = max - min || 1;
  const stepX = width / Math.max(data.length - 1, 1);
  ctx.beginPath();
  data.forEach((value, index) => {
    const x = index * stepX;
    const y = height - ((value - min) / range) * (height - 10) - 5;
    if (index === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  if (fill) {
    ctx.lineTo(width, height);
    ctx.lineTo(0, height);
    ctx.closePath();
    ctx.fillStyle = `${color}18`;
    ctx.fill();
  }
  ctx.beginPath();
  data.forEach((value, index) => {
    const x = index * stepX;
    const y = height - ((value - min) / range) * (height - 10) - 5;
    if (index === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.strokeStyle = color;
  ctx.lineWidth = 2;
  ctx.stroke();
}

function drawBars(canvasId, values, colors, horizontal = false) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const { ctx, width, height } = resizeCanvas(canvas);
  ctx.clearRect(0, 0, width, height);
  const max = Math.max(...values, 1);
  if (horizontal) {
    const rowH = height / values.length;
    values.forEach((value, index) => {
      const barW = (value / max) * (width - 20);
      ctx.fillStyle = colors[index % colors.length];
      ctx.fillRect(10, index * rowH + 8, barW, rowH - 14);
    });
  } else {
    const barW = width / Math.max(values.length * 1.6, 1);
    values.forEach((value, index) => {
      const x = 20 + index * barW * 1.4;
      const barH = (value / max) * (height - 20);
      ctx.fillStyle = colors[index % colors.length];
      ctx.fillRect(x, height - barH - 10, barW, barH);
    });
  }
}

function drawDoughnut(canvasId, values, colors) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const { ctx, width, height } = resizeCanvas(canvas);
  ctx.clearRect(0, 0, width, height);
  const total = values.reduce((sum, value) => sum + value, 0) || 1;
  const cx = width / 2;
  const cy = height / 2;
  const radius = Math.min(width, height) / 2 - 8;
  let start = -Math.PI / 2;
  values.forEach((value, index) => {
    const angle = (value / total) * Math.PI * 2;
    ctx.beginPath();
    ctx.strokeStyle = colors[index % colors.length];
    ctx.lineWidth = 22;
    ctx.arc(cx, cy, radius - 18, start, start + angle);
    ctx.stroke();
    start += angle;
  });
}

function buildSparkline(id, data, color) {
  if (window.Chart) {
    const canvas = document.getElementById(id);
    if (!canvas) return;
    const chart = new Chart(canvas, {
      type: "line",
      data: { labels: data.map((_, index) => index + 1), datasets: [{ data, borderColor: color, borderWidth: 1.5, fill: true, backgroundColor: `${color}18`, tension: 0.4, pointRadius: 0 }] },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false }, tooltip: { enabled: false } }, scales: { x: { display: false }, y: { display: false } } },
    });
    sparkCharts.push(chart);
    return;
  }
  drawPolyline(id, data, color, true);
}

function buildDashCharts() {
  const scenario = buildDashboardScenario();
  const categoryLabels = scenario.categories.map((item) => item.label);
  const categoryValues = scenario.categories.map((item) => item.value);
  const mttrLabels = scenario.mttrEquipment.map((item) => item.label);
  const mttrValues = scenario.mttrEquipment.map((item) => item.value);

  buildSparkline("spark-dispo", scenario.availabilitySeries, "#2563eb");
  buildSparkline("spark-mtbf", scenario.mtbfSeries, "#f97316");
  buildSparkline("spark-mttr", scenario.mttrSeries, "#16a34a");

  if (!window.Chart) {
    drawPolyline("ch-disp", scenario.availabilitySeries, "#2563eb", true);
    drawBars("ch-mtbf", scenario.mtbfSeries, ["#2563eb", "#2563eb", "#2563eb", "#2563eb", "#2563eb", "#2563eb"]);
    drawBars("ch-category", categoryValues, ["#2563eb", "#4d8cf6", "#7cb0ff", "#a9cbff", "#d9e8ff"], true);
    drawBars("ch-pareto", categoryValues, ["#2563eb", "#4d8cf6", "#7cb0ff", "#a9cbff", "#d9e8ff"]);
    drawBars("ch-mttr", mttrValues, ["#2563eb", "#4d8cf6", "#7cb0ff", "#a9cbff"], true);
    return;
  }

  const sharedLegend = {
    position: "bottom",
    labels: { usePointStyle: true, boxWidth: 8, padding: 14, font: { size: 10 } },
  };

  const dispCtx = document.getElementById("ch-disp");
  if (dispCtx) {
    dispChart = new Chart(dispCtx, {
      type: "line",
      data: {
        labels: scenario.months,
        datasets: [
          {
            label: "Disponibilité (%)",
            data: scenario.availabilitySeries,
            borderColor: "#2563eb",
            backgroundColor: "rgba(37,99,235,.08)",
            fill: true,
            tension: 0.35,
            pointRadius: 3,
            pointBackgroundColor: "#2563eb",
          },
          {
            label: "Objectif (%)",
            data: scenario.objectiveSeries,
            borderColor: "#94a3b8",
            borderDash: [5, 4],
            fill: false,
            tension: 0.2,
            pointRadius: 0,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: sharedLegend },
        scales: {
          y: { min: 0, max: 100, grid: { color: "rgba(148,163,184,.14)" }, ticks: { font: { size: 10 } } },
          x: { grid: { display: false }, ticks: { font: { size: 10 } } },
        },
      },
    });
  }

  const mtbfCtx = document.getElementById("ch-mtbf");
  if (mtbfCtx) {
    mtbfChart = new Chart(mtbfCtx, {
      data: {
        labels: scenario.months,
        datasets: [
          {
            type: "bar",
            label: "MTBF (h)",
            data: scenario.mtbfSeries,
            backgroundColor: "rgba(37,99,235,.82)",
            borderRadius: 5,
            yAxisID: "y",
          },
          {
            type: "line",
            label: "MTTR (h)",
            data: scenario.mttrSeries,
            borderColor: "#f97316",
            backgroundColor: "#f97316",
            tension: 0.32,
            pointRadius: 3,
            pointBackgroundColor: "#f97316",
            yAxisID: "y2",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: sharedLegend },
        scales: {
          y: { beginAtZero: true, grid: { color: "rgba(148,163,184,.14)" }, ticks: { font: { size: 10 } } },
          y2: { beginAtZero: true, position: "right", grid: { display: false }, ticks: { font: { size: 10 } } },
          x: { grid: { display: false }, ticks: { font: { size: 10 } } },
        },
      },
    });
  }

  const categoryCtx = document.getElementById("ch-category");
  if (categoryCtx) {
    categoryChart = new Chart(categoryCtx, {
      type: "bar",
      data: {
        labels: categoryLabels,
        datasets: [{
          label: "Nombre de pannes",
          data: categoryValues,
          backgroundColor: ["#2563eb", "#4d8cf6", "#7cb0ff", "#a9cbff", "#d9e8ff"],
          borderRadius: 5,
        }],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { beginAtZero: true, grid: { color: "rgba(148,163,184,.14)" }, ticks: { font: { size: 10 } } },
          y: { grid: { display: false }, ticks: { font: { size: 10 } } },
        },
      },
    });
  }

  const paretoCtx = document.getElementById("ch-pareto");
  if (paretoCtx) {
    paretoChart = new Chart(paretoCtx, {
      data: {
        labels: categoryLabels,
        datasets: [
          {
            type: "bar",
            label: "Nombre de pannes",
            data: categoryValues,
            backgroundColor: "rgba(37,99,235,.82)",
            borderRadius: 5,
            yAxisID: "y",
          },
          {
            type: "line",
            label: "Cumul %",
            data: scenario.paretoCumulative,
            borderColor: "#f97316",
            backgroundColor: "#f97316",
            pointRadius: 3,
            pointBackgroundColor: "#f97316",
            tension: 0.24,
            yAxisID: "y2",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: sharedLegend },
        scales: {
          y: { beginAtZero: true, grid: { color: "rgba(148,163,184,.14)" }, ticks: { font: { size: 10 } } },
          y2: { beginAtZero: true, position: "right", max: 100, grid: { display: false }, ticks: { font: { size: 10 }, callback: (value) => `${value}%` } },
          x: { grid: { display: false }, ticks: { font: { size: 10 } } },
        },
      },
    });
  }

  const mttrCtx = document.getElementById("ch-mttr");
  if (mttrCtx) {
    mttrChart = new Chart(mttrCtx, {
      type: "bar",
      data: {
        labels: mttrLabels,
        datasets: [{
          label: "MTTR (h)",
          data: mttrValues,
          backgroundColor: ["#2563eb", "#4d8cf6", "#7cb0ff", "#a9cbff"],
          borderRadius: 5,
        }],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { beginAtZero: true, grid: { color: "rgba(148,163,184,.14)" }, ticks: { font: { size: 10 } } },
          y: { grid: { display: false }, ticks: { font: { size: 10 } } },
        },
      },
    });
  }
}
