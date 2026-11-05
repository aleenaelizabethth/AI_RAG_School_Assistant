import json
import re

import mysql.connector
import requests

from config import DB_CONFIG
from policy_rag import search_policy

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2"

SCHOOL_NAME = "Excellent Public School"
SCHOOL_PHONE = "+91-XXXXXXXXXX"
SCHOOL_EMAIL = "info@excellentschool.example"

DAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")


def office_contact_response():
    return (
        "I'm sorry, I couldn't find a reliable answer to that. "
        f"Please contact {SCHOOL_NAME} for assistance.\n"
        f"Phone: {SCHOOL_PHONE}\nEmail: {SCHOOL_EMAIL}"
    )


def format_time(value):
    if hasattr(value, "total_seconds"):
        seconds = int(value.total_seconds())
    else:
        seconds = value.hour * 3600 + value.minute * 60
    hour, minute = seconds // 3600, seconds % 3600 // 60
    suffix = "AM" if hour < 12 else "PM"
    return f"{hour % 12 or 12}:{minute:02d} {suffix}"


def format_timetable(rows):
    lines = [f"**{rows[0]['class_name']} timetable**"]
    day = None
    for row in rows:
        if row["day_of_week"] != day:
            day = row["day_of_week"]
            lines.append(f"\n**{day}**")
        lines.append(
            f"- {row['start_time']} – {row['end_time']}: {row['subject_name']} "
            f"({row['teacher_name']}, {row['room_name']})"
        )
    return "\n".join(lines)

def clean_history(history):
    cleaned = []
    for message in history[-6:]:
        lines = [line for line in message["content"].splitlines()
                 if not line.startswith(("- ", "**"))]
        cleaned.append({"role": message["role"], "content": "\n".join(lines) or "Done."})
    return cleaned

