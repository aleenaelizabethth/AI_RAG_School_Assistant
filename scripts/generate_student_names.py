import random
import mysql.connector

first_names = [
    "Alan", "Anthony", "Manu", "Raghav", "Arjun",
    "Aarav", "Aditya", "Akash", "Amal", "Anand",
    "Anjali", "Ananya", "Asha", "Diya", "Dev",
    "Farhan", "Hari", "Ishaan", "Kiran", "Krishna",
    "Meera", "Maya", "Neha", "Nikhil", "Rahul",
    "Riya", "Rohan", "Sanjay", "Sneha", "Vivek",
    "Aiden", "Daniel", "Ethan", "Noah", "Oliver",
    "Emma", "Olivia", "Sophia", "Mia", "Zara"
]

last_names = [
    "Sharma", "Kumar", "Nair", "Menon", "Patel",
    "Reddy", "Verma", "Thomas", "Joseph", "Mathew",
    "Singh", "Das", "Pillai", "Rao", "Iyer",
    "Khan", "Fernandes", "Williams", "Brown", "Wilson"
]

random.seed(42)

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="school_operations"
)

cursor = connection.cursor()

cursor.execute("""
    SELECT student_id
    FROM students
    WHERE student_name LIKE 'Student %'
""")

student_ids = [row[0] for row in cursor.fetchall()]

used_names = set()

cursor.execute("SELECT student_name FROM students")
used_names.update(row[0] for row in cursor.fetchall())

for student_id in student_ids:
    while True:
        full_name = (
            f"{random.choice(first_names)} "
            f"{random.choice(last_names)}"
        )

        if full_name not in used_names:
            used_names.add(full_name)
            break

    cursor.execute("""
        UPDATE students
        SET student_name = %s
        WHERE student_id = %s
    """, (full_name, student_id))

connection.commit()

print(f"Updated names for {len(student_ids)} students.")

cursor.close()
connection.close()