const state = {
  rooms: [],
  reservations: [],
};

const el = {
  health: document.querySelector("#healthStatus"),
  healthSummary: document.querySelector("#healthSummary"),
  refreshAll: document.querySelector("#refreshAll"),
  roomForm: document.querySelector("#roomForm"),
  roomName: document.querySelector("#roomName"),
  roomCapacity: document.querySelector("#roomCapacity"),
  resetRoom: document.querySelector("#resetRoom"),
  roomsTable: document.querySelector("#roomsTable"),
  roomCount: document.querySelector("#roomCount"),
  roomSummary: document.querySelector("#roomSummary"),
  lookupRoomId: document.querySelector("#lookupRoomId"),
  lookupRoom: document.querySelector("#lookupRoom"),
  roomDetail: document.querySelector("#roomDetail"),
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

function setRoomCapacityFromName() {
  const selected = el.roomName.selectedOptions[0];
  const capacity = selected?.dataset.capacity || "";
  el.roomCapacity.value = capacity;
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

async function loadRooms() {
  const data = await api("/api/rooms");
  state.rooms = data.items || [];
  el.roomCount.textContent = `${data.count || 0}개`;
  el.roomSummary.textContent = `등록된 룸 ${data.count || 0}개`;
  renderRooms();
}

async function lookupRoom() {
  const id = el.lookupRoomId.value;
  if (!id) {
    el.roomDetail.textContent = "조회할 룸 ID를 입력하세요.";
    return;
  }
  const room = await api(`/api/rooms/${id}`);
  el.roomDetail.textContent = `${room.name} / 수용 ${room.capacity}명 / 장비 ${room.equipment || "없음"}`;
}

function renderRooms() {
  el.roomsTable.replaceChildren();
  state.rooms.forEach((room) => {
    const row = document.createElement("tr");
    ["id", "name", "capacity", "equipment"].forEach((key) => row.appendChild(td(room[key])));

    const actions = document.createElement("td");
    actions.className = "row-actions";
    actions.appendChild(actionButton("수정", "secondary", () => {
      el.roomForm.elements.id.value = room.id;
      el.roomForm.elements.name.value = room.name || "";
      el.roomForm.elements.capacity.value = room.capacity || "";
      el.roomForm.elements.equipment.value = room.equipment || "";
      el.roomForm.elements.name.focus();
    }));
    actions.appendChild(actionButton("삭제", "danger", async () => {
      if (!window.confirm(`${room.name} 룸을 삭제할까요?`)) return;
      await api(`/api/rooms/${room.id}`, { method: "DELETE" });
      showToast("세미나룸이 삭제되었습니다.");
      await Promise.all([loadRooms(), loadReservations()]);
    }));
    row.appendChild(actions);
    el.roomsTable.appendChild(row);
  });
}

async function submitRoom(event) {
  event.preventDefault();
  const data = normalizePayload(formData(el.roomForm), ["capacity"]);
  const fixedCapacity = Number(el.roomName.selectedOptions[0]?.dataset.capacity || 0);
  if (fixedCapacity && data.capacity !== fixedCapacity) {
    showToast("수용 인원은 룸 이름에 맞게 고정됩니다.");
    el.roomCapacity.value = String(fixedCapacity);
    return;
  }
  const id = data.id;
  delete data.id;
  await api(id ? `/api/rooms/${id}` : "/api/rooms", {
    method: id ? "PUT" : "POST",
    body: JSON.stringify(data),
  });
  el.roomForm.reset();
  showToast(id ? "세미나룸이 수정되었습니다." : "세미나룸이 생성되었습니다.");
  await loadRooms();
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
    await Promise.all([checkHealth(), loadRooms(), loadReservations()]);
  } catch (error) {
    showToast(error.message);
  }
}

el.refreshAll.addEventListener("click", refreshAll);
el.roomName.addEventListener("change", setRoomCapacityFromName);
el.roomForm.addEventListener("submit", (event) => submitRoom(event).catch((error) => showToast(error.message)));
el.resetRoom.addEventListener("click", () => {
  el.roomForm.reset();
  el.roomCapacity.value = "";
});
el.lookupRoom.addEventListener("click", () => lookupRoom().catch((error) => {
  el.roomDetail.textContent = "해당 룸을 찾을 수 없습니다.";
  showToast(error.message);
}));
el.reservationForm.addEventListener("submit", (event) => submitReservation(event).catch((error) => showToast(error.message)));
el.resetReservation.addEventListener("click", () => el.reservationForm.reset());
el.applyFilters.addEventListener("click", () => loadReservations().catch((error) => showToast(error.message)));

refreshAll();
