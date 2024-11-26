CREATE DATABASE IF NOT EXISTS logs;
CREATE DATABASE IF NOT EXISTS warehouse;

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

# TODO: create table for processed data
