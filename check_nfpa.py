import sqlite3

con = sqlite3.connect(r'C:\Users\whoba\AutoFire\catalog.db')
cur = con.cursor()
cur.execute("SELECT d.name, d.symbol, dt.code FROM devices d JOIN device_types dt ON d.type_id = dt.id WHERE dt.code = 'NFPA 170'")
rows = cur.fetchall()
print('Found', len(rows), 'NFPA 170 devices:')
for row in rows:
    print(' ', row[0], '(', row[1], ')')
con.close()