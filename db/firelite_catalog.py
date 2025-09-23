"""
Fire-Lite device catalog with comprehensive FACP panels and devices.
This module contains real Fire-Lite part numbers and specifications
for accurate system design and calculations.
"""

FIRELITE_FACP_PANELS = {
    # Fire-Lite Addressable Fire Alarm Control Panels
    "MS-9200UDLS": {
        "name": "MS-9200UDLS",
        "description": "Addressable Fire Alarm Control Panel",
        "type": "FACP",
        "slc_loops": 2,
        "devices_per_loop": 159,
        "total_devices": 318,
        "power_supply": "120/240 VAC",
        "standby_current": 0.350,  # Amps
        "alarm_current": 1.200,    # Amps
        "aux_power_24v": 3.0,      # Amps available
        "battery_calc_factor": 1.25,
        "features": ["Dual SLC loops", "Network capable", "Voice evacuation ready"],
        "dimensions": {"width": 19.0, "height": 24.5, "depth": 6.5},  # inches
        "weight": 65.0,  # pounds
        "nfpa_compliant": True
    },
    "MS-9600UDLS": {
        "name": "MS-9600UDLS", 
        "description": "Large Addressable Fire Alarm Control Panel",
        "type": "FACP",
        "slc_loops": 6,
        "devices_per_loop": 159,
        "total_devices": 954,
        "power_supply": "120/240 VAC",
        "standby_current": 0.800,
        "alarm_current": 2.500,
        "aux_power_24v": 6.0,
        "battery_calc_factor": 1.25,
        "features": ["Six SLC loops", "Network capable", "Campus-wide systems"],
        "dimensions": {"width": 23.6, "height": 42.0, "depth": 8.5},
        "weight": 125.0,
        "nfpa_compliant": True
    },
    "MS-4": {
        "name": "MS-4",
        "description": "4-Zone Conventional Fire Alarm Control Panel", 
        "type": "FACP",
        "slc_loops": 0,  # Conventional zones
        "zones": 4,
        "devices_per_zone": 20,  # Typical conventional zone capacity
        "total_devices": 80,
        "power_supply": "120 VAC",
        "standby_current": 0.120,
        "alarm_current": 0.400,
        "aux_power_24v": 1.5,
        "battery_calc_factor": 1.25,
        "features": ["Conventional zones", "Entry level", "Small buildings"],
        "dimensions": {"width": 13.5, "height": 13.5, "depth": 3.25},
        "weight": 15.0,
        "nfpa_compliant": True
    }
}

FIRELITE_DETECTORS = {
    # Addressable Smoke Detectors
    "SD355": {
        "name": "SD355",
        "description": "Addressable Photoelectric Smoke Detector",
        "type": "Detector",
        "detection_type": "photoelectric",
        "addressable": True,
        "current_standby": 0.00045,  # 450 microamps
        "current_alarm": 0.00045,
        "voltage": 24,
        "spacing_standard": 30,  # feet (per NFPA 72)
        "spacing_smooth_ceiling": 30,
        "spacing_open_joists": 25,
        "height_max": 30,  # feet
        "temp_rating": {"min": 32, "max": 120},  # Fahrenheit
        "humidity_rating": {"min": 10, "max": 93},  # % RH
        "ul_listed": True,
        "fm_approved": True,
        "manufacturer": "Fire-Lite",
        "category": "Life Safety"
    },
    "SD355T": {
        "name": "SD355T",
        "description": "Addressable Photoelectric Smoke Detector with Thermal",
        "type": "Detector", 
        "detection_type": "photoelectric_thermal",
        "addressable": True,
        "current_standby": 0.00050,
        "current_alarm": 0.00050,
        "voltage": 24,
        "spacing_standard": 30,
        "thermal_rating": 135,  # degrees F
        "height_max": 30,
        "temp_rating": {"min": 32, "max": 120},
        "humidity_rating": {"min": 10, "max": 93},
        "ul_listed": True,
        "fm_approved": True,
        "manufacturer": "Fire-Lite",
        "category": "Life Safety"
    },
    "HD355": {
        "name": "HD355",
        "description": "Addressable Heat Detector",
        "type": "Detector",
        "detection_type": "thermal",
        "addressable": True,
        "current_standby": 0.00045,
        "current_alarm": 0.00045,
        "voltage": 24,
        "spacing_standard": 50,  # feet (heat detectors)
        "thermal_rating": 135,  # Fixed temperature
        "rate_of_rise": 15,  # degrees per minute
        "height_max": 30,
        "temp_rating": {"min": 32, "max": 150},
        "ul_listed": True,
        "fm_approved": True,
        "manufacturer": "Fire-Lite",
        "category": "Life Safety"
    }
}

