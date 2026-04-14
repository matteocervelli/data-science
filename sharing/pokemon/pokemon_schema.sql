CREATE TABLE IF NOT EXISTS pokemon (
    pokemon_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    type_1 VARCHAR(20) NOT NULL,
    type_2 VARCHAR(20),
    total INTEGER NOT NULL,
    hp INTEGER NOT NULL,
    attack INTEGER NOT NULL,
    defense INTEGER NOT NULL,
    sp_atk INTEGER NOT NULL,
    sp_def INTEGER NOT NULL,
    speed INTEGER NOT NULL,
    generation INTEGER NOT NULL,
    legendary BOOLEAN NOT NULL
);

-- Import data from CSV
\copy pokemon (pokemon_id, name, type_1, type_2, total, hp, attack, defense, sp_atk, sp_def, speed, generation, legendary)
FROM '/Users/matteocervelli/dev/learning/google-data-science/pokemon/Pokemon.csv'
WITH (
    FORMAT csv,
    HEADER true,
    DELIMITER ',',
    NULL ''
);

-- Verification queries
SELECT COUNT(*) as total_rows FROM pokemon;

SELECT * FROM pokemon LIMIT 5;

-- Column statistics
SELECT 
    'pokemon_id' as column_name,
    COUNT(*) as total,
    COUNT(pokemon_id) as non_null,
    COUNT(DISTINCT pokemon_id) as unique_values
FROM pokemon;