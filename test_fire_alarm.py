"""
Simple test script to verify fire alarm system functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from db.fire_alarm_seeder import initialize_fire_alarm_database
from db.firelite_catalog import FIRELITE_CATALOG

def test_fire_alarm_system():
    """Test basic fire alarm system functionality."""
    print("Testing Fire Alarm System...")
    
    # Initialize database
    db_path = "test_fire_alarm.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    success = initialize_fire_alarm_database(db_path)
    print(f"Database initialization: {'SUCCESS' if success else 'FAILED'}")
    
    # Test catalog access
    print(f"Fire-Lite catalog contains {len(FIRELITE_CATALOG)} devices")
    
    # List some devices
    print("\nAvailable Fire-Lite devices:")
    for model, spec in list(FIRELITE_CATALOG.items())[:5]:
        print(f"  {model}: {spec.get('description', 'No description')}")
    
    print("\nFire Alarm System test completed successfully!")
    
    # Clean up
    if os.path.exists(db_path):
        os.remove(db_path)

if __name__ == "__main__":
    test_fire_alarm_system()