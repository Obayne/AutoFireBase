# AutoFire CAD Architecture Design - Professional Fire Alarm CAD System

## Overview

This document outlines the architectural design for transforming AutoFire into a professional fire alarm CAD system that competes with LibreCAD and approaches AutoCAD functionality while specializing in fire protection systems.

## Architecture Principles

### 1. Separation of Concerns

- **Geometry Engine**: Pure mathematics, no Qt dependencies
- **Coordinate System**: Real-world units with precision control
- **Model/Paper Space**: Separate design and layout environments
- **File Formats**: Abstracted I/O with pluggable format support
- **UI Layer**: Qt-based presentation with professional UX

### 2. Professional CAD Standards

- **Real Units**: Work in feet, inches, millimeters (not pixels)
- **Double Precision**: IEEE 754 double precision for accuracy
- **Industry Standards**: Follow fire alarm design conventions
- **Interoperability**: DWG/DXF/PDF import/export compatibility

### 3. Fire Alarm Specialization

- **Device Libraries**: NFPA-compliant symbols and specifications
- **Circuit Design**: SLC/NAC routing with electrical calculations
- **Code Compliance**: Built-in coverage and spacing validation
- **Professional Output**: Construction documents and permits

## Core Architecture Components

### 1. Geometry Engine (`cad_core/`)

```
cad_core/
├── __init__.py
├── geometry/
│   ├── __init__.py
│   ├── point.py          # 2D point with double precision
│   ├── vector.py         # 2D vector mathematics
│   ├── line.py          # Line segment and infinite line
│   ├── arc.py           # Circular arcs and circles
│   ├── polyline.py      # Multi-segment paths
│   ├── spline.py        # Cubic splines and curves
│   └── bounds.py        # Bounding boxes and regions
├── units/
│   ├── __init__.py
│   ├── system.py        # Unit conversion system
│   ├── precision.py     # Floating point precision control
│   └── formatting.py   # Display formatting (5'-6 3/4")
├── transforms/
│   ├── __init__.py
│   ├── matrix2d.py      # 2D transformation matrices
│   ├── viewport.py      # Model-to-paper space mapping
│   └── scaling.py       # Scale factor management
└── operations/
    ├── __init__.py
    ├── intersection.py  # Geometric intersections
    ├── offset.py        # Parallel offset operations
    ├── fillet.py        # Filleting and rounding
    ├── trim.py          # Trimming and extending
    └── measure.py       # Distance and area calculations
```

### 2. Coordinate System (`cad_core/coordinate/`)

```python
class CoordinateSystem:
    """Real-world coordinate system with unit support."""

    def __init__(self, units: Units = Units.FEET, precision: float = 0.001):
        self.units = units
        self.precision = precision
        self.origin = Point(0.0, 0.0)

    def snap_to_grid(self, point: Point, grid_size: float) -> Point:
        """Snap point to grid in real units."""

    def format_coordinate(self, point: Point) -> str:
        """Format for display: (10'-6", 8'-3 1/2")"""

    def parse_coordinate(self, text: str) -> Point:
        """Parse user input: 10.5,8.25 or 10'-6",8'-3.5\""""

class Units(Enum):
    FEET = "feet"
    INCHES = "inches"
    MILLIMETERS = "mm"
    METERS = "m"

    def to_base_factor(self) -> float:
        """Conversion factor to base units (feet)."""
        return {
            Units.FEET: 1.0,
            Units.INCHES: 1.0/12.0,
            Units.MILLIMETERS: 1.0/304.8,
            Units.METERS: 1.0/0.3048
        }[self]
```

### 3. Model/Paper Space System (`cad_core/spaces/`)

