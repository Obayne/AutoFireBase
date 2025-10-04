# AutoFire Next Development Round - Strategic Roadmap

**Planning Date**: December 2024
**Current Version**: 0.8.0
**Target**: Professional Fire Alarm CAD Software
**Based On**: Master spec compliance audit, competitor research, implementation assessment

## 🎯 Executive Strategic Direction

AutoFire has achieved a **solid foundation** with professional CAD infrastructure and basic fire alarm functionality. The next development round focuses on implementing the **critical professional features** that distinguish industry-standard fire alarm CAD software.

**Primary Objective**: Transform AutoFire from foundational CAD tool to professional fire alarm design software competitive with FireCAD.

## 📋 Development Phases Overview

### Phase 1: Core Professional Features (CRITICAL - 3 months)
**Goal**: Implement essential professional features for real project use
**Features**: Live calculations, circuit management, enhanced device catalog

### Phase 2: Professional Workflow (HIGH - 6 months)
**Goal**: Complete professional workflow with reports and automation
**Features**: Report generation, auto-addressing, project setup wizard

### Phase 3: Advanced Automation (MEDIUM - 12 months)
**Goal**: Industry-leading automation and AI assistance
**Features**: Advanced circuit automation, AI assistant, mobile integration

## 🚀 Phase 1: Core Professional Features (CRITICAL)

### Issue #1: Project Circuits Editor (CRITICAL PRIORITY)
**Epic**: Central Circuit Management Interface
**Scope**: Build FireCAD-equivalent circuit management hub
**Estimated Effort**: 3-4 weeks

**Requirements**:
- Central interface for all circuit operations
- Comprehensive circuit properties (name, lock, visibility, cable type)
- Wirepath labeling configuration
- EOL notation and T-tapping settings
- Battery calculation influence controls
- Address management (starting addresses, overrides)
- Warning threshold configuration
- Integration with existing circuit validation

**Acceptance Criteria**:
- [ ] Circuit list with filter/search functionality
- [ ] Editable circuit properties in grid format
- [ ] Real-time updates to connected devices
- [ ] Integration with System Builder staged circuits
- [ ] Professional UI matching FireCAD functionality

**Files to Create/Modify**:
- `frontend/panels/project_circuits_editor.py` (new)
- `frontend/windows/model_space.py` (add circuits editor dock)
- `backend/circuit_manager.py` (enhance circuit data model)

### Issue #2: Live Calculations Engine (CRITICAL PRIORITY)
**Epic**: Professional Electrical Calculations
**Scope**: Implement voltage drop, battery sizing, SLC analysis
**Estimated Effort**: 4-5 weeks

**Requirements**:
- Voltage drop calculations (V = I × R per segment)
- Battery sizing with AH calculations and derating factors
- SLC loop analysis (length, device count, capacitance limits)
- Conduit fill calculations with threshold warnings
- Live updates as circuits/devices change
- Professional calculation reports

**Acceptance Criteria**:
- [ ] Voltage drop calculated per circuit segment
- [ ] Battery AH requirements based on device loads
- [ ] SLC loop validation with capacitance limits
- [ ] Conduit fill percentages with color-coded warnings
- [ ] Real-time calculation updates
- [ ] Calculation results displayed in inspector panels

**Files to Create/Modify**:
- `cad_core/calculations/` (new module)
  - `voltage_drop.py` (V=IR calculations)
  - `battery_sizing.py` (AH calculations with derating)
  - `slc_analysis.py` (loop analysis)
  - `conduit_fill.py` (cable area calculations)
- `frontend/panels/calculations_panel.py` (new)

### Issue #3: Enhanced Device Catalog (HIGH PRIORITY)
**Epic**: Comprehensive Fire Alarm Device Library
**Scope**: Expand from 7 to 200+ devices with specifications
**Estimated Effort**: 2-3 weeks

**Requirements**:
- Expand device catalog to 200+ fire alarm devices
- Add technical specifications (current, voltage, mounting)
- Manufacturer-specific organization
- NFPA 170 compliant symbols
- Device properties integration with calculations

**Acceptance Criteria**:
- [ ] 200+ fire alarm devices in database
- [ ] Complete technical specifications for each device
- [ ] Manufacturer categories (Honeywell, Siemens, Edwards, etc.)
- [ ] NFPA 170 symbol compliance
- [ ] Device properties drive calculation inputs

**Files to Create/Modify**:
- `backend/data/device_library.sql` (new comprehensive device data)
- `backend/catalog.py` (enhance loading and organization)
- `scripts/import_device_library.py` (new data import tool)

### Issue #4: Advanced Wire Routing (HIGH PRIORITY)
**Epic**: Professional Wire Routing Tools
**Scope**: Follow-path, AutoRoute modes with 3D calculations
**Estimated Effort**: 3-4 weeks

