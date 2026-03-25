"""
Student and Attendance Management Module.
Handles student registration, attendance marking, and database operations.
"""
import sqlite3
import datetime
import time
from utilities import get_staff, sanitize_table_name


class AttendanceManager:
    """Manages attendance records and student information."""
    
    def __init__(self, db_path='Attendance.db'):
        """
        Initialize the AttendanceManager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()
    
    def add_student(self, roll_num, name, email, city, country, phone, dob):
        """
        Register a new student in the system.
        Adds student to main Students table and all subject attendance tables.
        
        Args:
            roll_num: Student's roll number
            name: Student's full name
            email: Student's email address
            city: Student's city
            country: Student's country
            phone: Student's phone number
            dob: Student's date of birth
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create Students table
            self.cur.execute("""
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
            
            # Insert student with parameterized query for safety
            self.cur.execute(
                "INSERT INTO Students VALUES (?, ?, ?, ?, ?, ?, ?)",
                (roll_num, name, email, city, country, phone, dob)
            )
            
            # Create or get Attendance table
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS Attendance (
                    roll_no VARCHAR(30) PRIMARY KEY,
                    name TEXT
                )
            """)
            self.cur.execute("INSERT INTO Attendance VALUES (?, ?)", (roll_num, name))
            
            # Add student to all existing subject tables
            try:
                self.cur.execute("SELECT * FROM STAFF")
                staff_list = self.cur.fetchall()
                for staff in staff_list:
                    subject = staff[2]
                    subject_table = sanitize_table_name(subject)
                    self.cur.execute(
                        f"INSERT INTO {subject_table} VALUES (?, ?)",
                        (roll_num, name)
                    )
            except sqlite3.Error:
                # No existing staff/subjects yet
                pass
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding student {roll_num}: {str(e)}")
            return False
    
    def add_staff(self, roll_num, name, subject):
        """
        Register a new staff member (teacher) in the system.
        Creates a subject-specific attendance table.
        
        Args:
            roll_num: Staff member's roll number
            name: Staff member's full name
            subject: Subject they teach
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create STAFF table
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS STAFF (
                    Roll_Number VARCHAR(30) PRIMARY KEY,
                    Name CHAR(30) NOT NULL,
                    Subject CHAR(30) NOT NULL
                )
            """)
            
            # Insert staff with parameterized query
            self.cur.execute("INSERT INTO STAFF VALUES (?, ?, ?)", (roll_num, name, subject))
            
            # Create subject-specific attendance table
            subject_table = sanitize_table_name(subject)
            try:
                self.cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS {subject_table} AS
                    SELECT roll_no, name FROM Students
                """)
            except sqlite3.OperationalError:
                # Table might exist or students table might be empty
                self.cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS {subject_table} (
                        roll_no VARCHAR(30) PRIMARY KEY,
                        name CHAR(30) NOT NULL
                    )
                """)
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding staff {roll_num}: {str(e)}")
            return False
    
    def reset_database(self):
        """
        Delete all tables from the database.
        WARNING: This operation cannot be undone!
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Drop Students table
            try:
                self.cur.execute("DROP TABLE Students")
            except sqlite3.OperationalError:
                pass
            
            # Drop all subject tables
            try:
                self.cur.execute("SELECT * FROM STAFF")
                staff_list = self.cur.fetchall()
                for staff in staff_list:
                    subject = staff[2]
                    subject_table = sanitize_table_name(subject)
                    try:
                        self.cur.execute(f"DROP TABLE {subject_table}")
                        self.cur.execute(f"DROP TABLE {subject_table}_col")
                    except sqlite3.OperationalError:
                        pass
            except sqlite3.OperationalError:
                pass
            
            # Drop STAFF and Attendance tables
            for table in ['STAFF', 'Attendance']:
                try:
                    self.cur.execute(f"DROP TABLE {table}")
                except sqlite3.OperationalError:
                    pass
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error resetting database: {str(e)}")
            return False
    
    def close(self):
        """Close database connection."""
        self.conn.close()


# Keep the old function names for backward compatibility with main.py
def Student_Details(conn, cur, roll_num, name, email, city, country, phone, dob):
    """Legacy function wrapper for add_student."""
    manager = AttendanceManager('Attendance.db')
    manager.add_student(roll_num, name, email, city, country, phone, dob)
    manager.close()


def Add_Staff(conn, cur, roll_num, name, subject):
    """Legacy function wrapper for add_staff."""
    manager = AttendanceManager('Attendance.db')
    manager.add_staff(roll_num, name, subject)
    manager.close()