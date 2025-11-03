# Professional CAD Standards Research - Model Space, Paper Space, and Workflow

## Core CAD Concepts from Research

### Model Space vs Paper Space (AutoCAD Standard)

#### Model Space

- **Purpose**: Infinite precision design environment for real-world geometry
- **Coordinate System**: Real-world units (feet, inches, millimeters)
- **Scale**: 1:1 actual size - draw objects at their real dimensions
- **Precision**: Double-precision floating point for architectural accuracy
- **Viewport**: Single viewport showing the entire design space
- **Usage**: All design work, geometry creation, modification

#### Paper Space (Layout Tabs)

- **Purpose**: Print/publication environment with multiple scaled views
- **Coordinate System**: Paper units (inches for print pages)
- **Scale**: Multiple viewports with different scales (1/4"=1', 1/8"=1', etc.)
- **Viewports**: Multiple windows into model space at different scales
- **Annotations**: Dimensions, text, title blocks at paper scale
- **Usage**: Creating construction documents, plot layouts

### LibreCAD Features Analysis

#### File Format Support

- **Read**: DXF (all versions), DWG (via libdxfrw), SVG, PDF import
- **Write**: DXF (2007, 2004, 2000, R14, R12), SVG, PDF export
- **Images**: BMP, PNG, JPEG, TIFF, WebP import as bitmap underlays
- **Fonts**: LFF (LibreCAD Font Format), CXF, TTF conversion

#### Drawing Tools

- **Primitives**: Line, Rectangle, Circle, Ellipse, Arc, Polyline, Spline
- **Text**: Single-line text, dimensions with styles
- **Modify**: Move, Copy, Rotate, Scale, Mirror, Trim, Extend, Fillet, Chamfer
- **Advanced**: Offset, Array, Hatch patterns, Layers, Blocks

#### Coordinate System

- **Units**: Real-world units (mm, inches, feet) with conversion
- **Grid**: Configurable grid spacing in drawing units
- **Snap**: Grid snap, object snap (endpoint, midpoint, center, etc.)
- **Input**: Coordinate entry, relative/absolute, polar coordinates

#### Professional Features

- **Layers**: Color, line type, line weight per layer
- **Blocks**: Reusable symbols and components
- **Dimensions**: Automatic dimensioning with customizable styles
- **Printing**: Multiple page sizes, scale factors, plot styles

### Fire Alarm CAD Requirements

#### Critical Missing Features in Our System

1. **Real Units System**
   - Currently: Everything in pixels (px_per_ft is primitive)
   - Need: True feet/inches/millimeters with proper conversion
   - Impact: Can't work with real-world dimensions

2. **Precision Coordinate Input**
   - Currently: Mouse-only placement
   - Need: Type exact coordinates (10.5,8.25) and distances
   - Impact: Impossible to create accurate technical drawings

3. **Model/Paper Space**
   - Currently: Mixed drawing and layout in one view
   - Need: Separate design space and print layouts
   - Impact: Can't create professional construction documents

4. **PDF Import**
   - Currently: Basic DXF import only
   - Need: Load architectural PDF drawings as underlays
   - Impact: Can't overlay fire alarm on architect's drawings

5. **DWG/DXF Export**
   - Currently: PNG/PDF export only
   - Need: Save as industry-standard CAD formats
   - Impact: Can't share with engineers, architects, AHJs

6. **Block System**
   - Currently: Basic device symbols
   - Need: Intelligent, reusable fire alarm device library
   - Impact: Inconsistent symbols, no standards compliance

7. **Dimension System**
   - Currently: Basic temporary dimensions
   - Need: Professional dimensioning with styles
   - Impact: Can't create code-compliant technical drawings

8. **Layer Management**
   - Currently: Basic grouping
   - Need: Industry-standard layer names and properties
   - Impact: Can't follow CAD standards for fire alarm

## Professional Fire Alarm CAD Workflow

### Traditional Workflow (Target)

1. **Import Architectural**: Load PDF/DWG architectural plans
2. **Set Scale**: Establish drawing scale (1/4"=1'-0")
3. **Create Layers**: Fire alarm devices, circuits, annotation
4. **Place Devices**: Use standard fire alarm symbols
5. **Route Circuits**: SLC/NAC wiring with proper representation
6. **Add Dimensions**: Code-required coverage distances
7. **Create Layouts**: Multiple sheets at different scales
8. **Export/Print**: DWG for engineers, PDF for permits

### Current Limitations

- No PDF import capabilities
- No real units or scaling
- No professional layer system
- Limited symbol library
- No circuit representation
- Basic dimensioning only
- No layout management

## Architecture Requirements

### Coordinate System Engine

```python
class CoordinateSystem:
    def __init__(self, units='feet', precision=0.001):
        self.units = units  # 'feet', 'inches', 'millimeters'
        self.precision = precision
        self.origin = Point(0, 0)

    def to_display_units(self, real_point):
        # Convert real-world to display pixels

    def to_real_units(self, display_point):
        # Convert display pixels to real-world

    def snap_to_grid(self, point, grid_size):
        # Snap to grid in real units
```

### Model/Paper Space System

```python
class ModelSpace:
    def __init__(self):
        self.coordinate_system = CoordinateSystem('feet')
        self.entities = []  # All drawing entities
        self.infinite_extent = True

class PaperSpace:
    def __init__(self, page_size):
        self.coordinate_system = CoordinateSystem('inches')
        self.page_size = page_size
        self.viewports = []  # Windows into model space
        self.annotations = []  # Paper-space text/dims

class Viewport:
    def __init__(self, bounds, model_area, scale):
        self.bounds = bounds  # Paper space rectangle
        self.model_area = model_area  # Model space area to show
        self.scale = scale  # 1/4"=1'-0" etc.
```

### File Format Support

```python
class FileManager:
    def import_pdf(self, path, scale=None):
        # Convert PDF to vector underlay

    def import_dwg(self, path):
        # Read DWG using ezdxf or similar

    def export_dwg(self, path, version='2018'):
        # Write DWG format

    def export_dxf(self, path, version='R2018'):
        # Write DXF format
```

### Block/Symbol System

```python
class Block:
    def __init__(self, name, entities, insertion_point):
        self.name = name
        self.entities = entities  # Component geometry
        self.insertion_point = insertion_point
        self.attributes = {}  # Custom properties

class BlockLibrary:
    def __init__(self):
        self.fire_alarm_devices = {}
        self.electrical_symbols = {}
        self.load_standard_library()
```

## Implementation Priority

### Phase 1: Foundation (Immediate)

1. Real units coordinate system
2. Precision input system
3. PDF import capability
4. Model/paper space separation

### Phase 2: Professional Tools

1. DWG/DXF export
2. Block library system
3. Professional dimensioning
4. Layer management

### Phase 3: Advanced Features

1. Advanced file format support
2. Command line interface
3. Customization system
4. Integration features

This research establishes the foundation for transforming AutoFire into a professional fire alarm CAD system that can compete with commercial solutions while maintaining the specialized focus on fire protection systems.
