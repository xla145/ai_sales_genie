SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS workflows;
DROP TABLE IF EXISTS project_runs;
DROP TABLE IF EXISTS project_sessions;
DROP TABLE IF EXISTS projects;

CREATE TABLE projects (
    project_id           VARCHAR(32) NOT NULL COMMENT '业务ID，如 proj_xxxxxxxx',
    name                 VARCHAR(255) NOT NULL,
    description          TEXT NULL,
    status               VARCHAR(32) NOT NULL DEFAULT 'created',
    workspace_path       VARCHAR(1024) NOT NULL,
    current_session_id   VARCHAR(32) NULL,
    created_at           DATETIME NOT NULL,
    updated_at           DATETIME NOT NULL,
    PRIMARY KEY (project_id),
    KEY idx_projects_status (status),
    KEY idx_projects_updated_at (updated_at),
    KEY idx_projects_current_session_id (current_session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='项目主记录表';


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
