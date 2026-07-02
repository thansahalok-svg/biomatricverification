-- PostgreSQL Database Schema for Biometric Attendance System

-- Create database
-- CREATE DATABASE biometric_attendance;

-- Admins table
CREATE TABLE IF NOT EXISTS admins (
    admin_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(120) UNIQUE,
    full_name VARCHAR(120),
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_admin_username ON admins(username);
CREATE INDEX idx_admin_email ON admins(email);

-- Students table
CREATE TABLE IF NOT EXISTS students (
    student_id SERIAL PRIMARY KEY,
    roll_number VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    phone VARCHAR(20),
    department VARCHAR(100) NOT NULL,
    semester INTEGER NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    biometric_registered BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_student_roll_number ON students(roll_number);
CREATE INDEX idx_student_email ON students(email);
CREATE INDEX idx_student_department ON students(department);

-- WebAuthn Credentials table
CREATE TABLE IF NOT EXISTS webauthn_credentials (
    credential_id VARCHAR(255) PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    public_key BYTEA NOT NULL,
    sign_count INTEGER DEFAULT 0,
    transports JSONB,
    authenticator_type VARCHAR(50),
    registered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_webauthn_student_id ON webauthn_credentials(student_id);

-- Attendance table
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    check_in_time TIME NOT NULL,
    status VARCHAR(20) DEFAULT 'present',
    verification_method VARCHAR(50) DEFAULT 'webauthn',
    device_information VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, date)
);

CREATE INDEX idx_attendance_student_id ON attendance(student_id);
CREATE INDEX idx_attendance_date ON attendance(date);
CREATE INDEX idx_attendance_student_date ON attendance(student_id, date);

-- Attendance Logs table
CREATE TABLE IF NOT EXISTS attendance_logs (
    log_id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(student_id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL,
    success BOOLEAN DEFAULT TRUE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(50),
    user_agent VARCHAR(255),
    device_info VARCHAR(255),
    details VARCHAR(500)
);

CREATE INDEX idx_log_student_id ON attendance_logs(student_id);
CREATE INDEX idx_log_action ON attendance_logs(action);
CREATE INDEX idx_log_timestamp ON attendance_logs(timestamp);

-- Views for reporting

-- Daily attendance report view
CREATE OR REPLACE VIEW attendance_daily_report AS
SELECT 
    a.date,
    s.department,
    COUNT(*) as total_students_present,
    SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) as on_time,
    SUM(CASE WHEN a.status = 'late' THEN 1 ELSE 0 END) as late,
    SUM(CASE WHEN a.status = 'absent' THEN 1 ELSE 0 END) as absent
FROM attendance a
JOIN students s ON a.student_id = s.student_id
GROUP BY a.date, s.department;

-- Student attendance percentage view
CREATE OR REPLACE VIEW student_attendance_percentage AS
SELECT 
    s.student_id,
    s.roll_number,
    s.full_name,
    s.department,
    COUNT(*) as total_days,
    SUM(CASE WHEN a.status IN ('present', 'late') THEN 1 ELSE 0 END) as present_days,
    SUM(CASE WHEN a.status = 'absent' THEN 1 ELSE 0 END) as absent_days,
    ROUND(100.0 * SUM(CASE WHEN a.status IN ('present', 'late') THEN 1 ELSE 0 END) / 
        NULLIF(COUNT(*), 0), 2) as attendance_percentage
FROM students s
LEFT JOIN attendance a ON s.student_id = a.student_id
GROUP BY s.student_id, s.roll_number, s.full_name, s.department;

-- Department-wise attendance view
CREATE OR REPLACE VIEW department_attendance_stats AS
SELECT 
    s.department,
    COUNT(DISTINCT s.student_id) as total_students,
    COUNT(DISTINCT CASE WHEN s.biometric_registered = TRUE THEN s.student_id END) as biometric_registered,
    COUNT(DISTINCT CASE WHEN a.attendance_id IS NOT NULL THEN s.student_id END) as students_present_today,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN a.attendance_id IS NOT NULL THEN s.student_id END) / 
        NULLIF(COUNT(DISTINCT s.student_id), 0), 2) as attendance_percentage_today
FROM students s
LEFT JOIN attendance a ON s.student_id = a.student_id AND a.date = CURRENT_DATE
GROUP BY s.department;
