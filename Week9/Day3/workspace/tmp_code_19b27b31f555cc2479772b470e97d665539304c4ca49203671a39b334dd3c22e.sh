# Ensure the database exists and has data before running the python script
python -c "import pandas as pd; import sqlite3; df = pd.read_csv('user_data.csv'); conn = sqlite3.connect('user_data.db'); df.to_sql('user_data', conn, if_exists='replace', index=False); conn.close()"
