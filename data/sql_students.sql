create database school_operations;
use school_operations;
CREATE TABLE students (
    student_id VARCHAR(10) PRIMARY KEY,
    student_name VARCHAR(100) NOT NULL,
    class_name VARCHAR(20) NOT NULL
);
INSERT INTO students (student_id, student_name, class_name)
VALUES
    ('S101', 'Ananya Sharma', 'Grade 8'),
    ('S102', 'Rahul Kumar', 'Grade 9'),
    ('S103', 'Meera Nair', 'Grade 8');
    select * from students;
    USE school_operations;

INSERT INTO students (student_id, student_name, class_name)
WITH RECURSIVE student_numbers (n) AS (
    SELECT 1
    UNION ALL
    SELECT n + 1
    FROM student_numbers
    WHERE n < 500
)
SELECT
    CONCAT('S', 1000 + n),
    CONCAT('Student ', n),
    CONCAT('Grade ', 1 + MOD(n - 1, 12))
FROM student_numbers;
SELECT COUNT(*) AS total_students
FROM students;
USE school_operations;

CREATE TABLE attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(10) NOT NULL,
    attendance_date DATE NOT NULL,
    status ENUM('Present', 'Absent') NOT NULL,
    FOREIGN KEY (student_id)
        REFERENCES students(student_id)
);
USE school_operations;

INSERT INTO attendance
    (student_id, attendance_date, status)
VALUES
    ('S101', '2026-10-19', 'Present'),
    ('S102', '2026-10-19', 'Absent'),
    ('S103', '2026-10-19', 'Present'),
    ('S101', '2026-10-20', 'Absent'),
    ('S102', '2026-10-20', 'Present'),
    ('S103', '2026-10-20', 'Present');
    SELECT
    s.student_name,
    s.class_name,
    a.attendance_date,
    a.status
FROM students s
JOIN attendance a
    ON s.student_id = a.student_id
WHERE a.attendance_date = '2026-10-19'
  AND a.status = 'Absent';
  USE school_operations;

SELECT
    class_name,
    COUNT(*) AS total_students
FROM students
GROUP BY class_name
ORDER BY class_name;
SELECT
    attendance_date,
    COUNT(*) AS absent_students
FROM attendance
WHERE status = 'Absent'
GROUP BY attendance_date
ORDER BY attendance_date;
SELECT COUNT(*) AS total_students
FROM students;
USE school_operations;

SET SESSION cte_max_recursion_depth = 600;

INSERT INTO attendance (student_id, attendance_date, status)
WITH RECURSIVE days AS (
    SELECT DATE('2026-09-20') AS d
    UNION ALL
    SELECT DATE_ADD(d, INTERVAL 1 DAY)
    FROM days
    WHERE d < '2026-10-19'
)
SELECT
    s.student_id,
    days.d,
    CASE
        WHEN RAND() < 0.10 THEN 'Absent'
        ELSE 'Present'
    END
FROM students s
CROSS JOIN days;
SELECT COUNT(*) AS total_attendance_records
FROM attendance;
USE school_operations;

CREATE TABLE attendance_school_days (
    attendance_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(10) NOT NULL,
    attendance_date DATE NOT NULL,
    status ENUM('Present', 'Absent') NOT NULL,

    UNIQUE KEY unique_student_day
        (student_id, attendance_date),

    FOREIGN KEY (student_id)
        REFERENCES students(student_id)
);
INSERT IGNORE INTO attendance_school_days
    (student_id, attendance_date, status)
WITH RECURSIVE calendar AS (
    SELECT DATE('2026-01-01') AS d

    UNION ALL

    SELECT DATE_ADD(d, INTERVAL 1 DAY)
    FROM calendar
    WHERE d < '2026-12-31'
),
ranked_days AS (
    SELECT
        d,
        ROW_NUMBER() OVER (ORDER BY d) AS day_number
    FROM calendar
    WHERE DAYOFWEEK(d) NOT IN (1, 7)
),
school_days AS (
    SELECT d
    FROM ranked_days
    WHERE day_number <= 200
)
SELECT
    s.student_id,
    d.d,
    CASE
        WHEN RAND() < 0.10 THEN 'Absent'
        ELSE 'Present'
    END