```python
class ModelSpace:
    """Infinite precision design environment."""

    def __init__(self, coordinate_system: CoordinateSystem):
        self.coord_system = coordinate_system
        self.entities: List[Entity] = []
        self.layers: Dict[str, Layer] = {}
        self.blocks: Dict[str, Block] = {}

    def add_entity(self, entity: Entity, layer: str = "0"):
        """Add geometry to model space."""

    def get_bounds(self) -> Bounds:
        """Calculate bounding box of all entities."""

class PaperSpace:
    """Print layout environment with viewports."""

    def __init__(self, page_size: PageSize):
        self.page_size = page_size
        self.coord_system = CoordinateSystem(Units.INCHES)
        self.viewports: List[Viewport] = []
        self.annotations: List[Annotation] = []

class Viewport:
    """Window into model space at specific scale."""

    def __init__(self, bounds: Rectangle, model_bounds: Rectangle, scale: Scale):
        self.paper_bounds = bounds      # Location on paper
        self.model_bounds = model_bounds # Area of model to show
        self.scale = scale              # 1/4"=1'-0" etc.

    def model_to_paper(self, point: Point) -> Point:
        """Transform model space point to paper space."""

    def paper_to_model(self, point: Point) -> Point:
        """Transform paper space point to model space."""
```

### 4. Entity System (`cad_core/entities/`)

```python
class Entity(ABC):
    """Base class for all drawable entities."""

    def __init__(self, id: str = None):
        self.id = id or uuid.uuid4().hex
        self.layer = "0"
        self.color = Color.BY_LAYER
        self.linetype = Linetype.BY_LAYER

    @abstractmethod
    def get_bounds(self) -> Bounds:
        """Get entity bounding box."""

    @abstractmethod
    def transform(self, matrix: Matrix2D) -> 'Entity':
        """Apply transformation matrix."""

class Line(Entity):
    def __init__(self, start: Point, end: Point):
        super().__init__()
        self.start = start
        self.end = end

class Circle(Entity):
    def __init__(self, center: Point, radius: float):
        super().__init__()
        self.center = center
        self.radius = radius

class Block(Entity):
    """Reusable symbol with attributes."""

    def __init__(self, name: str, entities: List[Entity], insertion_point: Point):
        super().__init__()
        self.name = name
        self.entities = entities
        self.insertion_point = insertion_point
        self.attributes: Dict[str, str] = {}
```

### 5. Fire Alarm Specific Components (`fire_alarm/`)

```
fire_alarm/
├── __init__.py
├── devices/
│   ├── __init__.py
│   ├── library.py       # NFPA device symbol library
│   ├── detectors.py     # Smoke, heat, beam detectors
│   ├── notification.py  # Horns, strobes, speakers
│   ├── control.py       # Panels, modules, interfaces
│   └── manual.py        # Pull stations, keys switches
├── circuits/
│   ├── __init__.py
│   ├── slc.py          # Signaling Line Circuits
│   ├── nac.py          # Notification Appliance Circuits
│   ├── routing.py      # Wire path optimization
│   └── calculations.py # Voltage drop, current draw
├── standards/
│   ├── __init__.py
│   ├── nfpa72.py       # NFPA 72 requirements
│   ├── coverage.py     # Device spacing validation
│   └── zones.py        # Fire alarm zones and areas
└── reports/
    ├── __init__.py
    ├── schedules.py     # Device schedules
    ├── calculations.py  # Circuit calculations
    └── compliance.py    # Code compliance reports
```

### 6. File Format Support (`cad_core/formats/`)

```python
class FormatManager:
    """Pluggable file format support."""

    def __init__(self):
        self.importers: Dict[str, Callable] = {}
        self.exporters: Dict[str, Callable] = {}
        self.register_builtin_formats()

    def import_file(self, path: Path, format: str = None) -> ModelSpace:
        """Import CAD file to model space."""

    def export_file(self, model: ModelSpace, path: Path, format: str):
        """Export model space to CAD file."""

class DWGImporter:
    """Import AutoCAD DWG files."""

    def import_dwg(self, path: Path) -> ModelSpace:
        # Use ezdxf or similar library

class PDFImporter:
    """Import PDF as vector underlay."""

    def import_pdf(self, path: Path, page: int = 1) -> List[Entity]:
        # Use pymupdf or similar library
```

