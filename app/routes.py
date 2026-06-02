import datetime
from flask import Blueprint, jsonify, request, abort, render_template
from app.catalog import ROOM_CATALOG, ROOM_CAPACITY_BY_NAME, get_catalog_room, get_catalog_room_by_number
from app.db import get_db

api_bp = Blueprint('api', __name__)

ROOM_FIELDS = [
    {"name": "id", "label": "ID", "type": "number", "readonly": True},
    {"name": "name", "label": "룸 이름", "type": "select", "required": True},
    {"name": "capacity", "label": "수용 인원", "type": "number", "readonly": True},
    {"name": "equipment", "label": "장비", "type": "text"},
]

RESERVATION_FIELDS = [
    {"name": "id", "label": "ID", "type": "number", "readonly": True},
    {"name": "room_id", "label": "룸", "type": "select", "required": True},
    {"name": "user_name", "label": "예약자", "type": "text", "required": True},
    {"name": "user_email", "label": "이메일", "type": "email", "required": True},
    {"name": "date", "label": "날짜", "type": "date", "required": True},
    {"name": "start_time", "label": "시작", "type": "time", "required": True},
    {"name": "end_time", "label": "종료", "type": "time", "required": True},
    {"name": "purpose", "label": "목적", "type": "text"},
]


@api_bp.route('/', methods=['GET'])
def index():
    return render_template(
        'index.html',
        room_fields=ROOM_FIELDS,
        reservation_fields=RESERVATION_FIELDS,
        room_catalog=ROOM_CATALOG,
    )


def capacity_matches_request(data, fixed_capacity):
    if data.get('capacity') is None:
        return True
    try:
        return int(data.get('capacity')) == fixed_capacity
    except (TypeError, ValueError):
        return False


def catalog_name_params():
    names = list(ROOM_CAPACITY_BY_NAME.keys())
    placeholders = ", ".join(["?"] * len(names))
    return names, placeholders


def serialize_room(row):
    row = serialize_row(row)
    # DB의 id(방 번호)를 프론트엔드가 요구하는 형식에 맞게 매핑
    row["room_number"] = row.get("id")
    row["db_id"] = row.get("id")
    return row

