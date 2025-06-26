-- AgroTrack Database Schema
-- PostgreSQL initialization script

-- Database initialization script for AgroTrack
-- Note: Database 'agrotrack' is created by Docker environment variables

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table for authentication and authorization
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'operator', 'logistics')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Silos table for storage facilities
CREATE TABLE silos (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    capacity_tons INTEGER NOT NULL,
    max_temperature DECIMAL(5, 2) DEFAULT 30.0,
    max_humidity DECIMAL(5, 2) DEFAULT 75.0,
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'maintenance')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Silo readings table for sensor data
CREATE TABLE silo_readings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    silo_id INTEGER REFERENCES silos(id) ON DELETE CASCADE,
    temperature DECIMAL(5, 2) NOT NULL,
    humidity DECIMAL(5, 2) NOT NULL,
    volume_percent DECIMAL(5, 2) NOT NULL,
    volume_tons DECIMAL(10, 2),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Alerts table for notifications
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    silo_id INTEGER REFERENCES silos(id) ON DELETE CASCADE,
    alert_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    value DECIMAL(10, 2),
    threshold DECIMAL(10, 2),
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Logistics table for shipment tracking
CREATE TABLE logistics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    truck_id VARCHAR(100) NOT NULL,
    driver_name VARCHAR(255) NOT NULL,
    route VARCHAR(255) NOT NULL,
    origin VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'in_transit', 'delivered', 'cancelled')),
    estimated_arrival TIMESTAMP WITH TIME ZONE,
    actual_arrival TIMESTAMP WITH TIME ZONE,
    cargo_weight DECIMAL(10, 2),
    silo_id INTEGER REFERENCES silos(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Logistics tracking table for GPS updates
CREATE TABLE logistics_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    logistics_id UUID REFERENCES logistics(id) ON DELETE CASCADE,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    speed DECIMAL(5, 2),
    heading DECIMAL(5, 2),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_silo_readings_silo_id ON silo_readings(silo_id);
CREATE INDEX idx_silo_readings_timestamp ON silo_readings(timestamp);
CREATE INDEX idx_alerts_silo_id ON alerts(silo_id);
CREATE INDEX idx_alerts_created_at ON alerts(created_at);
CREATE INDEX idx_alerts_is_resolved ON alerts(is_resolved);
CREATE INDEX idx_logistics_status ON logistics(status);
CREATE INDEX idx_logistics_tracking_logistics_id ON logistics_tracking(logistics_id);
CREATE INDEX idx_logistics_tracking_timestamp ON logistics_tracking(timestamp);

-- Insert default users with properly hashed passwords
-- Passwords: admin123, operator123, logistics123 respectively
INSERT INTO users (email, hashed_password, full_name, role) VALUES
('admin@agrotrack.com', '$2b$12$uDdbMavoOzt6kv0U2ecOt.0naMwzUOLB96N5iVpGITXZagmW.HOZe', 'System Administrator', 'admin'),
('operator@agrotrack.com', '$2b$12$s8hIyK9hbSyKjahnubaDo.PvW2BgMg7nmvm9Jy1J.PET7rR9adKA2', 'Field Operator', 'operator'),
('logistics@agrotrack.com', '$2b$12$YvhpWFf/79Ie4TmkjGP.SOpGnPzdxbAc1u2IvtMcd2MO5kAa57xJu', 'Logistics Manager', 'logistics');

-- Insert sample silos
INSERT INTO silos (name, location, latitude, longitude, capacity_tons) VALUES
('Silo Central A', 'Asunción, Paraguay', -25.2637, -57.5759, 1000),
('Silo Norte B', 'San Lorenzo, Paraguay', -25.3416, -57.5085, 800),
('Silo Sur C', 'Luque, Paraguay', -25.2662, -57.4950, 1200),
('Silo Este D', 'Capiatá, Paraguay', -25.3551, -57.4456, 900),
('Silo Oeste E', 'Mariano Roque Alonso, Paraguay', -25.2018, -57.5330, 750);

-- Insert sample logistics entries
INSERT INTO logistics (truck_id, driver_name, route, origin, destination, status, cargo_weight, silo_id) VALUES
('TRK001', 'Carlos Mendoza', 'Ruta 1 - Puerto', 'Silo Central A', 'Puerto de Asunción', 'in_transit', 45.5, 1),
('TRK002', 'Maria Gonzalez', 'Ruta 2 - Aeropuerto', 'Silo Norte B', 'Aeropuerto Silvio Pettirossi', 'pending', 32.8, 2),
('TRK003', 'Juan Pereira', 'Ruta 3 - Frontera', 'Silo Sur C', 'Ciudad del Este', 'delivered', 55.2, 3);

-- Create trigger to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_silos_updated_at BEFORE UPDATE ON silos FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_logistics_updated_at BEFORE UPDATE ON logistics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column(); 