-- Script completo per psql

-- Crea la tabella
CREATE TABLE IF NOT EXISTS us_baby_names (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    gender CHAR(1) NOT NULL CHECK (gender IN ('M', 'F')),
    year INTEGER NOT NULL CHECK (year >= 1880 AND year <= 2020),
    number INTEGER NOT NULL CHECK (number > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crea gli indici
CREATE INDEX idx_name ON us_baby_names(name);
CREATE INDEX idx_year ON us_baby_names(year);
CREATE INDEX idx_gender ON us_baby_names(gender);
CREATE INDEX idx_name_year ON us_baby_names(name, year);
CREATE INDEX idx_year_gender ON us_baby_names(year, gender);

-- Importa i dati usando \copy (client-side)
\copy us_baby_names(name, gender, year, number) FROM '/Users/matteocervelli/dev/learning/google-data-science/names/all_names.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',')

-- Verifica che i dati siano stati importati
SELECT COUNT(*) as total_records FROM us_baby_names;

-- Mostra alcuni record di esempio
SELECT * FROM us_baby_names LIMIT 10;