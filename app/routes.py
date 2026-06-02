import datetime
from flask import Blueprint, jsonify, request, abort, render_template
from app.db import get_db

api_bp = Blueprint('api', __name__)

ROOM_FIELDS = [
    {"name": "id", "label": "ID", "type": "number", "readonly": True},
    {"name": "name", "label": "룸 이름", "type": "text", "required": True},
    {"name": "capacity", "label": "수용 인원", "type": "number", "required": True},
    {"name": "equipment", "label": "장비", "type": "text"},
]

RESERVATION_FIELDS = [
    {"name": "id", "label": "ID", "type": "number", "readonly": True},
    {"name": "room_id", "label": "룸 ID", "type": "number", "required": True},
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
        api_spec={
            "rooms": ["GET /api/rooms", "POST /api/rooms", "PUT /api/rooms/<id>", "DELETE /api/rooms/<id>"],
            "reservations": ["GET /api/reservations", "POST /api/reservations", "DELETE /api/reservations/<id>"],
            "health": "GET /health",
        },
    )

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
    cursor.execute("SELECT * FROM rooms")
    rooms = [serialize_row(row) for row in cursor.fetchall()]
    return jsonify({"items": rooms, "count": len(rooms)}), 200

@api_bp.route('/api/rooms/<int:room_id>', methods=['GET'])
def get_room(room_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM rooms WHERE id = ?", (room_id,))
    room = cursor.fetchone()
    if not room:
        abort(404, description="Room not found")
    return jsonify(serialize_row(room)), 200

@api_bp.route('/api/rooms', methods=['POST'])
def create_room():
    data = request.get_json() or {}
    name = data.get('name')
    capacity = data.get('capacity')
    equipment = data.get('equipment')

    if not name or capacity is None:
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO rooms (name, capacity, equipment) VALUES (?, ?, ?)",
        (name, capacity, equipment)
    )
    return jsonify({"id": cursor.lastrowid, "message": "created"}), 201

@api_bp.route('/api/rooms/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    data = request.get_json() or {}
    name = data.get('name')
    capacity = data.get('capacity')
    equipment = data.get('equipment')

    if not name or capacity is None:
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE rooms SET name = ?, capacity = ?, equipment = ? WHERE id = ?",
        (name, capacity, equipment, room_id)
    )
    if cursor.rowcount == 0:
        abort(404, description="Room not found")
    return jsonify({"id": room_id, "message": "updated"}), 200

@api_bp.route('/api/rooms/<int:room_id>', methods=['DELETE'])
def delete_room(room_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM rooms WHERE id = ?", (room_id,))
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
    
    # 외래키 참조 방지를 위한 방어 코드 (룸이 실제로 존재하는지 점검)
    cursor.execute("SELECT id FROM rooms WHERE id = ?", (data['room_id'],))
    if not cursor.fetchone():
        return jsonify({"error": "Referenced room does not exist"}), 400

    cursor.execute(
        """INSERT INTO reservations 
           (room_id, user_name, user_email, date, start_time, end_time, purpose) 
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (data['room_id'], data['user_name'], data['user_email'], 
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
