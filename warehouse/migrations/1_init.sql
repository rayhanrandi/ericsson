CREATE DATABASE IF NOT EXISTS logs;
CREATE DATABASE IF NOT EXISTS warehouse;

-- configure log database/tables
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

-- configure data warehouse database/tables
USE warehouse;

-- processed data
CREATE TABLE IF NOT EXISTS analysis (
    timestamp DateTime,
    machine_id Int64,
    temperature Float64,
    humidity Float64,
    vibration Float64,
    gyro_x Float64,
    gyro_y Float64,
    gyro_z Float64,
    accel_x Float64,
    accel_y Float64,
    accel_z Float64,
    prediction Int64,
    cycle_time Float64,
    hour Int32,
    day_of_week Int32,
    month Int32,
    shift String,
    machine_type String,
    machine_age Int32,
    operator_id String,
    material_type String,
    days_since_last_maintenance Int32,
    PRIMARY KEY (timestamp)
) ENGINE = MergeTree()
ORDER BY timestamp;

-- rag summaries of recent data
CREATE TABLE IF NOT EXISTS rag (
    timestamp DateTime,
    summary String,
    PRIMARY KEY (timestamp)
) ENGINE = MergeTree()
ORDER BY timestamp;