def query_database(route):
    category = route.get("category", "")
    name = route.get("name", "").strip()
    student_id = route.get("student_id", "").strip()
    class_name = route.get("class_name", "").strip()
    subject = route.get("subject", "").strip()
    day = route.get("day", "").strip()
    exam = route.get("exam", "").strip()

    if category not in {
        "students", "attendance", "results", "teachers",
        "timetable", "inventory",
    }:
        return []

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    try:
        if category == "teachers":
            cursor.execute("""
                SELECT DISTINCT teacher_name, subject_name
                FROM teachers
                WHERE (%s = '' OR LOWER(teacher_name) LIKE LOWER(%s))
                  AND (%s = '' OR LOWER(subject_name) LIKE LOWER(%s))
                ORDER BY subject_name, teacher_name
                LIMIT 100
            """, (name, f"%{name}%", subject, f"%{subject}%"))

        elif category == "students":
            cursor.execute("""
                SELECT student_id, student_name, class_name
                FROM students
                WHERE (%s = '' OR student_id = %s)
                  AND (%s = '' OR LOWER(student_name) LIKE LOWER(%s))
                  AND (
                    %s = '' OR
                    CAST(REGEXP_SUBSTR(class_name, '[0-9]+') AS UNSIGNED)
                    = CAST(%s AS UNSIGNED)
                  )
                ORDER BY student_name
                LIMIT 100
            """, (
                student_id, student_id, name, f"%{name}%",
                class_name, class_name,
            ))

        elif category == "attendance":
            cursor.execute("""
                SELECT
                    s.student_id,
                    s.student_name,
                    s.class_name,
                    COUNT(a.attendance_id) AS recorded_days,
                    COALESCE(SUM(a.status = 'Present'), 0) AS present_days,
                    COALESCE(SUM(a.status = 'Absent'), 0) AS absent_days,
                    ROUND(
                        100.0 * COALESCE(SUM(a.status = 'Present'), 0)
                        / NULLIF(COUNT(a.attendance_id), 0), 2
                    ) AS attendance_percentage
                FROM students s
                LEFT JOIN attendance a ON a.student_id = s.student_id
                WHERE (%s = '' OR s.student_id = %s)
                  AND (%s = '' OR LOWER(s.student_name) LIKE LOWER(%s))
                  AND (
                    %s = '' OR
                    CAST(REGEXP_SUBSTR(s.class_name, '[0-9]+') AS UNSIGNED)
                    = CAST(%s AS UNSIGNED)
                  )
                GROUP BY s.student_id, s.student_name, s.class_name
                ORDER BY absent_days DESC
                LIMIT 100
            """, (
                student_id, student_id, name, f"%{name}%",
                class_name, class_name,
            ))

        elif category == "results":
        
            if route.get("ranking"):
                if not class_name:
                    return []

                exam_value = exam or "Final"
                exam_filter = (
                    "LOWER(ar.exam_name) LIKE '%mid%'"
                    if "mid" in exam_value.lower()
                    else "LOWER(ar.exam_name) LIKE '%final%'"
                )
                limit = max(1, min(int(route.get("top_n", 1)), 10))

                cursor.execute(f"""
                    SELECT
                        s.student_id,
                        s.student_name,
                        s.class_name,
                        COUNT(DISTINCT ar.subject_name) AS subjects_count,
                        SUM(ar.marks_obtained) AS total_marks,
                        SUM(ar.max_marks) AS total_max_marks,
                        ROUND(
                            100.0 * SUM(ar.marks_obtained)
                            / NULLIF(SUM(ar.max_marks), 0), 2
                        ) AS percentage
                    FROM students s
                    JOIN academic_results ar
                      ON ar.student_id = s.student_id
                    WHERE CAST(
                        REGEXP_SUBSTR(s.class_name, '[0-9]+')
                        AS UNSIGNED
                    ) = CAST(%s AS UNSIGNED)
                      AND {exam_filter}
                    GROUP BY s.student_id, s.student_name, s.class_name
                    ORDER BY percentage DESC, total_marks DESC
                    LIMIT {limit}
                """, (class_name,))

            else:
                cursor.execute("""
                    SELECT
                        s.student_id, s.student_name, s.class_name,
                        r.subject_name, r.exam_name,
                        r.marks_obtained, r.max_marks
                    FROM academic_results r
                    JOIN students s ON s.student_id = r.student_id
                    WHERE (%s = '' OR s.student_id = %s)
                      AND (%s = '' OR
                           LOWER(s.student_name) LIKE LOWER(%s))
                      AND (%s = '' OR
                           CAST(REGEXP_SUBSTR(s.class_name, '[0-9]+')
                           AS UNSIGNED) = CAST(%s AS UNSIGNED))
                      AND (%s = '' OR
                           LOWER(r.subject_name) LIKE LOWER(%s))
                      AND (%s = '' OR
                           LOWER(r.exam_name) LIKE LOWER(%s))
                    ORDER BY s.student_name, r.exam_name, r.subject_name
                    LIMIT 100
                """, (
                    student_id, student_id, name, f"%{name}%",
                    class_name, class_name, subject, f"%{subject}%",
                    exam, f"%{exam}%",
                ))

        elif category == "timetable":
            if not class_name:
                return []

            cursor.execute("""
                SELECT
                    t.class_name, t.day_of_week,
                    t.start_time, t.end_time, t.subject_name,
                    te.teacher_name, c.room_name
                FROM timetable t
                JOIN teachers te ON te.teacher_id = t.teacher_id
                JOIN classrooms c ON c.room_id = t.room_id
                WHERE CAST(
                    REGEXP_SUBSTR(t.class_name, '[0-9]+')
                    AS UNSIGNED
                ) = CAST(%s AS UNSIGNED)
                  AND (%s = '' OR LOWER(t.day_of_week) = LOWER(%s))
                  AND (%s = '' OR
                       LOWER(t.subject_name) LIKE LOWER(%s))
                ORDER BY FIELD(
                    LOWER(t.day_of_week),
                    'monday', 'tuesday', 'wednesday',
                    'thursday', 'friday', 'saturday', 'sunday'
                ), t.start_time
                LIMIT 100
            """, (class_name, day, day, subject, f"%{subject}%"))

        elif category == "inventory":
            cursor.execute("""
                SELECT item_code, item_name, category, quantity,
                       minimum_stock, storage_location,
                       CASE WHEN quantity < minimum_stock
                            THEN 'Restock needed'
                            ELSE 'Stock sufficient'
                       END AS stock_status
                FROM inventory_items
                WHERE (%s = '' OR LOWER(item_name) LIKE LOWER(%s)
                       OR LOWER(category) LIKE LOWER(%s))
                ORDER BY item_name
                LIMIT 100
            """, (name, f"%{name}%", f"%{name}%"))

        rows = cursor.fetchall()

        if category == "timetable":
            for row in rows:
                row["start_time"] = format_time(row["start_time"])
                row["end_time"] = format_time(row["end_time"])

        return rows

    finally:
        cursor.close()
        conn.close()



def make_tool(name, description, params, required=()):
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {
                    key: {"type": "string", "description": text}
                    for key, text in params.items()
                },
                "required": list(required),
            },
        },
    }


