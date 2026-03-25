"""
Utility functions for the Attendance Management System.
Provides database operations for staff management.
"""
import sqlite3


def get_staff(cur, staff_rollno):
    """
    Retrieve staff information by roll number.
    
    Args:
        cur: Database cursor object
        staff_rollno: Staff member's roll number (string)
    
    Returns:
        Tuple containing staff details (Roll_Number, Name, Subject)
        Returns None if staff not found
    """
    try:
        # Use parameterized query to prevent SQL injection
        cur.execute("SELECT * FROM STAFF WHERE Roll_Number = ?", (staff_rollno,))
        staff = cur.fetchone()
        return staff
    except Exception as e:
        print(f"Error retrieving staff with roll number {staff_rollno}: {str(e)}")
        return None


def add_staff(conn, cur, roll_num, name, subject):
    """
    Add a new staff member to the database.
    Creates a separate attendance table for each subject.
    
    Args:
        conn: Database connection object
        cur: Database cursor object
        roll_num: Staff member's roll number (string)
        name: Staff member's full name (string)
        subject: Subject taught (string)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create STAFF table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS STAFF (
                Roll_Number VARCHAR(30) PRIMARY KEY,
                Name CHAR(30) NOT NULL,
                Subject CHAR(30) NOT NULL
            )
        """)
        
        # Insert staff member with parameterized query
        cur.execute("INSERT INTO STAFF VALUES (?, ?, ?)", (roll_num, name, subject))
        
        # Create a subject-specific attendance table if needed
        subject_table_name = sanitize_table_name(subject)
        try:
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {subject_table_name} AS 
                SELECT roll_no, name FROM Students
            """)
        except sqlite3.OperationalError:
            # Table might not have students yet, create empty structure
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {subject_table_name} (
                    roll_no VARCHAR(30) PRIMARY KEY,
                    name CHAR(30) NOT NULL
                )
            """)
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding staff: {str(e)}")
        return False


def sanitize_table_name(name):
    """
    Sanitize table names to prevent SQL injection via table names.
    Converts subject names to valid SQL identifiers.
    
    Args:
        name: Original table name (string)
    
    Returns:
        Sanitized table name (string)
    """
    # Replace spaces and special characters with underscores
    sanitized = ''.join(c if c.isalnum() else '_' for c in name)
    # Ensure it doesn't start with a number
    if sanitized[0].isdigit():
        sanitized = '_' + sanitized
    return sanitized