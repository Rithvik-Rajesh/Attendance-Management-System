# Attendance Management System

A Flask-based web application for managing student attendance using QR or RFID scanning. The system records attendance in real time and classifies students as Present (P), Late (L), or Absent (A).

## Overview

This was my first software project while learning Python and web development. It works, but it also reflects beginner design choices. This README explains what the project does and how I would improve it if building it today.

## Features

- Real-time attendance tracking
- Web interface to add staff and students
- Subject-wise attendance records
- SQLite-based local storage
- Session timeout and late marking logic

## Project Structure

- `main.py`: Flask web app and routes
- `Scanner.py`: Attendance scanner process
- `practice.py`: Student and staff management logic
- `utilities.py`: Shared DB utility functions
- `reset.py`: Database reset utility
- `templates/`: HTML templates for UI
- `Attendance.db`: SQLite database
- `request_logs.txt`: Runtime log used by scanner flow

## Getting Started

### Prerequisites

- Python 3.x
- Flask 3.x
- SQLite3

### Installation

1. Activate virtual environment:

```bash
source virt/bin/activate
```

2. Run the web application:

```bash
python main.py
```

3. Run the scanner in another terminal:

```bash
python Scanner.py
```

## Quick Usage

1. Add staff via `/addstaffs`
2. Add students via `/addstudents`
3. Start `Scanner.py`
4. Scan staff ID to start a class session
5. Scan student IDs to mark attendance

## Database Schema

### Students

- `roll_no` (PK)
- `name`
- `email`
- `city`
- `country`
- `phone`
- `dob`

### STAFF

- `Roll_Number` (PK)
- `Name`
- `Subject`

### Subject Tables

For each subject, a table is created dynamically with student list and session columns.

### Subject Metadata Tables

For each subject, `[subject]_col` stores session column names.

## API Endpoints

- `GET /`: Home page
- `GET/POST /addstudents`: Register student
- `GET/POST /addstaffs`: Register staff
- `GET /students`: View students
- `GET /subject/<name>`: View attendance by subject
- `GET /server/request`: Scanner helper endpoint

## What Was Beginner-Level (And How To Improve)

### 1. SQL Query Construction

- Old approach used string interpolation in SQL
- Better approach is parameterized queries to prevent SQL injection

### 2. Broad Exception Handling

- Old code used many `except:` blocks
- Better approach is catching specific exceptions and logging useful error messages

### 3. Hardcoded Paths and Host

- Old code had machine-specific absolute paths and IPs
- Better approach is environment-based configuration

### 4. File-Based Process Communication

- Old flow used a text file for process communication
- Better approach is Redis, queue, or websocket-based messaging

### 5. Limited Input Validation

- Old code accepted raw form input with minimal checks
- Better approach is stricter validation and normalization for all fields

### 6. Flat Structure

- Logic spread across scripts with limited separation of concerns
- Better approach is layered modules (`routes`, `services`, `models`, `config`)

## If I Rebuilt It Today

- Use SQLAlchemy ORM + migrations
- Add authentication and role-based access
- Add unit and integration tests
- Replace file IPC with Redis or queue system
- Add structured logging
- Use `.env` configuration
- Containerize with Docker

## Security Notes

Current project is educational and local-first. Before production usage, add:

- Authentication and authorization
- HTTPS
- Input validation hardening
- Rate limiting
- Secret management
- Backup and recovery strategy

## Key Lessons Learned

1. Use parameterized SQL everywhere
2. Do not hide errors with bare exceptions
3. Validate every user input
4. Keep concerns separated in code structure
5. Avoid hardcoded environment-specific values
6. Add tests early
7. Keep docs accurate and simple

## Status

- Built with Flask, SQLite, Python 3.11
- Refactored for improved readability and safety
- Maintained as a learning-focused project
