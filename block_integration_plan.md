# Block Integration Plan for AutoFire

## Current Status
- ✅ Database with 14,704 devices successfully imported
- ✅ Database schema properly structured with manufacturers, categories, and device types
- ⏳ DWG blocks available but not yet integrated

## Approach for Block Integration

### 1. Database Structure Enhancement
We need to add block information to the existing database structure. This can be done by:

#### Option A: Add Block Information to Devices Table
Add columns to the [devices](file://c:\Dev\Autofire\backend\slc_addressing.py#L50-L50) table:
```sql
ALTER TABLE devices ADD COLUMN block_name TEXT;
ALTER TABLE devices ADD COLUMN block_path TEXT;
ALTER TABLE devices ADD COLUMN block_attributes TEXT; -- JSON for attribute mapping
```

#### Option B: Create Separate Block Table (Recommended)
```sql
CREATE TABLE IF NOT EXISTS cad_blocks(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER,
    block_name TEXT,
    block_path TEXT,
    block_attributes TEXT, -- JSON for attribute mapping
    FOREIGN KEY(device_id) REFERENCES devices(id)
);
```

### 2. Attribute Mapping Strategy
Based on the Excel data structure, we can map:
- `PartNo` → Block name/identifier
- `Manufacturer` → Block library
- `Category`/`SubCategory` → Block type
- Device specifications → Block attributes

### 3. Implementation Plan

#### Phase 1: Database Enhancement
1. Add block-related tables to [db/loader.py](file://c:\Dev\Autofire\db\loader.py)
2. Modify [fetch_devices](file://c:\Dev\Autofire\db\loader.py#L272-L284) function to include block information
3. Create block management functions

#### Phase 2: Block Management System
1. Create block registration system
2. Implement block attribute mapping
3. Develop block insertion functionality

#### Phase 3: Integration with Existing Workflow
1. Link block selection to device catalog
2. Implement block placement with attribute population
3. Add block library management

## Sample Implementation

### Database Schema Addition
```sql
CREATE TABLE IF NOT EXISTS cad_blocks(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER,
    block_name TEXT,
    block_path TEXT,
    block_attributes TEXT, -- JSON format
    FOREIGN KEY(device_id) REFERENCES devices(id)
);
```

### Sample Data Structure
For a device like:
- Manufacturer: Edwards
- Part Number: C2M-PD1
- Category: Smoke Detector
- Description: Smoke Detector - 2 Wire Photo electric

The block mapping might be:
- Block Name: C2M-PD1
- Block Path: Blocks/DEVICE DETAILBLOCKS.dwg
- Attributes: {"PartNo": "C2M-PD1", "Manufacturer": "Edwards", "Type": "Smoke Detector"}

## Next Steps

1. **Implement database schema enhancement** - Add block tables
2. **Create block registration utility** - Tool to register DWG blocks with devices
3. **Develop attribute mapping system** - Link block attributes to database fields
4. **Build block placement functionality** - Integrate with CAD interface

## Considerations for DWG Files

Since we have DWG files rather than DXF:
1. **Short term**: Manual registration of blocks with device data
2. **Medium term**: Implement DWG to DXF conversion workflow
3. **Long term**: Integrate commercial DWG libraries for direct reading

This approach allows us to get the block functionality working immediately while planning for more advanced integration later.