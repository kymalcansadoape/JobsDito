DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS applicant;
DROP TABLE IF EXISTS company;
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS applications;


CREATE TABLE users(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    roles TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE company(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT,
    company_name TEXT,
    user_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)

);

CREATE TABLE applications(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    applicant_id INTEGER,
    job_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(applicant_id) REFERENCES applicant(id),
    FOREIGN KEY(job_id) REFERENCES jobs(id)

);

CREATE TABLE jobs(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    job_name TEXT,
    job_description TEXT,
    job_level TEXT,
    company_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(company_id) REFERENCES company(id)

);

CREATE TABLE applicant(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    first_name TEXT DEFAULT NULL,
    last_name TEXT DEFAULT NULL,
    location TEXT DEFAULT NULL,
    user_id INTEGER,
    resume_path TEXT DEFAULT NULL,
    years_of_experience INTEGER DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) 
);



