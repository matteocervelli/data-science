import pandas as pd
import re

def pandas_to_postgres_type(pandas_dtype, max_length=None, unique_values=None):
    """Convert pandas data types to PostgreSQL data types"""

    if pandas_dtype == 'int64':
        return 'INTEGER'
    elif pandas_dtype == 'float64':
        return 'DECIMAL(10,2)'
    elif pandas_dtype == 'bool':
        return 'BOOLEAN'
    elif pandas_dtype == 'object':  # string
        if max_length <= 10:
            return 'VARCHAR(20)'
        elif max_length <= 50:
            return 'VARCHAR(100)'
        else:
            return 'TEXT'
    else:
        return 'TEXT'   # default to text for other types
        
def clean_column_name(col_name):
    """Clean column names for PostgreSQL"""

    # Remove special characters and convert to lowercase
    cleaned_name = re.sub(r'[^a-zA-Z0-9_]', '_', col_name.lower())
    
    # Remove leading and trailing underscores
    cleaned_name = re.sub(r'^_+|_+$', '', cleaned_name)

    # Remove multiple underscores
    cleaned_name = re.sub(r'_+', '_', cleaned_name)

    # Handle special cases
    if not cleaned_name:
        cleaned_name = 'pokemon_id'  # Specific for # column
    elif cleaned_name[0].isdigit():
        cleaned_name = 'col_' + cleaned_name

    return cleaned_name

def analyze_csv_and_generate_schema(csv_file_path, table_name):
    """Analyze a CSV file and generate a schema for PostgreSQL"""

    print(f"Analyzing CSV file: {csv_file_path}")
    df = pd.read_csv(csv_file_path)

    print(f"Analyzing {len(df)} rows and {len(df.columns)} columns")
    print("\n" + "="*50)

    # Analyze each column
    schema_parts = []
    cleaned_columns = []

    for col in df.columns:
        cleaned_col = clean_column_name(col)

        dtype = df[col].dtype
        null_count = df[col].isnull().sum()
        unique_count = df[col].nunique()

        # Calculate max length for string columns
        max_length = None
        if dtype == 'object' and not df[col].empty:
            max_length = df[col].astype(str).str.len().max()
        
        postgres_type = pandas_to_postgres_type(dtype, max_length, unique_count)

        # Determine constraints
        constraints = []
        if null_count == 0:  # No null values
            constraints.append("NOT NULL")
        
        # First column as PRIMARY KEY if it seems like an ID
        if col == df.columns[0] and dtype == 'int64' and unique_count == len(df):
            constraints.append("PRIMARY KEY")
        
        constraint_str = " " + " ".join(constraints) if constraints else ""
        
        schema_parts.append(f"    {cleaned_col} {postgres_type}{constraint_str}")
        cleaned_columns.append(cleaned_col)

        print(f"✅ {col} -> {cleaned_col}: {postgres_type}")
        print(f"   Null: {null_count}, Unique: {unique_count}")
        if max_length:
            print(f"   Max length: {max_length}")
        print()

    # Generate the CREATE TABLE SQL statement
    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
    create_table_sql += ",\n".join(schema_parts)
    create_table_sql += "\n);"
    
    # Generate COPY command
    copy_command = f"""-- Import data from CSV
COPY {table_name} ({', '.join(cleaned_columns)})
FROM '{csv_file_path}'
WITH (
    FORMAT csv,
    HEADER true,
    DELIMITER ',',
    NULL ''
);"""
    
    # Verification queries
    verification_queries = f"""-- Verification queries
SELECT COUNT(*) as total_rows FROM {table_name};

SELECT * FROM {table_name} LIMIT 5;

-- Column statistics
SELECT 
    '{cleaned_columns[0]}' as column_name,
    COUNT(*) as total,
    COUNT({cleaned_columns[0]}) as non_null,
    COUNT(DISTINCT {cleaned_columns[0]}) as unique_values
FROM {table_name};"""
    
    print("="*60)
    print("🎯 POSTGRESQL SCHEMA GENERATED:")
    print(create_table_sql)
    print("\n" + "="*60)
    print("📥 COPY COMMAND:")
    print(copy_command)
    print("\n" + "="*60)
    print("🔍 VERIFICATION QUERIES:")
    print(verification_queries)
    
    # Save to file
    with open(f'{table_name}_schema.sql', 'w') as f:
        f.write(create_table_sql + '\n\n')
        f.write(copy_command + '\n\n')
        f.write(verification_queries)
    
    print(f"\n💾 Schema saved in: {table_name}_schema.sql")
    
    return create_table_sql, copy_command, verification_queries

# Usage
if __name__ == "__main__":
    csv_file_path = 'Pokemon.csv'
    table_name = 'pokemon'
    analyze_csv_and_generate_schema(csv_file_path, table_name)