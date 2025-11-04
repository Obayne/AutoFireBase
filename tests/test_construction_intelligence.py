"""
Tests for AutoFire Construction Drawing Intelligence.
"""

import numpy as np

from autofire_construction_drawing_intelligence import (
    ArchitecturalSymbol,
    ConstructionDrawingIntelligence,
    DrawingElement,
    DrawingScale,
    DrawingType,
    TitleBlockInfo,
    enhance_autofire_with_construction_intelligence,
)


class TestConstructionDrawingIntelligence:
    """Test suite for ConstructionDrawingIntelligence class."""

    def test_init(self):
        """Test intelligence engine initialization."""
        intelligence = ConstructionDrawingIntelligence()
        assert intelligence.symbol_library is not None
        assert intelligence.line_weight_standards is not None
        assert intelligence.material_hatch_patterns is not None
        assert intelligence.scale_detection_patterns is not None

    def test_load_standard_symbols(self):
        """Test standard symbol library loading."""
        intelligence = ConstructionDrawingIntelligence()
        symbols = intelligence._load_standard_symbols()

        # Should have standard symbol categories
        assert "door" in symbols
        assert "window" in symbols
        assert "outlet" in symbols
        assert "smoke_detector" in symbols
        assert isinstance(symbols, dict)

    def test_load_line_weight_standards(self):
        """Test line weight standards loading."""
        intelligence = ConstructionDrawingIntelligence()
        standards = intelligence._load_line_weight_standards()

        # Should have standard line weights
        assert "heavy" in standards
        assert "medium" in standards
        assert "light" in standards
        assert "extra_light" in standards

        # Each should have thickness range and usage
        for weight, info in standards.items():
            assert "thickness_range" in info
            assert "usage" in info

    def test_load_material_patterns(self):
        """Test material hatch pattern loading."""
        intelligence = ConstructionDrawingIntelligence()
        patterns = intelligence._load_material_patterns()

        # Should have common materials
        assert "concrete" in patterns
        assert "brick" in patterns
        assert "insulation" in patterns
        assert "metal" in patterns
        assert "wood" in patterns
        assert "glass" in patterns

    def test_load_scale_patterns(self):
        """Test scale pattern loading."""
        intelligence = ConstructionDrawingIntelligence()
        patterns = intelligence._load_scale_patterns()

        # Should have list of regex patterns
        assert isinstance(patterns, list)
        assert len(patterns) > 0
        # Should include common architectural scales
        assert any("1/4" in p for p in patterns)
        assert any("1/8" in p for p in patterns)

    def test_extract_sheet_number(self):
        """Test sheet number extraction from text."""
        intelligence = ConstructionDrawingIntelligence()

        # Test various sheet number formats
        assert "A-101" in intelligence._extract_sheet_number("Sheet A-101 Floor Plan")
        assert "S001" in intelligence._extract_sheet_number("Structural S001")

        # Should handle no match
        result = intelligence._extract_sheet_number("No sheet number here")
        assert result == ""

    def test_classify_drawing_type_by_prefix(self):
        """Test drawing type classification by sheet prefix."""
        intelligence = ConstructionDrawingIntelligence()

        # Create mock title blocks with different prefixes
        architectural = TitleBlockInfo(sheet_number="A-101", sheet_title="Floor Plan")
        structural = TitleBlockInfo(sheet_number="S-001", sheet_title="Foundation Plan")
        electrical = TitleBlockInfo(sheet_number="E-201", sheet_title="Power Plan")
        mechanical = TitleBlockInfo(sheet_number="M-301", sheet_title="HVAC Plan")

        # Mock image for classification
        image = np.ones((500, 500, 3), dtype=np.uint8) * 255

        assert intelligence._classify_drawing_type(image, architectural) == DrawingType.FLOOR_PLAN
        assert intelligence._classify_drawing_type(image, structural) == DrawingType.STRUCTURAL
        assert intelligence._classify_drawing_type(image, electrical) == DrawingType.ELECTRICAL
        assert intelligence._classify_drawing_type(image, mechanical) == DrawingType.MECHANICAL

    def test_classify_drawing_type_by_title(self):
        """Test drawing type classification by title."""
        intelligence = ConstructionDrawingIntelligence()

        # Create title blocks with descriptive titles but no prefix
        floor_plan = TitleBlockInfo(sheet_number="1", sheet_title="First Floor Plan")
        elevation = TitleBlockInfo(sheet_number="2", sheet_title="North Elevation")
        section = TitleBlockInfo(sheet_number="3", sheet_title="Building Section")
        detail = TitleBlockInfo(sheet_number="4", sheet_title="Wall Detail")

        image = np.ones((500, 500, 3), dtype=np.uint8) * 255

        assert intelligence._classify_drawing_type(image, floor_plan) == DrawingType.FLOOR_PLAN
        assert intelligence._classify_drawing_type(image, elevation) == DrawingType.ELEVATION
        assert intelligence._classify_drawing_type(image, section) == DrawingType.SECTION
        assert intelligence._classify_drawing_type(image, detail) == DrawingType.DETAIL

    def test_get_drawing_classification(self):
        """Test drawing classification information retrieval."""
        intelligence = ConstructionDrawingIntelligence()

        # Test floor plan classification
        floor_plan_info = intelligence._get_drawing_classification(DrawingType.FLOOR_PLAN)
        assert floor_plan_info["discipline"] == "Architectural"
        assert "walls" in floor_plan_info["reading_priority"]

        # Test structural classification
        structural_info = intelligence._get_drawing_classification(DrawingType.STRUCTURAL)
        assert structural_info["discipline"] == "Structural Engineering"
        assert "foundations" in structural_info["reading_priority"]

    def test_analyze_drawing_professionally(self):
        """Test professional drawing analysis."""
        intelligence = ConstructionDrawingIntelligence()

        # Create test image
        image = np.ones((500, 500, 3), dtype=np.uint8) * 255

        result = intelligence.analyze_drawing_professionally(image)

        # Should return comprehensive analysis
        assert "title_block" in result
        assert "drawing_type" in result
        assert "drawing_classification" in result
        assert "legend_info" in result
        assert "symbols" in result
        assert "orientation" in result
        assert "grid_system" in result
        assert "structural_elements" in result
        assert "mep_elements" in result
        assert "coordination_issues" in result
        assert "scale_info" in result
        assert "professional_notes" in result
        assert "quality_flags" in result
        assert "industry_compliance" in result

    def test_enhance_autofire_visual_analysis(self):
        """Test AutoFire results enhancement."""
        intelligence = ConstructionDrawingIntelligence()

        # Mock AutoFire results
        autofire_results = {
            "rooms": [],
            "walls": [],
            "devices": [],
        }

        # Create test image
        image = np.ones((500, 500, 3), dtype=np.uint8) * 255

        enhanced = intelligence.enhance_autofire_visual_analysis(autofire_results, image)

        # Should enhance with professional analysis
        assert "professional_analysis" in enhanced
        assert "enhanced_rooms" in enhanced
        assert "enhanced_walls" in enhanced
        assert "device_validation" in enhanced
        assert "construction_intelligence" in enhanced

        # Should preserve original data
        assert "rooms" in enhanced
        assert "walls" in enhanced
        assert "devices" in enhanced

    def test_integration_function(self):
        """Test main integration function."""
        autofire_results = {"rooms": [], "walls": []}
        image = np.ones((500, 500, 3), dtype=np.uint8) * 255

        enhanced = enhance_autofire_with_construction_intelligence(autofire_results, image)

        # Should return enhanced results
        assert isinstance(enhanced, dict)
        assert "professional_analysis" in enhanced
        assert "construction_intelligence" in enhanced


