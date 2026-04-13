import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "erp.db")

def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    return render_template("login.html")

# =================================================================================

@app.route("/login", methods=["POST"])
def login():

    student_id = request.form["student_id"]
    password = request.form["password"]

    conn = sqlite3.connect("erp.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE student_id=? AND password=?",
                   (student_id, password))

    student = cursor.fetchone()
    conn.close()

    if student:
        session["student_id"] = student_id
        return redirect(url_for("dashboard"))
    else:
        return render_template("login.html", error="Invalid Credentials")
    
# ===================================================================================

@app.route("/dashboard")
def dashboard():

    if "student_id" not in session:
        return redirect(url_for("home"))

    student_id = session["student_id"]

    conn = sqlite3.connect("erp.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Student Info
    cursor.execute("SELECT * FROM students WHERE student_id=?", (student_id,))
    student = cursor.fetchone()

    # CGPA Records
    cursor.execute("""
        SELECT semester, cgpa FROM results
        WHERE student_id=?
        ORDER BY id
    """, (student_id,))
    records = cursor.fetchall()

    conn.close()

    cgpas = [row["cgpa"] for row in records]

    latest_cgpa = cgpas[-1] if cgpas else 0
    previous_cgpa = cgpas[-2] if len(cgpas) > 1 else latest_cgpa
    first_cgpa = cgpas[0] if cgpas else latest_cgpa

    # Trend
    if latest_cgpa > previous_cgpa:
        trend = "Improving ↑"
    elif latest_cgpa < previous_cgpa:
        trend = "Declining ↓"
    else:
        trend = "Stable →"

    # Academic Status
    if latest_cgpa >= 9:
        academic_status = "Excellent"
    elif latest_cgpa >= 8:
        academic_status = "Good"
    else:
        academic_status = "Needs Attention"

    # Scholarship
    scholarship_status = "Eligible (5%)" if latest_cgpa >= 9 else "Not Eligible"

    # Improvement %
    improvement = round(((latest_cgpa - first_cgpa) / first_cgpa) * 100, 2) if first_cgpa else 0

    # AI Confidence (simple score logic)
    confidence_score = min(95, max(70, int(latest_cgpa * 10)))

    # Smart Alerts (ONLY meaningful)
    alerts = []

    if latest_cgpa > previous_cgpa:
        alerts.append(f"CGPA improved by {round(latest_cgpa - previous_cgpa,2)} since last semester.")

    if latest_cgpa < previous_cgpa:
        alerts.append("Performance drop detected. Consider academic review.")

    if latest_cgpa >= 9:
        alerts.append("Scholarship eligibility activated.")

    if not alerts:
        alerts.append("Academic performance stable.")

    return render_template("dashboard.html",
                           student=student,
                           latest_cgpa=latest_cgpa,
                           academic_status=academic_status,
                           trend=trend,
                           scholarship_status=scholarship_status,
                           improvement=improvement,
                           confidence_score=confidence_score,
                           alerts=alerts)  

# ===============================================================================================

@app.route("/fee")
def fee():

    if "student_id" not in session:
        return redirect(url_for("home"))

    student_id = session["student_id"]

    conn = sqlite3.connect("erp.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get latest CGPA
    cursor.execute("""
        SELECT cgpa FROM results 
        WHERE student_id=? 
        ORDER BY id DESC LIMIT 1
    """, (student_id,))
    result = cursor.fetchone()

    cgpa = result["cgpa"] if result else 0

    # Get latest fee record
    cursor.execute("""
        SELECT * FROM fees 
        WHERE student_id=? 
        ORDER BY id DESC LIMIT 1
    """, (student_id,))
    fee_record = cursor.fetchone()

    conn.close()

    if not fee_record:
        return "No Fee Record Found"

    academic_fee = fee_record["academic_fee"]
    previous_due = fee_record["previous_due"]

    # Scholarship Logic
    scholarship = academic_fee * 0.05 if cgpa >= 9 else 0

    final_fee = academic_fee - scholarship
    total_payable = final_fee + previous_due

    no_due = True if previous_due == 0 else False

    return render_template("fee.html",
                           academic_fee=academic_fee,
                           cgpa=cgpa,
                           scholarship=scholarship,
                           previous_due=previous_due,
                           total_payable=total_payable,
                           no_due=no_due)

# ==========================================================================================

@app.route("/profile")
def profile():

    if "student_id" not in session:
        return redirect(url_for("home"))

    student_id = session["student_id"]

    conn = sqlite3.connect("erp.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE student_id=?",
                   (student_id,))
    student = cursor.fetchone()

    conn.close()

    return render_template("profile.html", student=student)

# ============================================================================================

@app.route("/scholarship-history")
def scholarship_history():

    if "student_id" not in session:
        return redirect(url_for("home"))

    student_id = session["student_id"]

    conn = sqlite3.connect("erp.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT semester, cgpa
        FROM results
        WHERE student_id=?
        ORDER BY semester
    """, (student_id,))

    records = cursor.fetchall()
    conn.close()

    year_data = {}

    for row in records:
        semester_str = row["semester"]       
        semester = int(semester_str.split()[1]) 

        cgpa = float(row["cgpa"])

        academic_year = (semester - 1) // 2 + 1

        if academic_year not in year_data:
            year_data[academic_year] = []

        year_data[academic_year].append(cgpa)

    history = []

    for year, cgpas in year_data.items():
        avg_cgpa = round(sum(cgpas) / len(cgpas), 2)

        if avg_cgpa >= 9:
            percent = 5
            amount = 8000
        else:
            percent = 0
            amount = 0

        history.append({
            "year": f"Year {year}",
            "cgpa": avg_cgpa,
            "percent": percent,
            "amount": amount
        })

    return render_template("scholarship_history.html", history=history)

# ========================================================================================

@app.route("/payment")
def payment():
    if "student_id" not in session:
        return redirect(url_for("home"))

    return render_template("payment.html")


import uuid
import datetime

# ========================================================================================

@app.route("/payment-success")
def payment_success():

    if "student_id" not in session:
        return redirect(url_for("home"))

    student_id = session["student_id"]

    conn = sqlite3.connect("erp.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get latest fee record
    cursor.execute("""
        SELECT * FROM fees
        WHERE student_id=?
        ORDER BY id DESC LIMIT 1
    """, (student_id,))
    fee_record = cursor.fetchone()

    if not fee_record:
        conn.close()
        return "No Fee Record Found"

    previous_due = fee_record["previous_due"]

    # Generate Transaction ID
    transaction_id = str(uuid.uuid4())[:8]

    today = datetime.date.today().strftime("%d-%m-%Y")

    # Insert into payments table
    cursor.execute("""
        INSERT INTO payments (student_id, transaction_id, amount, date)
        VALUES (?, ?, ?, ?)
    """, (student_id, transaction_id, previous_due, today))

    # Update fees table → clear due
    cursor.execute("""
        UPDATE fees
        SET previous_due=0
        WHERE id=?
    """, (fee_record["id"],))

    conn.commit()
    conn.close()

    return render_template("payment_success.html",transaction_id=transaction_id,amount=previous_due)

# ========================================================================================================

@app.route("/payment-history")
def payment_history():

    if "student_id" not in session:
        return redirect(url_for("home"))

    student_id = session["student_id"]

    conn = sqlite3.connect("erp.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT transaction_id, amount, date
        FROM payments
        WHERE student_id=?
        ORDER BY id DESC
    """, (student_id,))

    payments = cursor.fetchall()
    conn.close()

    return render_template("payment_history.html", payments=payments)

# =======================================================================================

@app.route("/cgpa-trend")
def cgpa_trend():

    if "student_id" not in session:
        return redirect(url_for("home"))

    student_id = session["student_id"]

    conn = sqlite3.connect("erp.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT semester, cgpa
        FROM results
        WHERE student_id=?
        ORDER BY id
    """, (student_id,))

    records = cursor.fetchall()
    conn.close()

    semesters = []
    cgpas = []

    # 🔥 Convert to Year-Sem format
    for index, row in enumerate(records, start=1):
        if index > 8:   # Safety check (B.Tech max 8 sem)
            break
        year = (index - 1) // 2 + 1     
        sem_in_year = 1 if index % 2 != 0 else 2

        semesters.append(f"Y{year}-S{sem_in_year}")
        cgpas.append(float(row["cgpa"]))

    improvement = 0
    performance = "No Data"
    scholarship_status = "Not Eligible"
    trend_text = "No Data"
    trend_class = "trend-stable"

    if len(cgpas) >= 2:
        improvement = round(cgpas[-1] - cgpas[-2], 2)

        if improvement > 0:
            trend_text = "Improving ↑"
            trend_class = "trend-up"
        elif improvement < 0:
            trend_text = "Slight Decline ↓"
            trend_class = "trend-down"
        else:
            trend_text = "Stable →"
            trend_class = "trend-stable"

    if cgpas:
        latest = cgpas[-1]

        if latest >= 9:
            performance = "Excellent"
            scholarship_status = "Eligible for 5% Scholarship"
        elif latest >= 8:
            performance = "Good"
        else:
            performance = "Needs Improvement"

    return render_template("cgpa_trend.html",
                           semesters=semesters,
                           cgpas=cgpas,
                           improvement=improvement,
                           performance=performance,
                           scholarship_status=scholarship_status,
                           trend_text=trend_text,
                           trend_class=trend_class)

# ==================================================================================   

@app.route("/logout")
def logout():
    session.pop("student_id", None)
    return redirect(url_for("home"))

# ==================================================================================

@app.route("/ai-prediction")
def ai_prediction():

    if "student_id" not in session:
        return redirect(url_for("home"))

    student_id = session["student_id"]

    conn = sqlite3.connect("erp.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT cgpa FROM results
        WHERE student_id=?
        ORDER BY id DESC LIMIT 3
    """, (student_id,))

    records = cursor.fetchall()
    conn.close()

    cgpas = [row["cgpa"] for row in records]

    if len(cgpas) == 0:
        prediction = "No academic records found."

    elif len(cgpas) == 1:
        prediction = "More semesters required for AI prediction."

    elif cgpas[0] > cgpas[1]:
        prediction = "Performance Improving 📈 - High Scholarship Probability"

    elif cgpas[0] < cgpas[1]:
        prediction = "Performance Dropping ⚠ - Risk of Losing Scholarship"

    else:
        prediction = "Stable Performance"

    return render_template("ai_prediction.html", prediction=prediction)


if __name__ == "__main__":
    app.run(debug=True)