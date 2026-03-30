import sqlite3
import pandas as pd
import os

# Rename the existing database file
if os.path.exists('user_data.db'):
    os.rename('user_data.db', 'user_data_backup.db')

# Load the CSV file
df = pd.read_csv('user_data.csv')

# Create a new database and table
conn = sqlite3.connect('user_data.db')
df.to_sql('users', conn, if_exists='replace', index=False)
conn.close()

print("File converted to SQL table successfully.")
