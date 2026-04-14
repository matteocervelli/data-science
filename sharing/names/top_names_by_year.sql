-- Query per trovare il nome maschile e femminile più popolare per ogni anno dal 1970 al 2019

WITH yearly_rankings AS (
    SELECT 
        year,
        name,
        gender,
        SUM(number) as total_count,
        ROW_NUMBER() OVER (PARTITION BY year, gender ORDER BY SUM(number) DESC) as rank_in_gender
    FROM us_baby_names
    WHERE year BETWEEN 1970 AND 2019
    GROUP BY year, name, gender
)
SELECT 
    year,
    MAX(CASE WHEN gender = 'M' AND rank_in_gender = 1 THEN name END) AS top_male_name,
    MAX(CASE WHEN gender = 'M' AND rank_in_gender = 1 THEN total_count END) AS male_count,
    MAX(CASE WHEN gender = 'F' AND rank_in_gender = 1 THEN name END) AS top_female_name,
    MAX(CASE WHEN gender = 'F' AND rank_in_gender = 1 THEN total_count END) AS female_count
FROM yearly_rankings
WHERE rank_in_gender = 1
GROUP BY year
ORDER BY year;

-- Query alternativa che mostra anche i top 3 per ogni genere
WITH yearly_rankings AS (
    SELECT 
        year,
        name,
        gender,
        SUM(number) as total_count,
        ROW_NUMBER() OVER (PARTITION BY year, gender ORDER BY SUM(number) DESC) as rank_in_gender
    FROM us_baby_names
    WHERE year BETWEEN 1970 AND 2019
    GROUP BY year, name, gender
)
SELECT 
    year,
    gender,
    STRING_AGG(
        name || ' (' || total_count || ')', 
        ', ' 
        ORDER BY rank_in_gender
    ) AS top_3_names
FROM yearly_rankings
WHERE rank_in_gender <= 3
GROUP BY year, gender
ORDER BY year, gender;