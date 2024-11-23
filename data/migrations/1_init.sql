CREATE DATABASE IF NOT EXISTS logs;

USE logs;

CREATE TABLE IF NOT EXISTS log_data (
    timestamp DateTime,
    component String,
    level String,
    message String,
    event_type String,
    record String,
    PRIMARY KEY (timestamp)
) ENGINE = MergeTree()
ORDER BY timestamp;
