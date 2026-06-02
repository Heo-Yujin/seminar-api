-- migrations/001_init.sql
CREATE DATABASE IF NOT EXISTS seminar_db;
USE seminar_db;

CREATE TABLE IF NOT EXISTS rooms (
  id INT AUTO_INCREMENT PRIMARY KEY,
  room_number INT NOT NULL,
  name VARCHAR(100) NOT NULL,
  capacity INT NOT NULL,
  equipment VARCHAR(255) NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE UNIQUE INDEX IF NOT EXISTS uq_rooms_name ON rooms (name);
CREATE UNIQUE INDEX IF NOT EXISTS uq_rooms_room_number ON rooms (room_number);

CREATE TABLE IF NOT EXISTS reservations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  room_id INT NOT NULL,
  user_name VARCHAR(100) NOT NULL,
  user_email VARCHAR(100) NOT NULL,
  date DATE NOT NULL,
  start_time TIME NOT NULL,
  end_time TIME NOT NULL,
  purpose VARCHAR(255) NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_reservations_room
    FOREIGN KEY (room_id) REFERENCES rooms(room_number) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT IGNORE INTO rooms (room_number, name, capacity, equipment) VALUES
(1, 'Grand Hall A', 180, NULL),
(2, 'Grand Hall B', 165, NULL),
(3, 'Grand Hall C', 150, NULL),
(4, 'Grand Hall D', 140, NULL),
(5, 'Grand Hall E', 132, NULL),
(6, 'Summit Room 1', 96, NULL),
(7, 'Summit Room 2', 90, NULL),
(8, 'Summit Room 3', 84, NULL),
(9, 'Summit Room 4', 78, NULL),
(10, 'Forum Room 1', 72, NULL),
(11, 'Forum Room 2', 66, NULL),
(12, 'Forum Room 3', 60, NULL),
(13, 'Forum Room 4', 56, NULL),
(14, 'Studio Room 1', 52, NULL),
(15, 'Studio Room 2', 48, NULL),
(16, 'Studio Room 3', 44, NULL),
(17, 'Studio Room 4', 40, NULL),
(18, 'Workshop Room 1', 36, NULL),
(19, 'Workshop Room 2', 34, NULL),
(20, 'Workshop Room 3', 32, NULL),
(21, 'Workshop Room 4', 30, NULL),
(22, 'Meeting Room 1', 28, NULL),
(23, 'Meeting Room 2', 26, NULL),
(24, 'Meeting Room 3', 24, NULL),
(25, 'Meeting Room 4', 22, NULL),
(26, 'Focus Room 1', 18, NULL),
(27, 'Focus Room 2', 16, NULL),
(28, 'Focus Room 3', 14, NULL),
(29, 'Focus Room 4', 12, NULL),
(30, 'Focus Room 5', 10, NULL);
