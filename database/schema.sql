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
    created_at TIMESTAMPZ DEFAULT CURRENT_TIMESTAMP NOT NULL
)

CREATE TYPE division_type AS ENUM ("ncaa_d1", "ncaa_d2", "ncaa_d3", "naia", "njcaa");
CREATE TYPE user_role_type AS ENUM ("best_player", "travel_squad", "redshirt_freshman", "walk_on");
CREATE TYPE school_type_enum AS ENUM ("public", "private_nonprofit", "private_forprofit");
CREATE TYPE climate_type AS ENUM ("warm", "moderate", "cold");

create table user_search_preferences (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- enums
    divisions division_type[] NOT NULL,
    user_role_desire user_role_type NOT NULL, -- What role the player wants on the team
    school_type school_type_enum NOT NULL,
    climate climate_type NOT NULL,

    -- regular values
    program_rank INT NOT NULL, -- minimum program rank
    academic_rigor TEXT NOT NULL,
    min_act INT NOT NULL,
    min_sat INT NOT NULL,
    user_test_score_tolerance INT NOT NULL, -- how strict the user is about minimum test scores
    max_distance INT NOT NULL,

    -- based on college scorecard numbering
    preferred_regions INT[] NOT NULL,
    school_size INT[] NOT NULL,
    school_setting INT[] NOT NULL
)

CREATE TYPE event_level_type AS ENUM ("local", "state", "regional", "national")

create table user_events (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_name VARCHAR(255) NOT NULL,
    event_tour_name VARCHAR(255) NULL,
    course_name VARCHAR(255) NULL,
    event_level event_level_type NULL,
    yardage INT NULL,
    scores INT[] NOT NULL,
    par INT NULL,
    finish INT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL
)

create table saved_matches (

)

create table college_events (

)

create table college_players (

)

create table college_programs (

)