class TestDrawingTypeEnum:
    """Test DrawingType enumeration."""

    def test_drawing_types_defined(self):
        """Test that all expected drawing types are defined."""
        assert DrawingType.SITE_PLAN.value == "site_plan"
        assert DrawingType.FLOOR_PLAN.value == "floor_plan"
        assert DrawingType.ELEVATION.value == "elevation"
        assert DrawingType.SECTION.value == "section"
        assert DrawingType.DETAIL.value == "detail"
        assert DrawingType.REFLECTED_CEILING_PLAN.value == "rcp"
        assert DrawingType.STRUCTURAL.value == "structural"
        assert DrawingType.MECHANICAL.value == "mechanical"
        assert DrawingType.ELECTRICAL.value == "electrical"
        assert DrawingType.PLUMBING.value == "plumbing"
        assert DrawingType.CIVIL.value == "civil"
        assert DrawingType.LANDSCAPE.value == "landscape"
        assert DrawingType.SURVEY.value == "survey"
        assert DrawingType.GENERAL.value == "general"


class TestDrawingScaleEnum:
    """Test DrawingScale enumeration."""

    def test_architectural_scales(self):
        """Test architectural scale definitions."""
        assert '1/8"' in DrawingScale.ARCH_1_8.value
        assert '1/4"' in DrawingScale.ARCH_1_4.value
        assert '1/2"' in DrawingScale.ARCH_1_2.value

    def test_engineering_scales(self):
        """Test engineering scale definitions."""
        assert "10'" in DrawingScale.ENG_1_10.value
        assert "20'" in DrawingScale.ENG_1_20.value
        assert "100'" in DrawingScale.ENG_1_100.value

    def test_metric_scales(self):
        """Test metric scale definitions."""
        assert DrawingScale.METRIC_1_100.value == "1:100"
        assert DrawingScale.METRIC_1_50.value == "1:50"
        assert DrawingScale.METRIC_1_10.value == "1:10"

    def test_special_scales(self):
        """Test special scale values."""
        assert DrawingScale.NTS.value == "NTS"


class TestDataClasses:
    """Test data classes for construction drawing intelligence."""

    def test_title_block_info(self):
        """Test TitleBlockInfo dataclass."""
        info = TitleBlockInfo(
            project_name="Test Project",
            sheet_number="A-101",
            sheet_title="First Floor Plan",
            drawing_scale='1/4" = 1\'-0"',
            date="2024-01-01",
            revision="Rev 2",
            architect_engineer="Test Architect",
            discipline="Architectural",
            north_arrow_present=True,
        )

        assert info.project_name == "Test Project"
        assert info.sheet_number == "A-101"
        assert info.drawing_scale == '1/4" = 1\'-0"'
        assert info.north_arrow_present is True

    def test_architectural_symbol(self):
        """Test ArchitecturalSymbol dataclass."""
        symbol = ArchitecturalSymbol(
            symbol_type="door",
            location=(100, 200),
            confidence=0.9,
            description="Standard swing door",
            standard_meaning="Entry/exit point",
        )

        assert symbol.symbol_type == "door"
        assert symbol.location == (100, 200)
        assert symbol.confidence == 0.9
        assert len(symbol.description) > 0
        assert len(symbol.standard_meaning) > 0

    def test_drawing_element(self):
        """Test DrawingElement dataclass."""
        element = DrawingElement(
            element_type="wall",
            coordinates=[(0, 0), (100, 0)],
            line_weight="Heavy",
            line_type="Solid",
            material_hatch="concrete",
            dimension_info={"length": 100},
        )

        assert element.element_type == "wall"
        assert len(element.coordinates) == 2
        assert element.line_weight == "Heavy"
        assert element.line_type == "Solid"
        assert element.material_hatch == "concrete"
        assert element.dimension_info["length"] == 100
