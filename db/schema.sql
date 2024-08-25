-- CREATE DATABASE scheduling;

CREATE TYPE task_state AS ENUM ('pending', 'processing', 'completed', 'aborted');

CREATE TABLE IF NOT EXISTS task (
	id SERIAL PRIMARY KEY,
	created_at timestamp DEFAULT current_timestamp,
	state task_state DEFAULT 'pending',
	message text
);
