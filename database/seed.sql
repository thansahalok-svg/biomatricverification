-- Insert default admin user
-- Note: Change these credentials in production!
-- Password is hashed using bcrypt: admin123

INSERT INTO admins (username, password_hash, email, full_name)
VALUES (
    'admin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5EQUZqK9QYF/6',
    'admin@biometricattendance.com',
    'System Administrator'
) ON CONFLICT (username) DO NOTHING;

-- Insert sample students
INSERT INTO students (roll_number, full_name, email, phone, department, semester, password_hash, is_active)
VALUES 
    ('CS001', 'Arun Kumar', 'arun@example.com', '9876543210', 'Computer Science', 4, '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5EQUZqK9QYF/6', TRUE),
    ('CS002', 'Priya Singh', 'priya@example.com', '9876543211', 'Computer Science', 4, '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5EQUZqK9QYF/6', TRUE),
    ('EC001', 'Raj Patel', 'raj@example.com', '9876543212', 'Electronics', 3, '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5EQUZqK9QYF/6', TRUE),
    ('EC002', 'Neha Verma', 'neha@example.com', '9876543213', 'Electronics', 3, '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5EQUZqK9QYF/6', TRUE),
    ('ME001', 'Vikram Singh', 'vikram@example.com', '9876543214', 'Mechanical', 2, '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5EQUZqK9QYF/6', TRUE)
ON CONFLICT (roll_number) DO NOTHING;
