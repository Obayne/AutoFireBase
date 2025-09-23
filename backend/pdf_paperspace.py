"""
PDF paperspace system for fire alarm CAD drawings.
Handles PDF generation with proper scaling, sizing, and layout
similar to AutoCAD paperspace functionality.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import math
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4, A3, A2, A1, A0, legal
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import black, red, blue, green
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from PySide6.QtCore import QRectF, QPointF
from PySide6.QtGui import QPainter, QPen, QBrush, QColor


class PaperSize(Enum):
    """Standard paper sizes."""
    LETTER = "Letter"
    LEGAL = "Legal"
    TABLOID = "Tabloid"
    A4 = "A4"
    A3 = "A3"
    A2 = "A2"
    A1 = "A1"
    A0 = "A0"


class DrawingScale(Enum):
    """Common architectural scales."""
    SCALE_1_8 = "1/8\" = 1'"      # 1:96
    SCALE_1_4 = "1/4\" = 1'"      # 1:48
    SCALE_3_8 = "3/8\" = 1'"      # 1:32
    SCALE_1_2 = "1/2\" = 1'"      # 1:24
    SCALE_3_4 = "3/4\" = 1'"      # 1:16
    SCALE_1_1 = "1\" = 1'"        # 1:12
    SCALE_1_2_INCH = "1-1/2\" = 1'"  # 1:8
    SCALE_3_INCH = "3\" = 1'"     # 1:4
    SCALE_FULL = "Full Size"      # 1:1


@dataclass
class Viewport:
    """Represents a viewport in paperspace."""
    name: str
    paper_rect: QRectF  # Rectangle on paper (in paper units)
    model_rect: QRectF  # Rectangle in model space
    scale_factor: float
    layer_visibility: Dict[str, bool]
    title: str = ""
    frozen_layers: List[str] | None = None
    
    def __post_init__(self):
        if self.frozen_layers is None:
            self.frozen_layers = []


@dataclass
class TitleBlock:
    """Title block information for drawings."""
    project_name: str = ""
    drawing_title: str = ""
    drawing_number: str = ""
    sheet_number: str = ""
    revision: str = "0"
    drawn_by: str = ""
    checked_by: str = ""
    date: str = ""
    scale: str = ""
    client: str = ""
    
    def __post_init__(self):
        if not self.date:
            self.date = datetime.now().strftime("%m/%d/%Y")


@dataclass
class PaperSpaceLayout:
    """Complete paperspace layout configuration."""
    name: str
    paper_size: PaperSize
    orientation: str  # "Portrait" or "Landscape"
    margin_inches: Tuple[float, float, float, float]  # left, top, right, bottom
    viewports: List[Viewport]
    title_block: TitleBlock
    border: bool = True
    grid: bool = False
    
    def get_paper_dimensions(self) -> Tuple[float, float]:
        """Get paper dimensions in points."""
        size_map = {
            PaperSize.LETTER: letter,
            PaperSize.LEGAL: legal,
            PaperSize.A4: A4,
            PaperSize.A3: A3,
            PaperSize.A2: A2,
            PaperSize.A1: A1,
            PaperSize.A0: A0
        }
        
        width, height = size_map.get(self.paper_size, letter)
        
        if self.orientation == "Landscape":
            return height, width
        return width, height


class PDFGenerator:
    """Generates PDF drawings from CAD data."""
    
    def __init__(self):
        self.scale_factors = {
            DrawingScale.SCALE_1_8: 96.0,
            DrawingScale.SCALE_1_4: 48.0,
            DrawingScale.SCALE_3_8: 32.0,
            DrawingScale.SCALE_1_2: 24.0,
            DrawingScale.SCALE_3_4: 16.0,
            DrawingScale.SCALE_1_1: 12.0,
            DrawingScale.SCALE_1_2_INCH: 8.0,
            DrawingScale.SCALE_3_INCH: 4.0,
            DrawingScale.SCALE_FULL: 1.0
        }
        
    def create_pdf(self, layout: PaperSpaceLayout, filename: str, 
                   cad_data: Dict[str, Any] = None):
        """Create PDF from paperspace layout."""
        paper_width, paper_height = layout.get_paper_dimensions()
        
        # Create PDF canvas
        c = canvas.Canvas(filename, pagesize=(paper_width, paper_height))
        
        # Draw border if enabled
        if layout.border:
            self._draw_border(c, layout, paper_width, paper_height)
            
        # Draw viewports
        for viewport in layout.viewports:
            self._draw_viewport(c, viewport, cad_data)
            
        # Draw title block
        self._draw_title_block(c, layout.title_block, paper_width, paper_height)
        
        # Add metadata
        c.setTitle(layout.title_block.drawing_title)
        c.setAuthor(layout.title_block.drawn_by)
        c.setSubject(f"Fire Alarm Plan - {layout.title_block.project_name}")
        
        c.save()
        
    def _draw_border(self, canvas_obj, layout: PaperSpaceLayout, 
                    paper_width: float, paper_height: float):
        """Draw page border."""
        margin_left, margin_top, margin_right, margin_bottom = layout.margin_inches
        
        # Convert to points
        left = margin_left * inch
        bottom = margin_bottom * inch
        right = paper_width - margin_right * inch
        top = paper_height - margin_top * inch
        
        # Draw border rectangle
        canvas_obj.setStrokeColor(black)
        canvas_obj.setLineWidth(2)
        canvas_obj.rect(left, bottom, right - left, top - bottom)
        
    def _draw_viewport(self, canvas_obj, viewport: Viewport, cad_data: Dict[str, Any]):
        """Draw a viewport with its contents."""
        # Set clipping region
        canvas_obj.saveState()
        
        # Create clipping path for viewport
        path = canvas_obj.beginPath()
        path.rect(viewport.paper_rect.x(), viewport.paper_rect.y(),
                 viewport.paper_rect.width(), viewport.paper_rect.height())
        canvas_obj.clipPath(path, stroke=0)
        
        # Calculate transformation from model to paper
        model_width = viewport.model_rect.width()
        model_height = viewport.model_rect.height()
        paper_width = viewport.paper_rect.width()
        paper_height = viewport.paper_rect.height()
        
        # Scale factor to fit model in viewport
        scale_x = paper_width / model_width if model_width > 0 else 1.0
        scale_y = paper_height / model_height if model_height > 0 else 1.0
        scale = min(scale_x, scale_y) * viewport.scale_factor
        
        # Translation to center model in viewport
        center_x = viewport.paper_rect.x() + viewport.paper_rect.width() / 2
        center_y = viewport.paper_rect.y() + viewport.paper_rect.height() / 2
        model_center_x = viewport.model_rect.x() + viewport.model_rect.width() / 2
        model_center_y = viewport.model_rect.y() + viewport.model_rect.height() / 2
        
        # Apply transformation
        canvas_obj.translate(center_x, center_y)
        canvas_obj.scale(scale, scale)
        canvas_obj.translate(-model_center_x, -model_center_y)
        
        # Draw CAD content
        if cad_data:
            self._draw_cad_content(canvas_obj, cad_data, viewport.layer_visibility)
            
        # Draw viewport border
        canvas_obj.restoreState()
        canvas_obj.setStrokeColor(black)
        canvas_obj.setLineWidth(1)
        canvas_obj.rect(viewport.paper_rect.x(), viewport.paper_rect.y(),
                       viewport.paper_rect.width(), viewport.paper_rect.height())
                       
        # Add viewport title
        if viewport.title:
            canvas_obj.setFont("Helvetica", 8)
            canvas_obj.drawString(viewport.paper_rect.x(), 
                                viewport.paper_rect.y() - 10, viewport.title)
                                
    def _draw_cad_content(self, canvas_obj, cad_data: Dict[str, Any], 
                         layer_visibility: Dict[str, bool]):
        """Draw CAD content (devices, lines, etc.)."""
        # Draw devices
        devices = cad_data.get('devices', [])
        for device in devices:
            layer = device.get('layer', 'FA-DEVICES')
            if layer_visibility.get(layer, True):
                self._draw_device(canvas_obj, device)
                
        # Draw connections/wires
        connections = cad_data.get('connections', [])
        for connection in connections:
            layer = connection.get('layer', 'FA-WIRING')
            if layer_visibility.get(layer, True):
                self._draw_connection(canvas_obj, connection)
                
        # Draw floor plan elements
        floor_plan = cad_data.get('floor_plan', [])
        for element in floor_plan:
            layer = element.get('layer', 'A-WALL')
            if layer_visibility.get(layer, True):
                self._draw_floor_plan_element(canvas_obj, element)
                
    def _draw_device(self, canvas_obj, device: Dict[str, Any]):
        """Draw a fire alarm device."""
        x = device.get('x', 0)
        y = device.get('y', 0)
        symbol = device.get('symbol', 'DEV')
        device_type = device.get('type', 'Device')
        
        # Set color based on device type
        if device_type == 'FACP':
            canvas_obj.setStrokeColor(red)
            canvas_obj.setFillColor(red)
        elif 'Detector' in device_type:
            canvas_obj.setStrokeColor(blue)
            canvas_obj.setFillColor(blue)
        else:
            canvas_obj.setStrokeColor(black)
            canvas_obj.setFillColor(black)
            
        # Draw device symbol (simplified - would be more complex in real implementation)
        canvas_obj.circle(x, y, 3, stroke=1, fill=1)
        
        # Add device label
        canvas_obj.setFont("Helvetica", 6)
        canvas_obj.drawString(x + 5, y + 5, symbol)
        
        # Add address if available
        address = device.get('address')
        if address:
            canvas_obj.drawString(x + 5, y - 5, f"#{address}")
            
    def _draw_connection(self, canvas_obj, connection: Dict[str, Any]):
        """Draw a wire connection."""
        path = connection.get('path', [])
        connection_type = connection.get('type', 'SLC')
        
        # Set line style based on connection type
        if connection_type == 'SLC':
            canvas_obj.setStrokeColor(red)
            canvas_obj.setLineWidth(1)
        elif connection_type == 'NAC':
            canvas_obj.setStrokeColor(blue)
            canvas_obj.setLineWidth(1)
        else:
            canvas_obj.setStrokeColor(black)
            canvas_obj.setLineWidth(0.5)
            
        # Draw path
        if len(path) >= 2:
            canvas_obj.beginPath()
            canvas_obj.moveTo(path[0]['x'], path[0]['y'])
            for point in path[1:]:
                canvas_obj.lineTo(point['x'], point['y'])
            canvas_obj.stroke()
            
    def _draw_floor_plan_element(self, canvas_obj, element: Dict[str, Any]):
        """Draw floor plan elements (walls, doors, etc.)."""
        element_type = element.get('type', 'line')
        
        canvas_obj.setStrokeColor(black)
        canvas_obj.setLineWidth(2)
        
        if element_type == 'line':
            start = element.get('start', {})
            end = element.get('end', {})
            canvas_obj.line(start.get('x', 0), start.get('y', 0),
                          end.get('x', 0), end.get('y', 0))
        elif element_type == 'rectangle':
            x = element.get('x', 0)
            y = element.get('y', 0)
            width = element.get('width', 0)
            height = element.get('height', 0)
            canvas_obj.rect(x, y, width, height)
            
    def _draw_title_block(self, canvas_obj, title_block: TitleBlock,
                         paper_width: float, paper_height: float):
        """Draw title block."""
        # Position title block in bottom right
        tb_width = 4 * inch
        tb_height = 2 * inch
        tb_x = paper_width - tb_width - 0.5 * inch
        tb_y = 0.5 * inch
        
        # Draw title block border
        canvas_obj.setStrokeColor(black)
        canvas_obj.setLineWidth(1)
        canvas_obj.rect(tb_x, tb_y, tb_width, tb_height)
        
        # Add title block text
        canvas_obj.setFont("Helvetica-Bold", 12)
        canvas_obj.drawString(tb_x + 10, tb_y + tb_height - 20, title_block.project_name)
        
        canvas_obj.setFont("Helvetica", 10)
        canvas_obj.drawString(tb_x + 10, tb_y + tb_height - 40, title_block.drawing_title)
        
        canvas_obj.setFont("Helvetica", 8)
        y_pos = tb_y + tb_height - 60
        
        fields = [
            f"Drawing No: {title_block.drawing_number}",
            f"Sheet: {title_block.sheet_number}",
            f"Scale: {title_block.scale}",
            f"Date: {title_block.date}",
            f"Drawn: {title_block.drawn_by}",
            f"Checked: {title_block.checked_by}",
            f"Rev: {title_block.revision}"
        ]
        
        for field in fields:
            canvas_obj.drawString(tb_x + 10, y_pos, field)
            y_pos -= 12


class PaperSpaceManager:
    """Manages paperspace layouts and PDF generation."""
    
    def __init__(self):
        self.layouts: Dict[str, PaperSpaceLayout] = {}
        self.default_layout = self._create_default_layout()
        
    def _create_default_layout(self) -> PaperSpaceLayout:
        """Create default fire alarm layout."""
        title_block = TitleBlock(
            project_name="Fire Alarm Project",
            drawing_title="Fire Alarm Plan",
            drawing_number="FA-100",
            sheet_number="1 of 1",
            scale="1/4\" = 1'-0\""
        )
        
        # Create main viewport
        main_viewport = Viewport(
            name="Main Plan",
            paper_rect=QRectF(inch, inch, 7*inch, 9*inch),
            model_rect=QRectF(0, 0, 100*12, 100*12),  # 100' x 100' in inches
            scale_factor=1.0/48.0,  # 1/4" = 1' scale
            layer_visibility={
                'FA-DEVICES': True,
                'FA-WIRING': True,
                'FA-PANELS': True,
                'A-WALL': True,
                'A-DOOR': True
            },
            title="Fire Alarm Floor Plan"
        )
        
        layout = PaperSpaceLayout(
            name="Fire Alarm Plan",
            paper_size=PaperSize.LETTER,
            orientation="Portrait",
            margin_inches=(0.5, 0.5, 0.5, 0.5),
            viewports=[main_viewport],
            title_block=title_block
        )
        
        return layout
        
    def create_layout(self, name: str, paper_size: PaperSize = PaperSize.LETTER,
                     orientation: str = "Portrait") -> PaperSpaceLayout:
        """Create a new paperspace layout."""
        title_block = TitleBlock(drawing_title=name)
        
        layout = PaperSpaceLayout(
            name=name,
            paper_size=paper_size,
            orientation=orientation,
            margin_inches=(0.5, 0.5, 0.5, 0.5),
            viewports=[],
            title_block=title_block
        )
        
        self.layouts[name] = layout
        return layout
        
    def add_viewport(self, layout_name: str, viewport: Viewport):
        """Add viewport to a layout."""
        if layout_name in self.layouts:
            self.layouts[layout_name].viewports.append(viewport)
            
    def generate_pdf(self, layout_name: str, filename: str, 
                    cad_data: Dict[str, Any] | None = None):
        """Generate PDF from layout."""
        layout = self.layouts.get(layout_name, self.default_layout)
        generator = PDFGenerator()
        generator.create_pdf(layout, filename, cad_data)
        
    def get_available_scales(self) -> List[str]:
        """Get list of available drawing scales."""
        return [scale.value for scale in DrawingScale]
        
    def calculate_scale_factor(self, scale: DrawingScale) -> float:
        """Calculate scale factor for drawing scale."""
        generator = PDFGenerator()
        return 1.0 / generator.scale_factors.get(scale, 48.0)
        
    def calculate_viewport_size(self, model_size: Tuple[float, float],
                              scale: DrawingScale,
                              max_paper_size: Tuple[float, float]) -> Tuple[float, float]:
        """Calculate optimal viewport size for model at given scale."""
        model_width, model_height = model_size
        max_width, max_height = max_paper_size
        
        generator = PDFGenerator()
        scale_factor = generator.scale_factors.get(scale, 48.0)
        
        # Calculate required paper size at scale
        paper_width = model_width / scale_factor
        paper_height = model_height / scale_factor
        
        # Constrain to maximum paper size
        if paper_width > max_width:
            ratio = max_width / paper_width
            paper_width = max_width
            paper_height *= ratio
            
        if paper_height > max_height:
            ratio = max_height / paper_height
            paper_height = max_height
            paper_width *= ratio
            
        return paper_width, paper_height