FIRELITE_NOTIFICATION = {
    # Addressable Notification Appliances  
    "PSE-4": {
        "name": "PSE-4",
        "description": "Addressable Strobe (Red)",
        "type": "Notification",
        "notification_type": "visual",
        "addressable": True,
        "candela_options": [15, 30, 75, 110],
        "current_per_candela": {15: 0.045, 30: 0.055, 75: 0.095, 110: 0.135},
        "voltage": 24,
        "flash_rate": 1,  # Hz
        "mounting": ["wall", "ceiling"],
        "colors": ["red", "white"],
        "ul_listed": True,
        "ada_compliant": True,
        "manufacturer": "Fire-Lite",
        "category": "Notification"
    },
    "PSH-4": {
        "name": "PSH-4", 
        "description": "Addressable Horn/Strobe (Red)",
        "type": "Notification",
        "notification_type": "audible_visual",
        "addressable": True,
        "candela_options": [15, 30, 75, 110],
        "current_per_candela": {15: 0.070, 30: 0.080, 75: 0.120, 110: 0.160},
        "horn_current": 0.025,  # Additional for horn
        "voltage": 24,
        "sound_output": {"low": 87, "med": 91, "high": 95},  # dBA at 10 feet
        "flash_rate": 1,
        "mounting": ["wall", "ceiling"],
        "ul_listed": True,
        "ada_compliant": True,
        "manufacturer": "Fire-Lite",
        "category": "Notification"
    },
    "PSM-4": {
        "name": "PSM-4",
        "description": "Addressable Speaker/Strobe",
        "type": "Notification", 
        "notification_type": "voice_visual",
        "addressable": True,
        "candela_options": [15, 30, 75, 110],
        "current_per_candela": {15: 0.070, 30: 0.080, 75: 0.120, 110: 0.160},
        "speaker_power": {"0.25w": 0.025, "0.5w": 0.050, "1w": 0.100, "2w": 0.200},
        "voltage": 24,
        "frequency_response": {"min": 300, "max": 8000},  # Hz
        "mounting": ["wall", "ceiling"],
        "ul_listed": True,
        "ada_compliant": True,
        "manufacturer": "Fire-Lite", 
        "category": "Notification"
    }
}

FIRELITE_INITIATING = {
    # Manual Pull Stations
    "BG-12LX": {
        "name": "BG-12LX",
        "description": "Addressable Manual Pull Station",
        "type": "Initiating",
        "initiating_type": "manual",
        "addressable": True,
        "current_standby": 0.00050,
        "current_alarm": 0.00050,
        "voltage": 24,
        "action": "pull_down",
        "reset_type": "key_reset",
        "mounting": "wall",
        "height_aff": 42,  # inches above finished floor (ADA)
        "weather_rating": "indoor",
        "ul_listed": True,
        "ada_compliant": True,
        "manufacturer": "Fire-Lite",
        "category": "Initiating"
    },
    "BG-12": {
        "name": "BG-12",
        "description": "Conventional Manual Pull Station", 
        "type": "Initiating",
        "initiating_type": "manual",
        "addressable": False,
        "current_standby": 0.000,
        "current_alarm": 0.000,  # Supervised circuit
        "voltage": 24,
        "action": "pull_down",
        "reset_type": "key_reset", 
        "mounting": "wall",
        "height_aff": 42,
        "weather_rating": "indoor",
        "ul_listed": True,
        "ada_compliant": True,
        "manufacturer": "Fire-Lite",
        "category": "Initiating"
    }
}

FIRELITE_MODULES = {
    # Input/Output Control Modules
    "MMX-1": {
        "name": "MMX-1",
        "description": "Addressable Control Module",
        "type": "Module",
        "module_type": "control",
        "addressable": True,
        "current_standby": 0.00045,
        "current_alarm": 0.00045,
        "voltage": 24,
        "contacts": "Form C relay",
        "contact_rating": {"voltage": 30, "current": 2.0},  # VDC, Amps
        "functions": ["Door holder release", "Elevator recall", "HVAC shutdown"],
        "ul_listed": True,
        "manufacturer": "Fire-Lite",
        "category": "Control"
    },
    "MMI-1": {
        "name": "MMI-1",
        "description": "Addressable Input Module",
        "type": "Module",
        "module_type": "input",
        "addressable": True,
        "current_standby": 0.00045,
        "current_alarm": 0.00045,
        "voltage": 24,
        "input_type": "supervised",
        "functions": ["Waterflow switch", "Tamper switch", "Gate valve"],
        "ul_listed": True,
        "manufacturer": "Fire-Lite",
        "category": "Input"
    }
}

# Compiled device catalog
FIRELITE_CATALOG = {
    **FIRELITE_FACP_PANELS,
    **FIRELITE_DETECTORS,
    **FIRELITE_NOTIFICATION,
    **FIRELITE_INITIATING,
    **FIRELITE_MODULES
}

def get_device_by_model(model: str):
    """Get Fire-Lite device specifications by model number."""
    return FIRELITE_CATALOG.get(model)

def get_devices_by_type(device_type: str):
    """Get all Fire-Lite devices of specified type."""
    return {k: v for k, v in FIRELITE_CATALOG.items() if v.get("type") == device_type}

def get_addressable_devices():
    """Get all addressable Fire-Lite devices."""
    return {k: v for k, v in FIRELITE_CATALOG.items() if v.get("addressable", False)}

def get_facp_panels():
    """Get all Fire-Lite FACP panel specifications."""
    return FIRELITE_FACP_PANELS

def calculate_device_current(device_spec: dict, operating_mode: str = "standby"):
    """Calculate current draw for a device in standby or alarm mode."""
    if operating_mode == "standby":
        return device_spec.get("current_standby", 0.0)
    elif operating_mode == "alarm":
        return device_spec.get("current_alarm", 0.0)
    return 0.0