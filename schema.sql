
DROP TABLE IF EXISTS classifications;
DROP TABLE IF EXISTS users;

-- Create users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

-- Create classifications table
CREATE TABLE classifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    disease_name TEXT NOT NULL,
    accuracy INTEGER NOT NULL,
    preventive_measure TEXT NOT NULL,
    date DATETIME DEFAULT CURRENT_TIMESTAMP
);

