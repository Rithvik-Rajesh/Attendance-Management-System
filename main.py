"""
Attendance Management System - Web Interface

A Flask web application for managing student attendance.
Features:
- Add/view students and staff
- Display real-time attendance by subject
- Request logging for debugging

Author: Rithvik Rajesh
"""

from flask import Flask, render_template, request, jsonify
import sqlite3
from practice import Student_Details, Add_Staff

# Initialize Flask application
app = Flask(__name__)

# List of endpoints that should not be logged (static assets and internal APIs)
RESERVED_ENDPOINTS = ["/favicon.ico", "/styles.css", "/server/request", 
                       "/addstudents", "/addstaffs", "/students", "/subject"]

# Database path
DATABASE_PATH = 'Attendance.db'
REQUEST_LOG_FILE = 'request_logs.txt'


def init_database():
    """Initialize database with required tables if they don't exist."""
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    
    # Create Students table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Students (
            roll_no TEXT PRIMARY KEY,
            name TEXT,
            email TEXT,
            city TEXT,
            country TEXT,
            phone TEXT,
            dob TEXT
        )
    """)
    
    # Create STAFF table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS STAFF (
            Roll_Number VARCHAR(30) PRIMARY KEY,
            Name CHAR(30) NOT NULL,
            Subject CHAR(30) NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()


@app.before_request
def before_request():
    """Initialize database before first request."""
    init_database()


@app.route("/")
def home():
    """
    Home page - displays list of all staff members.
    Shows welcome page if no staff are registered yet.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    
    try:
        cur.execute('SELECT * FROM STAFF')
        staff_list = cur.fetchall()
        
        if len(staff_list) > 0:
            return render_template("home.html", data=staff_list)
        else:
            # No staff registered yet
            return render_template("No_Staff.html")
    except sqlite3.Error as e:
        return f"Database error: {str(e)}", 500
    finally:
        conn.close()


@app.after_request
def log_request(response):
    """
    Log non-static endpoint requests for debugging.
    Skips reserved endpoints to reduce noise in logs.
    """
    endpoint = request.path
    
    # Only log user-facing endpoints
    is_reserved = (endpoint in RESERVED_ENDPOINTS or 
                   "/subject/" in endpoint)
    
    if not is_reserved:
        try:
            with open(REQUEST_LOG_FILE, 'a') as file:
                file.write(endpoint[1:] + '\n')
        except IOError as e:
            print(f"Warning: Could not write to request log: {str(e)}")
    
    return response


@app.route('/addstudents', methods=['GET', 'POST'])
def add_students():
    """
    Handle GET and POST requests for student registration.
    GET: Display student registration form
    POST: Process student registration form data
    """
    if request.method == 'POST':
        try:
            # Extract form data
            roll_no = request.form.get('rollno', '').strip()
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            city = request.form.get('city', '').strip()
            country = request.form.get('country', '').strip()
            phone = request.form.get('phone', '').strip()
            dob = request.form.get('dofb', '').strip()
            
            # Validate required fields
            if not all([roll_no, name, email, city, country, phone, dob]):
                return render_template("addstudents.html", 
                                      error="All fields are required"), 400
            
            # Add student to database
            conn = sqlite3.connect(DATABASE_PATH)
            cur = conn.cursor()
            Student_Details(conn, cur, roll_no, name, email, city, country, phone, dob)
            conn.close()
            
            return render_template("addstudents.html", 
                                  success="Student added successfully!")
        except sqlite3.IntegrityError:
            return render_template("addstudents.html", 
                                  error="Student with this roll number already exists"), 400
        except Exception as e:
            return render_template("addstudents.html", 
                                  error=f"Error: {str(e)}"), 500
    else:
        return render_template('addstudents.html')


@app.route('/addstaffs', methods=['GET', 'POST'])
def add_staff():
    """
    Handle GET and POST requests for staff registration.
    GET: Display staff registration form
    POST: Process staff registration form data
    """
    if request.method == 'POST':
        try:
            # Extract form data
            roll_no = request.form.get('rollno', '').strip()
            name = request.form.get('name', '').strip()
            subject = request.form.get('subject', '').strip()
            
            # Validate required fields
            if not all([roll_no, name, subject]):
                return render_template("addstaff.html", 
                                      error="All fields are required"), 400
            
            # Add staff to database
            conn = sqlite3.connect(DATABASE_PATH)
            cur = conn.cursor()
            Add_Staff(conn, cur, roll_no, name, subject)
            conn.close()
            
            return render_template("addstaff.html", 
                                  success="Staff member added successfully!")
        except sqlite3.IntegrityError:
            return render_template("addstaff.html", 
                                  error="Staff with this roll number already exists"), 400
        except Exception as e:
            return render_template("addstaff.html", 
                                  error=f"Error: {str(e)}"), 500
    else:
        return render_template('addstaff.html')


@app.route('/students')
def students():
    """Display list of all registered students."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cur = conn.cursor()
        cur.execute('SELECT * FROM Students')
        
        students_list = cur.fetchall()
        return render_template("students.html", data=students_list)
    except sqlite3.Error as e:
        return f"Database error: {str(e)}", 500
    finally:
        conn.close()


@app.route('/subject/<subject_name>')
def display_attendance(subject_name):
    """
    Display attendance records for a specific subject.
    Shows student column headers with attendance status.
    
    Args:
        subject_name: Name of the subject/class
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cur = conn.cursor()
        
        # Fetch attendance records for the subject
        cur.execute(f'SELECT * FROM {subject_name}')
        attendance_records = cur.fetchall()
        
        # Fetch column headers (date/time sessions)
        columns_table = subject_name + "_col"
        cur.execute(f'SELECT * FROM {columns_table}')
        column_headers = cur.fetchall()
        
        return render_template("subject.html", 
                              data=attendance_records, 
                              col=column_headers)
    except sqlite3.Error as e:
        return f"Database error: {str(e)}", 500
    finally:
        conn.close()


@app.route('/server/request', methods=['GET'])
def get_last_scanned():
    """
    API endpoint for Scanner.py to retrieve last scanned roll number.
    Used for real-time attendance updating.
    
    Returns:
        JSON with last scanned roll number or error message
    """
    try:
        with open(REQUEST_LOG_FILE, 'r') as file:
            lines = file.readlines()
            if lines:
                last_line = lines[-1].strip()
                return jsonify({'last_line': last_line}), 200
            else:
                return jsonify({'error': 'No requests yet'}), 404
    except FileNotFoundError:
        return jsonify({'error': 'Request log not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    # Note: For production, use a proper WSGI server like Gunicorn
    # Also, replace hardcoded IP with environment variables
    app.run(host="192.168.21.160", debug=True)