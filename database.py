import sqlite3
import datetime

# ======================
# CONNECT DATABASE
# ======================

conn = sqlite3.connect("erp.db")
cursor = conn.cursor()

# Enable Foreign Key Support
cursor.execute("PRAGMA foreign_keys = ON")

# ======================
# CREATE TABLES (SAFE MODE)
# ======================

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    student_id TEXT PRIMARY KEY,
    password TEXT,
    name TEXT,
    department TEXT,
    course TEXT,
    year TEXT,
    semester TEXT,
    admission_no TEXT,
    enrollment_no TEXT,
    father_name TEXT,
    dob TEXT,
    email TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS fees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    academic_fee REAL,
    previous_due REAL,
    total_fee REAL,
    year TEXT,
    semester TEXT,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    amount REAL,
    date TEXT,
    transaction_id TEXT,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    semester TEXT,
    cgpa REAL,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS scholarship_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    year TEXT,
    cgpa REAL,
    percentage INTEGER,
    amount REAL,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
)
""")

# ======================
# STUDENT DATA
# ======================

students_data = [

("23131011071","Strong@123","Liam Anderson","CSE","B.Tech","2nd Year","4th Semester","GU2023CSE071","23131011071","Michael Anderson","2005-02-15","liam@email.com"),
("23131011072","Strong@123","Olivia Bennett","CSE","B.Tech","2nd Year","4th Semester","GU2023CSE072","23131011072","Daniel Bennett","2005-05-21","olivia@email.com"),
("23131011073","Strong@123","Noah Carter","CSE","B.Tech","2nd Year","4th Semester","GU2023CSE073","23131011073","James Carter","2004-11-12","noah@email.com"),
("23131011074","Strong@123","Emma Davis","CSE","B.Tech","2nd Year","4th Semester","GU2023CSE074","23131011074","Robert Davis","2005-08-30","emma@email.com"),
("23131011075","Strong@123","William Evans","CSE","B.Tech","2nd Year","4th Semester","GU2023CSE075","23131011075","Joseph Evans","2004-03-19","william@email.com"),
("23131011076","Strong@123","Sophia Foster","CSE","B.Tech","2nd Year","4th Semester","GU2023CSE076","23131011076","Anthony Foster","2005-06-09","sophia@email.com"),
("23131011077","Strong@123","James Green","CSE","B.Tech","2nd Year","4th Semester","GU2023CSE077","23131011077","Christopher Green","2005-01-28","james@email.com"),
("23131011078","Strong@123","Isabella Harris","CSE","B.Tech","2nd Year","4th Semester","GU2023CSE078","23131011078","Matthew Harris","2004-09-17","isabella@email.com"),
("23131011079","Strong@123","Benjamin Johnson","CSE","B.Tech","2nd Year","4th Semester","GU2023CSE079","23131011079","Andrew Johnson","2005-12-03","benjamin@email.com"),
("231310110710","Strong@123","Mia King","CSE","B.Tech","2nd Year","4th Semester","GU2023CSE0710","231310110710","David King","2005-04-14","mia@email.com"),
]

# Insert Students (Safe Insert)
for student in students_data:
    cursor.execute("""
    INSERT OR IGNORE INTO students
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, student)

# ======================
# INSERT FEES + RESULTS + SCHOLARSHIP
# ======================

cgpa_sets = [
[9.2, 9.1, 9.3, 9.4],
[8.7, 8.9, 9.0, 9.1],
[7.8, 8.0, 8.2, 8.5],
[9.5, 9.6, 9.4, 9.3],
[8.2, 8.3, 8.4, 8.6],
[7.5, 7.8, 8.0, 8.1],
[9.0, 9.2, 9.1, 9.3],
[8.8, 8.9, 9.1, 9.2],
[7.9, 8.1, 8.4, 8.7],
[9.3, 9.4, 9.5, 9.6]
]

for i, student in enumerate(students_data):

    sid = student[0]
    academic_fee = 160000
    previous_due = (i+1) * 1000
    total_fee = academic_fee + previous_due

    cursor.execute("""
    INSERT INTO fees (student_id, academic_fee, previous_due, total_fee, year, semester)
    VALUES (?,?,?,?,?,?)
    """, (sid, academic_fee, previous_due, total_fee, "2nd Year", "4th Semester"))

    for sem_index, cgpa in enumerate(cgpa_sets[i]):

        cursor.execute("""
        INSERT INTO results (student_id, semester, cgpa)
        VALUES (?,?,?)
        """, (sid, f"Sem {sem_index+1}", cgpa))

        percent = 5 if cgpa >= 9 else 0
        amount = academic_fee * (percent/100)

        cursor.execute("""
        INSERT INTO scholarship_history
        (student_id, year, cgpa, percentage, amount)
        VALUES (?,?,?,?,?)
        """, (sid, f"Year {sem_index+1}", cgpa, percent, amount))

conn.commit()
conn.close()

print("✅ 10 Professional Students Added Successfully")