FROM students s
CROSS JOIN school_days d;
SELECT
    COUNT(*) AS total_records,
    COUNT(DISTINCT student_id) AS students,
    COUNT(DISTINCT attendance_date) AS dates
FROM attendance_school_days;
USE school_operations;

CREATE TABLE academic_results (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(10) NOT NULL,
    subject_name VARCHAR(50) NOT NULL,
    exam_name VARCHAR(50) NOT NULL,
    marks_obtained DECIMAL(5,2) NOT NULL,
    max_marks DECIMAL(5,2) NOT NULL,
    FOREIGN KEY (student_id)
        REFERENCES students(student_id),
    CHECK (marks_obtained >= 0),
    CHECK (max_marks > 0),
    CHECK (marks_obtained <= max_marks)
);
USE school_operations;

CREATE TABLE IF NOT EXISTS teachers (
    teacher_id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_name VARCHAR(100) NOT NULL,
    subject_name VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS classrooms (
    room_id INT AUTO_INCREMENT PRIMARY KEY,
    room_name VARCHAR(50) NOT NULL UNIQUE,
    room_type VARCHAR(30) NOT NULL
);

CREATE TABLE IF NOT EXISTS timetable (
    timetable_id INT AUTO_INCREMENT PRIMARY KEY,
    class_name VARCHAR(20) NOT NULL,
    subject_name VARCHAR(50) NOT NULL,
    teacher_id INT NOT NULL,
    room_id INT NOT NULL,
    day_of_week ENUM(
        'Monday', 'Tuesday', 'Wednesday',
        'Thursday', 'Friday', 'Saturday'
    ) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id),
    FOREIGN KEY (room_id) REFERENCES classrooms(room_id),
    CHECK (end_time > start_time)
);
USE school_operations;

CREATE TABLE IF NOT EXISTS teachers (
    teacher_id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_name VARCHAR(100) NOT NULL,
    subject_name VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS classrooms (
    room_id INT AUTO_INCREMENT PRIMARY KEY,
    room_name VARCHAR(50) NOT NULL UNIQUE,
    room_type VARCHAR(30) NOT NULL
);

CREATE TABLE IF NOT EXISTS timetable (
    timetable_id INT AUTO_INCREMENT PRIMARY KEY,
    class_name VARCHAR(20) NOT NULL,
    subject_name VARCHAR(50) NOT NULL,
    teacher_id INT NOT NULL,
    room_id INT NOT NULL,
    day_of_week ENUM(
        'Monday', 'Tuesday', 'Wednesday',
        'Thursday', 'Friday', 'Saturday'
    ) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    FOREIGN KEY (teacher_id)
        REFERENCES teachers(teacher_id),
    FOREIGN KEY (room_id)
        REFERENCES classrooms(room_id),
    CHECK (end_time > start_time)
);
use school_operations;
show tables
USE school_operations;

CREATE TABLE teachers (
    teacher_id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_name VARCHAR(100) NOT NULL,
    subject_name VARCHAR(50) NOT NULL
);

CREATE TABLE classrooms (
    room_id INT AUTO_INCREMENT PRIMARY KEY,
    room_name VARCHAR(50) NOT NULL UNIQUE,
    room_type VARCHAR(30) NOT NULL
);
USE school_operations;

CREATE TABLE timetable (
    timetable_id INT AUTO_INCREMENT PRIMARY KEY,
    class_name VARCHAR(20) NOT NULL,
    subject_name VARCHAR(50) NOT NULL,
    teacher_id INT NOT NULL,
    room_id INT NOT NULL,
    day_of_week ENUM(
        'Monday', 'Tuesday', 'Wednesday',
        'Thursday', 'Friday', 'Saturday'
    ) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id),
    FOREIGN KEY (room_id) REFERENCES classrooms(room_id),
    CHECK (end_time > start_time)
);
use school_operations;
show tables
USE school_operations;

