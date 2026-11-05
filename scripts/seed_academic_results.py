import random
import mysql.connector
from config import DB_CONFIG

# Connect to the existing school database
connection = mysql.connector.connect(**DB_CONFIG)

cursor = connection.cursor()

# Use repeatable fictional test data
random.seed(42)

subjects = [
    "Mathematics",
    "Science",
    "English",
    "Social Studies",
    "Computer Science"
]

exams = [
    "Midterm",
    "Final"
]

# Get all students from the database
cursor.execute("SELECT student_id FROM students")
students = cursor.fetchall()

# Avoid adding duplicate results if you run this again
cursor.execute("SELECT COUNT(*) FROM academic_results")
existing_results = cursor.fetchone()[0]

if existing_results > 0:
    print(f"Academic results already exist: {existing_results} records.")
    print("No new records added. This prevents duplicate results.")
else:
    records = []

    for (student_id,) in students:
        for subject in subjects:
            for exam in exams:
                max_marks = 100
                marks = random.randint(25, 100)

                records.append((
                    student_id,
                    subject,
                    exam,
                    marks,
                    max_marks
                ))

    sql = """
        INSERT INTO academic_results
        (student_id, subject_name, exam_name,
         marks_obtained, max_marks)
        VALUES (%s, %s, %s, %s, %s)
    """

    cursor.executemany(sql, records)
    connection.commit()

    print(f"Students found: {len(students)}")
    print(f"Academic results added: {len(records)}")

cursor.close()
connection.close()