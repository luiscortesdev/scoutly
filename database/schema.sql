CREATE TYPE gender_type as ENUM ("men", "women")

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(500) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    gender gender_type NOT NULL,
    birth_date DATE NOT NULL,
    graduation_year VARCHAR(4) NULL,
    address VARCHAR(500) NOT NULL,
    city VARCHAR(500) NOT NULL,
    state VARCHAR(500) NOT NULL,
    zip VARCHAR(500) NOT NULL,
    sat_reading INT NULL,
    sat_math INT NULL,
    sat_total INT NULL,
    act_cumulative INT NULL,
    gpa_unweighted NUMERIC(3,2) NULL,
    gpa_weighted NUMERIC(3,2) NULL,
    handicap VARCHAR(10) NULL,
    home_course VARCHAR(255) NULL,
    lat NUMERIC(9,6) NULL,
    lon NUMERIC(9,6) NULL,
    scoring_avg NUMERIC(6, 3) NULL,
    created_at TIMESTAMPZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
)

create table saved_matches (

)

create table user_search_preferences (

)

create table user_events (

)

create table college_events (

)

create table college_players (

)

create table college_programs (
    
)