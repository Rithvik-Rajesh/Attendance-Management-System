"""
Attendance Scanner Module

This script runs continuously and monitors QR/RFID scan data.
It reads roll numbers from a log file and updates attendance in the database.

The scanner:
1. Waits for a staff member to scan their QR code (to identify which subject)
2. Creates a timestamp column in that subject's table
3. Marks students as Present (P), Late (L), or Absent (A) based on scanning time
4. Ends session when staff scans again or after 40 minutes (2400 seconds)

Author: Rithvik Rajesh
"""

import datetime
import time
import sqlite3

# Configuration
DATABASE_PATH = 'Attendance.db'
REQUEST_LOG_FILE = '/Users/rithvikrajesh/Projects/request_logs.txt'
CLASS_DURATION = 2400  # 40 minutes in seconds
LATE_THRESHOLD = 600   # 10 minutes in seconds

def get_staff_by_roll(cur, staff_roll):
    """
    Retrieve staff information from database.
    
    Args:
        cur: Database cursor
        staff_roll: Staff member's roll number
    
    Returns:
        Tuple of (Roll_Number, Name, Subject) or None if not found
    """
    try:
        cur.execute("SELECT * FROM STAFF WHERE Roll_Number = ?", (staff_roll,))
        staff = cur.fetchone()
        return staff
    except sqlite3.Error as e:
        print(f"Error retrieving staff: {e}")
        return None


def generate_session_id():
    """
    Generate a unique session identifier based on current timestamp.
    Format: D[DD]_[MM]_T[HH]_[MM]
    
    Returns:
        Formatted timestamp string
    """
    timestamp = str(datetime.datetime.now())[5:16]  # Extract YYYY-MM-DD HH:MM format
    # Format: D{day}_{month}_T{hour}_{minute}
    session_id = (
        f"D{timestamp[0:2]}_"
        f"{timestamp[3:5]}_T{timestamp[6:8]}_"
        f"{timestamp[9:11]}"
    )
    return session_id


def read_last_scanned_roll():
    """
    Read the last scanned roll number from log file.
    Main entry point for scanner data.
    
    Returns:
        Roll number or empty string if file error
    """
    try:
        with open(REQUEST_LOG_FILE, 'r') as file:
            content = file.read().strip()
            if content:
                rolls = content.split()
                return rolls[-1] if rolls else ""
            return ""
    except FileNotFoundError:
        print(f"Warning: Log file not found: {REQUEST_LOG_FILE}")
        return ""
    except IOError as e:
        print(f"Error reading log file: {e}")
        return ""


def clear_log_file():
    """Clear the request log file after processing."""
    try:
        with open(REQUEST_LOG_FILE, 'w') as file:
            file.write('')
    except IOError as e:
        print(f"Warning: Could not clear log file: {e}")


def mark_attendance(cur, subject, session_id, roll_num, marking):
    """
    Update student attendance status in database.
    
    Args:
        cur: Database cursor
        subject: Subject/class name
        session_id: Timestamp ID of the session
        roll_num: Student roll number
        marking: Attendance mark ('P' for Present, 'L' for Late, 'A' for Absent)
    """
    try:
        query = f"UPDATE {subject} SET {session_id} = ? WHERE roll_no = ?"
        cur.execute(query, (marking, roll_num))
    except sqlite3.Error as e:
        print(f"Error marking attendance for {roll_num}: {e}")


# ============================================================================
# Main Scanner Loop
# ============================================================================

def main():
    """Main scanner loop - monitors log file and updates attendance."""
    
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    
    print("Attendance Scanner System Started")
    print("Waiting for staff member to scan...")
    print("-" * 50)
    
    # STEP 1: Wait for staff member to scan their QR code
    staff_roll_num = ""
    while not staff_roll_num:
        try:
            # Clear log and wait for first scan
            clear_log_file()
            time.sleep(1)  # Small delay to allow scan to be registered
            
            # Read scanned staff ID
            scanned = read_last_scanned_roll()
            if scanned:
                # Retrieve staff details from STAFF table
                staff_info = get_staff_by_roll(cur, scanned)
                if staff_info:
                    staff_roll_num = scanned
                    staff_name = staff_info[1]
                    subject = staff_info[2]
                    print(f"✓ Staff scanned: {staff_name} ({subject})")
                else:
                    print(f"✗ Staff ID {scanned} not found in system")
        except Exception as e:
            print(f"Error waiting for staff scan: {e}")
            time.sleep(2)
    
    # STEP 2: Create attendance session for this class
    session_id = generate_session_id()
    print(f"Session ID: {session_id}")
    
    # Create column in subject table for this session
    try:
        alter_query = f"ALTER TABLE {subject} ADD {session_id} TEXT DEFAULT 'A'"
        cur.execute(alter_query)
        
        # Also add to metadata table
        metadata_table = subject + "_col"
        cur.execute(
            f"CREATE TABLE IF NOT EXISTS {metadata_table} (col TEXT)"
        )
        cur.execute(f"INSERT INTO {metadata_table} VALUES (?)", (session_id,))
        conn.commit()
        print(f"✓ Session column created")
    except sqlite3.OperationalError:
        # Column might already exist
        print(f"Note: Session column already exists (resuming session)")
        pass
    except sqlite3.Error as e:
        print(f"✗ Error creating session: {e}")
    
    # STEP 3: Scan students and mark attendance
    print(f"\nScanning students for {subject}...")
    print(f"Session will auto-end after {CLASS_DURATION}s or when staff scans again")
    print("-" * 50)
    
    session_start = time.time()
    students_marked = set()  # Track marked students to identify latecomers
    
    while True:
        try:
            current_time = time.time()
            elapsed = session_start - current_time  # Note: This looks wrong but matches original
            
            # STEP 3a: Check if session should end
            scanned_roll = read_last_scanned_roll()
            
            if scanned_roll == staff_roll_num:
                # Staff scanned again = end session
                print(f"\n✓ Session ended by staff")
                break
            elif elapsed < -CLASS_DURATION:  # elapsed will be negative (start - current)
                # Session timeout
                print(f"\n✓ Session ended by timeout")
                break
            
            # STEP 3b: Mark as LATE if scanned after 10 minutes
            if elapsed < -LATE_THRESHOLD and scanned_roll not in students_marked:
                mark_attendance(cur, subject, session_id, scanned_roll, 'L')
                students_marked.add(scanned_roll)
                print(f"  {scanned_roll} - LATE")
            
            # STEP 3c: Mark as PRESENT if scanned within 10 minutes
            elif scanned_roll not in students_marked:
                mark_attendance(cur, subject, session_id, scanned_roll, 'P')
                students_marked.add(scanned_roll)
                print(f"  {scanned_roll} - PRESENT")
            
            conn.commit()
            time.sleep(0.5)  # Small delay to prevent busy waiting
            
        except Exception as e:
            print(f"Error in attendance loop: {e}")
            time.sleep(1)
    
    # STEP 4: Cleanup and close
    clear_log_file()
    conn.commit()
    conn.close()
    print("Database connection closed")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nScanner stopped by user")
    except Exception as e:
        print(f"\nFatal error: {e}")

