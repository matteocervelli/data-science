import pandas as pd
import numpy as np

df = pd.read_csv('Pokemon.csv')

print(df.info())
print("\n" + "="*50)
print(df.dtypes)

print("\n" + "="*50 + "\nANALISI DETTAGLIATA:")

# Analisi per ogni colonna
for col in df.columns:
    print(f"\n{col}:")
    print(f"  Tipo pandas: {df[col].dtype}")
    print(f"  Valori nulli: {df[col].isnull().sum()}")
    print(f"  Valori unici: {df[col].nunique()}")
    
    # Esempi specifici per tipo
    if df[col].dtype == 'object':
        print(f"  Lunghezza max: {df[col].str.len().max()}")
        print(f"  Esempi: {df[col].dropna().head(3).tolist()}")
    elif df[col].dtype in ['int64', 'float64']:
        print(f"  Min: {df[col].min()}, Max: {df[col].max()}")
    elif df[col].dtype == 'bool':
        print(f"  Distribuzione: {df[col].value_counts().to_dict()}")

# Verifica specifiche per Type 2
print(f"\n{'='*50}\nSPECIFICO Type 2:")
print(f"Pokemon con solo 1 tipo: {df['Type 2'].isnull().sum()}")
print(f"Pokemon con 2 tipi: {df['Type 2'].notnull().sum()}")