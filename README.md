# Attendance Management System

**Pull Request Title:** 97486751

## Description

This project is a web-based attendance management system designed to track student attendance in real-time. It uses a Flask web server to manage student and staff data, and a separate Python script to process attendance records. The system is ideal for classrooms or any setting where automated attendance tracking is needed.

## Features

- **Real-time Attendance Tracking**: The system marks attendance as present or late based on when a student's ID is scanned.
- **Web-based Interface**: A simple web interface for managing students and staff, and for viewing attendance records.
- **SQLite Database**: All data is stored in a local SQLite database, making it easy to set up and manage.
- **Dynamic Subject Tables**: Attendance tables are created dynamically for each subject, allowing for flexible class management.

## Project Structure

- `main.py`: The main Flask application that runs the web server and handles all web-related functionalities.
- `Scanner.py`: A script that processes attendance records in real-time by monitoring a log file.
- `Attendance.db`: The SQLite database file where all student, staff, and attendance data is stored.
- `templates/`: This directory contains all the HTML templates used for the web interface.
- `request_logs.txt`: A temporary file used to pass information from the web server to the `Scanner.py` script.

## Setup and Usage

### Prerequisites

- Python 3
- Flask
- SQLite3

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install dependencies:**
   ```bash
   pip install Flask
   ```

### Running the Application

1. **Start the Flask web server:**
   ```bash
   python main.py
   ```
   The server will start on `http://<your-local-ip>:5000`.

2. **Run the attendance scanner:**
   In a separate terminal, run the `Scanner.py` script:
   ```bash
   python Scanner.py
   ```

### How to Use

1. **Add Staff**:
   - Navigate to the "Add Staff" page to add new staff members and the subjects they teach.

2. **Add Students**:
   - Go to the "Add Students" page to register new students with their details.

3. **Take Attendance**:
   - When a staff member starts a session from the main page, the `Scanner.py` script begins monitoring for student check-ins.
   - Students can "check-in" by having their roll number sent to the server (simulated by accessing `http://<your-local-ip>:5000/<roll-number>`).
   - The system marks attendance as "Present" or "Late" based on the time of check-in.

4. **View Attendance**:
   - Attendance records can be viewed by navigating to the subject-specific pages.