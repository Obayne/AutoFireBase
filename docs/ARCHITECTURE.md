# Architecture Overview

**AutoFire** follows a clean, modular architecture that separates UI, business logic, and CAD algorithms into distinct layers. This architecture was fully implemented in the major restructure (commit: `feat: Complete project restructure to modular architecture`).

## 🏗️ Architectural Principles

- **Separation of Concerns**: Clear boundaries between UI, business logic, and algorithms
- **Modularity**: Independent, testable components with well-defined interfaces
- **Maintainability**: Easy to modify, extend, and debug individual components
- **Testability**: Pure functions and mockable dependencies

## 📁 Directory Structure

```
AutoFireBase/
├── frontend/              # UI Layer - PySide6/Qt Interface
│   ├── windows/          # Main application windows
│   │   ├── model_space.py     # CAD design workspace
│   │   ├── paperspace.py      # Print layout workspace
│   │   ├── project_overview.py # Project management hub
│   │   └── scene.py           # Shared graphics scene utilities
│   ├── dialogs/          # Modal dialogs and forms
│   ├── ui/               # Reusable UI components
│   ├── controller.py     # Application controller & coordination
│   └── app.py            # Qt application bootstrap
├── backend/              # Business Logic Layer - Headless Services
│   ├── catalog.py        # Device catalog management
│   ├── logging_config.py # Centralized logging configuration
│   ├── data/             # Data persistence interfaces
│   │   ├── iface.py      # Data interface definitions
│   │   └── sqlite_store.py # SQLite implementations
│   └── dxf_import.py     # File import/export services
├── cad_core/             # CAD Algorithms Layer - Pure Python
│   ├── tools/            # CAD operations and tools
│   │   ├── draw.py       # Drawing primitives
│   │   ├── move_tool.py  # Object manipulation
│   │   ├── measure_tool.py # Measurement tools
│   │   └── ...           # Additional CAD tools
│   └── units.py          # Unit conversion utilities
├── db/                   # Database Layer
│   ├── loader.py         # Database connection & schema management
│   └── schema.py         # Database schema definitions
├── tests/                # Test Suite
│   ├── test_frontend/    # UI component tests
│   ├── test_backend/     # Business logic tests
│   └── test_cad_core/    # Algorithm unit tests
└── main.py               # Clean application entry point
```

## 🔄 Layer Interactions

### Data Flow
```
User Input → Frontend → Backend → CAD Core → Backend → Frontend → UI Update
```

### Communication Patterns
- **Frontend → Backend**: Service method calls for data operations
- **Frontend → CAD Core**: Direct algorithm calls for CAD operations
- **Backend → CAD Core**: Algorithm calls for data processing
- **Controller Signals**: Qt signals for cross-window coordination

## 📦 Component Details

### Frontend Layer (`frontend/`)

**Purpose**: User interface and interaction handling using PySide6/Qt.

**Key Components:**
- **Controller**: `AutoFireController` - Manages application lifecycle, window coordination, and global state
- **Windows**: Independent Qt windows for different workspaces
- **Dialogs**: Modal forms for configuration and data entry
- **UI Components**: Reusable widgets and graphics items

**Responsibilities:**
- User input handling and validation
- UI state management
- Window coordination and layout
- Graphics rendering and interaction

### Backend Layer (`backend/`)

**Purpose**: Business logic, data persistence, and external integrations.

**Key Components:**
- **Catalog Service**: Device catalog management and search
- **Data Services**: CRUD operations for projects and configurations
- **Import/Export**: DXF, PDF, and other file format handling
- **Configuration**: Application settings and preferences

**Responsibilities:**
- Data validation and business rules
- File I/O operations
- External service integrations
- Configuration management

### CAD Core Layer (`cad_core/`)

**Purpose**: Pure Python CAD algorithms and geometric operations.

**Key Components:**
- **Tools**: Individual CAD operations (draw, modify, measure)
- **Geometry**: Mathematical operations and transformations
- **Units**: Coordinate system and unit conversions
- **Snapping**: Object snap and alignment algorithms

**Responsibilities:**
- Geometric calculations
- CAD tool implementations
- Unit conversions
- Algorithm optimization

## 🔌 Interface Definitions

### Controller Signals
```python
# Cross-window communication
model_space_changed = Signal(dict)    # Model space updates
paperspace_changed = Signal(dict)     # Paperspace updates
project_changed = Signal(dict)        # Project state changes
```

### Service Interfaces
```python
# Backend services
class CatalogService:
    def load_catalog() -> list[dict]
    def search_devices(query: str) -> list[dict]

class DataService:
    def save_project(project: dict) -> bool
    def load_project(id: int) -> dict
```

### Tool Interfaces
```python
# CAD tools
class CadTool(ABC):
    def start(self, **kwargs) -> None
    def update(self, **kwargs) -> None
    def cancel(self) -> None
    def commit(self) -> None
```

## 🧪 Testing Strategy

### Unit Tests (`tests/`)
- **CAD Core**: Pure algorithm testing with mock data
- **Backend**: Service testing with in-memory databases
- **Frontend**: Component testing with Qt mocking

### Integration Tests
- End-to-end workflows across layers
- Database integration testing
- File import/export validation

### Test Coverage Goals
- CAD Core: >90% coverage
- Backend Services: >80% coverage
- Frontend Components: >70% coverage

## 🚀 Application Lifecycle

1. **Bootstrap** (`main.py` → `frontend/app.py`)
   - Qt application initialization
   - Logging configuration
   - Controller instantiation

2. **Controller Setup** (`frontend/controller.py`)
   - Preferences loading
   - Device catalog initialization
   - Window creation and layout

3. **Window Initialization**
   - Scene and view setup
   - Tool registration
   - Signal connections

4. **Runtime Operation**
   - Event-driven UI updates
   - Cross-window coordination
   - Data persistence

## 🔧 Development Guidelines

### Adding New Features
1. **Identify Layer**: Determine which layer owns the functionality
2. **Define Interface**: Specify clear contracts between components
3. **Implement Core**: Start with CAD Core or Backend logic
4. **Add UI**: Build frontend components last
5. **Add Tests**: Ensure test coverage for new code

### Code Organization
- **One Responsibility**: Each module/class has a single purpose
- **Dependency Injection**: Pass dependencies explicitly
- **Interface Segregation**: Small, focused interfaces
- **Configuration**: Externalize settings and preferences

### Performance Considerations
- **CAD Core**: Optimize geometric algorithms for real-time interaction
- **Backend**: Cache frequently accessed data
- **Frontend**: Virtualize large datasets and use efficient rendering

## 📋 Migration Notes

This architecture was fully implemented in the major restructure, eliminating the legacy monolithic `app/` structure. Key changes:

- ✅ **Completed**: Migration from `app/` to modular structure
- ✅ **Completed**: Service layer separation
- ✅ **Completed**: Clean entry point implementation
- ✅ **Completed**: Cross-window communication via signals

## 📚 Related Documentation

- `AGENTS.md`: Development principles and team guidelines
- `README.md`: Quick start and development setup
- `docs/CONTRIBUTING.md`: Detailed contribution guidelines
- `CHANGELOG.md`: Version history and feature tracking
