# AutoFire Development Tasklist

## Overview
This tasklist tracks remaining development work for AutoFire CAD application. Last updated: 2025-09-28

## âœ… COMPLETED
- [x] **Drawing Tools Fix** - Line, Circle, Rectangle, Polyline, Arc tools now work as overlays on DXF underlays
- [x] **Wire Tool** - Implemented using DrawController WIRE mode for drawing electrical connections
- [x] **Basic Modify Tools** - Move, Copy, Rotate, Scale tools are fully functional
- [x] **Database Initialization** - Added database initialization to AppController for NFPA coverage lookups
- [x] **Multiple Window Architecture** - Fixed AppController to show separate ModelSpaceWindow/PaperspaceWindow instances
- [x] **Settings Dialog** - Robust settings dialog with theme, grid, snap, and pixels-per-foot controls
- [x] **DXF Import** - Layer-aware rendering and auto-fit functionality
- [x] **PNG/PDF Export** - Both implemented with page frame support
- [x] **PDF Import** - PDF underlay import using QtPdf module
- [x] **Coverage Overlays** - Detector circles, strobe patterns, speaker coverage
- [x] **Device Placement** - Enhanced visibility with white borders/backgrounds
- [x] **Layer Management** - Proper Z-value ordering (underlay=-50, sketch=40, devices=100)
- [x] **Trim Tool** - Implemented in `app/tools/trim_tool.py`
- [x] **Extend Tool** - Implemented in `app/tools/extend_tool.py`
- [x] **Move Tool** - Implemented in `app/tools/move_tool.py`
- [x] **Rotate Tool** - Implemented in `app/tools/rotate_tool.py`
- [x] **Scale Tool** - Implemented in `app/tools/scale_tool.py`
- [x] **Mirror Tool** - Implemented in `app/tools/mirror_tool.py`
- [x] **Fillet Tool** - Implemented in `app/tools/fillet_tool.py`
- [x] **Chamfer Tool** - Implemented in `app/tools/chamfer_tool.py`
- [x] **Text Tool** - Implemented in `app/tools/text_tool.py`
- [x] **MText Tool** - Implemented in `app/tools/mtext_tool.py`
- [x] **Freehand Tool** - Implemented in `app/tools/freehand.py`
- [x] **Leader Tool** - Implemented in `app/tools/leader.py`
- [x] **Cloud Tool** - Implemented in `app/tools/revision_cloud.py`
- [x] **Measure Tool** - Implemented in `app/tools/measure_tool.py`
- [x] **Dimension Tool** - Implemented in `app/tools/dimension.py`

## ðŸ”„ IN PROGRESS

## ðŸ“‹ TODO - High Priority

### Core CAD Functionality
- [x] **Wire Tool** (`start_wiring`) - Implemented using DrawController WIRE mode for drawing electrical connections
- [x] **Trim Tool** (`start_trim`) - Implemented in `app/tools/trim_tool.py`
- [x] **Extend Tool** (`start_extend`) - Implemented in `app/tools/extend_tool.py`
- [x] **Move Tool** (`start_move`) - Implemented in `app/tools/move_tool.py`
- [x] **Copy Tool** (`start_copy`) - Implemented in `app/tools/move_tool.py` (same tool)
- [x] **Rotate Tool** (`start_rotate`) - Implemented in `app/tools/rotate_tool.py`
- [x] **Scale Tool** (`start_scale`) - Implemented in `app/tools/scale_tool.py`
- [x] **Mirror Tool** (`start_mirror`) - Implemented in `app/tools/mirror_tool.py`
- [x] **Fillet Tool** (`start_fillet`) - Implemented in `app/tools/fillet_tool.py`
- [x] **Chamfer Tool** (`start_chamfer`) - Implemented in `app/tools/chamfer_tool.py`
- [x] **Offset Tool** (`offset_selected_dialog`) - Offset selected geometry

### Annotation & Documentation
- [x] **Text Tool** (`start_text`) - Implemented in `app/tools/text_tool.py`
- [x] **MText Tool** (`start_mtext`) - Implemented in `app/tools/mtext_tool.py`
- [x] **Freehand Tool** (`start_freehand`) - Implemented in `app/tools/freehand.py`
- [x] **Leader Tool** (`start_leader`) - Implemented in `app/tools/leader.py`
- [x] **Cloud Tool** (`start_cloud`) - Implemented in `app/tools/revision_cloud.py`

- [ ] **Dimensioning** (All show "not yet implemented")
  - [x] **Measure Tool** (`start_measure`) - Distance measurements
  - [x] **Dimension Tool** (`start_dimension`) - Formal dimensions