CREATE TABLE teachers (
    teacher_id INT NOT NULL AUTO_INCREMENT,
    teacher_name VARCHAR(100) NOT NULL,
    subject_name VARCHAR(50) NOT NULL,
    PRIMARY KEY (teacher_id)
);
show tables
USE school_operations;

CREATE TABLE timetable (
    timetable_id INT AUTO_INCREMENT PRIMARY KEY,
    class_name VARCHAR(20) NOT NULL,
    subject_name VARCHAR(50) NOT NULL,
    teacher_id INT NOT NULL,
    room_id INT NOT NULL,
    day_of_week ENUM(
        'Monday', 'Tuesday', 'Wednesday',
        'Thursday', 'Friday', 'Saturday'
    ) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,

    FOREIGN KEY (teacher_id)
        REFERENCES teachers(teacher_id),

    FOREIGN KEY (room_id)
        REFERENCES classrooms(room_id),

    CHECK (end_time > start_time)
);
USE school_operations;

INSERT INTO teachers (teacher_name, subject_name)
VALUES
    ('Arun Thomas', 'Mathematics'),
    ('Priya Nair', 'Science'),
    ('Meera Joseph', 'English'),
    ('Rahul Menon', 'Social Studies'),
    ('Anita Das', 'Computer Science');

INSERT INTO classrooms (room_name, room_type)
VALUES
    ('Room 101', 'Classroom'),
    ('Room 102', 'Classroom'),
    ('Science Lab', 'Laboratory'),
    ('Computer Lab', 'Laboratory'),
    ('Room 201', 'Classroom');
    USE school_operations;

CREATE TABLE IF NOT EXISTS inventory_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    item_code VARCHAR(20) NOT NULL UNIQUE,
    item_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    minimum_stock INT NOT NULL DEFAULT 5,
    storage_location VARCHAR(100),
    CHECK (quantity >= 0),
    CHECK (minimum_stock >= 0)
);

INSERT IGNORE INTO inventory_items
(item_code, item_name, category, quantity,
 minimum_stock, storage_location)
VALUES
('INV001', 'Student Library Books', 'Books', 500, 50, 'Library'),
('INV002', 'Desktop Computers', 'Electronics', 40, 10, 'Computer Lab'),
('INV003', 'Science Microscopes', 'Lab Equipment', 12, 5, 'Science Lab'),
('INV004', 'Classroom Projectors', 'Electronics', 8, 3, 'Store Room'),
('INV005', 'Student Desks', 'Furniture', 180, 20, 'Furniture Store'),
('INV006', 'Printer Paper Packs', 'Stationery', 4, 10, 'Admin Office'),
('INV007', 'Football Equipment Sets', 'Sports', 15, 5, 'Sports Room'),
('INV008', 'Laboratory Safety Goggles', 'Safety Equipment', 25, 10, 'Science Lab');

SELECT * FROM inventory_items;
use school_operations;
show tables;
USE school_operations;

CREATE TABLE inventory_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    item_code VARCHAR(20) NOT NULL UNIQUE,
    item_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    minimum_stock INT NOT NULL DEFAULT 5,
    storage_location VARCHAR(100)
);
show tables;
USE school_operations;

INSERT INTO inventory_items
(item_code, item_name, category, quantity,
 minimum_stock, storage_location)
