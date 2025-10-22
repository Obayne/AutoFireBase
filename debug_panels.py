import sqlite3


def main() -> None:
    """Simple debug helper to validate the fetch_panels SQL."""
    con = sqlite3.connect("autofire.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    print("Testing fetch_panels query...")

    try:
        cur.execute(
            "SELECT p.id, p.manufacturer_id, p.model, p.name, p.panel_type, "
            "p.max_devices, p.properties_json, m.name as manufacturer_name "
            "FROM panels p "
            "LEFT JOIN manufacturers m ON m.id = p.manufacturer_id "
            "ORDER BY m.name, p.model"
        )
        rows = cur.fetchall()
        print(f"Query succeeded, found {len(rows)} rows")
        for i, row in enumerate(rows):
            print(f"Row {i}: {dict(row) if hasattr(row, 'keys') else row}")
    except Exception as e:
        print(f"Query failed: {e}")
    finally:
        con.close()


if __name__ == "__main__":
    main()
