import random
import sys
from pathlib import Path

import mysql.connector

sys.path.append(str(Path(__file__).parent.parent / "core"))
from config import DB_CONFIG

male = ["Anil", "Rajesh", "Suresh", "Vinod", "Manoj", "Thomas", "George", "Joseph",
        "Ravi", "Sanjay", "Arun", "Biju", "Dinesh", "Mohan", "Prakash", "Sunil",
        "Vijay", "Ramesh", "Anand", "Jacob"]
female = ["Priya", "Anita", "Sunita", "Meera", "Latha", "Deepa", "Smitha", "Rekha",
          "Nisha", "Sheela", "Lakshmi", "Maya", "Jessy", "Annie", "Divya", "Kavitha",
          "Preethi", "Sindhu", "Revathi", "Mary"]
last = ["Nair", "Menon", "Pillai", "Thomas", "Joseph", "Mathew", "Iyer", "Varghese",
        "Kumar", "Sharma", "Reddy", "Rao", "Kurian", "George", "Fernandes", "Das",
        "Krishnan", "Raj", "Philip", "Jacob"]

random.seed(7)

conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

# Replace placeholder teacher names like "Mathematics Teacher 05"
cursor.execute("SELECT teacher_id FROM teachers WHERE teacher_name LIKE '% Teacher %'")
teacher_ids = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT teacher_name FROM teachers")
used = {row[0] for row in cursor.fetchall()}

for teacher_id in teacher_ids:
    while True:
        if random.random() < 0.5:
            name = f"Mr. {random.choice(male)} {random.choice(last)}"
        else:
            name = f"Ms. {random.choice(female)} {random.choice(last)}"
        if name not in used:
            used.add(name)
            break
    cursor.execute("UPDATE teachers SET teacher_name = %s WHERE teacher_id = %s",
                   (name, teacher_id))

# Replace placeholder room names like "Timetable Room 05"
cursor.execute("SELECT room_id, room_name FROM classrooms WHERE room_name LIKE 'Timetable Room %'")
for room_id, room_name in cursor.fetchall():
    number = int(room_name.split()[-1])
    cursor.execute("UPDATE classrooms SET room_name = %s WHERE room_id = %s",
                   (f"Grade {number} Classroom", room_id))

conn.commit()
print(f"Renamed {len(teacher_ids)} teachers.")

cursor.close()
conn.close()