VALUES
('INV001', 'Library Books', 'Books', 500, 50, 'Library'),
('INV002', 'Desktop Computers', 'Electronics', 40, 10, 'Computer Lab'),
('INV003', 'Science Microscopes', 'Lab Equipment', 12, 5, 'Science Lab'),
('INV004', 'Classroom Projectors', 'Electronics', 8, 3, 'Store Room'),
('INV005', 'Student Desks', 'Furniture', 180, 20, 'Furniture Store'),
('INV006', 'Printer Paper Packs', 'Stationery', 4, 10, 'Admin Office'),
('INV007', 'Football Equipment Sets', 'Sports', 15, 5, 'Sports Room'),
('INV008', 'Safety Goggles', 'Safety Equipment', 25, 10, 'Science Lab');

SELECT * FROM inventory_items;
USE school_operations;

INSERT INTO inventory_items
(item_code, item_name, category, quantity,
 minimum_stock, storage_location)
VALUES
('INV001', 'Library Books', 'Books', 500, 50, 'Library'),
('INV002', 'Desktop Computers', 'Electronics', 40, 10, 'Computer Lab'),
('INV003', 'Science Microscopes', 'Lab Equipment', 12, 5, 'Science Lab'),
('INV004', 'Classroom Projectors', 'Electronics', 8, 3, 'Store Room'),
('INV005', 'Student Desks', 'Furniture', 180, 20, 'Furniture Store'),
('INV006', 'Printer Paper Packs', 'Stationery', 4, 10, 'Admin Office'),
('INV007', 'Football Equipment Sets', 'Sports', 15, 5, 'Sports Room'),
('INV008', 'Safety Goggles', 'Safety Equipment', 25, 10, 'Science Lab');
select * from inventory_items;
use school_operations;
select * from teachers;
select * from classrooms;
select * from teachers;
show create table teachers;
USE school_operations;

INSERT INTO teachers (teacher_name, subject_name)
VALUES
('Arun Thomas', 'Mathematics'),
('Priya Nair', 'Science'),
('Meera Joseph', 'English'),
('Rahul Menon', 'Social Studies'),
('Anita Das', 'Computer Science');

SELECT * FROM teachers;
USE school_operations;

SELECT COUNT(*) AS total_teachers FROM teachers;
SELECT teacher_id, teacher_name, subject_name
FROM school_operations.teachers;
INSERT INTO school_operations.teachers (teacher_name, subject_name)
VALUES
('Arun Thomas', 'Mathematics'),
('Priya Nair', 'Science'),
('Meera Joseph', 'English'),
('Rahul Menon', 'Social Studies'),
('Anita Das', 'Computer Science');
SELECT COUNT(*) AS total_teachers FROM teachers;
select * from teachers;
USE school_operations;

INSERT INTO timetable
(class_name, subject_name, teacher_id, room_id,
 day_of_week, start_time, end_time)
SELECT
    'Grade 8', t.subject_name, t.teacher_id, c.room_id,
    'Monday', '09:00:00', '10:00:00'
FROM teachers t
JOIN classrooms c ON c.room_name = 'Room 101'
WHERE t.subject_name = 'Mathematics';

INSERT INTO timetable
(class_name, subject_name, teacher_id, room_id,
 day_of_week, start_time, end_time)
SELECT
    'Grade 8', t.subject_name, t.teacher_id, c.room_id,
    'Monday', '10:00:00', '11:00:00'
FROM teachers t
JOIN classrooms c ON c.room_name = 'Science Lab'
WHERE t.subject_name = 'Science';

INSERT INTO timetable
(class_name, subject_name, teacher_id, room_id,
 day_of_week, start_time, end_time)
SELECT
    'Grade 9', t.subject_name, t.teacher_id, c.room_id,
    'Monday', '09:00:00', '10:00:00'
FROM teachers t
JOIN classrooms c ON c.room_name = 'Room 102'
WHERE t.subject_name = 'English';
select * from timetable;
USE school_operations;

INSERT INTO timetable
(class_name, subject_name, teacher_id, room_id,
 day_of_week, start_time, end_time)