TOOLS = [
    make_tool("policy_search",
              "Search school policies: timings, fees, leave, sports, activities, transport, conduct, contacts.",
              {"question": "The policy question"}, ["question"]),
    make_tool("timetable", "Get a class timetable.",
              {"class_name": "Class number, e.g. 5",
               "day": "Optional day, e.g. Monday"},
              ["class_name"]),
    make_tool("results", "Get exam marks of a student or a class.",
              {"name": "Student name", "class_name": "Class number",
               "subject": "Subject", "exam": "Midterm or Final"}),
    make_tool("ranking", "Get the top students of a class by total marks.",
              {"class_name": "Class number", "exam": "Midterm or Final",
               "top_n": "How many students, default 1"}, ["class_name"]),
    make_tool("attendance", "Get attendance and absences of a student or class.",
              {"name": "Student name", "class_name": "Class number"}),
    make_tool("students", "Find students by name or class.",
              {"name": "Student name", "class_name": "Class number"}),
    make_tool("teachers", "Find teachers by name or subject.",
              {"name": "Teacher name", "subject": "Subject"}),
    make_tool("inventory", "Check school inventory stock.",
              {"name": "Item or category name"}),
]

SYSTEM_PROMPT = f"""You are the assistant for {SCHOOL_NAME}.
Use the tools to look up facts. Never guess or invent data.
You may use more than one tool for a question.
Leave out optional arguments the user did not mention.
Timetables are shown to the user automatically.
Answer only the other parts of the question, and never mention timetables.
If the tools find nothing, say so and give the office contact: {SCHOOL_PHONE}, {SCHOOL_EMAIL}.
Keep answers short and clear."""


def run_tool(name, args):
    
    args = {key: str(value).strip() for key, value in args.items()}
    args = {
        key: ("" if value.lower() in ("none", "null", "n/a", "all") else value)
        for key, value in args.items()
    }

    if name == "policy_search":
        results = search_policy(args.get("question", ""), top_k=2)
        return "\n\n".join(r["text"] for r in results) or "No relevant policy found."

    if "class_name" in args:
        match = re.search(r"\d+", args["class_name"])
        args["class_name"] = match.group() if match else ""

    if name == "ranking":
        route = {
            "category": "results",
            "ranking": True,
            "class_name": args.get("class_name", ""),
            "exam": args.get("exam", "") or "Final",
            "top_n": int(args["top_n"]) if args.get("top_n", "").isdigit() else 1,
        }
    else:
        route = {"category": name, **args}

    records = query_database(route)
    if not records:
        return "No records found."
    if name == "timetable":
        return format_timetable(records)
    return json.dumps(records[:30], default=str)

def ask_ollama_tools(messages):
    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "messages": messages, "tools": TOOLS, "stream": False},
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["message"]


def agent_answer(question, history, max_steps=4):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + clean_history(history)
    messages.append({"role": "user", "content": question})
    timetables = []  # shown exactly as formatted, never written by the model

    for _ in range(max_steps):
        reply = ask_ollama_tools(messages)
        calls = reply.get("tool_calls")

        if not calls:
            text = reply["content"].strip()
            if timetables:
                # The program shows timetables itself, so drop model sentences about them.
                text = "\n".join(
                    line for line in text.splitlines() if "timetable" not in line.lower()
                )
            parts = [text.strip()] + timetables
            return "\n\n".join(p for p in parts if p) or office_contact_response()

        messages.append(reply)
        names = []
        for call in calls:
            name = call["function"]["name"]
            args = call["function"]["arguments"]
            if isinstance(args, str):
                args = json.loads(args)

            if not any(day in question.lower() for day in DAYS):
                args.pop("day", None)

            print(f"[tool] {name} {args}")
            result = run_tool(name, args)
            names.append(name)

            if name == "timetable" and result != "No records found.":
                if result not in timetables:
                    timetables.append(result)
                result = "Timetable retrieved and shown to the user. If the question has other parts, use the other tools."
            messages.append({"role": "tool", "tool_name": name, "content": result})

        if timetables and all(n == "timetable" for n in names) and " and " not in question.lower():
            return "\n\n".join(timetables)

    return "\n\n".join(timetables) or office_contact_response()

def main():
    print(f"\n{SCHOOL_NAME}")
    print("Hi! Have a nice day. How can I help you?")
    print("Type 'exit' to quit.\n")

    history = []

    while True:
        question = input("You: ").strip()

        if question.lower() in {"exit", "quit", "bye"}:
            print("Assistant: Thank you. Have a great day!")
            break

        if not question:
            continue

        try:
            answer = agent_answer(question, history)
            print(f"\nAssistant: {answer}\n")

            history.extend([
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer},
            ])
            history = history[-12:]

        except (mysql.connector.Error, requests.RequestException) as error:
            print(f"\nError connecting to a required service: {error}\n")
        except Exception as error:
            print(f"\nAn error occurred: {error}\n")


if __name__ == "__main__":
    main()