**Requirements**:
- Follow-path routing mode (trace architectural paths)
- AutoRoute algorithms for optimal wire paths
- 3D length calculations with elevation changes
- Service loop and waste factor calculations
- Conduit assignment and management

**Acceptance Criteria**:
- [ ] Follow-path mode traces building paths
- [ ] AutoRoute suggests optimal wire paths
- [ ] 3D length calculations include elevation
- [ ] Service loops automatically calculated
- [ ] Conduit fill tracking per conduit run

**Files to Create/Modify**:
- `cad_core/tools/wire_routing.py` (new routing algorithms)
- `cad_core/tools/path_finder.py` (new AutoRoute logic)
- `frontend/tools/routing_tools.py` (new UI tools)

## 🏗️ Phase 2: Professional Workflow (HIGH PRIORITY)

### Issue #5: Report Generation Engine (HIGH PRIORITY)
**Epic**: Professional Fire Alarm Reports
**Scope**: Riser diagrams, cable schedules, BOM, submittal packets
**Estimated Effort**: 4-5 weeks

**Requirements**:
- Automated riser diagram generation from circuit data
- Cable schedules with specifications and lengths
- Comprehensive BOM with devices, wire, labor, costs
- Voltage drop reports per circuit
- Battery sizing reports with recommendations
- Professional submittal packet assembly

**Acceptance Criteria**:
- [ ] Riser diagrams auto-generated from circuits
- [ ] Cable schedules with complete specifications
- [ ] BOM with accurate pricing and quantities
- [ ] Professional PDF output with title blocks
- [ ] Submittal packet assembly automation

**Files to Create/Modify**:
- `backend/reports/` (new module)
  - `riser_generator.py` (diagram generation)
  - `cable_schedule.py` (wire schedules)
  - `bom_generator.py` (bill of materials)
  - `submittal_packet.py` (document assembly)

### Issue #6: Auto-Addressing System (HIGH PRIORITY)
**Epic**: Intelligent Device Address Assignment
**Scope**: Automatic addressing with policy enforcement
**Estimated Effort**: 2-3 weeks

**Requirements**:
- Automatic address assignment when circuits complete
- Duplicate address prevention and validation
- Reserved range enforcement per AHJ policies
- Address locking mechanism before exports
- Custom addressing schemes (sequential, zone-based)

**Acceptance Criteria**:
- [ ] Automatic addressing when loops complete
- [ ] Duplicate prevention with conflict resolution
- [ ] Reserved ranges enforced per policies
- [ ] Address locking prevents accidental changes
- [ ] Multiple addressing scheme support

**Files to Create/Modify**:
- `backend/addressing/` (new module)
  - `auto_addressing.py` (assignment algorithms)
  - `address_policies.py` (policy enforcement)
  - `address_validation.py` (conflict detection)

### Issue #7: Project Setup Wizard (MEDIUM PRIORITY)
**Epic**: Professional Project Creation Workflow
**Scope**: New project wizard with DXF import and templates
**Estimated Effort**: 3-4 weeks

**Requirements**:
- New project wizard with client/address/AHJ setup
- DXF/PDF import with scale calibration
- NFPA 72 compliant project templates
- Architectural layer locking and management
- Project file format with version control

**Acceptance Criteria**:
- [ ] New project wizard guides setup
- [ ] DXF/PDF import with scale calibration
- [ ] Project templates with NFPA guidance
- [ ] Layer management with presets
- [ ] Professional project file format

**Files to Create/Modify**:
- `frontend/dialogs/project_wizard.py` (new)
- `backend/project_manager.py` (new)
- `backend/dxf_import.py` (enhance with scaling)

## 🚀 Phase 3: Advanced Automation (MEDIUM PRIORITY)

### Issue #8: Advanced Circuit Automation (MEDIUM PRIORITY)
**Epic**: FireCAD-Level Circuit Automation
**Scope**: T-tapping, wirepath labeling, advanced routing
**Estimated Effort**: 3-4 weeks

**Requirements**:
- T-tapping optimization for shared wire runs
- Automated wirepath labeling with customizable formats
- Advanced routing with architectural awareness
- Circuit optimization suggestions
- Professional wire management tools

**Files to Create/Modify**:
- `cad_core/automation/` (new module)
- `frontend/tools/automation_tools.py` (new)

### Issue #9: AI Assistant Enhancement (MEDIUM PRIORITY)
**Epic**: Intelligent Design Assistance
**Scope**: Placement suggestions, compliance guidance, optimization
**Estimated Effort**: 4-5 weeks

