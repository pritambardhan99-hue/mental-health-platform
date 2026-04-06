-- MySQL Initialization Script
-- Runs once when MySQL container first starts

-- Create database with proper character set for emoji support
CREATE DATABASE IF NOT EXISTS mental_health_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- Grant all privileges to app user
GRANT ALL PRIVILEGES ON mental_health_db.* TO 'mental_health_user'@'%';
FLUSH PRIVILEGES;