### Import/Export

### Reports & Documentation
- [ ] **Reports System** (All show "not yet implemented")
  - [ ] **Calculations Report** (`show_calculations`)
  - [ ] **Bill of Materials** (`show_bom_report`)
  - [ ] **Device Schedule** (`show_device_schedule_report`)
  - [ ] **Riser Diagram** (`generate_riser_diagram`)
  - [ ] **Circuit Properties** (`show_circuit_properties`)

### UI Dialogs & Panels
- [x] **Settings Dialog** (`open_settings`) - Robust settings dialog with theme, grid, snap, and pixels-per-foot controls
- [x] **Layer Manager** (`open_layer_manager`) - Layer visibility and management
- [x] **Grid Style Dialog** (`grid_style_dialog`) - Grid appearance customization

### Advanced Features
- [ ] **FACP Panel Configuration** (`place_facp_panel`)
  - Panel wizard for fire alarm control panels
  - Circuit configuration
  - Device assignment

- [ ] **Token Placement** (`place_token`)
  - Custom symbol placement
  - Token library management

- [ ] **Job Information** (`show_job_info_dialog`)
  - Project metadata management
  - Client information
  - Job specifications

- [ ] **Symbol Legend** (`place_symbol_legend`)
  - Automatic legend generation
  - Symbol documentation

### Paperspace & Layout
- [ ] **Page Frame** (`add_page_frame`, `remove_page_frame`)
  - Standard page borders
  - Title block integration

- [ ] **Title Block** (`add_or_update_title_block`)
  - Standard title block templates
  - Custom title block creation

- [ ] **Page Setup** (`page_setup_dialog`)
  - Paper size selection
  - Orientation settings
  - Margins and scaling

- [ ] **Viewport System** (`add_viewport`)
  - Model space viewports in paperspace
  - Scale management
  - Viewport properties

### System Integration
- [ ] **Wire Spool** (`open_wire_spool`)
  - Wire inventory management
  - Spool tracking
  - Usage reporting

- [ ] **System Builder** (`open_system_builder`)
  - Automated system configuration
  - NFPA compliance checking
  - Design validation

- [ ] **Device Manager** (`open_device_manager`)
  - Device library management
  - Custom device creation
  - Specification editing

- [ ] **Parts Warehouse** (`open_parts_warehouse`)
  - Component inventory
  - Supplier integration
  - Cost tracking

## ðŸ§ª Testing & Quality Assurance
- [ ] **Unit Tests**
  - [ ] Wire tool tests
  - [ ] Modify tools tests
  - [ ] Annotation tools tests
  - [ ] Import/export tests
  - [ ] Reports tests

- [ ] **Integration Tests**
  - [ ] End-to-end workflow testing
  - [ ] Database integration testing
  - [ ] Multi-window architecture testing

- [ ] **Performance Testing**
  - [ ] Large DXF file handling
  - [ ] Complex device placement scenarios
  - [ ] Memory usage optimization

## ðŸ“š Documentation
- [ ] **User Guide** (`show_user_guide`)
- [ ] **Keyboard Shortcuts** (`show_shortcuts`) — docs/SHORTCUTS.md added
- [ ] **API Documentation**
- [ ] **Developer Guide**

## ðŸ”§ Infrastructure
- [ ] **Build System**
  - [ ] PyInstaller configuration
  - [ ] Cross-platform builds
  - [ ] Automated release process

- [ ] **CI/CD Pipeline**
  - [ ] Automated testing
  - [ ] Code quality checks
  - [ ] Release automation

## ðŸŽ¯ Future Enhancements
- [ ] **Summary Window** - Project management with progress tracking
- [ ] **AI Assistance** - Design suggestions and validation
- [ ] **Cloud Integration** - Project sharing and collaboration
- [ ] **Mobile Companion App** - Field verification and updates
- [ ] **Advanced Analysis** - Coverage optimization algorithms

## ðŸ“Š Priority Matrix

### Critical (Block Core Workflows)
- Wire Tool
- Basic Modify Tools (Move, Copy, Rotate)
- PDF Import/Export
- Settings Dialog

### High (Essential CAD Features)
- Text Tools
- Dimensioning
- Reports System
- Layer Manager

### Medium (Productivity Features)
- Advanced Modify Tools
- Annotation Tools
- FACP Panel Configuration
- Paperspace Features

### Low (Nice-to-Have)
- AI Features
- Cloud Integration
- Mobile App
- Advanced Analysis

---

*This tasklist is maintained in TASKLIST.md and should be updated as work progresses.*