SELECT
    schedule.class_name,
    t.subject_name,
    t.teacher_id,
    c.room_id,
    schedule.day_of_week,
    schedule.start_time,
    schedule.end_time
FROM (
    SELECT 'Grade 1' AS class_name, 'Mathematics' AS subject_name,
           'Tuesday' AS day_of_week, '09:00:00' AS start_time, '10:00:00' AS end_time,
           'Room 101' AS room_name
    UNION ALL SELECT 'Grade 2', 'Science', 'Tuesday', '09:00:00', '10:00:00', 'Science Lab'
    UNION ALL SELECT 'Grade 3', 'English', 'Tuesday', '09:00:00', '10:00:00', 'Room 102'
    UNION ALL SELECT 'Grade 4', 'Social Studies', 'Tuesday', '09:00:00', '10:00:00', 'Room 201'
    UNION ALL SELECT 'Grade 5', 'Computer Science', 'Tuesday', '09:00:00', '10:00:00', 'Computer Lab'
    UNION ALL SELECT 'Grade 6', 'Mathematics', 'Wednesday', '09:00:00', '10:00:00', 'Room 101'
    UNION ALL SELECT 'Grade 7', 'Science', 'Wednesday', '09:00:00', '10:00:00', 'Science Lab'
    UNION ALL SELECT 'Grade 8', 'English', 'Wednesday', '09:00:00', '10:00:00', 'Room 102'
    UNION ALL SELECT 'Grade 9', 'Social Studies', 'Wednesday', '09:00:00', '10:00:00', 'Room 201'
    UNION ALL SELECT 'Grade 10', 'Computer Science', 'Wednesday', '09:00:00', '10:00:00', 'Computer Lab'
    UNION ALL SELECT 'Grade 11', 'Mathematics', 'Thursday', '09:00:00', '10:00:00', 'Room 101'
    UNION ALL SELECT 'Grade 12', 'Science', 'Thursday', '09:00:00', '10:00:00', 'Science Lab'
    UNION ALL SELECT 'Grade 1', 'English', 'Thursday', '10:00:00', '11:00:00', 'Room 102'
    UNION ALL SELECT 'Grade 2', 'Social Studies', 'Thursday', '10:00:00', '11:00:00', 'Room 201'
    UNION ALL SELECT 'Grade 3', 'Computer Science', 'Thursday', '10:00:00', '11:00:00', 'Computer Lab'
) AS schedule
JOIN teachers t ON t.subject_name = schedule.subject_name
JOIN classrooms c ON c.room_name = schedule.room_name;
select * from timetable;
SELECT COUNT(*) AS total_lessons
FROM timetable;

SELECT class_name, COUNT(*) AS lesson_count
FROM timetable
GROUP BY class_name
ORDER BY class_name;
USE school_operations;

INSERT INTO timetable
(class_name, subject_name, teacher_id, room_id,
 day_of_week, start_time, end_time)
SELECT
    s.class_name,
    s.subject_name,
    t.teacher_id,
    c.room_id,
    s.day_of_week,
    s.start_time,
    s.end_time
