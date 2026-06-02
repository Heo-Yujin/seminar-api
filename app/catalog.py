ROOM_CATALOG = [
    {"number": 1, "name": "Grand Hall A", "capacity": 180},
    {"number": 2, "name": "Grand Hall B", "capacity": 165},
    {"number": 3, "name": "Grand Hall C", "capacity": 150},
    {"number": 4, "name": "Grand Hall D", "capacity": 140},
    {"number": 5, "name": "Grand Hall E", "capacity": 132},
    {"number": 6, "name": "Summit Room 1", "capacity": 96},
    {"number": 7, "name": "Summit Room 2", "capacity": 90},
    {"number": 8, "name": "Summit Room 3", "capacity": 84},
    {"number": 9, "name": "Summit Room 4", "capacity": 78},
    {"number": 10, "name": "Forum Room 1", "capacity": 72},
    {"number": 11, "name": "Forum Room 2", "capacity": 66},
    {"number": 12, "name": "Forum Room 3", "capacity": 60},
    {"number": 13, "name": "Forum Room 4", "capacity": 56},
    {"number": 14, "name": "Studio Room 1", "capacity": 52},
    {"number": 15, "name": "Studio Room 2", "capacity": 48},
    {"number": 16, "name": "Studio Room 3", "capacity": 44},
    {"number": 17, "name": "Studio Room 4", "capacity": 40},
    {"number": 18, "name": "Workshop Room 1", "capacity": 36},
    {"number": 19, "name": "Workshop Room 2", "capacity": 34},
    {"number": 20, "name": "Workshop Room 3", "capacity": 32},
    {"number": 21, "name": "Workshop Room 4", "capacity": 30},
    {"number": 22, "name": "Meeting Room 1", "capacity": 28},
    {"number": 23, "name": "Meeting Room 2", "capacity": 26},
    {"number": 24, "name": "Meeting Room 3", "capacity": 24},
    {"number": 25, "name": "Meeting Room 4", "capacity": 22},
    {"number": 26, "name": "Focus Room 1", "capacity": 18},
    {"number": 27, "name": "Focus Room 2", "capacity": 16},
    {"number": 28, "name": "Focus Room 3", "capacity": 14},
    {"number": 29, "name": "Focus Room 4", "capacity": 12},
    {"number": 30, "name": "Focus Room 5", "capacity": 10},
]

ROOM_CAPACITY_BY_NAME = {room["name"]: room["capacity"] for room in ROOM_CATALOG}
ROOM_NUMBER_BY_NAME = {room["name"]: room["number"] for room in ROOM_CATALOG}
ROOM_BY_NUMBER = {room["number"]: room for room in ROOM_CATALOG}

def get_catalog_room(name):
    room_number = ROOM_NUMBER_BY_NAME.get(name)
    if room_number is None:
        return None
    return ROOM_BY_NUMBER[room_number]


def get_catalog_room_by_number(room_number):
    try:
        return ROOM_BY_NUMBER.get(int(room_number))
    except (TypeError, ValueError):
        return None
