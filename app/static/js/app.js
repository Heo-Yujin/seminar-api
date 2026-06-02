const state = {
  reservations: [],
};

const el = {
  health: document.querySelector("#healthStatus"),
  healthSummary: document.querySelector("#healthSummary"),
  refreshAll: document.querySelector("#refreshAll"),
  reservationForm: document.querySelector("#reservationForm"),
  resetReservation: document.querySelector("#resetReservation"),
  reservationsTable: document.querySelector("#reservationsTable"),
  reservationCount: document.querySelector("#reservationCount"),
  reservationSummary: document.querySelector("#reservationSummary"),
  filterRoomId: document.querySelector("#filterRoomId"),
  filterDate: document.querySelector("#filterDate"),
  applyFilters: document.querySelector("#applyFilters"),
  toast: document.querySelector("#toast"),
};

function showToast(message) {
  el.toast.textContent = message;
  el.toast.classList.add("show");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => el.toast.classList.remove("show"), 2400);
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || data.message || data.description || "요청 처리에 실패했습니다.");
  }
  return data;
}

function formData(form) {
  return Object.fromEntries(new FormData(form).entries());
}

function normalizePayload(data, numberFields = []) {
  const payload = {};
  Object.entries(data).forEach(([key, value]) => {
    if (value === "") return;
    payload[key] = numberFields.includes(key) ? Number(value) : value;
  });
  return payload;
}

function td(value) {
  const cell = document.createElement("td");
  cell.textContent = value ?? "";
  return cell;
}

function actionButton(label, className, onClick) {
  const button = document.createElement("button");
  button.type = "button";
  button.textContent = label;
  button.className = className;
  button.addEventListener("click", onClick);
  return button;
}

async function checkHealth() {
  try {
    const data = await api("/health");
    el.health.textContent = `health: ${data.status}`;
    el.healthSummary.textContent = "정상";
    el.health.className = "status-pill ok";
  } catch (error) {
    el.health.textContent = "health: error";
    el.healthSummary.textContent = "오류";
    el.health.className = "status-pill error";
  }
}

function reservationQuery() {
  const params = new URLSearchParams();
  if (el.filterRoomId.value) params.set("room_id", el.filterRoomId.value);
  if (el.filterDate.value) params.set("date", el.filterDate.value);
  const query = params.toString();
  return query ? `?${query}` : "";
}

async function loadReservations() {
  const data = await api(`/api/reservations${reservationQuery()}`);
  state.reservations = data.items || [];
  el.reservationCount.textContent = `${data.count || 0}개`;
  el.reservationSummary.textContent = `조회된 예약 ${data.count || 0}개`;
  renderReservations();
}

function renderReservations() {
  el.reservationsTable.replaceChildren();
  state.reservations.forEach((reservation) => {
    const row = document.createElement("tr");
    ["id", "room_id", "user_name", "user_email", "date", "start_time", "end_time", "purpose"].forEach((key) => {
      row.appendChild(td(reservation[key]));
    });

    const actions = document.createElement("td");
    actions.className = "row-actions";
    actions.appendChild(actionButton("취소", "danger", async () => {
      if (!window.confirm(`${reservation.user_name}님의 예약을 취소할까요?`)) return;
      await api(`/api/reservations/${reservation.id}`, { method: "DELETE" });
      showToast("예약이 취소되었습니다.");
      await loadReservations();
    }));
    row.appendChild(actions);
    el.reservationsTable.appendChild(row);
  });
}

async function submitReservation(event) {
  event.preventDefault();
  const data = normalizePayload(formData(el.reservationForm), ["room_id"]);
  await api("/api/reservations", {
    method: "POST",
    body: JSON.stringify(data),
  });
  el.reservationForm.reset();
  showToast("예약이 등록되었습니다.");
  await loadReservations();
}

async function refreshAll() {
  try {
    await Promise.all([checkHealth(), loadReservations()]);
  } catch (error) {
    showToast(error.message);
  }
}

el.refreshAll.addEventListener("click", refreshAll);
el.reservationForm.addEventListener("submit", (event) => submitReservation(event).catch((error) => showToast(error.message)));
el.resetReservation.addEventListener("click", () => el.reservationForm.reset());
el.applyFilters.addEventListener("click", () => loadReservations().catch((error) => showToast(error.message)));

refreshAll();
