-- Query per confrontare i nomi nel tempo con varianti
-- Risultato: tabella con colonne year, Matteo, Sara, Emma, Maria, Anna

SELECT 
    year,
    -- Matteo e varianti
    COALESCE(SUM(CASE 
        WHEN name IN ('Matteo', 'Mateo', 'Mathew', 'Matthew', 'Matt', 'Mat', 'Mattie', 'Matty') 
        THEN number 
        ELSE 0 
    END), 0) AS Matteo,
    
    -- Sara e varianti
    COALESCE(SUM(CASE 
        WHEN name IN ('Sara', 'Sarah') 
        THEN number 
        ELSE 0 
    END), 0) AS Sara,
    
    -- Emma e varianti
    COALESCE(SUM(CASE 
        WHEN name IN ('Emma', 'Ema') 
        THEN number 
        ELSE 0 
    END), 0) AS Emma,
    
    -- Maria e varianti
    COALESCE(SUM(CASE 
        WHEN name IN ('Maria', 'Mary', 'Mariah', 'Marie', 'María', 'Mariam', 'Miriam', 'Myriam') 
        THEN number 
        ELSE 0 
    END), 0) AS Maria,
    
    -- Anna e varianti
    COALESCE(SUM(CASE 
        WHEN name IN ('Anna', 'Hannah', 'Anne', 'Ann', 'Ana', 'Hanna', 'Hanne') 
        THEN number 
        ELSE 0 
    END), 0) AS Anna

FROM us_baby_names
GROUP BY year
ORDER BY year;

-- Query alternativa con risultati più dettagliati (mostra M/F separatamente)
SELECT 
    year,
    gender,
    -- Matteo e varianti
    COALESCE(SUM(CASE 
        WHEN name IN ('Matteo', 'Mateo', 'Mathew', 'Matthew', 'Matt', 'Mat', 'Mattie', 'Matty') 
        THEN number 
        ELSE 0 
    END), 0) AS Matteo,
    
    -- Sara e varianti
    COALESCE(SUM(CASE 
        WHEN name IN ('Sara', 'Sarah') 
        THEN number 
        ELSE 0 
    END), 0) AS Sara,
    
    -- Emma e varianti
    COALESCE(SUM(CASE 
        WHEN name IN ('Emma', 'Ema') 
        THEN number 
        ELSE 0 
    END), 0) AS Emma,
    
    -- Maria e varianti
    COALESCE(SUM(CASE 
        WHEN name IN ('Maria', 'Mary', 'Mariah', 'Marie', 'María', 'Mariam', 'Miriam', 'Myriam') 
        THEN number 
        ELSE 0 
    END), 0) AS Maria,
    
    -- Anna e varianti
    COALESCE(SUM(CASE 
        WHEN name IN ('Anna', 'Hannah', 'Anne', 'Ann', 'Ana', 'Hanna', 'Hanne') 
        THEN number 
        ELSE 0 
    END), 0) AS Anna

FROM us_baby_names
GROUP BY year, gender
ORDER BY year, gender;

-- Query per vedere il trend di un nome specifico nel tempo (esempio: Matteo)
SELECT 
    year,
    name,
    gender,
    number
FROM us_baby_names
WHERE name IN ('Matteo', 'Mateo', 'Mathew', 'Matthew', 'Matt', 'Mat', 'Mattie', 'Matty')
ORDER BY year, name, gender;