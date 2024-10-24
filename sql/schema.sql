CREATE TABLE project2 (id INTEGER NOT NULL,title VARCHAR(64) NOT NULL,description TEXT NOT NULL,github_url VARCHAR(128) NOT NULL,image VARCHAR(64) NOT NULL,is_wip BOOLEAN NOT NULL,shield VARCHAR(128), lastupdate TEXT,PRIMARY KEY (id),UNIQUE (title));

INSERT INTO project2 (title, description, github_url, image, is_wip, shield) SELECT title, description, github_url, image, is_wip, shield FROM project;

CREATE TABLE skill2 (id INTEGER NOT NULL,print_name VARCHAR(16) NOT NULL,icon_name VARCHAR(32) NOT NULL,prio INTEGER NOT NULL DEFAULT 100,PRIMARY KEY (id));

CREATE TABLE user2 (id INTEGER NOT NULL,username VARCHAR(32) NOT NULL,email VARCHAR(32) NOT NULL,password VARCHAR(64) NOT NULL,bio TEXT,PRIMARY KEY (id),UNIQUE (username),UNIQUE (email));