import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

try:
    print("MainWindow imported successfully")

    from db import loader

    print("Database loader imported successfully")

    con = loader.connect()
    print("Database connection established")

    layers = loader.fetch_layers(con)
    print(f"Layers fetched successfully: {len(layers)} layers")

    print("All components working correctly!")

except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
