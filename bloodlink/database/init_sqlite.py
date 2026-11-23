import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "bloodlink.sqlite3")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executescript("""
    DROP TABLE IF EXISTS audit_log;
    DROP TABLE IF EXISTS alert;
    DROP TABLE IF EXISTS blood_allocation;
    DROP TABLE IF EXISTS donor_match;
    DROP TABLE IF EXISTS emergency_request;
    DROP TABLE IF EXISTS inventory;
    DROP TABLE IF EXISTS blood_unit;
    DROP TABLE IF EXISTS donation;
    DROP TABLE IF EXISTS hospital;
    DROP TABLE IF EXISTS blood_bank;
    DROP TABLE IF EXISTS donor;
    DROP TABLE IF EXISTS blood_group;
    DROP TABLE IF EXISTS "user";
    DROP TABLE IF EXISTS location;

    CREATE TABLE location (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT NOT NULL,
        state TEXT NOT NULL,
        country TEXT NOT NULL,
        zip_code TEXT,
        UNIQUE (city, state, country, zip_code)
    );

    CREATE TABLE "user" (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        full_name TEXT,
        role TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        location_id INTEGER REFERENCES location(id)
    );

    CREATE TABLE blood_group (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_name TEXT NOT NULL UNIQUE,
        rh_factor TEXT NOT NULL CHECK (rh_factor IN ('+', '-'))
    );

    CREATE TABLE donor (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL UNIQUE REFERENCES "user"(id),
        date_of_birth DATE NOT NULL,
        gender TEXT CHECK (gender IN ('Male', 'Female', 'Other')),
        registration_number TEXT NOT NULL UNIQUE,
        last_donation_date DATE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        location_id INTEGER REFERENCES location(id)
    );

    CREATE TABLE blood_bank (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        address TEXT NOT NULL,
        location_id INTEGER REFERENCES location(id),
        contact_number TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE hospital (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        address TEXT NOT NULL,
        location_id INTEGER REFERENCES location(id),
        contact_number TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE donation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        donor_id INTEGER NOT NULL REFERENCES donor(id),
        donation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        volume_ml INTEGER NOT NULL CHECK (volume_ml > 0),
        notes TEXT
    );

    CREATE TABLE blood_unit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        donation_id INTEGER NOT NULL REFERENCES donation(id),
        blood_bank_id INTEGER NOT NULL REFERENCES blood_bank(id),
        blood_group_id INTEGER NOT NULL REFERENCES blood_group(id),
        collection_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        expiry_date DATETIME NOT NULL,
        status TEXT NOT NULL DEFAULT 'AVAILABLE' CHECK (status IN ('AVAILABLE','RESERVED','ALLOCATED','EXPIRED','DISCARDED'))
    );

    CREATE TABLE inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        blood_bank_id INTEGER NOT NULL REFERENCES blood_bank(id),
        blood_group_id INTEGER NOT NULL REFERENCES blood_group(id),
        units_available INTEGER NOT NULL DEFAULT 0,
        units_reserved INTEGER NOT NULL DEFAULT 0,
        minimum_threshold INTEGER NOT NULL DEFAULT 0,
        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (blood_bank_id, blood_group_id)
    );

    CREATE TABLE emergency_request (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hospital_id INTEGER NOT NULL REFERENCES hospital(id),
        blood_group_id INTEGER NOT NULL REFERENCES blood_group(id),
        required_units INTEGER NOT NULL CHECK (required_units > 0),
        urgency_level TEXT NOT NULL CHECK (urgency_level IN ('LOW','MEDIUM','HIGH','CRITICAL')),
        status TEXT NOT NULL DEFAULT 'OPEN' CHECK (status IN ('OPEN','FULFILLED','CANCELLED')),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        deadline DATETIME
    );

    -- Sample Seed Data
    INSERT INTO location (city, state, country, zip_code) VALUES
        ('Bengaluru', 'Karnataka', 'India', '560001'),
        ('Mumbai', 'Maharashtra', 'India', '400001'),
        ('Delhi', 'Delhi', 'India', '110001');

    INSERT INTO blood_group (group_name, rh_factor) VALUES
        ('A+', '+'), ('A-', '-'),
        ('B+', '+'), ('B-', '-'),
        ('AB+', '+'), ('AB-', '-'),
        ('O+', '+'), ('O-', '-');

    INSERT INTO "user" (username, email, password_hash, full_name, role, location_id) VALUES
        ('rajesh_k', 'rajesh@example.com', 'hash123', 'Rajesh Kumar', 'donor', 1),
        ('priya_s', 'priya@example.com', 'hash123', 'Priya Sharma', 'donor', 1),
        ('anil_m', 'anil@example.com', 'hash123', 'Anil Mehta', 'donor', 2),
        ('staff_bb1', 'staff@citybank.org', 'hash123', 'Vikram Sen', 'staff', 1);

    INSERT INTO donor (user_id, date_of_birth, gender, registration_number, last_donation_date, location_id) VALUES
        (1, '1998-05-12', 'Male', 'DON-2026-081', '2026-06-15', 1),
        (2, '2001-08-24', 'Female', 'DON-2026-144', '2026-05-10', 1),
        (3, '1995-11-03', 'Male', 'DON-2026-209', '2026-10-30', 2);

    INSERT INTO blood_bank (name, address, location_id, contact_number) VALUES
        ('City Central Blood Bank', 'MG Road, Central', 1, '+91-80-22223333'),
        ('LifeCare Blood Centre', 'Indiranagar 100ft Rd', 1, '+91-80-44445555'),
        ('Metro Red Cross Bank', 'Nariman Point', 2, '+91-22-66667777');

    INSERT INTO hospital (name, address, location_id, contact_number) VALUES
        ('Apex Heart & Trauma Hospital', 'Koramangala 4th Block', 1, '+91-80-88889999'),
        ('St. Jude Memorial Hospital', 'Whitefield Main Rd', 1, '+91-80-77778888'),
        ('Lilavati Super Specialty', 'Bandra West', 2, '+91-22-55556666');

    INSERT INTO donation (donor_id, donation_date, volume_ml, notes) VALUES
        (1, '2026-11-10 10:00:00', 450, 'Regular donation - excellent vitals'),
        (2, '2026-11-12 11:30:00', 350, 'First time voluntary blood camp');

    INSERT INTO blood_unit (donation_id, blood_bank_id, blood_group_id, collection_date, expiry_date, status) VALUES
        (1, 1, 7, '2026-11-10 10:00:00', '2026-12-15 10:00:00', 'AVAILABLE'),
        (1, 1, 8, '2026-11-10 10:00:00', '2026-11-28 10:00:00', 'AVAILABLE'),
        (2, 2, 5, '2026-11-12 11:30:00', '2026-11-27 11:30:00', 'AVAILABLE'),
        (2, 2, 1, '2026-11-12 11:30:00', '2026-12-20 11:30:00', 'AVAILABLE');

    INSERT INTO inventory (blood_bank_id, blood_group_id, units_available, units_reserved, minimum_threshold) VALUES
        (1, 7, 45, 5, 20), -- O+
        (1, 8, 8, 2, 10),  -- O-
        (1, 1, 15, 3, 10), -- A+
        (2, 5, 12, 1, 8),  -- AB+
        (2, 1, 24, 4, 15), -- A+
        (3, 3, 30, 2, 15); -- B+

    INSERT INTO emergency_request (hospital_id, blood_group_id, required_units, urgency_level, status, created_at, deadline) VALUES
        (1, 8, 4, 'CRITICAL', 'OPEN', '2026-11-23 07:00:00', '2026-11-23 14:00:00'),
        (2, 5, 2, 'HIGH', 'OPEN', '2026-11-23 08:00:00', '2026-11-23 20:00:00'),
        (3, 3, 5, 'MEDIUM', 'OPEN', '2026-11-22 18:00:00', '2026-11-24 18:00:00');
    """)

    conn.commit()
    conn.close()
    print("SQLite database initialized successfully at:", DB_PATH)

if __name__ == "__main__":
    init_db()
