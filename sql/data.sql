INSERT INTO projects(title, github_url, `image`, `description`, languages, is_wip)
VALUES ('Sentiment Analysis', 'github.com/repo/sampleurl.git', 'sentimentgraph.png', 'SAMPLE DESCRIPTION', 'Python', FALSE);
INSERT INTO projects(title, github_url, `image`, `description`, languages, is_wip)
VALUES ('EasyTuya', 'https://github.com/ASchoe311/EasyTuya', 'tuyaimg.png',
"EasyTuya is a package containing nearly all needed functionality for interacting with your Tuya powered IOT devices through Python and Tuya's web API.", 'Python', TRUE);
INSERT INTO projects(title, github_url, `image`, `description`, languages, is_wip)
VALUES ('QueueBot', 'https://github.com/ASchoe311/RicksDoorQueue', 'queuebotimg.png', "QueueBot is a chat bot that runs in the staff GroupMe chat of my work. Since I and a majority of my coworkers are students, we often need shifts picked up. With a few simple commands QueueBot can keep track of the shift pickup queue for each day to simplify this process.", 'NodeJS,HTML5', FALSE);

INSERT INTO extras(proj_id, disp_text, `url`)
VALUES (3, "Live Queue Site", "http://doorqueue.adamschoe.com");
INSERT INTO extras(proj_id, disp_text, `url`)
VALUES (2, "PyPi Release", "https://pypi.org/project/EasyTuya/");
INSERT INTO extras(proj_id, disp_text, `url`)
VALUES (2, "Documentation", "https://aschoe311.github.io/EasyTuya/");
