SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS users (
    user_id               VARCHAR(32) NOT NULL,
    email                 VARCHAR(255) NOT NULL,
    display_name          VARCHAR(255) NOT NULL,
    password_hash         VARCHAR(255) NOT NULL,
    status                VARCHAR(32) NOT NULL DEFAULT 'active',
    created_at            DATETIME NOT NULL,
    updated_at            DATETIME NOT NULL,
    PRIMARY KEY (user_id),
    UNIQUE KEY uk_users_email (email),
    KEY idx_users_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
