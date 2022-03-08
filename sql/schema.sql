PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS projects(
    proj_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    title varchar(50) UNIQUE NOT NULL,
    github_url varchar(100) NOT NULL,
    `image` varchar(50) NOT NULL,
    `description` text NOT NULL,
    languages text NOT NULL,
    is_wip boolean NOT NULL default FALSE
);

CREATE TABLE IF NOT EXISTS extras(
    extra_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    proj_id INTEGER NOT NULL,
    disp_text TEXT NOT NULL,
    `url` TEXT NOT NULL,
    FOREIGN KEY (proj_id) REFERENCES projects(proj_id) ON DELETE CASCADE
);

-- CREATE TABLE myinfo(
--     resume_file varchar(50) NOT NULL,
--     phone_num varchar(12) NOT NULL,
--     email varchar(25) NOT NULL,
--     addr_ln1 varchar(50) NOT NULL,
--     addr_ln2 varchar(50),
--     city varchar(50) NOT NULL,
--     state varchar(50) NOT NULL,
--     zip INTEGER NOT NULL
-- );