FROM (
    SELECT 'Grade 8' AS class_name, 'Mathematics' AS subject_name,
           'Tuesday' AS day_of_week, '09:00:00' AS start_time,
           '10:00:00' AS end_time, 'Room 101' AS room_name
    UNION ALL SELECT 'Grade 8', 'Science', 'Tuesday', '10:00:00', '11:00:00', 'Science Lab'
    UNION ALL SELECT 'Grade 9', 'English', 'Tuesday', '09:00:00', '10:00:00', 'Room 102'
    UNION ALL SELECT 'Grade 9', 'Social Studies', 'Tuesday', '10:00:00', '11:00:00', 'Room 201'
    UNION ALL SELECT 'Grade 10', 'Computer Science', 'Tuesday', '09:00:00', '10:00:00', 'Computer Lab'

    UNION ALL SELECT 'Grade 8', 'English', 'Wednesday', '09:00:00', '10:00:00', 'Room 102'
    UNION ALL SELECT 'Grade 8', 'Social Studies', 'Wednesday', '10:00:00', '11:00:00', 'Room 201'
    UNION ALL SELECT 'Grade 9', 'Mathematics', 'Wednesday', '09:00:00', '10:00:00', 'Room 101'
    UNION ALL SELECT 'Grade 9', 'Science', 'Wednesday', '10:00:00', '11:00:00', 'Science Lab'
    UNION ALL SELECT 'Grade 10', 'English', 'Wednesday', '09:00:00', '10:00:00', 'Room 102'

    UNION ALL SELECT 'Grade 8', 'Computer Science', 'Thursday', '09:00:00', '10:00:00', 'Computer Lab'
    UNION ALL SELECT 'Grade 8', 'Mathematics', 'Thursday', '10:00:00', '11:00:00', 'Room 101'
    UNION ALL SELECT 'Grade 9', 'Science', 'Thursday', '09:00:00', '10:00:00', 'Science Lab'
    UNION ALL SELECT 'Grade 9', 'English', 'Thursday', '10:00:00', '11:00:00', 'Room 102'
    UNION ALL SELECT 'Grade 10', 'Social Studies', 'Thursday', '09:00:00', '10:00:00', 'Room 201'

    UNION ALL SELECT 'Grade 8', 'Science', 'Friday', '09:00:00', '10:00:00', 'Science Lab'
    UNION ALL SELECT 'Grade 8', 'English', 'Friday', '10:00:00', '11:00:00', 'Room 102'
    UNION ALL SELECT 'Grade 9', 'Computer Science', 'Friday', '09:00:00', '10:00:00', 'Computer Lab'
    UNION ALL SELECT 'Grade 9', 'Mathematics', 'Friday', '10:00:00', '11:00:00', 'Room 101'
    UNION ALL SELECT 'Grade 10', 'Science', 'Friday', '09:00:00', '10:00:00', 'Science Lab'
) AS s
JOIN teachers t ON t.subject_name = s.subject_name
JOIN classrooms c ON c.room_name = s.room_name;
SELECT day_of_week, COUNT(*) AS lesson_count
FROM timetable
GROUP BY day_of_week
ORDER BY FIELD(
    day_of_week,
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'
);
SELECT day_of_week, COUNT(*) AS lesson_count
FROM timetable
GROUP BY day_of_week
ORDER BY FIELD(
    day_of_week,
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'
);
USE school_operations;

START TRANSACTION;

DELETE FROM timetable
WHERE LOWER(class_name) = 'grade 10';

INSERT INTO timetable
(class_name, subject_name, teacher_id, room_id,
 day_of_week, start_time, end_time)
SELECT
    'Grade 10',
    s.subject_name,
    t.teacher_id,
    c.room_id,
    s.day_of_week,
    s.start_time,
    s.end_time