### 7. User Interface Architecture (`frontend/`)

```
frontend/
├── workspaces/
│   ├── __init__.py
│   ├── model_space.py   # Model space viewport
│   ├── paper_space.py   # Paper space layout
│   └── dual_view.py     # Split model/paper view
├── input/
│   ├── __init__.py
│   ├── coordinate.py    # Precision coordinate input
│   ├── command.py       # Command line interface
│   └── snap.py          # Object snap system
├── tools/
│   ├── __init__.py
│   ├── draw/           # Drawing tool implementations
│   ├── modify/         # Modification tools
│   ├── measure/        # Measurement tools
│   └── fire_alarm/     # Fire alarm specific tools
└── dialogs/
    ├── __init__.py
    ├── preferences.py   # System preferences
    ├── layers.py       # Layer management
    └── blocks.py       # Block library management
```

## Implementation Phases

### Phase 1: Foundation (4-6 weeks)

1. **Geometry Engine**: Pure Python geometry with double precision
2. **Coordinate System**: Real units with conversion and formatting
3. **Entity System**: Base entity classes with transforms
4. **Basic File I/O**: DXF import/export, PDF import

**Deliverables:**

- Working coordinate system with feet/inches
- Basic geometry operations (line, circle, arc)
- DXF file import/export
- PDF import as vector underlay

### Phase 2: Model/Paper Space (3-4 weeks)

1. **Model Space**: Infinite precision design environment
2. **Paper Space**: Print layout with viewports
3. **Viewport System**: Scale management and transforms
4. **Drawing Tools**: Professional drawing tool integration

**Deliverables:**

- Separate model and paper space workspaces
- Viewport scaling system
- Professional drawing tools with real units
- Multi-sheet layout capability

### Phase 3: Fire Alarm Specialization (4-5 weeks)

1. **Device Library**: NFPA-compliant fire alarm symbols
2. **Circuit Tools**: SLC/NAC routing and calculations
3. **Code Compliance**: Coverage validation and reporting
4. **Professional Output**: Construction document generation

**Deliverables:**

- Complete fire alarm device library
- Circuit design and calculation tools
- Code compliance validation
- Professional drawing export

### Phase 4: Advanced Features (3-4 weeks)

1. **Command Line**: AutoCAD-style command interface
2. **Advanced File Support**: Full DWG compatibility
3. **Customization**: User-defined blocks and standards
4. **Integration**: External system integration

**Deliverables:**

- Command line interface
- Full DWG/DXF compatibility
- User customization system
- External integration APIs

## Success Metrics

### Technical Metrics

- **Precision**: Sub-millimeter accuracy in drawings
- **Performance**: <100ms response for common operations
- **Compatibility**: 95%+ DXF/DWG compatibility
- **Standards**: 100% NFPA 72 symbol compliance

### User Experience Metrics

- **Workflow Efficiency**: 50%+ faster than current tools
- **Learning Curve**: <2 hours for CAD-experienced users
- **Professional Output**: Permit-ready construction documents
- **Industry Adoption**: Positive feedback from fire alarm professionals

## Risk Mitigation

### Technical Risks

- **Precision Issues**: Use IEEE 754 double precision consistently
- **Performance**: Profile and optimize critical geometry operations
- **Compatibility**: Test against industry-standard DWG/DXF files
- **Complexity**: Modular architecture allows incremental development

### User Adoption Risks

- **Learning Curve**: Maintain familiar CAD paradigms
- **Feature Gaps**: Focus on fire alarm workflow essentials first
- **Quality**: Extensive testing with real fire alarm projects
- **Support**: Comprehensive documentation and examples

This architecture provides a roadmap for creating a professional fire alarm CAD system that competes with commercial solutions while maintaining the specialized focus and workflow efficiency that fire alarm designers need.