# MariaDB 데이터 타입(Date, Timedelta)을 JSON 직렬화 가능한 형태로 변환하는 헬퍼 함수
def serialize_row(row):
    if not row:
        return row
    for k, v in row.items():
        if isinstance(v, (datetime.date, datetime.datetime)):
            row[k] = v.isoformat()
        elif isinstance(v, datetime.timedelta):
            total_seconds = int(v.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            row[k] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return row
# 5.3 헬스체크
@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200
# 5.1 세미나룸 CRUD
@api_bp.route('/api/rooms', methods=['GET'])
def get_rooms():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    names, placeholders = catalog_name_params()
    # 에러 원인이던 room_number를 제거하고 지시서 스키마대로 id를 조회 및 정렬합니다.
    cursor.execute(
        f"""SELECT id, name, capacity, equipment, created_at, updated_at
            FROM rooms
            WHERE name IN ({placeholders})
            ORDER BY id ASC""",
        tuple(names),
    )
    rooms = [serialize_room(row) for row in cursor.fetchall()]
    return jsonify({"items": rooms, "count": len(rooms)}), 200

@api_bp.route('/api/rooms/<int:room_id>', methods=['GET'])
def get_room(room_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    # room_number 대신 id로 조회합니다.
    cursor.execute(
        "SELECT id, name, capacity, equipment, created_at, updated_at FROM rooms WHERE id = ?",
        (room_id,),
    )
    room = cursor.fetchone()
    if not room or not get_catalog_room(room["name"]):
        abort(404, description="Room not found")
    return jsonify(serialize_room(room)), 200

@api_bp.route('/api/rooms', methods=['POST'])
def create_room():
    data = request.get_json() or {}
    catalog_room = get_catalog_room(data.get('name'))
    if not catalog_room:
        return jsonify({"error": "Room name must be selected from the fixed room catalog"}), 400

    name = catalog_room["name"]
    room_number = catalog_room["number"] # 카탈로그 고유 번호 (예: 101)
    capacity = catalog_room["capacity"]
    equipment = data.get('equipment')

    if not capacity_matches_request(data, capacity):
        return jsonify({"error": "Capacity is fixed by room name"}), 400

    conn = get_db()
    cursor = conn.cursor()
    # 이미 등록된 방인지 id(배정 번호) 또는 이름으로 중복 체크합니다.
    cursor.execute("SELECT id FROM rooms WHERE name = ? OR id = ?", (name, room_number))
    if cursor.fetchone():
        return jsonify({"error": "Room already exists in catalog"}), 409

    # 지시서의 테이블 id 컬럼에 카탈로그 방 번호를 명시적으로 삽입합니다.
    cursor.execute(
        "INSERT INTO rooms (id, name, capacity, equipment) VALUES (?, ?, ?, ?)",
        (room_number, name, capacity, equipment)
    )
    return jsonify({"id": room_number, "message": "created"}), 201

@api_bp.route('/api/rooms/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    data = request.get_json() or {}
    catalog_room = get_catalog_room(data.get('name'))
    if not catalog_room:
        return jsonify({"error": "Room name must be selected from the fixed room catalog"}), 400

    name = catalog_room["name"]
    room_number = catalog_room["number"]
    capacity = catalog_room["capacity"]
    equipment = data.get('equipment')

    if not capacity_matches_request(data, capacity):
        return jsonify({"error": "Capacity is fixed by room name"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM rooms WHERE room_number = ?", (room_id,))
    if not cursor.fetchone():
        abort(404, description="Room not found")
    cursor.execute(
        "UPDATE rooms SET id = ?, name = ?, capacity = ?, equipment = ? WHERE id = ?",
        (room_number, name, capacity, equipment, room_id)
    )
    return jsonify({"id": room_id, "message": "updated"}), 200

@api_bp.route('/api/rooms/<int:room_id>', methods=['DELETE'])
def delete_room(room_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM rooms WHERE room_number = ?", (room_id,))

    if cursor.rowcount == 0:
        abort(404, description="Room not found")
    return jsonify({"id": room_id, "message": "deleted"}), 200

# 5.2 예약 관리 CRUD
@api_bp.route('/api/reservations', methods=['GET'])
def get_reservations():
    room_id = request.args.get('room_id')
    date = request.args.get('date')

    query = "SELECT * FROM reservations WHERE 1=1"
    params = []

    if room_id:
        query += " AND room_id = ?"
        params.append(room_id)
    if date:
        query += " AND date = ?"
        params.append(date)

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, tuple(params))
    reservations = [serialize_row(row) for row in cursor.fetchall()]
    return jsonify({"items": reservations, "count": len(reservations)}), 200

@api_bp.route('/api/reservations', methods=['POST'])
def create_reservation():
    data = request.get_json() or {}
    required_fields = ['room_id', 'user_name', 'user_email', 'date', 'start_time', 'end_time']

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db()
    cursor = conn.cursor()

    catalog_room = get_catalog_room_by_number(data['room_id'])
    if not catalog_room:
        return jsonify({"error": "Room ID must be selected from the fixed room catalog"}), 400

    # 외래키 참조 점검 시 rooms 테이블의 id 컬럼을 대조합니다.
    cursor.execute("SELECT id FROM rooms WHERE id = ?", (catalog_room["number"],))
    if not cursor.fetchone():
        return jsonify({"error": "Referenced room does not exist"}), 400

    cursor.execute(
        """INSERT INTO reservations
           (room_id, user_name, user_email, date, start_time, end_time, purpose)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (catalog_room["number"], data['user_name'], data['user_email'],
         data['date'], data['start_time'], data['end_time'], data.get('purpose'))
    )
    return jsonify({"id": cursor.lastrowid, "message": "reserved"}), 201

@api_bp.route('/api/reservations/<int:res_id>', methods=['DELETE'])
def delete_reservation(res_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reservations WHERE id = ?", (res_id,))
    if cursor.rowcount == 0:
        abort(404, description="Reservation not found")
    return jsonify({"id": res_id, "message": "cancelled"}), 200
