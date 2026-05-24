SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS project_attachments;
DROP TABLE IF EXISTS requirement_pending_items;
DROP TABLE IF EXISTS requirement_risks;
DROP TABLE IF EXISTS requirement_scenarios;
DROP TABLE IF EXISTS requirement_analyses;
DROP TABLE IF EXISTS workflows;
DROP TABLE IF EXISTS project_runs;
DROP TABLE IF EXISTS project_sessions;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id               VARCHAR(32) NOT NULL COMMENT '业务ID，如 user_xxxxxxxx',
    email                 VARCHAR(255) NOT NULL,
    display_name          VARCHAR(255) NOT NULL,
    password_hash         VARCHAR(255) NOT NULL,
    status                VARCHAR(32) NOT NULL DEFAULT 'active',
    created_at            DATETIME NOT NULL,
    updated_at            DATETIME NOT NULL,
    PRIMARY KEY (user_id),
    UNIQUE KEY uk_users_email (email),
    KEY idx_users_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='登录用户表';


CREATE TABLE projects (
    project_id           VARCHAR(32) NOT NULL COMMENT '业务ID，如 proj_xxxxxxxx',
    created_id           VARCHAR(32) NULL COMMENT '创建用户ID',
    update_id            VARCHAR(32) NULL COMMENT '更新用户ID',
    name                 VARCHAR(255) NOT NULL,
    description          TEXT NULL,
    status               VARCHAR(32) NOT NULL DEFAULT 'created',
    workspace_path       VARCHAR(1024) NOT NULL,
    current_session_id   VARCHAR(32) NULL,
    client_info          VARCHAR(255) NULL COMMENT '前端 config.clientInfo',
    province             VARCHAR(64) NULL COMMENT '前端 config.province',
    city                 VARCHAR(64) NULL COMMENT '前端 config.city',
    stage                VARCHAR(64) NULL COMMENT '前端 config.stage',
    industry             VARCHAR(128) NULL COMMENT '前端 config.industry',
    created_at           DATETIME NOT NULL,
    updated_at           DATETIME NOT NULL,
    PRIMARY KEY (project_id),
    KEY idx_projects_created_id (created_id),
    KEY idx_projects_update_id (update_id),
    KEY idx_projects_status (status),
    KEY idx_projects_updated_at (updated_at),
    KEY idx_projects_current_session_id (current_session_id),
    CONSTRAINT fk_projects_created_user
        FOREIGN KEY (created_id) REFERENCES users(user_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_projects_update_user
        FOREIGN KEY (update_id) REFERENCES users(user_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='项目主记录表';


CREATE TABLE requirement_analyses (
    project_id           VARCHAR(32) NOT NULL,
    project_name         VARCHAR(255) NOT NULL DEFAULT '' COMMENT 'basic.projectName',
    project_summary      TEXT NOT NULL COMMENT 'basic.projectSummary',
    basic_industry       VARCHAR(128) NOT NULL DEFAULT '' COMMENT 'basic.industry',
    project_type         VARCHAR(128) NOT NULL DEFAULT '' COMMENT 'basic.projectType',
    keywords             VARCHAR(512) NOT NULL DEFAULT '' COMMENT 'basic.keywords',
    background           TEXT NOT NULL COMMENT 'core.background',
    goal                 TEXT NOT NULL COMMENT 'core.goal',
    users                TEXT NOT NULL COMMENT 'core.users',
    pain_points          TEXT NOT NULL COMMENT 'core.painPoints',
    function_desc        JSON NOT NULL COMMENT 'functions.functionDesc',
    non_function         JSON NOT NULL COMMENT 'functions.nonFunction',
    constraints_json     JSON NOT NULL COMMENT 'functions.constraints',
    unknown_info         TEXT NOT NULL COMMENT 'pending.unknownInfo',
    assumptions          TEXT NOT NULL COMMENT 'pending.assumptions',
    supplement_notes     TEXT NOT NULL COMMENT 'supplement.notes',
    created_id           VARCHAR(32) NULL COMMENT '创建用户ID',
    update_id            VARCHAR(32) NULL COMMENT '更新用户ID',
    created_at           DATETIME NOT NULL,
    updated_at           DATETIME NOT NULL,
    PRIMARY KEY (project_id),
    CONSTRAINT fk_requirement_analyses_project
        FOREIGN KEY (project_id) REFERENCES projects(project_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='需求分析主表';


CREATE TABLE requirement_scenarios (
    id                   BIGINT NOT NULL AUTO_INCREMENT,
    project_id           VARCHAR(32) NOT NULL,
    sort_order           INT NOT NULL DEFAULT 0,
    item_key             VARCHAR(64) NOT NULL DEFAULT '',
    title                VARCHAR(255) NOT NULL DEFAULT '',
    description          TEXT NOT NULL,
    flow                 TEXT NOT NULL,
    created_id           VARCHAR(32) NULL COMMENT '创建用户ID',
    update_id            VARCHAR(32) NULL COMMENT '更新用户ID',
    PRIMARY KEY (id),
    KEY idx_requirement_scenarios_project_id (project_id),
    KEY idx_requirement_scenarios_sort_order (sort_order),
    CONSTRAINT fk_requirement_scenarios_project
        FOREIGN KEY (project_id) REFERENCES projects(project_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='需求分析-场景列表';


CREATE TABLE requirement_risks (
    id                   BIGINT NOT NULL AUTO_INCREMENT,
    project_id           VARCHAR(32) NOT NULL,
    sort_order           INT NOT NULL DEFAULT 0,
    item_key             VARCHAR(64) NOT NULL DEFAULT '',
    title                VARCHAR(255) NOT NULL DEFAULT '',
    level                VARCHAR(32) NOT NULL DEFAULT '中',
    description          TEXT NOT NULL,
    impact               TEXT NOT NULL,
    strategy             TEXT NOT NULL,
    created_id           VARCHAR(32) NULL COMMENT '创建用户ID',
    update_id            VARCHAR(32) NULL COMMENT '更新用户ID',
    PRIMARY KEY (id),
    KEY idx_requirement_risks_project_id (project_id),
    KEY idx_requirement_risks_sort_order (sort_order),
    CONSTRAINT fk_requirement_risks_project
        FOREIGN KEY (project_id) REFERENCES projects(project_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='需求分析-风险列表';


CREATE TABLE requirement_pending_items (
    id                   BIGINT NOT NULL AUTO_INCREMENT,
    project_id           VARCHAR(32) NOT NULL,
    sort_order           INT NOT NULL DEFAULT 0,
    title                VARCHAR(255) NOT NULL DEFAULT '',
    text                 TEXT NOT NULL,
    checked              TINYINT(1) NOT NULL DEFAULT 0,
    created_id           VARCHAR(32) NULL COMMENT '创建用户ID',
    update_id            VARCHAR(32) NULL COMMENT '更新用户ID',
    PRIMARY KEY (id),
    KEY idx_requirement_pending_items_project_id (project_id),
    KEY idx_requirement_pending_items_sort_order (sort_order),
    CONSTRAINT fk_requirement_pending_items_project
        FOREIGN KEY (project_id) REFERENCES projects(project_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='需求分析-待确认事项';


CREATE TABLE project_attachments (
    id                   BIGINT NOT NULL AUTO_INCREMENT,
    project_id           VARCHAR(32) NOT NULL,
    sort_order           INT NOT NULL DEFAULT 0,
    name                 VARCHAR(255) NOT NULL DEFAULT '',
    meta                 TEXT NOT NULL,
    size                 BIGINT NULL,
    content_type         VARCHAR(255) NULL,
    storage_path         VARCHAR(1024) NULL,
    uploaded_at          DATETIME NULL,
    created_id           VARCHAR(32) NULL COMMENT '创建用户ID',
    update_id            VARCHAR(32) NULL COMMENT '更新用户ID',
    PRIMARY KEY (id),
    KEY idx_project_attachments_project_id (project_id),
    KEY idx_project_attachments_sort_order (sort_order),
    CONSTRAINT fk_project_attachments_project
        FOREIGN KEY (project_id) REFERENCES projects(project_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='需求分析-附件记录';


CREATE TABLE project_sessions (
    session_id            VARCHAR(32) NOT NULL COMMENT '业务ID，如 sess_xxxxxxxx',
    project_id            VARCHAR(32) NOT NULL,
    workspace_path        VARCHAR(1024) NOT NULL,
    conversation          VARCHAR(255) NOT NULL,
    base_url              VARCHAR(1024) NULL,
    llm_provider          VARCHAR(128) NULL,
    provider_session_ref  VARCHAR(255) NULL,
    status                VARCHAR(32) NOT NULL DEFAULT 'active',
    hermes_session_ref    VARCHAR(255) NULL,
    created_id            VARCHAR(32) NULL COMMENT '创建用户ID',
    update_id             VARCHAR(32) NULL COMMENT '更新用户ID',
    created_at            DATETIME NOT NULL,
    updated_at            DATETIME NOT NULL,
    PRIMARY KEY (session_id),
    KEY idx_sessions_project_id (project_id),
    KEY idx_sessions_status (status),
    KEY idx_sessions_created_at (created_at),
    CONSTRAINT fk_sessions_project
        FOREIGN KEY (project_id) REFERENCES projects(project_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='项目会话主记录表';


CREATE TABLE project_runs (
    run_id                VARCHAR(32) NOT NULL COMMENT '业务ID，如 run_xxxxxxxx',
    project_id            VARCHAR(32) NOT NULL,
    session_id            VARCHAR(32) NOT NULL,
    phase_id              VARCHAR(32) NOT NULL,
    phase_name            VARCHAR(255) NOT NULL,
    skill_name            VARCHAR(255) NOT NULL,
    status                VARCHAR(32) NOT NULL DEFAULT 'pending',
    started_at            DATETIME NOT NULL,
    ended_at              DATETIME NULL,
    error_message         TEXT NULL,
    log_path              VARCHAR(1024) NOT NULL,
    output_path           VARCHAR(1024) NULL,
    result_summary_path   VARCHAR(1024) NULL,
    detail_path           VARCHAR(1024) NULL,
    created_id            VARCHAR(32) NULL COMMENT '创建用户ID',
    update_id             VARCHAR(32) NULL COMMENT '更新用户ID',
    PRIMARY KEY (run_id),
    KEY idx_runs_project_id (project_id),
    KEY idx_runs_session_id (session_id),
    KEY idx_runs_status (status),
    KEY idx_runs_phase_id (phase_id),
    KEY idx_runs_started_at (started_at),
    CONSTRAINT fk_runs_project
        FOREIGN KEY (project_id) REFERENCES projects(project_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_runs_session
        FOREIGN KEY (session_id) REFERENCES project_sessions(session_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='单次运行主记录表';


CREATE TABLE workflows (
    workflow_id           VARCHAR(32) NOT NULL COMMENT '业务ID，如 wf_xxxxxxxx',
    project_id            VARCHAR(32) NOT NULL,
    session_id            VARCHAR(32) NOT NULL,
    status                VARCHAR(32) NOT NULL DEFAULT 'pending',
    current_phase_id      VARCHAR(32) NULL,
    created_id            VARCHAR(32) NULL COMMENT '创建用户ID',
    update_id             VARCHAR(32) NULL COMMENT '更新用户ID',
    created_at            DATETIME NOT NULL,
    started_at            DATETIME NULL,
    ended_at              DATETIME NULL,
    error_message         TEXT NULL,
    log_path              VARCHAR(1024) NOT NULL,
    detail_path           VARCHAR(1024) NULL COMMENT 'workflow 明细 JSON 路径',
    PRIMARY KEY (workflow_id),
    KEY idx_workflows_project_id (project_id),
    KEY idx_workflows_session_id (session_id),
    KEY idx_workflows_status (status),
    KEY idx_workflows_created_at (created_at),
    CONSTRAINT fk_workflows_project
        FOREIGN KEY (project_id) REFERENCES projects(project_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_workflows_session
        FOREIGN KEY (session_id) REFERENCES project_sessions(session_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='工作流主记录表';

SET FOREIGN_KEY_CHECKS = 1;