FROM (
    SELECT 'Mathematics' AS subject_name, 'Monday' AS day_of_week,
           '09:00:00' AS start_time, '09:50:00' AS end_time,
           'Room 101' AS room_name
    UNION ALL SELECT 'Science', 'Monday', '10:00:00', '10:50:00', 'Science Lab'
    UNION ALL SELECT 'English', 'Monday', '11:00:00', '11:50:00', 'Room 102'
    UNION ALL SELECT 'Computer Science', 'Monday', '12:00:00', '12:30:00', 'Computer Lab'

    UNION ALL SELECT 'English', 'Tuesday', '09:00:00', '09:50:00', 'Room 102'
    UNION ALL SELECT 'Mathematics', 'Tuesday', '10:00:00', '10:50:00', 'Room 101'
    UNION ALL SELECT 'Social Studies', 'Tuesday', '11:00:00', '11:50:00', 'Room 201'
    UNION ALL SELECT 'Science', 'Tuesday', '12:00:00', '12:30:00', 'Science Lab'

    UNION ALL SELECT 'Science', 'Wednesday', '09:00:00', '09:50:00', 'Science Lab'
    UNION ALL SELECT 'Computer Science', 'Wednesday', '10:00:00', '10:50:00', 'Computer Lab'
    UNION ALL SELECT 'Mathematics', 'Wednesday', '11:00:00', '11:50:00', 'Room 101'
    UNION ALL SELECT 'English', 'Wednesday', '12:00:00', '12:30:00', 'Room 102'

    UNION ALL SELECT 'Social Studies', 'Thursday', '09:00:00', '09:50:00', 'Room 201'
    UNION ALL SELECT 'English', 'Thursday', '10:00:00', '10:50:00', 'Room 102'
    UNION ALL SELECT 'Science', 'Thursday', '11:00:00', '11:50:00', 'Science Lab'
    UNION ALL SELECT 'Mathematics', 'Thursday', '12:00:00', '12:30:00', 'Room 101'

    UNION ALL SELECT 'Computer Science', 'Friday', '09:00:00', '09:50:00', 'Computer Lab'
    UNION ALL SELECT 'Mathematics', 'Friday', '10:00:00', '10:50:00', 'Room 101'
    UNION ALL SELECT 'English', 'Friday', '11:00:00', '11:50:00', 'Room 102'
    UNION ALL SELECT 'Science', 'Friday', '12:00:00', '12:30:00', 'Science Lab'
) AS s
JOIN teachers t ON t.subject_name = s.subject_name
JOIN classrooms c ON c.room_name = s.room_name;

COMMIT;

SELECT class_name, day_of_week, subject_name,
       start_time, end_time
