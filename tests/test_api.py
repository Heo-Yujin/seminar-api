# tests/test_api.py
import pytest
from unittest.mock import patch, MagicMock
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# 1. 헬스체크 테스트
def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}

def test_index_page_renders(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Seminar Room Reservation" in response.data
    assert b'<select name="name"' not in response.data
    assert b'<select name="room_id"' in response.data
    assert b'id="roomsTable"' not in response.data
    assert b'id="roomForm"' not in response.data

# 2. 세미나룸 전체 조회 테스트 (Mocking DB)
@patch('app.routes.get_db')
def test_get_rooms(mock_get_db, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        {"id": 1, "name": "Room A", "capacity": 10, "equipment": "Projector"}
    ]
    mock_conn.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_conn

    response = client.get('/api/rooms')
    assert response.status_code == 200
    data = response.get_json()
    assert data['count'] == 1
    assert data['items'][0]['name'] == "Room A"

# 3. 세미나룸 생성 테스트
@patch('app.routes.get_db')
def test_create_room(mock_get_db, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_cursor.lastrowid = 1
    mock_conn.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_conn

    room_data = {"name": "Grand Hall A", "capacity": 180, "equipment": "Whiteboard"}
    response = client.post('/api/rooms', json=room_data)

    assert response.status_code == 201
    assert response.get_json() == {"id": 1, "message": "created"}

# 4. 예약 신청 테스트
@patch('app.routes.get_db')
def test_create_reservation(mock_get_db, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    
    # 룸 존재 여부 확인(fetchone) 및 생성완료 결과 처리
    mock_cursor.fetchone.return_value = (1,)
    mock_cursor.lastrowid = 100
    mock_conn.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_conn

    res_data = {
        "room_id": 1,
        "user_name": "유저A",
        "user_email": "userA@test.com",
        "date": "2026-06-03",
        "start_time": "14:00:00",
        "end_time": "16:00:00",
        "purpose": "프로젝트 회의"
    }
    response = client.post('/api/reservations', json=res_data)
    assert response.status_code == 201
    assert response.get_json() == {"id": 100, "message": "reserved"}