**Requirements**:
- Device placement suggestions based on coverage
- NFPA/ADA compliance checking with clause references
- Circuit optimization recommendations
- Design quality analysis and suggestions
- Natural language guidance system

### Issue #10: Layout System & Paper Space (MEDIUM PRIORITY)
**Epic**: Professional Drawing Output
**Scope**: Multi-sheet layouts with title blocks
**Estimated Effort**: 3-4 weeks

**Requirements**:
- Model space to layout conversion
- Professional title blocks with attributes
- Multi-sheet drawing coordination
- Print optimization and scaling
- Professional drawing standards compliance

## 📊 Resource Allocation & Timeline

### Phase 1 Timeline (3 months - Critical Features)
```
Month 1: Project Circuits Editor + Live Calculations Engine
Month 2: Enhanced Device Catalog + Advanced Wire Routing
Month 3: Integration, testing, and refinement
```

### Phase 2 Timeline (3-6 months - Professional Workflow)
```
Months 4-5: Report Generation + Auto-Addressing
Month 6: Project Setup Wizard + workflow integration
```

### Phase 3 Timeline (6-12 months - Advanced Features)
```
Months 7-9: Advanced Circuit Automation + AI Assistant
Months 10-12: Layout System + polish for market release
```

## 🎯 Success Metrics & Milestones

### Phase 1 Success Criteria
- [ ] Can complete full fire alarm design with calculations
- [ ] Circuit management comparable to FireCAD baseline
- [ ] Professional electrical validation and reporting

### Phase 2 Success Criteria
- [ ] Can generate professional submittal packages
- [ ] Automated addressing eliminates manual errors
- [ ] Complete project workflow from setup to delivery

### Phase 3 Success Criteria
- [ ] Industry-leading automation and AI assistance
- [ ] Professional drawing output competitive with AutoCAD
- [ ] Market-ready for fire alarm design professionals

## 🔧 Technical Implementation Notes

### Architecture Enhancements Required
1. **Calculation Engine**: New `cad_core/calculations/` module
2. **Circuit Management**: Enhanced circuit data models
3. **Report Generation**: New `backend/reports/` module
4. **Addressing System**: New `backend/addressing/` module
5. **Professional UI**: Additional dock panels and dialogs

### Database Schema Updates
1. **Device Expansion**: Enhanced device table with specifications
2. **Circuit Properties**: Extended circuit data model
3. **Project Templates**: New project template system
4. **Calculation Storage**: Results caching and history

### Integration Points
1. **Qt Scene Integration**: Calculations update graphics in real-time
2. **Command Stack**: All new features support undo/redo
3. **Testing Framework**: Comprehensive test coverage for new features
4. **Documentation**: User guides and API documentation

## 🏆 Competitive Positioning

### Post-Phase 1 Position
- **Core professional functionality** competitive with FireCAD
- **Modern Qt architecture** advantage over AutoCAD dependency
- **Fire alarm specialization** vs generic CAD tools

### Post-Phase 2 Position
- **Complete professional workflow** from project setup to delivery
- **Automated features** reduce design time and errors
- **Professional outputs** meet industry submittal requirements

### Post-Phase 3 Position
- **Industry-leading automation** with AI assistance
- **Professional integration** with mobile and cloud services
- **Market leader** in modern fire alarm CAD software

## 📋 GitHub Issues Creation Plan

### Immediate Issues to Create (Phase 1)
1. **#1 Project Circuits Editor** - Epic with detailed requirements
2. **#2 Live Calculations Engine** - Epic with calculation specifications
3. **#3 Enhanced Device Catalog** - Epic with device library expansion
4. **#4 Advanced Wire Routing** - Epic with routing algorithm requirements

### Labels to Use
- `epic` - Major feature development
- `critical` - Phase 1 essential features
- `high-priority` - Phase 2 important features
- `enhancement` - Phase 3 advanced features
- `professional` - Features required for market readiness
- `calculations` - Electrical calculation features
- `circuits` - Circuit management features
- `ui` - User interface enhancements

### Milestone Structure
- **v0.9.0 - Core Professional** (Phase 1 completion)
- **v1.0.0 - Professional Workflow** (Phase 2 completion)
- **v1.1.0 - Advanced Automation** (Phase 3 completion)

## 🎯 Strategic Conclusion

This roadmap provides a **clear path** from AutoFire's current solid foundation to a professional fire alarm CAD tool competitive with industry standards. The phased approach ensures:

1. **Critical features first** - Live calculations and circuit management
2. **Professional workflow** - Complete design-to-delivery capability
3. **Market differentiation** - Advanced automation and modern architecture

The research and analysis provide confidence that AutoFire has the **engineering foundation** to execute this roadmap successfully and achieve market leadership in fire alarm CAD software.
