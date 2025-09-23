from db import loader
import sqlite3

def analyze_database():
    con = loader.connect()
    devs = loader.fetch_devices(con)
    
    print(f"Total devices: {len(devs)}")
    
    # Count named vs unnamed devices
    named_devices = [d for d in devs if d['name'] and d['name'].strip()]
    unnamed_devices = [d for d in devs if not d['name'] or not d['name'].strip()]
    
    print(f"Named devices: {len(named_devices)}")
    print(f"Unnamed devices: {len(unnamed_devices)}")
    
    # Show sample named devices
    print("\nSample named devices:")
    for i, d in enumerate(named_devices[:10]):
        print(f"{i+1}. {d['name']} ({d['symbol']}) - {d['manufacturer']} - {d['type']} - {d['system_category']}")
    
    # Show sample unnamed devices
    print("\nSample unnamed devices:")
    for i, d in enumerate(unnamed_devices[:10]):
        print(f"{i+1}. ({d['symbol']}) - {d['manufacturer']} - {d['type']} - {d['system_category']} - {d['part_number']}")
    
    # Analyze categories
    categories = {}
    for d in devs:
        cat = d['system_category'] or 'Uncategorized'
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\nTop 10 categories:")
    sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)
    for cat, count in sorted_cats[:10]:
        print(f"  {cat}: {count}")
    
    # Analyze manufacturers
    manufacturers = {}
    for d in devs:
        mfr = d['manufacturer'] or 'Unknown'
        manufacturers[mfr] = manufacturers.get(mfr, 0) + 1
    
    print(f"\nTop 10 manufacturers:")
    sorted_mfrs = sorted(manufacturers.items(), key=lambda x: x[1], reverse=True)
    for mfr, count in sorted_mfrs[:10]:
        print(f"  {mfr}: {count}")
    
    # Analyze device types
    types = {}
    for d in devs:
        typ = d['type'] or 'Unknown'
        types[typ] = types.get(typ, 0) + 1
    
    print(f"\nDevice types:")
    sorted_types = sorted(types.items(), key=lambda x: x[1], reverse=True)
    for typ, count in sorted_types:
        print(f"  {typ}: {count}")
    
    con.close()

if __name__ == "__main__":
    analyze_database()