# db/coverage_tables.py

WALL_STROBE_TABLE_NAME = 'wall_strobe_coverage'
CEILING_STROBE_TABLE_NAME = 'ceiling_strobe_coverage'

def create_tables(con):
    cur = con.cursor()
    cur.execute(f'''
        CREATE TABLE IF NOT EXISTS {WALL_STROBE_TABLE_NAME} (
            room_size INTEGER PRIMARY KEY,
            candela INTEGER NOT NULL
        )
    ''')
    cur.execute(f'''
        CREATE TABLE IF NOT EXISTS {CEILING_STROBE_TABLE_NAME} (
            ceiling_height INTEGER,
            room_size INTEGER,
            candela INTEGER NOT NULL,
            PRIMARY KEY (ceiling_height, room_size)
        )
    ''')
    # Strobe radius table for coverage calculations
    cur.execute('''
        CREATE TABLE IF NOT EXISTS strobe_candela (
            candela INTEGER PRIMARY KEY,
            radius_ft REAL NOT NULL
        )
    ''')
    con.commit()

def populate_tables(con):
    cur = con.cursor()
    # Wall-mounted data
    wall_data = [
        (20, 15),
        (30, 30),
        (40, 60),
        (50, 95),
        (60, 135),
        (70, 185),
    ]
    cur.executemany(f"INSERT OR REPLACE INTO {WALL_STROBE_TABLE_NAME} VALUES (?, ?)", wall_data)

    # Ceiling-mounted data
    ceiling_data = [
        (10, 24, 15),
        (10, 40, 30),
        (10, 54, 60),
        (10, 70, 95),
        (10, 80, 115),
        (10, 96, 150),
        (20, 20, 15),
        (20, 30, 30),
        (20, 40, 60),
        (20, 50, 95),
        (20, 60, 115),
        (20, 70, 150),
        (30, 15, 15),
        (30, 25, 30),
        (30, 35, 60),
        (30, 45, 95),
        (30, 55, 115),
        (30, 65, 150),
    ]
    cur.executemany(f"INSERT OR REPLACE INTO {CEILING_STROBE_TABLE_NAME} VALUES (?, ?, ?)", ceiling_data)
    # Strobe radius data
    radius_data = [
        (15, 15.0),
        (30, 20.0),
        (75, 30.0),
        (95, 35.0),
        (110, 38.0),
        (135, 43.0),
        (185, 50.0),
    ]
    cur.executemany("INSERT OR REPLACE INTO strobe_candela VALUES (?, ?)", radius_data)
    con.commit()
