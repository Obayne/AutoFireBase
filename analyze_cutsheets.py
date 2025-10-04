#!/usr/bin/env python3
"""
FIRELITE & System Sensor Cutsheet Analysis Tool
Compare actual manufacturer specifications with AutoFire database
"""

import sqlite3
from pathlib import Path


def analyze_cutsheet_directories():
    """Analyze what cutsheet models we have vs what's in the database."""

    cutsheet_path = Path("cutsheets_analysis")

    print("🔥 FIRELITE & SYSTEM SENSOR CUTSHEET ANALYSIS")
    print("=" * 60)

    # Get all model directories from cutsheets
    firelite_models = []
    system_sensor_models = []

    for item in cutsheet_path.iterdir():
        if item.is_dir():
            model_name = item.name

            # Categorize by typical naming patterns
            if model_name.startswith(("MS-", "ANN-", "BG-", "ES-", "ECC-")):
                firelite_models.append(model_name)
            elif model_name.startswith(("2W", "4W", "56", "CO", "D4", "HW", "P2", "PC2", "S")):
                system_sensor_models.append(model_name)
            else:
                # Check the contents to determine manufacturer
                firelite_models.append(model_name)  # Default to Firelite for now

    print(f"\n📁 FIRELITE MODELS IN CUTSHEETS ({len(firelite_models)}):")
    for model in sorted(firelite_models):
        print(f"   {model}")

    print(f"\n📁 SYSTEM SENSOR MODELS IN CUTSHEETS ({len(system_sensor_models)}):")
    for model in sorted(system_sensor_models):
        print(f"   {model}")

    # Now compare with database
    print("\n🔍 DATABASE COMPARISON:")
    print("-" * 40)

    try:
        conn = sqlite3.connect("autofire.db")
        cursor = conn.cursor()

        # Get all panels from database
        cursor.execute("SELECT model, name FROM panels ORDER BY model")
        db_panels = cursor.fetchall()

        print(f"\n📊 PANELS IN DATABASE ({len(db_panels)}):")
        for model, name in db_panels:
            print(f"   {model} - {name}")

        # Get all devices from database
        cursor.execute("SELECT model, name FROM devices ORDER BY model")
        db_devices = cursor.fetchall()

        print(f"\n📊 DEVICES IN DATABASE ({len(db_devices)}):")
        for model, name in db_devices:
            print(f"   {model} - {name}")

        conn.close()

        # Analysis: What's missing?
        print("\n❌ MISSING FROM DATABASE:")
        print("-" * 30)

        db_panel_models = [model for model, name in db_panels]
        db_device_models = [model for model, name in db_devices]
        all_db_models = set(db_panel_models + db_device_models)

        cutsheet_models = set(firelite_models + system_sensor_models)

        missing_from_db = cutsheet_models - all_db_models
        missing_from_cutsheets = all_db_models - cutsheet_models

        if missing_from_db:
            print("Missing from DATABASE (have cutsheets but not in DB):")
            for model in sorted(missing_from_db):
                print(f"   📋 {model}")

        if missing_from_cutsheets:
            print("\nMissing CUTSHEETS (in DB but no cutsheet):")
            for model in sorted(missing_from_cutsheets):
                print(f"   🗄️ {model}")

        # Special focus on MS models
        print("\n🎯 MS MODEL ANALYSIS:")
        print("-" * 25)

        ms_cutsheets = [m for m in firelite_models if m.startswith("MS-")]
        ms_database = [m for m in all_db_models if m.startswith("MS-")]

        print(f"MS models in CUTSHEETS: {ms_cutsheets}")
        print(f"MS models in DATABASE: {ms_database}")

        if "MS-9050UD" in ms_database and "MS-9050UD" not in ms_cutsheets:
            print("❗ ISSUE: MS-9050UD is in database but no cutsheet found!")
            print("   Available MS cutsheets suggest different model numbers.")

        # Assembly complexity insights
        print("\n🔧 ASSEMBLY COMPLEXITY INSIGHTS:")
        print("-" * 35)
        print("FIRELITE Models (Simple Assembly):")
        for model in sorted(firelite_models):
            print(f"   ✅ {model} - Basic installation")

        print("\nSystem Sensor Models (Detector Compatibility):")
        for model in sorted(system_sensor_models):
            print(f"   🔗 {model} - Check panel compatibility")

    except Exception as e:
        print(f"Database error: {e}")


if __name__ == "__main__":
    analyze_cutsheet_directories()
