-- Query per ottenere il ranking di ogni gruppo di nomi per anno
-- Risultato: tabella con colonne year, Matteo_rank, Sara_rank, Emma_rank, Maria_rank, Anna_rank

WITH name_counts AS (
    -- Prima calcoliamo i totali per ogni gruppo di nomi per anno
    SELECT 
        year,
        -- Matteo e varianti
        SUM(CASE 
            WHEN name IN ('Matteo', 'Mateo', 'Mathew', 'Matthew', 'Matt', 'Mat', 'Mattie', 'Matty') 
            THEN number 
            ELSE 0 
        END) AS matteo_total,
        
        -- Sara e varianti
        SUM(CASE 
            WHEN name IN ('Sara', 'Sarah') 
            THEN number 
            ELSE 0 
        END) AS sara_total,
        
        -- Emma e varianti
        SUM(CASE 
            WHEN name IN ('Emma', 'Ema') 
            THEN number 
            ELSE 0 
        END) AS emma_total,
        
        -- Maria e varianti
        SUM(CASE 
            WHEN name IN ('Maria', 'Mary', 'Mariah', 'Marie', 'María', 'Mariam', 'Miriam', 'Myriam') 
            THEN number 
            ELSE 0 
        END) AS maria_total,
        
        -- Anna e varianti
        SUM(CASE 
            WHEN name IN ('Anna', 'Hannah', 'Anne', 'Ann', 'Ana', 'Hanna', 'Hanne') 
            THEN number 
            ELSE 0 
        END) AS anna_total
    FROM us_baby_names
    GROUP BY year
),
all_names_by_year AS (
    -- Calcoliamo il totale per ogni nome (non gruppo) per anno per il ranking
    SELECT 
        year,
        name,
        SUM(number) as total_count
    FROM us_baby_names
    GROUP BY year, name
),
ranked_names AS (
    -- Assegniamo un rank a ogni nome per anno
    SELECT 
        year,
        name,
        total_count,
        RANK() OVER (PARTITION BY year ORDER BY total_count DESC) as popularity_rank
    FROM all_names_by_year
)
-- Query finale che mostra il ranking per ogni gruppo
SELECT 
    nc.year,
    -- Rank di Matteo (basato sul totale del gruppo)
    (SELECT MIN(rn.popularity_rank) 
     FROM ranked_names rn 
     WHERE rn.year = nc.year 
     AND rn.total_count <= nc.matteo_total
     AND nc.matteo_total > 0) AS Matteo_rank,
    
    -- Rank di Sara
    (SELECT MIN(rn.popularity_rank) 
     FROM ranked_names rn 
     WHERE rn.year = nc.year 
     AND rn.total_count <= nc.sara_total
     AND nc.sara_total > 0) AS Sara_rank,
    
    -- Rank di Emma
    (SELECT MIN(rn.popularity_rank) 
     FROM ranked_names rn 
     WHERE rn.year = nc.year 
     AND rn.total_count <= nc.emma_total
     AND nc.emma_total > 0) AS Emma_rank,
    
    -- Rank di Maria
    (SELECT MIN(rn.popularity_rank) 
     FROM ranked_names rn 
     WHERE rn.year = nc.year 
     AND rn.total_count <= nc.maria_total
     AND nc.maria_total > 0) AS Maria_rank,
    
    -- Rank di Anna
    (SELECT MIN(rn.popularity_rank) 
     FROM ranked_names rn 
     WHERE rn.year = nc.year 
     AND rn.total_count <= nc.anna_total
     AND nc.anna_total > 0) AS Anna_rank

FROM name_counts nc
ORDER BY nc.year;

-- Query alternativa più semplice che mostra rank approssimativo basato sui 5 gruppi
WITH name_groups AS (
    SELECT 
        year,
        'Matteo' as name_group,
        SUM(CASE 
            WHEN name IN ('Matteo', 'Mateo', 'Mathew', 'Matthew', 'Matt', 'Mat', 'Mattie', 'Matty') 
            THEN number 
            ELSE 0 
        END) AS total
    FROM us_baby_names
    GROUP BY year
    
    UNION ALL
    
    SELECT 
        year,
        'Sara' as name_group,
        SUM(CASE 
            WHEN name IN ('Sara', 'Sarah') 
            THEN number 
            ELSE 0 
        END) AS total
    FROM us_baby_names
    GROUP BY year
    
    UNION ALL
    
    SELECT 
        year,
        'Emma' as name_group,
        SUM(CASE 
            WHEN name IN ('Emma', 'Ema') 
            THEN number 
            ELSE 0 
        END) AS total
    FROM us_baby_names
    GROUP BY year
    
    UNION ALL
    
    SELECT 
        year,
        'Maria' as name_group,
        SUM(CASE 
            WHEN name IN ('Maria', 'Mary', 'Mariah', 'Marie', 'María', 'Mariam', 'Miriam', 'Myriam') 
            THEN number 
            ELSE 0 
        END) AS total
    FROM us_baby_names
    GROUP BY year
    
    UNION ALL
    
    SELECT 
        year,
        'Anna' as name_group,
        SUM(CASE 
            WHEN name IN ('Anna', 'Hannah', 'Anne', 'Ann', 'Ana', 'Hanna', 'Hanne') 
            THEN number 
            ELSE 0 
        END) AS total
    FROM us_baby_names
    GROUP BY year
),
ranked_groups AS (
    SELECT 
        year,
        name_group,
        total,
        RANK() OVER (PARTITION BY year ORDER BY total DESC) as group_rank
    FROM name_groups
    WHERE total > 0
)
-- Pivot per mostrare i rank in colonne
SELECT 
    year,
    MAX(CASE WHEN name_group = 'Matteo' THEN group_rank END) AS Matteo_rank,
    MAX(CASE WHEN name_group = 'Sara' THEN group_rank END) AS Sara_rank,
    MAX(CASE WHEN name_group = 'Emma' THEN group_rank END) AS Emma_rank,
    MAX(CASE WHEN name_group = 'Maria' THEN group_rank END) AS Maria_rank,
    MAX(CASE WHEN name_group = 'Anna' THEN group_rank END) AS Anna_rank
FROM ranked_groups
GROUP BY year
ORDER BY year;