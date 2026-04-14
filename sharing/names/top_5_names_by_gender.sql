-- Query per mostrare i top 5 nomi maschili e femminili per ogni anno dal 1970 al 2019
-- Risultato: una riga per anno con due colonne (M e F) contenenti i top 5 nomi

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
    STRING_AGG(
        CASE WHEN gender = 'F' THEN name END, 
        ', ' 
        ORDER BY rank_in_gender
    ) AS top_5_female,
    STRING_AGG(
        CASE WHEN gender = 'M' THEN name END, 
        ', ' 
        ORDER BY rank_in_gender
    ) AS top_5_male
FROM yearly_rankings
WHERE rank_in_gender <= 5
GROUP BY year
ORDER BY year;