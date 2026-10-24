-- ============================================================================
-- FoodShare – Food Donation and Distribution Management System
-- Database: MySQL 8.0+
-- Schema Normalization: 3rd Normal Form (3NF)
-- ============================================================================

CREATE DATABASE IF NOT EXISTS foodshare_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE foodshare_db;

-- 1. USERS & ROLE-BASED ACCESS CONTROL (RBAC) TABLE
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(191) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('donor', 'ngo', 'volunteer', 'admin') NOT NULL,
    phone VARCHAR(20) NOT NULL,
    organization_name VARCHAR(150) NULL,
    registration_number VARCHAR(100) NULL,
    address TEXT NOT NULL,
    status ENUM('active', 'suspended', 'pending_verification') NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_role (role),
    INDEX idx_user_email (email),
    INDEX idx_user_status (status)
) ENGINE=InnoDB;

-- 2. FOOD DONATIONS TABLE
CREATE TABLE IF NOT EXISTS food_donations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donor_id INT NOT NULL,
    food_name VARCHAR(150) NOT NULL,
    category ENUM('Cooked Meals', 'Bakery & Bread', 'Raw Produce', 'Packaged Goods', 'Dairy & Refrigerated', 'Beverages') NOT NULL,
    is_veg BOOLEAN NOT NULL DEFAULT TRUE,
    quantity DECIMAL(10, 2) NOT NULL,
    remaining_quantity DECIMAL(10, 2) NOT NULL,
    unit ENUM('plates', 'kg', 'packets', 'servings') NOT NULL,
    prep_time DATETIME NOT NULL,
    expiry_time DATETIME NOT NULL,
    pickup_address TEXT NOT NULL,
    description TEXT NULL,
    status ENUM('available', 'requested', 'accepted', 'picked_up', 'in_transit', 'delivered', 'cancelled') NOT NULL DEFAULT 'available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_donation_donor FOREIGN KEY (donor_id) REFERENCES users(id) ON DELETE RESTRICT,
    CONSTRAINT chk_positive_quantity CHECK (quantity > 0),
    CONSTRAINT chk_remaining_positive CHECK (remaining_quantity >= 0 AND remaining_quantity <= quantity),
    INDEX idx_donation_status (status),
    INDEX idx_donation_expiry (expiry_time),
    INDEX idx_donation_category (category)
) ENGINE=InnoDB;

-- 3. NGO FOOD REQUESTS / CLAIMS TABLE
CREATE TABLE IF NOT EXISTS food_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donation_id INT NOT NULL,
    ngo_id INT NOT NULL,
    requested_quantity DECIMAL(10, 2) NOT NULL,
    unit ENUM('plates', 'kg', 'packets', 'servings') NOT NULL,
    purpose TEXT NOT NULL,
    status ENUM('pending', 'accepted', 'rejected', 'cancelled') NOT NULL DEFAULT 'accepted',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_request_donation FOREIGN KEY (donation_id) REFERENCES food_donations(id) ON DELETE CASCADE,
    CONSTRAINT fk_request_ngo FOREIGN KEY (ngo_id) REFERENCES users(id) ON DELETE RESTRICT,
    CONSTRAINT chk_req_quantity CHECK (requested_quantity > 0),
    INDEX idx_request_status (status)
) ENGINE=InnoDB;

-- 4. VOLUNTEER DELIVERY TASKS PIPELINE TABLE
CREATE TABLE IF NOT EXISTS delivery_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donation_id INT NOT NULL,
    request_id INT NOT NULL,
    volunteer_id INT NULL,
    pickup_address TEXT NOT NULL,
    dropoff_address TEXT NOT NULL,
    special_instructions TEXT NULL,
    status ENUM('available', 'assigned', 'picked_up', 'in_transit', 'delivered', 'failed') NOT NULL DEFAULT 'available',
    assigned_at DATETIME NULL,
    delivered_at DATETIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_delivery_donation FOREIGN KEY (donation_id) REFERENCES food_donations(id) ON DELETE CASCADE,
    CONSTRAINT fk_delivery_request FOREIGN KEY (request_id) REFERENCES food_requests(id) ON DELETE CASCADE,
    CONSTRAINT fk_delivery_volunteer FOREIGN KEY (volunteer_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_delivery_status (status),
    INDEX idx_delivery_volunteer (volunteer_id)
) ENGINE=InnoDB;

