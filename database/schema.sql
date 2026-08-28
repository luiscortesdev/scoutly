-- Enums
CREATE TYPE gender_type as ENUM ('men', 'women');
CREATE TYPE division_type AS ENUM ('ncaa_d1', 'ncaa_d2', 'ncaa_d3', 'naia', 'njcaa_i', 'njcaa_ii', 'njcaa_iii');
CREATE TYPE user_role_type AS ENUM ('best_player', 'travel_squad', 'redshirt_freshman', 'walk_on');
CREATE TYPE school_type_enum AS ENUM ('public', 'private_nonprofit', 'private_forprofit');
CREATE TYPE climate_type AS ENUM ('warm', 'moderate', 'cold');
CREATE TYPE event_level_type AS ENUM ('local', 'state', 'regional', 'national');
CREATE TYPE recruiting_tier_type AS ENUM ('reach', 'target', 'safety', 'undecided');
CREATE TYPE academic_rigor_type as ENUM ('low rigor', 'medium rigor', 'high rigor');

-- Tables
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
    latitude NUMERIC(9,6) NULL,
    longitude NUMERIC(9,6) NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE user_search_preferences (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    divisions division_type[] NOT NULL,
    user_role_desire user_role_type NOT NULL, -- What role the player wants on the team
    school_type school_type_enum NOT NULL,
    climate climate_type NOT NULL,
    program_rank INT NOT NULL, -- minimum program rank
    academic_rigor academic_rigor_type NOT NULL,
    min_act INT NOT NULL,
    min_sat INT NOT NULL,
    user_test_score_tolerance INT NOT NULL, -- how strict the user is about minimum test scores
    max_distance INT NOT NULL,
    -- based on college scorecard numbering
    preferred_regions INT[] NOT NULL,
    school_size INT[] NOT NULL,
    school_setting INT[] NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE user_events (
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
    end_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE colleges (
    unit_id INT PRIMARY KEY, -- Unique ID from the DOE
    opeid VARCHAR(50) NULL,
    opeid6 VARCHAR(50) NULL,
    name VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state CHAR(10) NOT NULL,
    zip VARCHAR(20) NOT NULL,
    accreditation_agency VARCHAR(255) NULL,
    institution_url VARCHAR(255) NULL,
    net_price_calculator_url VARCHAR(255) NULL,
    is_main_campus BOOLEAN NULL,
    region INT NULL,
    locale INT NULL,
    latitude NUMERIC(9,6) NULL,
    longitude NUMERIC(9,6) NULL,
    admissions_rate NUMERIC(4,2) NULL,
    
    sat_reading_25th INT NULL,
    sat_reading_75th INT NULL,
    sat_reading_50th INT NULL,
    sat_math_25th INT NULL,
    sat_math_75th INT NULL,
    sat_math_50th INT NULL,
    sat_total_25th INT NULL,
    sat_total_75th INT NULL,
    sat_total_50th INT NULL,
    sat_avg INT NULL,
    
    act_25th INT NULL,
    act_75th INT NULL,
    act_50th INT NULL,
    
    undergrad_size INT NULL,
    graduate_size INT NULL,
    in_state_tuition INT NULL,
    out_of_state_tuition INT NULL,
    school_type VARCHAR(100) NULL,
    address VARCHAR(500) NULL,
    median_earnings_9yrs INT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE programs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    college_id INT NOT NULL REFERENCES colleges(unit_id) ON DELETE CASCADE,
    clippd_id VARCHAR(50) UNIQUE NULL,
    gender gender_type NOT NULL,
    name VARCHAR(255) NOT NULL,
    conference VARCHAR(255) NULL,
    division division_type NULL,
    head_coach VARCHAR(255) NULL,
    rank INT NULL,
    scoring_avg NUMERIC(18, 13) NULL,
    adjusted_scoring_avg NUMERIC(18, 13) NULL,
    top3_finishes INT NULL,
    total_rounds INT NULL,
    win_loss_tie VARCHAR(255) NULL,
    wins INT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,

    CONSTRAINT unique_program UNIQUE (clippd_id)
);

CREATE TABLE program_events (
    id SERIAL PRIMARY KEY,
    program_uuid UUID REFERENCES programs(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    position VARCHAR(10) NULL,
    field_size VARCHAR(10) NULL,
    score VARCHAR(10) NULL,
    event_sg NUMERIC(6, 3) NULL DEFAULT 0,
    total_points NUMERIC(6, 3) NULL DEFAULT 0,
    weighted_points NUMERIC(6, 3) NULL DEFAULT 0,
    total_rounds INT NULL,
    start_date DATE NULL DEFAULT CURRENT_DATE,
    end_date DATE NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE players (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    program_uuid UUID REFERENCES programs(id) ON DELETE CASCADE,
    clippd_id VARCHAR(50) UNIQUE NULL,
    name VARCHAR(255) NOT NULL,
    rank INT NULL,
    scoring_avg NUMERIC(18, 13) NULL,
    adjusted_scoring_avg NUMERIC(18, 13) NULL,
    top3_finishes INT NULL,
    total_rounds INT NULL,
    win_loss_tie VARCHAR(255) NULL,
    wins INT NULL,
    -- graduation_year VARCHAR(50) NULL, -- graudation year requires scraping additional details is too computationally expensive. this field may be deleted soon.
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

/*
For now, we are not going to store any events for individual players
CREATE TABLE player_events (
    id SERIAL PRIMARY KEY,
    player_uuid UUID REFERENCES players(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    position VARCHAR(10) NULL,
    field_size VARCHAR(10) NULL,
    score VARCHAR(10) NULL,
    event_sg NUMERIC(6, 3) NULL DEFAULT 0,
    total_points NUMERIC(6, 3) NULL DEFAULT 0,
    weighted_points NUMERIC(6, 3) NULL DEFAULT 0,
    total_rounds INT NULL,
    start_date DATE NULL DEFAULT CURRENT_DATE,
    end_date DATE NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);
*/

CREATE TABLE saved_matches (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    program_id UUID NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
    tier recruiting_tier_type NOT NULL DEFAULT 'undecided',
    notes TEXT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT unique_user_program UNIQUE (user_id, program_id)
);

-- Views
-- Need to update this view to adjust for each individual rounds playing level and apply modifiers to adjust it to the college level.
-- Also, need to update it to adjust for the courses par itself.
CREATE OR REPLACE VIEW user_scoring_averages AS
WITH individual_rounds AS (
    SELECT 
        user_id,
        unnest(scores) AS score
    FROM user_events
)
SELECT 
    user_id,
    COUNT(score) AS total_rounds_played,
    MIN(score) AS personal_best,
    ROUND(AVG(score), 2) AS lifetime_scoring_avg
FROM individual_rounds
GROUP BY user_id;