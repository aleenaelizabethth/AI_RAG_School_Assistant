import mysql.connector
from datetime import time

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "1234",
    "database": "school_operations",
}

SUBJECTS = [
    "Mathematics",
    "English",
    "Science",
    "Social Studies",
    "Computer Science",
]

PERIODS = [
    (time(8, 30), time(9, 30)),
    (time(9, 30), time(10, 30)),
    (time(10, 45), time(11, 45)),
    (time(11, 45), time(12, 45)),
]

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
GRADES = [f"Grade {i}" for i in range(1, 13)]

conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

try:
    conn.start_transaction()

    # Ensure 12 teachers are available for each subject.
    teacher_ids = {}

    for subject in SUBJECTS:
        cursor.execute(
            "SELECT teacher_id FROM teachers "
            "WHERE subject_name = %s ORDER BY teacher_id",
            (subject,),
        )
        ids = [row[0] for row in cursor.fetchall()]

        while len(ids) < 12:
            number = len(ids) + 1
            name = f"{subject} Teacher {number:02d}"

            cursor.execute(
                "INSERT INTO teachers (teacher_name, subject_name) "
                "VALUES (%s, %s)",
                (name, subject),
            )
            ids.append(cursor.lastrowid)

        teacher_ids[subject] = ids[:12]

    # Ensure 12 distinct classrooms exist.
    cursor.execute("SELECT room_name, room_id FROM classrooms")
    rooms = {name: room_id for name, room_id in cursor.fetchall()}

    for number in range(1, 13):
        room_name = f"Timetable Room {number:02d}"

        if room_name not in rooms:
            cursor.execute(
                "INSERT INTO classrooms (room_name, room_type) "
                "VALUES (%s, %s)",
                (room_name, "Classroom"),
            )
            rooms[room_name] = cursor.lastrowid

    room_ids = [
        rooms[f"Timetable Room {number:02d}"]
        for number in range(1, 13)
    ]

    # Replace timetable records only. Other school tables are preserved.
    cursor.execute("DELETE FROM timetable")

    # Four lessons daily; subjects rotate through the five-subject list.
    for day_index, day in enumerate(DAYS):
        for period_index, (start_time, end_time) in enumerate(PERIODS):
            subject = SUBJECTS[(day_index + period_index) % len(SUBJECTS)]

            for grade_index, grade in enumerate(GRADES):
                cursor.execute(
                    """
                    INSERT INTO timetable
                    (class_name, subject_name, teacher_id, room_id,
                     day_of_week, start_time, end_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        grade,
                        subject,
                        teacher_ids[subject][grade_index],
                        room_ids[grade_index],
                        day,
                        start_time,
                        end_time,
                    ),
                )

    conn.commit()
    print("Timetable rebuilt successfully!")
    print("Grades: 1–12")
    print("Days: Monday–Friday")
    print("Lessons created: 240")
    print("Four periods per day; break: 10:30–10:45 AM")
    print("Other school data preserved.")

except Exception:
    conn.rollback()
    raise

finally:
    cursor.close()
    conn.close()