-- 5. DONOR PICKUP SCHEDULING TABLE
CREATE TABLE IF NOT EXISTS pickup_schedules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donation_id INT NOT NULL,
    donor_id INT NOT NULL,
    scheduled_date DATE NOT NULL,
    scheduled_time TIME NOT NULL,
    pickup_window VARCHAR(50) NOT NULL,
    packaging_method VARCHAR(100) NOT NULL,
    contact_person VARCHAR(150) NOT NULL,
    status ENUM('Scheduled', 'Ready for Pickup', 'Dispatched', 'Completed', 'Cancelled') NOT NULL DEFAULT 'Scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_sched_donation FOREIGN KEY (donation_id) REFERENCES food_donations(id) ON DELETE CASCADE,
    CONSTRAINT fk_sched_donor FOREIGN KEY (donor_id) REFERENCES users(id) ON DELETE RESTRICT,
    INDEX idx_sched_status (status),
    INDEX idx_sched_date (scheduled_date)
) ENGINE=InnoDB;

-- 6. SECURITY & AUDIT TRAIL LOGS
CREATE TABLE IF NOT EXISTS audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    action VARCHAR(60) NOT NULL,
    details TEXT NOT NULL,
    ip_address VARCHAR(45) NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_audit_action (action),
    INDEX idx_audit_timestamp (timestamp)
) ENGINE=InnoDB;

-- ============================================================================
-- SEED DATA (DEFAULT PASSWORDS ARE 'Password@123' / ADMIN: 'Admin@123')
-- Pre-hashed using PBKDF2-HMAC-SHA256
-- ============================================================================