FROM timetable
WHERE LOWER(class_name) = 'grade 10'
ORDER BY FIELD(day_of_week,
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'),
    start_time;
    SELECT
    day_of_week,
    start_time,
    end_time,
    COUNT(*) AS lesson_count
FROM timetable
GROUP BY day_of_week, start_time, end_time
ORDER BY
    FIELD(day_of_week,
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'),
    start_time;
    USE school_operations;

SELECT
    class_name,
    subject_name,
    teacher_id,
    room_id,
    day_of_week,
    start_time,
    end_time,
    COUNT(*) AS copies
FROM timetable
GROUP BY
    class_name, subject_name, teacher_id, room_id,
    day_of_week, start_time, end_time
HAVING COUNT(*) > 1;
SELECT DISTINCT class_name
FROM timetable
ORDER BY class_name;
SELECT
    class_name,
    subject_name,
    teacher_id,
    room_id,
    day_of_week,
    start_time,
    end_time,
    COUNT(*) AS copies
FROM school_operations.timetable
GROUP BY
    class_name,
    subject_name,
    teacher_id,
    room_id,
    day_of_week,
    start_time,
    end_time
HAVING COUNT(*) > 1;
USE school_operations;

SELECT
    class_name,
    subject_name,
    teacher_id,
    room_id,
    day_of_week,
    start_time,
    end_time,
    COUNT(*) AS copies,
    MIN(timetable_id) AS row_to_keep
FROM timetable
GROUP BY
    class_name,
    subject_name,
    teacher_id,
    room_id,
    day_of_week,
    start_time,
    end_time
HAVING COUNT(*) > 1;
USE school_operations;

START TRANSACTION;

DELETE FROM timetable;

SELECT COUNT(*) AS remaining_lessons
FROM timetable;
commit;
SELECT COUNT(*) AS remaining_lessons FROM school_operations.timetable;
USE school_operations;

DELETE FROM timetable;
SELECT COUNT(*) AS remaining_lessons;
delete from timetable;
USE school_operations;

SET SQL_SAFE_UPDATES = 0;

DELETE FROM timetable;

SELECT COUNT(*) AS remaining_lessons
FROM timetable;

USE school_operations;

CREATE TABLE IF NOT EXISTS academic_results (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject VARCHAR(100) NOT NULL,
    exam_name ENUM('Midterm', 'Final Exam') NOT NULL,
    marks_obtained DECIMAL(5,2) NOT NULL,
    maximum_marks DECIMAL(5,2) NOT NULL DEFAULT 100,
    academic_year VARCHAR(9) NOT NULL DEFAULT '2026',
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    CHECK (marks_obtained >= 0),
    CHECK (maximum_marks > 0),
    CHECK (marks_obtained <= maximum_marks)
);
USE school_operations;

DESCRIBE academic_results;
SELECT * FROM academic_results LIMIT 10;
SELECT
    COUNT(DISTINCT student_id) AS students_with_marks,
    COUNT(*) AS total_result_records,
    COUNT(DISTINCT subject) AS total_subjects,
    COUNT(DISTINCT exam_name) AS exam_types
FROM academic_results;
describe acedemic_results;
use school_operations;
describe acedemic_results;
use school_operations;
show tables;
show columns from academic_results;
USE school_operations;

SELECT
    COUNT(DISTINCT student_id) AS students_with_marks,
    COUNT(*) AS total_result_records,
    COUNT(DISTINCT subject_name) AS total_subjects,
    COUNT(DISTINCT exam_name) AS exam_types
FROM academic_results;
show columns from students;
USE school_operations;

SELECT
    s.student_id,
    s.student_name,
    s.class_name,
    SUM(ar.marks_obtained) AS total_marks,
    SUM(ar.max_marks) AS total_max_marks,
    ROUND(
        100.0 * SUM(ar.marks_obtained) / SUM(ar.max_marks), 2
    ) AS percentage
FROM students s
JOIN academic_results ar
    ON s.student_id = ar.student_id
WHERE s.class_name LIKE '%12%'
  AND ar.exam_name = 'Final Exam'
GROUP BY s.student_id, s.student_name, s.class_name
ORDER BY percentage DESC
LIMIT 1;
SELECT DISTINCT class_name
FROM students
ORDER BY class_name;
SELECT DISTINCT s.class_name, ar.exam_name
FROM students s
JOIN academic_results ar ON s.student_id = ar.student_id
ORDER BY s.class_name, ar.exam_name;
USE school_operations;

INSERT INTO academic_results
    (student_id, subject_name, exam_name, marks_obtained, max_marks)
SELECT
    s.student_id,
    sub.subject_name,
    ex.exam_name,
    FLOOR(50 + RAND() * 51) AS marks_obtained,
    100 AS max_marks
FROM students s
CROSS JOIN (
    SELECT 'English' AS subject_name
    UNION ALL SELECT 'Mathematics'
    UNION ALL SELECT 'Science'
    UNION ALL SELECT 'Social Studies'
    UNION ALL SELECT 'Computer'
) sub
CROSS JOIN (
    SELECT 'Midterm' AS exam_name
    UNION ALL SELECT 'Final Exam'
) ex
WHERE NOT EXISTS (
    SELECT 1
    FROM academic_results ar
    WHERE ar.student_id = s.student_id
      AND ar.subject_name = sub.subject_name
      AND ar.exam_name = ex.exam_name
);

USE school_operations;

SELECT
    s.class_name,
    s.student_id,
    s.student_name,
    SUM(ar.marks_obtained) AS total_marks,
    SUM(ar.max_marks) AS total_max_marks,
    ROUND(
        100.0 * SUM(ar.marks_obtained) / SUM(ar.max_marks), 2
    ) AS percentage
FROM students s
JOIN academic_results ar
    ON s.student_id = ar.student_id
WHERE ar.exam_name = 'Final Exam'
GROUP BY
    s.class_name,
    s.student_id,
    s.student_name
ORDER BY
    CAST(s.class_name AS UNSIGNED),
    total_marks DESC;