from db import connection

connection.initialize_database(in_memory=False)
conn = connection.get_connection()
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM devices')
print(f'✅ APP CONNECTED TO PERSISTENT DATABASE')
print(f'Total devices: {cursor.fetchone()[0]}')

cursor.execute('SELECT COUNT(DISTINCT manufacturer_id) FROM devices')
print(f'Manufacturers: {cursor.fetchone()[0]}')

cursor.execute('SELECT name FROM manufacturers LIMIT 10')
print('\nSample manufacturers:')
for row in cursor.fetchall():
    print(f'  - {row[0]}')

cursor.execute('SELECT model, name FROM devices WHERE model LIKE "%177CD%" LIMIT 5')
print('\nSample high-candela strobes:')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}')

cursor.execute('SELECT category, COUNT(*) as cnt FROM (SELECT json_extract(properties_json, \"$.type\") as category FROM devices) GROUP BY category ORDER BY cnt DESC LIMIT 10')
print('\nDevice distribution:')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]} devices')