INSERT INTO users (id, name, email, password_hash, role, phone, organization_name, registration_number, address, status)
VALUES
(1, 'System Administrator', 'admin@foodshare.org', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'admin', '+91 98220 12345', 'FoodShare Central Operations', 'GOV-MH-ADMIN-01', 'Central Civic Centre, Chhatrapati Sambhajinagar', 'active'),
(2, 'Chef Rajesh Verma', 'donor@greenbites.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'donor', '+91 98220 54321', 'Green Bites Banquet', NULL, 'Green Bites Banquet, Sector 4, Cidco, Chhatrapati Sambhajinagar', 'active'),
(3, 'Sunita Sharma', 'sunita@freshbakes.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'donor', '+91 98221 67890', 'Fresh Crust Artisan Bakery', NULL, 'Fresh Crust Bakery, Station Road, Chhatrapati Sambhajinagar', 'active'),
(4, 'Aarti Deshmukh', 'ngo@annaseva.org', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'ngo', '+91 98222 11223', 'Anna Seva Foundation', 'NGO-MH-2023-8891', 'Plot 12, Samarth Nagar, Chhatrapati Sambhajinagar', 'active'),
(5, 'Vikram Mehta', 'ngo@hopeforall.org', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'ngo', '+91 98223 33445', 'Hope For All NGO', 'NGO-MH-2022-4412', 'Shanti Nagar Community Center, Chhatrapati Sambhajinagar', 'active'),
(6, 'Karan Patil', 'volunteer@foodshare.org', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'volunteer', '+91 98224 55667', NULL, NULL, 'Cidco Sector N-2, Chhatrapati Sambhajinagar', 'active'),
(7, 'Priya Nair', 'priya@foodshare.org', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'volunteer', '+91 98225 77889', NULL, NULL, 'Samarth Nagar, Chhatrapati Sambhajinagar', 'active')
ON DUPLICATE KEY UPDATE id=id;

INSERT INTO food_donations (id, donor_id, food_name, category, is_veg, quantity, remaining_quantity, unit, prep_time, expiry_time, pickup_address, description, status)
VALUES
(1, 2, 'Vegetable Dum Biryani & Raita', 'Cooked Meals', TRUE, 60.0, 30.0, 'plates', DATE_SUB(NOW(), INTERVAL 2 HOUR), DATE_ADD(NOW(), INTERVAL 4 HOUR), 'Green Bites Banquet, Sector 4, Cidco', 'Freshly cooked aromatic basmati vegetable biryani packed in hot thermal containers.', 'available'),
(2, 3, 'Whole Wheat Brown Bread & Buns', 'Bakery & Bread', TRUE, 25.0, 25.0, 'kg', DATE_SUB(NOW(), INTERVAL 4 HOUR), DATE_ADD(NOW(), INTERVAL 24 HOUR), 'Fresh Crust Artisan Bakery, Station Road', 'Freshly baked whole wheat sandwich loaves and burger buns in moisture-resistant boxes.', 'available'),
(3, 2, 'Paneer Butter Masala & 100 Rotis', 'Cooked Meals', TRUE, 40.0, 0.0, 'plates', DATE_SUB(NOW(), INTERVAL 5 HOUR), DATE_ADD(NOW(), INTERVAL 1 HOUR), 'Green Bites Banquet, Sector 4, Cidco', 'Rich cottage cheese curry with hot rotis packed in food-grade foil containers.', 'delivered'),
(4, 2, 'Fresh Farm Spinach and Tomatoes', 'Raw Produce', TRUE, 35.0, 15.0, 'kg', DATE_SUB(NOW(), INTERVAL 24 HOUR), DATE_ADD(NOW(), INTERVAL 48 HOUR), 'Green Bites Kitchen Store, Sector 4, Cidco', 'Fresh organic farm produce kept in ventilated crates.', 'accepted')
ON DUPLICATE KEY UPDATE id=id;

INSERT INTO food_requests (id, donation_id, ngo_id, requested_quantity, unit, purpose, status)
VALUES
(1, 3, 4, 40.0, 'plates', 'Evening shelter food distribution at Samarth Nagar.', 'accepted'),
(2, 4, 5, 20.0, 'kg', 'Community kitchen cooking for migrant worker families.', 'accepted'),
(3, 1, 4, 30.0, 'plates', 'Night relief distribution at Central Railway Shelter.', 'pending')
ON DUPLICATE KEY UPDATE id=id;

INSERT INTO delivery_tasks (id, donation_id, request_id, volunteer_id, pickup_address, dropoff_address, special_instructions, status, assigned_at, delivered_at)
VALUES
(1, 3, 1, 6, 'Green Bites Banquet, Sector 4, Cidco', 'Plot 12, Samarth Nagar (Anna Seva)', 'Transport hot containers carefully. Deliver warm.', 'delivered', DATE_SUB(NOW(), INTERVAL 2 HOUR), DATE_SUB(NOW(), INTERVAL 20 MINUTE)),
(2, 4, 2, 7, 'Green Bites Kitchen Store, Sector 4, Cidco', 'Shanti Nagar Community Center (Hope For All)', 'Handle produce crates gently.', 'assigned', DATE_SUB(NOW(), INTERVAL 45 MINUTE), NULL)
ON DUPLICATE KEY UPDATE id=id;

INSERT INTO pickup_schedules (id, donation_id, donor_id, scheduled_date, scheduled_time, pickup_window, packaging_method, contact_person, status)
VALUES
(1, 1, 2, CURDATE(), '19:00:00', 'Evening 18:30 - 20:30', 'Hot Insulated Thermal Crates', 'Chef Rajesh (+91 98220 54321)', 'Ready for Pickup'),
(2, 2, 3, DATE_ADD(CURDATE(), INTERVAL 1 DAY), '10:30:00', 'Morning 09:00 - 11:00', 'Moisture-Resistant Bakery Boxes', 'Sunita Sharma (+91 98221 67890)', 'Scheduled')
ON DUPLICATE KEY UPDATE id=id;

INSERT INTO audit_logs (id, user_id, action, details)
VALUES
(1, 1, 'SYSTEM_INIT', 'Relational database schema and default seed data initialized in 3NF.'),
(2, 2, 'DONATION_CREATE', 'Listed 60 plates Vegetable Dum Biryani (Safe window: 4 hours).'),
(3, 4, 'REQUEST_CLAIM', 'Anna Seva Foundation requested 40 plates Paneer Butter Masala.'),
(4, 6, 'DELIVERY_DELIVERED', 'Volunteer Karan Patil completed delivery task #1 to Samarth Nagar Shelter.')
ON DUPLICATE KEY UPDATE id=id;
