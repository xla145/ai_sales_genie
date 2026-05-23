SET NAMES utf8mb4;

ALTER TABLE projects
    ADD COLUMN IF NOT EXISTS client_info VARCHAR(255) NULL COMMENT '前端 config.clientInfo',
    ADD COLUMN IF NOT EXISTS province VARCHAR(64) NULL COMMENT '前端 config.province',
    ADD COLUMN IF NOT EXISTS city VARCHAR(64) NULL COMMENT '前端 config.city',
    ADD COLUMN IF NOT EXISTS stage VARCHAR(64) NULL COMMENT '前端 config.stage',
    ADD COLUMN IF NOT EXISTS industry VARCHAR(128) NULL COMMENT '前端 config.industry';

CREATE TABLE IF NOT EXISTS requirement_analyses (
    project_id           VARCHAR(32) NOT NULL,
    project_name         VARCHAR(255) NOT NULL DEFAULT '',
    project_summary      TEXT NOT NULL,
    basic_industry       VARCHAR(128) NOT NULL DEFAULT '',
    project_type         VARCHAR(128) NOT NULL DEFAULT '',
    keywords             VARCHAR(512) NOT NULL DEFAULT '',
    background           TEXT NOT NULL,
    goal                 TEXT NOT NULL,
    users                TEXT NOT NULL,
    pain_points          TEXT NOT NULL,
    function_desc        JSON NOT NULL,
    non_function         JSON NOT NULL,
    constraints_json     JSON NOT NULL,
    unknown_info         TEXT NOT NULL,
    assumptions          TEXT NOT NULL,
    supplement_notes     TEXT NOT NULL,
    created_at           DATETIME NOT NULL,
    updated_at           DATETIME NOT NULL,
    PRIMARY KEY (project_id),
    CONSTRAINT fk_requirement_analyses_project
        FOREIGN KEY (project_id) REFERENCES projects(project_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS requirement_scenarios (
    id                   BIGINT NOT NULL AUTO_INCREMENT,
    project_id           VARCHAR(32) NOT NULL,
    sort_order           INT NOT NULL DEFAULT 0,
    item_key             VARCHAR(64) NOT NULL DEFAULT '',
    title                VARCHAR(255) NOT NULL DEFAULT '',
    description          TEXT NOT NULL,
    flow                 TEXT NOT NULL,
    PRIMARY KEY (id),
    KEY idx_requirement_scenarios_project_id (project_id),
    KEY idx_requirement_scenarios_sort_order (sort_order),
    CONSTRAINT fk_requirement_scenarios_project
        FOREIGN KEY (project_id) REFERENCES projects(project_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS requirement_risks (
    id                   BIGINT NOT NULL AUTO_INCREMENT,
    project_id           VARCHAR(32) NOT NULL,
    sort_order           INT NOT NULL DEFAULT 0,
    item_key             VARCHAR(64) NOT NULL DEFAULT '',
    title                VARCHAR(255) NOT NULL DEFAULT '',
    level                VARCHAR(32) NOT NULL DEFAULT '中',
    description          TEXT NOT NULL,
    impact               TEXT NOT NULL,
    strategy             TEXT NOT NULL,
    PRIMARY KEY (id),
    KEY idx_requirement_risks_project_id (project_id),
    KEY idx_requirement_risks_sort_order (sort_order),
    CONSTRAINT fk_requirement_risks_project
        FOREIGN KEY (project_id) REFERENCES projects(project_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS requirement_pending_items (
    id                   BIGINT NOT NULL AUTO_INCREMENT,
    project_id           VARCHAR(32) NOT NULL,
    sort_order           INT NOT NULL DEFAULT 0,
    title                VARCHAR(255) NOT NULL DEFAULT '',
    text                 TEXT NOT NULL,
    checked              TINYINT(1) NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    KEY idx_requirement_pending_items_project_id (project_id),
    KEY idx_requirement_pending_items_sort_order (sort_order),
    CONSTRAINT fk_requirement_pending_items_project
        FOREIGN KEY (project_id) REFERENCES projects(project_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS project_attachments (
    id                   BIGINT NOT NULL AUTO_INCREMENT,
    project_id           VARCHAR(32) NOT NULL,
    sort_order           INT NOT NULL DEFAULT 0,
    name                 VARCHAR(255) NOT NULL DEFAULT '',
    meta                 TEXT NOT NULL,
    storage_path         VARCHAR(1024) NULL,
    PRIMARY KEY (id),
    KEY idx_project_attachments_project_id (project_id),
    KEY idx_project_attachments_sort_order (sort_order),
    CONSTRAINT fk_project_attachments_project
        FOREIGN KEY (project_id) REFERENCES projects(project_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
