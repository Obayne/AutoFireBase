import sys

sys.path.insert(0, ".")
from db import loader as db_loader

con = db_loader.connect()
db_loader.ensure_schema(con)
cur = con.cursor()

# Sample device models to understand categorization
cur.execute("SELECT DISTINCT model FROM devices WHERE model LIKE ? LIMIT 10", ("%smoke%",))
print("Smoke-related devices:")
for row in cur.fetchall():
    print(f'  {row["model"]}')

cur.execute("SELECT DISTINCT model FROM devices WHERE model LIKE ? LIMIT 10", ("%camera%",))
print("\nCamera-related devices:")
for row in cur.fetchall():
    print(f'  {row["model"]}')

cur.execute("SELECT DISTINCT model FROM devices WHERE model LIKE ? LIMIT 10", ("%burglar%",))
print("\nBurglar-related devices:")
for row in cur.fetchall():
    print(f'  {row["model"]}')

cur.execute("SELECT DISTINCT model FROM devices WHERE model LIKE ? LIMIT 10", ("%access%",))
print("\nAccess-related devices:")
for row in cur.fetchall():
    print(f'  {row["model"]}')

con.close()
