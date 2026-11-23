-- PostgreSQL schema for BloodLink
-- This script creates all required tables and constraints in 3NF.

-- 1. LOCATION: stores geographic locations (city, state, country).
CREATE TABLE location (
    id SERIAL PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    zip_code VARCHAR(20),
    UNIQUE (city, state, country, zip_code)
);

-- 2. USER: system users (admin, staff, etc.).
CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    location_id INTEGER REFERENCES location(id) ON DELETE SET NULL ON UPDATE CASCADE
);

-- 3. BLOOD_GROUP: predefined blood groups.
CREATE TABLE blood_group (
    id SERIAL PRIMARY KEY,
    group_name VARCHAR(3) NOT NULL UNIQUE, -- e.g., 'A+', 'O-'
    rh_factor CHAR(1) NOT NULL CHECK (rh_factor IN ('+', '-'))
);

-- 4. DONOR: person who donates blood.
CREATE TABLE donor (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES "user"(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(10) CHECK (gender IN ('Male', 'Female', 'Other')),
    registration_number VARCHAR(30) NOT NULL UNIQUE,
    last_donation_date DATE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    location_id INTEGER REFERENCES location(id) ON DELETE SET NULL ON UPDATE CASCADE
);

-- 5. BLOOD_BANK: entity that stores blood units.
CREATE TABLE blood_bank (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    address VARCHAR(255) NOT NULL,
    location_id INTEGER REFERENCES location(id) ON DELETE SET NULL ON UPDATE CASCADE,
    contact_number VARCHAR(30),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 6. HOSPITAL: hospitals that request blood.
CREATE TABLE hospital (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    address VARCHAR(255) NOT NULL,
    location_id INTEGER REFERENCES location(id) ON DELETE SET NULL ON UPDATE CASCADE,
    contact_number VARCHAR(30),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 7. DONATION: a donor's donation event.
CREATE TABLE donation (
    id SERIAL PRIMARY KEY,
    donor_id INTEGER NOT NULL REFERENCES donor(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    donation_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    volume_ml INTEGER NOT NULL CHECK (volume_ml > 0),
    notes TEXT
);

-- 8. BLOOD_UNIT: individual units derived from a donation.
CREATE TABLE blood_unit (
    id SERIAL PRIMARY KEY,
    donation_id INTEGER NOT NULL REFERENCES donation(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    blood_bank_id INTEGER NOT NULL REFERENCES blood_bank(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    blood_group_id INTEGER NOT NULL REFERENCES blood_group(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    collection_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expiry_date TIMESTAMP NOT NULL CHECK (expiry_date > collection_date),
    status VARCHAR(20) NOT NULL DEFAULT 'AVAILABLE',
    CHECK (status IN ('AVAILABLE','RESERVED','ALLOCATED','EXPIRED','DISCARDED')),
    UNIQUE (donation_id, blood_group_id, collection_date) -- avoid duplicate units for same donation
);

-- 9. INVENTORY: aggregate view per bank & blood group.
CREATE TABLE inventory (
    id SERIAL PRIMARY KEY,
    blood_bank_id INTEGER NOT NULL REFERENCES blood_bank(id) ON DELETE CASCADE ON UPDATE CASCADE,
    blood_group_id INTEGER NOT NULL REFERENCES blood_group(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    units_available INTEGER NOT NULL DEFAULT 0 CHECK (units_available >= 0),
    units_reserved INTEGER NOT NULL DEFAULT 0 CHECK (units_reserved >= 0),
    minimum_threshold INTEGER NOT NULL DEFAULT 0 CHECK (minimum_threshold >= 0),
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (blood_bank_id, blood_group_id)
);

-- 10. EMERGENCY_REQUEST: request from a hospital for blood.
CREATE TABLE emergency_request (
    id SERIAL PRIMARY KEY,
    hospital_id INTEGER NOT NULL REFERENCES hospital(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    blood_group_id INTEGER NOT NULL REFERENCES blood_group(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    required_units INTEGER NOT NULL CHECK (required_units > 0),
    urgency_level VARCHAR(20) NOT NULL CHECK (urgency_level IN ('LOW','MEDIUM','HIGH','CRITICAL')),
    status VARCHAR(20) NOT NULL DEFAULT 'OPEN',
    CHECK (status IN ('OPEN','FULFILLED','CANCELLED')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deadline TIMESTAMP
);

-- 11. DONOR_MATCH: matches donors to an emergency request based on blood group and location.
CREATE TABLE donor_match (
    id SERIAL PRIMARY KEY,
    emergency_request_id INTEGER NOT NULL REFERENCES emergency_request(id) ON DELETE CASCADE ON UPDATE CASCADE,
    donor_id INTEGER NOT NULL REFERENCES donor(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    match_score NUMERIC(5,2) NOT NULL CHECK (match_score >= 0 AND match_score <= 100),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (emergency_request_id, donor_id)
);

-- 12. BLOOD_ALLOCATION: allocation of specific blood units to a request.
CREATE TABLE blood_allocation (
    id SERIAL PRIMARY KEY,
    emergency_request_id INTEGER NOT NULL REFERENCES emergency_request(id) ON DELETE CASCADE ON UPDATE CASCADE,
    blood_unit_id INTEGER NOT NULL REFERENCES blood_unit(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    allocated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    UNIQUE (emergency_request_id, blood_unit_id)
);

-- 13. ALERT: system alerts for low inventory, expiration, etc.
CREATE TABLE alert (
    id SERIAL PRIMARY KEY,
    blood_bank_id INTEGER REFERENCES blood_bank(id) ON DELETE CASCADE ON UPDATE CASCADE,
    blood_group_id INTEGER REFERENCES blood_group(id) ON DELETE SET NULL ON UPDATE CASCADE,
    alert_type VARCHAR(50) NOT NULL CHECK (alert_type IN ('LOW_INVENTORY','EXPIRING_UNIT','DISCARDED_UNIT')),
    message TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN NOT NULL DEFAULT FALSE
);

-- 14. AUDIT_LOG: record of critical actions.
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES "user"(id) ON DELETE SET NULL ON UPDATE CASCADE,
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(50),
    record_id INTEGER,
    description TEXT,
    performed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for frequent look‑ups
CREATE INDEX idx_blood_unit_status ON blood_unit(status);
CREATE INDEX idx_inventory_bank_group ON inventory(blood_bank_id, blood_group_id);
CREATE INDEX idx_emergency_request_status ON emergency_request(status);
CREATE INDEX idx_donor_location ON donor(location_id);
CREATE INDEX idx_hospital_location ON hospital(location_id);
CREATE INDEX idx_blood_bank_location ON blood_bank(location_id);

-- Triggers to keep inventory in sync (simplified example)
-- When a blood unit status changes to AVAILABLE, RESERVED, or ALLOCATED we update inventory.
CREATE OR REPLACE FUNCTION update_inventory_on_status_change() RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        IF NEW.status = 'AVAILABLE' THEN
            UPDATE inventory SET units_available = units_available + 1, last_updated = CURRENT_TIMESTAMP
            WHERE blood_bank_id = NEW.blood_bank_id AND blood_group_id = NEW.blood_group_id;
        END IF;
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        IF OLD.status <> NEW.status THEN
            -- Decrease previous status count
            IF OLD.status = 'AVAILABLE' THEN
                UPDATE inventory SET units_available = units_available - 1, last_updated = CURRENT_TIMESTAMP
                WHERE blood_bank_id = OLD.blood_bank_id AND blood_group_id = OLD.blood_group_id;
            ELSIF OLD.status = 'RESERVED' THEN
                UPDATE inventory SET units_reserved = units_reserved - 1, last_updated = CURRENT_TIMESTAMP
                WHERE blood_bank_id = OLD.blood_bank_id AND blood_group_id = OLD.blood_group_id;
            END IF;
            -- Increase new status count
            IF NEW.status = 'AVAILABLE' THEN
                UPDATE inventory SET units_available = units_available + 1, last_updated = CURRENT_TIMESTAMP
                WHERE blood_bank_id = NEW.blood_bank_id AND blood_group_id = NEW.blood_group_id;
            ELSIF NEW.status = 'RESERVED' THEN
                UPDATE inventory SET units_reserved = units_reserved + 1, last_updated = CURRENT_TIMESTAMP
                WHERE blood_bank_id = NEW.blood_bank_id AND blood_group_id = NEW.blood_group_id;
            END IF;
        END IF;
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_blood_unit_status_change
AFTER INSERT OR UPDATE ON blood_unit
FOR EACH ROW EXECUTE FUNCTION update_inventory_on_status_change();

-- End of DDL
