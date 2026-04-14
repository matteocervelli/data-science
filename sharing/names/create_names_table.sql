-- Create table for US baby names data
CREATE TABLE IF NOT EXISTS us_baby_names (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    gender CHAR(1) NOT NULL CHECK (gender IN ('M', 'F')),
    year INTEGER NOT NULL CHECK (year >= 1880 AND year <= 2020),
    count INTEGER NOT NULL CHECK (count > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for common queries
CREATE INDEX idx_name ON us_baby_names(name);
CREATE INDEX idx_year ON us_baby_names(year);
CREATE INDEX idx_gender ON us_baby_names(gender);
CREATE INDEX idx_name_year ON us_baby_names(name, year);
CREATE INDEX idx_year_gender ON us_baby_names(year, gender);

-- Load data from CSV file
-- Note: Adjust the path to the CSV file location
\copy us_baby_names(name, gender, year, count)
FROM '/Users/matteocervelli/dev/learning/google-data-science/names/all_names.csv'
DELIMITER ','
CSV HEADER;

-- Example queries to test the data
-- Get top 10 most popular names in 2019
SELECT name, gender, SUM(count) as total_count
FROM us_baby_names
WHERE year = 2019
GROUP BY name, gender
ORDER BY total_count DESC
LIMIT 10;

-- Get trend for a specific name over years
SELECT year, SUM(count) as yearly_count
FROM us_baby_names
WHERE name = 'Emma'
GROUP BY year
ORDER BY year;